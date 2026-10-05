# Dev container

Reusable VS Code development container for PowerShell and Azure development.
Image-owned development tools are installed by `.devcontainer/Dockerfile`.
The local devcontainer adds the Docker-outside-of-Docker Feature for access to
the host Docker daemon; this requires Docker on the host and a container rebuild.
The published image does not include that Feature. The image is published to
GitHub Container Registry. Consumers can add their own `features` alongside `image`.

## Published image

```text
ghcr.io/lbonjean/devcontainer:latest
```

The GitHub Actions workflow builds and smoke-tests the image before publishing.
It runs for image/workflow changes, every pull request (without publishing),
every Monday on the default branch, and manually for a selected branch.
Builds use `--pull --no-cache` to incorporate upstream updates.

For a pull request from this repository, the workflow checks whether this same
workflow has a completed, successful **push** run for the exact PR head SHA and
branch. If so, it reuses that result and skips rebuilding and smoke-testing the
image; the existing `Build dev container` check still succeeds and links the
reused run in its summary. Workflow safeguard unit tests always run.
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
| `1.2.3` | Manual release; never reassigned to different content by the workflow |
| `build-<run-id>-<attempt>` | Each published build, including reruns |
| `branch-<branch>` | Successful builds of that branch (compatibility/testing) |

`latest` means the newest tested main build, not necessarily a stable release.
The image revision label records the Git commit; the build summary records the
registry digest. Old `sha-<commit>` tags are no longer updated because rebuilding
the same commit can produce different content.

### Release and rollback

After merging these workflows into `main`, create/push a `staging` branch that
contains them. Develop/test there and merge approved code into `main` as usual.
The branch must exist remotely for its push/manual builds to run.

In **Actions → Release or roll back image → Run workflow**, select **main**:

1. For a release, choose `release`, enter a version such as `1.2.3`, and select
   source `staging`, `latest`, or `build-<run-id>-<attempt>`. Prefer the unique build
   tag when approving a particular tested candidate. Versions have no `v` prefix:
   MAJOR for incompatible changes, MINOR for additions, PATCH for fixes.
2. The action resolves the source once and copies its exact registry manifest to
   `1.2.3` and `stable`, without rebuilding. Repeating the same version/source is
   safe; using an existing version for different content fails. If staging moved
   since a previous attempt, use the original unique build tag when retrying.
3. For rollback, choose `rollback` and an existing version such as `1.2.2`.
   Only `stable` moves; `latest`, `staging`, and version tags remain unchanged.

This versions container images; it does not create Git tags or GitHub Releases.
Release/rollback jobs are serialized. GitHub concurrency may replace an older
pending run, so check the selected run completed. Retain versioned images and
their manifests in GHCR: rollback depends on them. This workflow deletes none.
Tag immutability is enforced by this workflow, not against external registry writes.

For daily use choose `ghcr.io/lbonjean/devcontainer:stable`. To pin a release use
`:1.2.3`, or use `ghcr.io/lbonjean/devcontainer@sha256:<digest>` for exact content.
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

Docker with BuildKit and Linux amd64 containers is required. The pinned upstream
PowerShell worker uses x64 build tools; arm64 builds are not supported.

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

The Dockerfile retains PowerShell 7.6.5 and its seven configured modules, Node
22.22.2 with nvm, the latest npm/Yarn/pnpm, Azure Static Web Apps CLI (`swa`),
and native compilation dependencies, GitHub CLI,
Azure CLI and Bicep, the latest .NET LTS SDK plus the .NET 8 runtime, and Azure
Functions Core Tools with PowerShell worker 4.0.5362. The base is the official
`ubuntu:24.04` (Ubuntu 24.04 LTS, Noble Numbat), directly from Ubuntu.
The Dockerfile supplies the `vscode` user (UID/GID 1000), passwordless sudo,
git, SSH client, zsh and UTF-8 locale explicitly. Azure CLI uses its native
Ubuntu 24.04/noble repository. PowerShell and Core Tools use official GitHub
release downloads to retain the explicitly pinned versions;
no older Ubuntu feeds are mixed in. Core Tools is pinned to 4.14.0 through
`CORE_TOOLS_VERSION`.
The image does not include the Microsoft base's Oh My Zsh customization;
the existing PowerShell Oh My Posh profile is retained.

Validated in the running Ubuntu 24.04 Linux amd64 container: all tool/module smoke
tests and HTTP invocation through Core Tools 4.14.0 with PowerShell 7.6.5 in the
worker. The October 2026 validation tested the existing container, not a fresh
Docker build.
This verifies this development image; cloud deployment, authenticated Azure
operations and other Functions languages are outside this test.
See the [Core Tools installation table](https://github.com/Azure/azure-functions-core-tools#linux).
The standalone PowerShell installation is described
in [Microsoft's Ubuntu instructions](https://learn.microsoft.com/en-us/powershell/scripting/install/install-ubuntu).

Oh My Posh is installed globally. The supplied PowerShell settings script
initializes it when sourced; automatic profile loading is currently disabled in
the Dockerfile. The smoke test exercises prompt initialization explicitly, not
automatic history/profile loading.
For prompt icons, select a Nerd Font in your local VS Code terminal settings.
The Node installation upgrades npm first, installs the latest global packages,
and updates their dependencies on each uncached build. Rebuild the devcontainer
to use the updated tools; existing containers keep their installed versions.
The build allows npm installation scripts for Yarn and SWA's native `keytar`
dependency and includes libsecret plus its compilation prerequisites.
See the [npm script policy](https://docs.npmjs.com/cli/install/),
[SWA Linux troubleshooting](https://azure.github.io/static-web-apps-cli/docs/contribute/Troubleshooting/),
and [Oh My Posh installation](https://ohmyposh.dev/docs/installation/linux).

Versions are controlled by Dockerfile build arguments. Unpinned packages follow
their upstream repositories when the corresponding layer is rebuilt; use
`--pull --no-cache` when explicitly refreshing all upstream tools.

Downloads and package caches are removed in the RUN instruction that creates
them. The worker is compiled in a separate stage: source, NuGet cache, packaging
SDK and build-only modules are excluded from the final image. The normal .NET
SDK and node-gyp dependencies remain available for development. A `.dockerignore`
limits the build context to image inputs. Docker's local build cache is separate
from the published image and is intentionally left under the developer's control.

Azure CLI's shipped Python bytecode is retained to avoid recompilation on every
invocation and upstream Python `SyntaxWarning` messages. This costs approximately
281 MB in Azure CLI 2.90.0. The image smoke test checks `az bicep version` in both
Bash and PowerShell and rejects Python syntax warnings.

Dependabot checks the base image and GitHub Actions dependencies weekly.
