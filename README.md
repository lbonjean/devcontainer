# Dev container

Reusable VS Code development container for PowerShell and Azure development.
Image-owned development tools are installed by `.devcontainer/Dockerfile`.
The local devcontainer adds the Docker-outside-of-Docker Feature for access to
the host Docker daemon; this requires Docker on the host and a container rebuild.
The published image does not include that Feature. The image is published to
GitHub Container Registry. Consumers can add their own `features` alongside `image`.

## Global npm packages Feature

The local `.devcontainer/features/npm-global-packages` Feature installs npm
packages globally during a devcontainer rebuild. npm must already be available
in the image. Set its comma-separated `packages` option in `devcontainer.json`,
as with the `modules` option of the PowerShell Feature:

```json
"features": {
  "./features/npm-global-packages": {
    "packages": "@openai/codex,@fission-ai/openspec@latest"
  }
}
```

The path is relative to the directory containing `devcontainer.json`. Package
specs may include versions; without a version, npm resolves the current release
when the devcontainer is rebuilt. The Feature is also published to GHCR as described below.

## PowerShell modules Feature

The `.devcontainer/features/powershell-modules` Feature installs modules and their
dependencies from PSGallery for all users. PowerShell and PowerShellGet must
already be installed. Configure comma-separated module names:

```json
"features": {
  "./features/powershell-modules": {
    "modules": "Pester,ImportExcel"
  }
}
```

An empty list skips installation. Repeated installation is supported. Modules
resolve to the latest stable Gallery version at build time; required module
licenses are accepted during installation. Existing module versions are retained.

## Published features

After merging to `main`, the **Publish dev container features** workflow packages
and publishes both Features to GHCR. Pull requests validate packaging without
publishing. You can also run the workflow manually on `main`.
Use these references from another repository:

```json
"features": {
  "ghcr.io/lbonjean/devcontainer/npm-global-packages:latest": {
    "packages": "@openai/codex,@fission-ai/openspec@latest"
  },
  "ghcr.io/lbonjean/devcontainer/powershell-modules:latest": {
    "modules": "Pester,ImportExcel"
  }
}
```

No Git tags, GitHub Releases or separate release workflow are needed. When
changing a Feature, increment its `version` in `devcontainer-feature.json`
(for example `1.0.0` → `1.0.1`). The official CLI publishes the version aliases
and `latest` automatically; an already published version is skipped.
Consumers keep using `:latest`; rebuild the devcontainer to apply changes.
If a consumer has a `devcontainer-lock.json`, update its locked Feature digest
with `devcontainer features upgrade` before rebuilding to get a newer publication.

