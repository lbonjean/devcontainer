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
                    extra=None, denied=""):
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
                       OPERATION=operation, VERSION=version, SOURCE=source, DENIED=denied)
            result = subprocess.run(["bash", str(SCRIPT)], env=env,
                                    capture_output=True, text=True)
            return result, state, json.loads(registry.read_text())

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
