"""Exercise release safety with a fake registry; never publish real images."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).with_name("image-release.sh").resolve()
A = "sha256:" + "a" * 64
B = "sha256:" + "b" * 64
FAKE_DOCKER = '''#!/usr/bin/env python3
import json, os, sys
from pathlib import Path
p = Path(os.environ["REGISTRY"])
state = json.loads(p.read_text())
args = sys.argv[1:]
if args[:3] == ["buildx", "imagetools", "inspect"]:
    ref = args[3]
    tag = ref.split(":")[-1]
    if os.environ.get("DENIED") == tag:
        sys.exit("unauthorized: authentication required")
    digest = ref.split("@", 1)[1] if "@" in ref else state.get(tag)
    if not digest or digest not in state.values():
        sys.exit("manifest unknown")
    print(json.dumps({"digest": digest}))
elif args[:3] == ["buildx", "imagetools", "create"]:
    assert "--prefer-index=false" in args
    tag = args[args.index("--tag") + 1].split(":")[-1]
    state[tag] = args[-1].split("@", 1)[1]
    p.write_text(json.dumps(state))
else:
    sys.exit("unexpected docker call")
'''


class ReleaseTests(unittest.TestCase):
    def run_release(self, operation="release", version="2026.11.24.01", source="staging",
                    extra=None, denied="", ref="refs/heads/main", event="push"):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            docker = root / "docker"
            docker.write_text(FAKE_DOCKER)
            docker.chmod(0o755)
            state = {"staging": A, "latest": B, "stable": B, **(extra or {})}
            registry = root / "registry.json"
            registry.write_text(json.dumps(state))
            env = dict(os.environ, PATH=f"{root}:{os.environ['PATH']}",
                       REGISTRY=str(registry), GITHUB_REPOSITORY="Owner/Image",
                       GITHUB_STEP_SUMMARY=str(root / "summary"),
                       OPERATION=operation, VERSION=version, SOURCE=source, DENIED=denied,
                       GITHUB_REF=ref, GITHUB_EVENT_NAME=event)
            date = root / "date"
            date.write_text('#!/bin/bash\nif [[ "$*" == "-u +%Y.%m.%d" ]]; then echo 2026.11.24; else exec /usr/bin/date "$@"; fi\n')
            date.chmod(0o755)
            result = subprocess.run(["bash", str(SCRIPT)], env=env,
                                    capture_output=True, text=True)
            return result, state, json.loads(registry.read_text())

    def test_main_build_publishes_date_and_latest_without_stable(self):
        result, before, after = self.run_release(
            operation="publish", source="build-42-1", extra={"build-42-1": A})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(after, {**before, "2026.11.24.01": A, "latest": A})

    def test_next_build_increments_daily_sequence(self):
        result, before, after = self.run_release(
            operation="publish", source="build-42-1",
            extra={"build-42-1": A, "2026.11.24.01": B})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(after, {**before, "2026.11.24.02": A, "latest": A})

    def test_retry_reuses_date_tag_for_same_digest(self):
        result, before, after = self.run_release(
            operation="publish", source="build-42-1",
            extra={"build-42-1": A, "2026.11.24.01": A})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(after, {**before, "latest": A})

    def test_daily_sequence_exhaustion_changes_nothing(self):
        result, before, after = self.run_release(
            operation="publish", source="build-42-1",
            extra={"build-42-1": A, **{f"2026.11.24.{n:02}": B for n in range(1, 100)}})
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("99", result.stderr)
        self.assertEqual(after, before)

    def test_auto_registry_error_does_not_allocate_or_update_latest(self):
        result, before, after = self.run_release(
            operation="publish", source="build-42-1", extra={"build-42-1": A},
            denied="2026.11.24.01")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(after, before)

    def test_auto_publish_requires_unique_build_source(self):
        result, before, after = self.run_release(operation="publish", source="latest")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(after, before)

    def test_auto_publish_rejects_branches_and_pull_requests(self):
        for kwargs in ({"ref": "refs/heads/feature"}, {"event": "pull_request"}):
            with self.subTest(**kwargs):
                result, before, after = self.run_release(
                    operation="publish", source="build-42-1", extra={"build-42-1": A}, **kwargs)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(after, before)

    def test_new_day_starts_at_first_sequence(self):
        result, before, after = self.run_release(
            operation="publish", source="build-42-1",
            extra={"build-42-1": A, "2026.11.23.99": B})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(after, {**before, "2026.11.24.01": A, "latest": A})

    def test_manual_stable_promotion_from_calendar_version(self):
        result, before, after = self.run_release(
            source="2026.11.24.01", extra={"2026.11.24.01": A})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(after, {**before, "stable": A})

    def test_release_promotes_exact_source(self):
        result, before, after = self.run_release()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(after, {**before, "2026.11.24.01": A, "stable": A})

    def test_repeat_same_release(self):
        result, _, after = self.run_release(extra={"2026.11.24.01": A})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(after["stable"], A)

    def test_existing_version_cannot_change(self):
        result, before, after = self.run_release(extra={"2026.11.24.01": B})
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(after, before)

    def test_rollback_only_moves_stable(self):
        result, before, after = self.run_release(operation="rollback", extra={"2026.11.24.01": A})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(after, {**before, "stable": A})

    def test_missing_rollback_version_changes_nothing(self):
        result, before, after = self.run_release(operation="rollback")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(after, before)

    def test_registry_auth_failure_is_not_missing_version(self):
        result, before, after = self.run_release(denied="2026.11.24.01")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(after, before)

    def test_padded_date_and_leap_day(self):
        for version in ("2027.01.05.01", "2028.02.29.99"):
            with self.subTest(version=version):
                result, _, after = self.run_release(version=version)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(after[version], A)

    def test_legacy_rollback(self):
        for version in ("1.2.3", "2026.11.2401"):
            with self.subTest(version=version):
                result, before, after = self.run_release(
                    operation="rollback", version=version, extra={version: A})
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(after, {**before, "stable": A})

    def test_invalid_calendar_release_changes_nothing(self):
        for version in ("1.2.3", "2026.11.2401", "2026.02.29.01",
                        "2026.04.31.01", "2026.13.01.01", "2026.00.01.01",
                        "2026.01.00.01", "2026.1.05.01", "2026.01.5.01",
                        "2026.01.05.00", "2026.01.05.1", "2026.01.05.100"):
            for operation in ("release", "rollback"):
                if operation == "rollback" and version.count(".") == 2:
                    continue
                with self.subTest(version=version, operation=operation):
                    result, before, after = self.run_release(version=version, operation=operation)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertEqual(after, before)

    def test_bad_inputs_change_nothing(self):
        for kwargs in ({"version": "v2026.11.24.01"}, {"version": "02026.11.24.01"},
                       {"source": "stable"}, {"source": "$(touch nope)"},
                       {"operation": "delete"}):
            with self.subTest(**kwargs):
                result, before, after = self.run_release(**kwargs)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(after, before)

    def test_missing_build_changes_nothing(self):
        result, before, after = self.run_release(source="build-42-1")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(after, before)


if __name__ == "__main__":
    unittest.main()
