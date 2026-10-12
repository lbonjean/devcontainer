# Validation — 2026-10-12

Scope: add repeatable Ubuntu 24.04 system dependencies for the project's
Playwright Chromium browser and record whether the host Windows Hello
platform authenticator can be used from the Linux browser window.

| Check | Result |
| --- | --- |
| `bash -n .devcontainer/test-image.sh` | Passed |
| `git diff --check` | Passed |
| Editor error checks for changed files | No errors reported |
| `apt-get install --simulate` for the added package names | Resolved against the agent host's Ubuntu 26.04 package indexes; this did not validate the Ubuntu 24.04 target |
| Agent Docker build from `ubuntu:24.04` | Stopped after roughly six minutes because package downloads were too slow; the user later rebuilt with VS Code's Open in Container action |
| `.devcontainer/test-image.sh` in the user's rebuilt image | Passed in a temporary container using the workspace image and repository bind mount |

The Dockerfile adds Playwright's Ubuntu 24.04 Chromium runtime libraries and
font packages, but not the browser binary. The project should continue to use
`npx --no-install playwright install chromium --no-shell` so the installed
browser matches its Playwright dependency. The rebuilt image passed the package
presence assertions, full tool/module checks, and the local Functions HTTP
checks. The invocation returned `Hello, SmokeTest.` and the PowerShell worker
reported version `7.6.5`. Corepack downloaded Yarn and pnpm during the smoke test
because those package-manager versions were not cached in the image; both checks
passed. Expected noninteractive Bash job-control notices were printed.

The reported headed browser used X11 display forwarding. That forwards the
window and user input only; it does not forward Windows Hello/FIDO platform
authentication into the Linux browser. A Windows-host browser or a supported
Windows RDP session with WebAuthn redirection is required for that authenticator.
No RDP server or host-authenticator forwarding was added to the container.

The initial smoke-test attempt from the agent shell failed before tests started
because that shell runs as host user `luc`, not container user `vscode`. The
rebuilt image was then tested directly with Docker, without restarting the
stopped VS Code container. No commit was created. The pre-existing untracked
`.devcontainer/devcontainer-lock.json` was left untouched.