GHCR packages can initially be private. After the first publication, set each
package's visibility to **Public** in GitHub package settings for use without
registry authentication, or authenticate to GHCR for private use.
See the [official Feature publishing tools](https://github.com/devcontainers/action).

## Published image

```text
ghcr.io/lbonjean/devcontainer:latest
```

The GitHub Actions workflow builds and smoke-tests the image before publishing.
It runs for every branch push, every pull request (without publishing),
every Monday on the default branch, and manually for a selected branch.
Builds use `--pull --no-cache` to incorporate upstream updates.

For a pull request from this repository, the workflow checks whether this same
workflow has a completed, successful **push** run for the exact PR head SHA and
branch. If so, it reuses that result and skips rebuilding and smoke-testing the
image; the existing `Build dev container` check still succeeds and links the
reused run in its summary. Workflow safeguard unit tests always run.
The lookup filters by push event, branch and commit, then checks completion and
success locally: GitHub's API status filter can omit a successful run.
New commits, missing/failed/in-progress push runs, and fork PRs receive the full
PR build and smoke test. API errors fail explicitly rather than skipping tests.
Push, scheduled and manual runs always build/test; PR runs never publish.
Reusing a head-commit result intentionally does not test the synthetic merge
commit or changes made only to the PR base branch.

| Image tag | Updated by |
| --- | --- |
| `latest` | Successful builds on `main`, including scheduled/manual builds |
| `staging` | Successful builds on the separate `staging` branch |
| `stable` | Manual release or rollback |
| `2026.11.24.01` | Automatically assigned after a successful main build; never reassigned |
| `build-<run-id>-<attempt>` | Each published build, including reruns |
| `branch-<branch>` | Successful builds of that branch (compatibility/testing) |

`latest` means the newest tested main build, not necessarily a stable release.
The image revision label records the Git commit; the build summary records the
registry digest. Old `sha-<commit>` tags are no longer updated because rebuilding
the same commit can produce different content.

### Automatic versions and manual stable promotion

A merge into `main` triggers a clean build and smoke tests. Only after these
pass, the workflow publishes the unique build tag, assigns an immutable calendar
tag such as `2026.11.24.01`, and updates `latest` to that same registry digest.
Scheduled and manually dispatched main builds follow the same rule. Branch and
pull-request builds do not allocate calendar versions or update `latest`/`stable`.

Versions use YYYY.MM.DD.NN: the UTC publication date and a daily sequence from
01 to 99. The allocator skips existing versions with different content and reuses
an existing tag when retrying the same digest on the same day. A newly built image
with a different digest gets the next available sequence. After 99 releases in a
day, publication fails without moving `latest`. Retain all calendar tags: do not
delete tags and recycle their numbers. Registry/authentication errors fail the
workflow rather than being treated as available version slots.

`stable` changes only when you approve an image. In **Actions → Release or roll
back image → Run workflow**, select **main**:

1. Choose `release`, enter an existing calendar version such as `2026.11.24.01`,
   and set source to that same version to promote it to `stable`.
2. The action resolves the source once and copies its exact registry manifest,
   without rebuilding. Repeating the same promotion is safe. Existing calendar
   tags cannot be assigned different content. For compatibility, a manual release
   can also name a new calendar tag for `latest`, `staging` or a unique build tag.
3. For rollback, choose `rollback` and an existing version such as `2026.11.23.01`.
   Only `stable` moves. Legacy three-component versions remain valid for rollback.

This versions container images; it does not create Git tags or GitHub Releases.
Main builds and manual release/rollback share one concurrency group, serializing
version allocation and channel updates across both workflows. GitHub concurrency
may replace an older pending run, so check the selected run completed.
Retain versioned images and their manifests in GHCR: rollback depends on them.
These workflows delete none. Tag immutability is enforced by these workflows,
not against external registry writes; use a digest for an immutable reference.

For daily use choose `ghcr.io/lbonjean/devcontainer:stable`. To pin a release use
`:2026.11.24.01`, or use `ghcr.io/lbonjean/devcontainer@sha256:<digest>` for exact content.
After switching versions or rolling back, recreate the devcontainer with a fresh
pull (for example `runArgs: ["--pull=always"]`); running containers do not change.
Consumer-local Features are reapplied and are not covered by the image digest.

References: [Docker manifest promotion](https://docs.docker.com/reference/cli/docker/buildx/imagetools/create/)
and [GitHub manual workflows](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/manually-run-a-workflow).

To use the image from another repository, start from the configuration in
`examples/powershell-7.6.5/.devcontainer/devcontainer.json` (which uses a testing
branch tag), or use the following configuration. If the package is private,
authenticate first with `docker login ghcr.io`.

```json
{
  "image": "ghcr.io/lbonjean/devcontainer:latest",
  "remoteUser": "vscode",
  "features": {
    "ghcr.io/devcontainers/features/docker-outside-of-docker:1": {}
  }
}
```

## Build and validate locally

Docker with BuildKit and Linux amd64 containers is required. The PowerShell and
Core Tools downloads target amd64; arm64 builds are not supported.

```sh
docker build --progress=plain -f .devcontainer/Dockerfile -t devcontainer:local .
docker run --rm --user vscode --mount type=bind,source="$(pwd)",target=/src,readonly devcontainer:local bash /src/.devcontainer/test-image.sh
```

To test the already-built, running development container without rebuilding:

```sh
bash .devcontainer/test-image.sh
python3 -m unittest discover -s .github/scripts -p 'test_*.py'
```

These existing Bash/Python scripts are retained. The image smoke test assumes a
clean image: installing packages in a running container can make its package-cache
checks fail. The separate release safeguard tests require `jq`, which is available
on GitHub's Ubuntu runners but must be installed separately in this devcontainer.

The base is official `ubuntu:26.04` (Ubuntu 26.04 LTS, Resolute Raccoon).
NodeSource apt supplies Node.js 24 LTS and its bundled npm. The signed
`node_24.x` repository keeps the major at 24 while picking up new patches at
build time. Dependabot does not update this apt repository selection. Ubuntu apt
supplies the .NET 10 SDK, system utilities and browser libraries. The Ubuntu
.NET backports PPA supplies the additional .NET 8 runtime. No NVM, manual Node binary installation, npm self-upgrade or Oh My Posh is used.
Azure CLI uses Microsoft's signed resolute repository; GitHub CLI uses its
signed upstream apt repository.

PowerShell is installed from an official GitHub release as a standalone deb. Core Tools remains pinned to `CORE_TOOLS_VERSION=4.16.0`, downloaded
as the official Linux x64 archive with its bundled PowerShell worker. Bicep uses
the official release binary. PowerShell modules use PowerShell Gallery. These
installations are not automatically maintained by Dependabot.

Yarn, pnpm and Azure Static Web Apps CLI (`swa`) are installed through NodeSource's
bundled npm with engine compatibility checks. Their global prefix is
`/usr/local/share/npm-global`, owned by `vscode`, so the global npm Feature and
interactive installs remain writable. Native compilation dependencies for SWA's
keytar are retained. Feature-specific packages are installed during devcontainer
creation, separately from the base-image workflow.

The image supplies `vscode` (UID/GID 1000), passwordless sudo, git, SSH, zsh and
UTF-8 locale. The PowerShell settings script retains Azure completion and history
settings; automatic profile loading remains disabled.

The build workflow runs functional image tests before publishing: CLI commands,
module imports, real manual rendering, global npm writes, compilation/execution
of a .NET console app, and an HTTP-triggered PowerShell function through Core
Tools. Tests do not assert tool or OS version numbers. A successful version
command alone does not establish Core Tools compatibility. Authenticated Azure
operations, deployment and other Functions languages are outside this check.

Dependabot checks Docker images, GitHub Actions and devcontainer Features weekly.
Ubuntu update proposals are restricted to the 26.04 series. Actions retain major
tags such as `@v4`; Feature lockfiles record their resolved digests. Apt packages
refresh during uncached builds rather than through individual Dependabot PRs.
The separate Feature-publication job keeps its existing Node 22 setup.

Rebuild the devcontainer to consume new packages; existing containers retain
their installed versions. Use `--pull --no-cache` to refresh upstream inputs.
Downloads and apt caches are removed in the layer that creates them. Docker's
local build cache is separate and remains under the developer's control.

References: [Ubuntu .NET installation](https://learn.microsoft.com/en-us/dotnet/core/install/linux-ubuntu-install),
[PowerShell installation](https://learn.microsoft.com/en-us/powershell/scripting/install/install-ubuntu),
[Core Tools](https://github.com/Azure/azure-functions-core-tools#linux), and
[Dependabot for Features](https://containers.dev/guide/dependabot).

Azure CLI's shipped Python bytecode is retained to avoid recompilation on every
invocation and upstream Python `SyntaxWarning` messages. This costs approximately
281 MB in Azure CLI 2.90.0. The image smoke test checks `az bicep version` in both
Bash and PowerShell and rejects Python syntax warnings.

Dependabot checks the base image and GitHub Actions dependencies weekly.
