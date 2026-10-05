# Ubuntu 24.04 tests and push/PR reuse — 2026-10-05

## User requests (verbatim)

```text
ik heb de image aangepast om naar ubuntu 24.04 te gaan. Kan je de setup nakijken en ook de tests draaien, zodat de github action goed kan testen?
De github action doe een test bij push en pull request. Als de test bij de push geslaagd is dient de test bij het pull request niet te gebeuren als er geen commits mee zijn bijgekomen.
Kan je eerst de test nakijken, en daarna de github action / workflow aanpassen?
```

Read-only attachments supplied snapshots of the Bash and PowerShell image tests;
they were inspected but not modified.

```text
de build is gelukt, enkel de test moet gebeuren.
```

```text
je mag niks aanpassen aan de docker file. Je mag wel pakketten installeren in de huidige container.
```

## Decisions and delivered result

- Tested the existing Ubuntu 24.04 container; no image rebuild was attempted.
- With user approval, installed jq locally for release tests and added the
  Docker-outside-of-Docker Feature to the local devcontainer configuration for a
  future rebuild with an available host Docker daemon.
- Dockerfile is unchanged. An intermediate jq addition was completely reverted
  when the user clarified that Dockerfile changes were prohibited; jq is not an
  image-test requirement.
- Strengthened the Bash image test with failure locations, a nonempty SDK check,
  exact Core Tools/worker versions, Python/PyYAML and bwrap/tmux availability.
  Retained the existing PowerShell module/prompt test and disabled automatic
  profile behavior.
- Added a paginated GitHub Actions lookup and eight unit tests. PRs reuse only
  successful completed push runs of this workflow for their exact same-repository
  head SHA and branch. Other PRs still build/test the merge checkout.
  Push/scheduled/manual builds and publishing behavior remain unchanged.
  API errors fail explicitly. Workflow safeguard tests always run, and the
  existing check name is preserved even when image tests are reused.
- Updated README for Ubuntu 24.04, local Docker access, current profile behavior,
  test prerequisites and the intentional omission of synthetic-merge/base-only
  tests when reusing push results. Added durable lessons and validation records.

## Validation and corrections

- Initial release suite: three failures because jq was missing. After local
  installation, all eight release safeguard tests passed.
- The baseline image test overlapped apt installation and detected the populated
  package lists. Cleaning installation caches and rerunning passed.
- An added executable check initially used the package name bubblewrap rather
  than bwrap; corrected and reran successfully.
- Final image smoke test passed, including all seven user PowerShell modules,
  HelloWorld HTTP invocation and worker version 7.6.5.
- All 16 workflow/release unit tests passed using the existing unittest runner.
  The editor test tool reported no tests found; command-line discovery succeeded.
- Bash syntax, workflow YAML/conditional checks and actionlint 1.7.12 passed.
  actionlint was temporarily downloaded and checksum-verified; optional external
  ShellCheck integration was disabled because ShellCheck is not installed.
- git diff --check and the staged whitespace check passed. Dockerfile's diff is
  empty. Changes were committed locally; nothing was pushed or deployed.
- Live workflow inspection was unavailable: gh had no authentication, and the
  existing Git credential helper supplied no usable credential. No login flow
  was initiated.
- Setup-doctor reported one pre-existing failure: /home/vscode/.codex/AGENTS.md
  does not resolve to /home/vscode/.agents/AGENTS.md. Remaining setup checks
  passed, including an actual Bubblewrap sandbox launch.
- Expected noninteractive Bash job-control notices remained; no image-test
  failure resulted. Docker client/daemon/socket are absent from this running
  container; the new Feature needs a rebuild and host Docker.

See [validation details](../../.development-history/2026-10-05-ubuntu2404/research/validation.md).
