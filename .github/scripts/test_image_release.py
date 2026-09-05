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
    def run_release(self, operation="release", version="1.2.3", source="staging",
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
        self.assertEqual(after, {**before, "1.2.3": A, "stable": A})

    def test_repeat_same_release(self):
        result, _, after = self.run_release(extra={"1.2.3": A})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(after["stable"], A)

    def test_existing_version_cannot_change(self):
        result, before, after = self.run_release(extra={"1.2.3": B})
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(after, before)

    def test_rollback_only_moves_stable(self):
        result, before, after = self.run_release(operation="rollback", extra={"1.2.3": A})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(after, {**before, "stable": A})

    def test_missing_rollback_version_changes_nothing(self):
        result, before, after = self.run_release(operation="rollback")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(after, before)

    def test_registry_auth_failure_is_not_missing_version(self):
        result, before, after = self.run_release(denied="1.2.3")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(after, before)

    def test_bad_inputs_change_nothing(self):
        for kwargs in ({"version": "v1.2.3"}, {"version": "01.2.3"},
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
