# npm and Oh My Posh — 2026-09-05

## User request (verbatim)

```text
# Context from my IDE setup:

## Active file: .devcontainer/devcontainer.json

## Open tabs:
- devcontainer.json: .devcontainer/devcontainer.json
- Dockerfile: .devcontainer/Dockerfile
- devcontainer.yml: .github/workflows/devcontainer.yml
- image-release.yml: .github/workflows/image-release.yml
- test-image.ps1: .devcontainer/test-image.ps1

## My request:
node. je geralteerd:

- in de devcontainer via de docker file zit blijkbaar een oudere versie van npm, die mag up to date gemaakt worden
- dit mag ook uitgevoerd worden: npm install -g @azure/static-web-apps-cli
- alle npm packages mogen geupdate worden.

powershell geralteerd:

- de oh-my-posh mag ook toegevoegd worden
```

## Implementation and decisions

- Update Dockerfile installation to resolve latest npm, Yarn, pnpm and Azure Static Web Apps CLI, then update global dependencies. No project package manifests exist. Preserve the existing Node 22.22.2 pin.
- Use a temporary npm bootstrap outside the global prefix; direct npm 10.9.7 self-update failed with missing `promise-retry`, including with `--no-fund`. Remove bootstrap and caches in the installation layer.
- npm 12 blocks dependency install scripts by default. Allow only Yarn and keytar for these global installs; install libsecret development files and pkg-config for SWA's native dependency.
- Install standalone Oh My Posh globally and initialize it in the image-owned PowerShell profile. Document local Nerd Font configuration.
- Extend existing smoke checks with SWA, global package listing, native keytar loading and PowerShell prompt initialization. Update README.
- Initial Docker and registry reads were blocked by the sandbox. Authorized elevated Docker access worked. Interrupted an intermediate build to correct the skipped native install scripts.

## Validation

- PowerShell scripts parse successfully; initial `git diff --check` passed.
- Final Docker build and smoke tests pending at this point; results appended below.

## Final results and delivered response

- Docker image `devcontainer:npm-posh-test` built successfully; full existing smoke suite passed as vscode, including native keytar import, Oh My Posh PowerShell initialization, all seven module imports, profile history configuration, and a real Functions HTTP response. Build reused unchanged base/apt/.NET layers while rebuilding changed installation layers.
- Verified npm 12.0.2, Yarn 1.22.22, pnpm 11.25.0, SWA CLI 2.0.10, Corepack 0.36.0, and Oh My Posh 31.1.3. `npm outdated -g --depth=0` returned no outdated packages (exit 0).
- Remaining upstream warnings: SWA transitive dependencies include deprecated prebuild-install, inflight, glob, rimraf and sudo-prompt; Azure CLI emits its existing experimental config and Python SyntaxWarnings. Interactive Bash smoke check emits expected no-TTY job-control warnings. Corepack downloaded its Yarn/pnpm distributions during first execution.
- PowerShell syntax validation and final `git diff --check` passed. Temporary build/smoke output files removed after summarizing. Durable bootstrap/script-policy findings added to LESSONS_LEARNED.md.
- Delivered: updated packages and prompt setup are committed locally; rebuild/recreate the devcontainer to consume changes. No push or publication performed.
