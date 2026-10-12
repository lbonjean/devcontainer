# Chromium image dependencies and Windows Hello — 2026-10-12

## User request (verbatim)

in de dockerfile ontbreken wat zaken, die gerapporteerd werden. De Dockerfile zou aangepast moeten worden. Ik zouook graag hebbendat als chromium start in een soort rdsachtig venster de webauthn naar de host wordt gebracht zodat ik de keys uit windows hello kan gebruiken.
# Chromium in the devcontainer

## Installation (Ubuntu 24.04)

Run these commands in PowerShell from the repository root. Project npm
dependencies must already be installed (`npm ci --no-audit --no-fund` on a fresh
checkout).

```powershell
npx --no-install playwright install chromium --no-shell
npx --no-install playwright install-deps chromium
```

The first command downloads the Chromium version pinned by this project's
Playwright dependency into the current user's `~/.cache/ms-playwright` directory.
The second installs the required Linux libraries and fonts using apt and sudo.
Run it as the normal container user: Playwright invokes sudo itself. In this
container, `sudo npx ...` does not work because npx is not on sudo's PATH.
Both commands completed successfully on 2026-10-12.

## Open an interactive login window

```powershell
npx --no-install playwright open --browser chromium https://purple-bay-07020ef03.3.azurestaticapps.net/.auth/login/aad
```

A visible browser needs host display forwarding. This container has `DISPLAY=:0`
and an X11 socket at `/tmp/.X11-unix/X0`; a headed Playwright browser launched
successfully and reached the Microsoft login page. If a rebuilt container lacks
display forwarding, installing Chromium alone will not create a visible window.
Xvfb is useful for automated tests but does not provide a window the user can see.

Enter credentials manually in the browser. Do not save authentication traces,
videos, screenshots, or storage-state files during login investigation.

## Rebuild follow-up

These installations affect the running container and user browser cache; they
were not added to the devcontainer image. Rerun the commands after rebuilding if
the packages or cache are missing. Consider baking Linux browser dependencies
into the base image for repeatable startup. No browser prerequisite remains
missing in the current container.

For the shared-browser investigation, `xdotool` was also installed to navigate
the existing Chromium window through X11. This is optional and is not needed
for Chromium or Playwright itself:

```powershell
sudo -n apt-get install --yes --no-install-recommends xdotool
```

## Delivered

- Added the Ubuntu 24.04 Playwright Chromium runtime libraries and fonts to `.devcontainer/Dockerfile`. Chromium itself remains installed by the consuming project's Playwright version, so the Docker image does not pin a browser release.
- Added checks for those packages to `.devcontainer/test-image.sh` and recorded the X11/WebAuthn constraint in `prompts/LESSONS_LEARNED.md`.
- X11 display forwarding can show a headed Chromium window, but it does not forward the Windows Hello platform authenticator. Use a Windows-host browser, or a Windows RDP session configured for WebAuthn redirection; an RDS-style Linux/Chromium window alone will not make Windows Hello available.
- Validation: `bash -n .devcontainer/test-image.sh`, `git diff --check`, and editor error checks passed. An apt simulation against the agent's Ubuntu 26.04 package indexes accepted the names, but this is not the target Ubuntu 24.04 image. The Ubuntu 24.04 Docker build was stopped after roughly six minutes of package downloads because the network connection was slow; the image smoke test was therefore not run.
- Preserved the existing untracked `.devcontainer/devcontainer-lock.json` without modifying it. No commit was created.
