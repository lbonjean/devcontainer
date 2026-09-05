# Devcontainer optimization — 2026-09-05

## User request (verbatim)

```text
# Context from my IDE setup:

## Active file: .devcontainer/devcontainer.json

## Open tabs:
- devcontainer.json: .devcontainer/devcontainer.json
- devcontainer-lock.json: .devcontainer/devcontainer-lock.json

## My request:
ik zou graag deze devcontainer optimaliseren. alles wat in de features zit zou ik graag verhuizen naar de docker file, zodat ik later als ik een devcontainer maak op basis van deze image ik nog features kan toevoegen.
Let erop ook dat de uiteindelijke image zo klein mogelijk moet zijn. Alles wat wordt gedownload,cache wat niet nodig is voor de werking dient verwijderd te worden, via de docker file zodat het niet mee in de layers komt. Check dat de container kan builden.
```

## Work and decisions

- Moved tool installation from `devcontainer.json` into a multi-stage Dockerfile. Reused common-utils already provided by the existing Ubuntu base; retained tool versions, Node package managers, native build dependencies, .NET LTS SDK and .NET 8 runtime.
- Removed the local worker feature. Its source, build-only SDKs, modules and NuGet packages are isolated in a builder stage. The final Core Tools installation consumes only the Release worker output through a BuildKit mount.
- Removed APT/download/user caches in their creating RUN instructions, including Azure CLI Python bytecode caches. Added a narrow `.dockerignore`.
- Added image smoke tests for user permissions, tools, all seven PowerShell modules and a real HTTP function using the 7.6 worker. Wired these tests into the existing CI action and documented local builds and additional consumer features.
- The IDE-mentioned lock file was absent from the working tree; no lock file was deleted or regenerated.

## Failures and corrections

- Initial Docker access was denied by the sandbox; the approved elevated Docker invocation connected to the existing Docker Desktop Linux engine.
- An initial patch attempted delete/add operations on the same Dockerfile path and was rejected without applying changes; the file was then written successfully.
- The first Docker build passed, but the non-root smoke test exposed missing CurrentUser PowerShellGet: `Install-Module` had warned about modules already in use and skipped installation. Switched to `Save-Module` in a temporary directory followed by copying into the user module directory.
- The first smoke test also reported permission denial when inspecting APT's root-only partial directory; the cache assertion now uses passwordless sudo.
- Core Tools 4.14.0 installs under `/usr/lib/azure-functions-core-tools-4`, unlike the earlier hardcoded path. The final Dockerfile and test resolve the installation directory through `readlink -f` on `func`; the worker config supports 7.6.

## Final validation

- Direct Docker build: passed on Docker Desktop Linux amd64. Dev Container CLI 0.89.0 configuration validation and repository build also passed. The final locally available image is `devcontainer:optimized`.
- Full non-root smoke test: passed. Verified Node 22.22.2, nvm, npm, Yarn, pnpm, GitHub CLI 2.100.0, Azure CLI 2.90.0, Bicep 0.46.1, .NET SDK 10.0.400, .NET 8.0.30 runtime, Core Tools 4.14.0, network tools, writable user/volume paths, and PowerShell profile/history.
- Module imports passed: PowerShellGet 2.2.5, PSReadLine 2.4.5, Az.Accounts 5.5.3, Microsoft.Graph.Authentication 2.39.0, PnP.PowerShell 3.4.1, Pester 6.1.0, ExchangeOnlineManagement 3.10.1.
- Started Core Tools with `FUNCTIONS_WORKER_RUNTIME_VERSION=7.6`; the HTTP trigger returned `Hello, SmokeTest. This HTTP triggered function executed successfully.`
- Built a separate temporary consumer using the final image plus `ghcr.io/devcontainers/features/git-lfs:1`. Dev Container CLI reported success, and Git LFS 3.8.0 executed as vscode. Validation-only configuration and logs are in the OS temporary directory, outside the repository.
- Final image size: 3,974,683,308 bytes versus 6,132,299,306 bytes for the previously available published image: 2,157,615,998 bytes (35.2%) smaller, measured as local uncompressed Docker image sizes. This is a comparison against the existing published image, not a same-version rebuild of the old Dockerfile.
- Root/non-root checks confirmed no worker source, build-only SDK 3.1.426, root NuGet/cache directory, NVM download cache, APT archives/index files, or Azure CLI bytecode caches in the final image. The base's remaining oh-my-zsh cache directory contains only a zero-byte `.gitkeep`.
- Non-blocking warnings: Azure CLI's experimental `az config` command during build; Python SyntaxWarnings in upstream Azure SDK source during uncached CLI startup; interactive bash job-control warnings in the non-TTY smoke test. No build/test failures remain. Python startup tradeoff is documented.
- `git diff --check` passed. Changes, documentation, tests and this log are committed locally; no image push or deployment was performed.
