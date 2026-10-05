"""Reuse a successful push run only for the exact same in-repository PR head."""
import json
import os
from pathlib import Path
import subprocess
from urllib.parse import urlencode


def successful_push(event: dict, repository: str) -> dict | None:
    head = event["pull_request"]["head"]
    if head["repo"] is None or head["repo"]["full_name"] != repository:
        return None

    query = urlencode({
        "event": "push",
        "status": "success",
        "head_sha": head["sha"],
        "branch": head["ref"],
        "per_page": 100,
    })
    endpoint = (
        f"repos/{repository}/actions/workflows/devcontainer.yml/runs?{query}"
    )
    pages = json.loads(subprocess.check_output(
        ["gh", "api", "--paginate", "--slurp", endpoint], text=True
    ))
    for page in pages:
        for run in page["workflow_runs"]:
            if (
                run["event"] == "push"
                and run["status"] == "completed"
                and run["conclusion"] == "success"
                and run["head_sha"] == head["sha"]
                and run["head_branch"] == head["ref"]
                and run["head_repository"] is not None
                and run["head_repository"]["full_name"] == repository
            ):
                return run
    return None


def main() -> None:
    event = json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text())
    run = successful_push(event, os.environ["GITHUB_REPOSITORY"])
    with Path(os.environ["GITHUB_OUTPUT"]).open("a") as output:
        output.write(f"skip={'true' if run else 'false'}\n")
    if run:
        message = (
            f"Reusing successful push tests for PR head "
            f"`{event['pull_request']['head']['sha']}`: {run['html_url']}. "
            "No new image build or smoke test is needed."
        )
    else:
        message = "No successful push run for this PR head; build and test the PR."
    print(message)
    with Path(os.environ["GITHUB_STEP_SUMMARY"]).open("a") as summary:
        summary.write(f"### PR image validation\n\n{message}\n")


if __name__ == "__main__":
    main()
