"""Test push-result reuse without GitHub access."""
import copy
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import check_push_test

REPOSITORY = "owner/image"
SHA = "a" * 40
EVENT = {"pull_request": {"head": {
    "sha": SHA, "ref": "ubuntu2404", "repo": {"full_name": REPOSITORY},
}}}
RUN = {
    "event": "push", "status": "completed", "conclusion": "success",
    "head_sha": SHA, "head_branch": "ubuntu2404",
    "head_repository": {"full_name": REPOSITORY},
    "html_url": "https://github.com/owner/image/actions/runs/123",
}


class PushReuseTests(unittest.TestCase):
    def lookup(self, runs, event=None):
        with patch("check_push_test.subprocess.check_output",
                   return_value=json.dumps(runs)) as api:
            result = check_push_test.successful_push(event or EVENT, REPOSITORY)
        return result, api

    def test_exact_success_is_reused(self):
        result, api = self.lookup([{"workflow_runs": [RUN]}])
        self.assertEqual(result, RUN)
        args = api.call_args.args[0]
        self.assertEqual(args[:4], ["gh", "api", "--paginate", "--slurp"])
        self.assertIn("workflows/devcontainer.yml/runs?", args[4])
        self.assertIn(f"head_sha={SHA}", args[4])
        self.assertIn("event=push", args[4])
        self.assertIn("branch=ubuntu2404", args[4])

    def test_no_push_builds_pr(self):
        self.assertIsNone(self.lookup([{"workflow_runs": []}])[0])

    def test_new_commit_builds_pr(self):
        event = copy.deepcopy(EVENT)
        event["pull_request"]["head"]["sha"] = "b" * 40
        self.assertIsNone(self.lookup([{"workflow_runs": [RUN]}], event)[0])

    def test_nonmatching_runs_cannot_skip(self):
        for field, value in (
            ("event", "pull_request"), ("event", "workflow_dispatch"),
            ("status", "in_progress"), ("status", "queued"),
            ("conclusion", "failure"), ("conclusion", "cancelled"),
            ("conclusion", "skipped"), ("head_sha", "b" * 40),
            ("head_branch", "another-branch"), ("head_repository", None),
            ("head_repository", {"full_name": "fork/image"}),
        ):
            with self.subTest(field=field, value=value):
                run = {**RUN, field: value}
                self.assertIsNone(self.lookup([{"workflow_runs": [run]}])[0])

    def test_fork_or_deleted_repository_does_not_query_api(self):
        for repository in (None, {"full_name": "fork/image"}):
            event = copy.deepcopy(EVENT)
            event["pull_request"]["head"]["repo"] = repository
            result, api = self.lookup([{"workflow_runs": [RUN]}], event)
            self.assertIsNone(result)
            api.assert_not_called()

    def test_pagination_finds_success(self):
        result, _ = self.lookup([
            {"workflow_runs": [{**RUN, "conclusion": "failure"}]},
            {"workflow_runs": [RUN]},
        ])
        self.assertEqual(result, RUN)

    def test_api_failure_is_not_silently_ignored(self):
        with patch("check_push_test.subprocess.check_output",
                   side_effect=subprocess.CalledProcessError(1, ["gh", "api"])):
            with self.assertRaises(subprocess.CalledProcessError):
                check_push_test.successful_push(EVENT, REPOSITORY)

    def test_main_outputs_decision_and_summary(self):
        for run, expected in ((RUN, "true"), (None, "false")):
            with self.subTest(skip=expected), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                event_file = root / "event.json"
                event_file.write_text(json.dumps(EVENT))
                with patch.dict(os.environ, {
                    "GITHUB_EVENT_PATH": str(event_file),
                    "GITHUB_REPOSITORY": REPOSITORY,
                    "GITHUB_OUTPUT": str(root / "output"),
                    "GITHUB_STEP_SUMMARY": str(root / "summary"),
                }), patch("check_push_test.successful_push", return_value=run):
                    check_push_test.main()
                self.assertEqual((root / "output").read_text(), f"skip={expected}\n")
                summary = (root / "summary").read_text()
                self.assertIn("PR image validation", summary)
                self.assertIn(RUN["html_url"] if run else "build and test the PR", summary)


if __name__ == "__main__":
    unittest.main()
