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

## Follow-up: authenticated push and workflow inspection

### User requests (verbatim)

```text
met de files ~/dotfiles/bin/set-gh-token.ps1 en/of ~/dotfiles/bin/set-gh-token.sh kan je het gh token goed zetten in de sessie waar je zit. Je mag pushen om de build na te kijken.
```

The user also supplied a read-only Dockerfile snapshot; no Dockerfile changes
were requested or made.

```text
ik doe de powershell versie van het script, en dan toont het mij hoe ik aangelogd ben. In deze container, dus het lijkt wel te werken.
```

```text
zeg laar wat ik van git/gh commandos moet uitvoeren en ik zal het regelen.
```

### Result and validation

- The worktree was clean at the start, on ubuntu2404 tracking origin/ubuntu2404.
- Inspected both token helpers and attempted each in the agent shell. Both failed
  while retrieving the Git credential; no push occurred.
- Verified that the configured VS Code helper and Node binary exist, but its
  required REMOTE_CONTAINERS_IPC variable is absent from the agent environment.
  This explains why authentication can work in the user's terminal and fail in
  this execution environment. No credentials were printed or persisted.
- The user chose to run the authenticated commands themselves. Provided
  PowerShell commands to initialize the token in their session, push the current
  branch, locate the push workflow for the exact HEAD SHA, watch its result and
  retrieve failed-step logs if necessary. Workflow execution remains unverified
  until those commands are run.
- Dockerfile and implementation remain unchanged. Recorded this verified
  environment limitation as a reusable lesson. Documentation-only follow-up
  committed locally after whitespace validation; nothing pushed by the agent.
