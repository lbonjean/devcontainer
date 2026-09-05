# Dev container

Reusable VS Code development container for PowerShell and Azure development.
All development tools are installed by `.devcontainer/Dockerfile`; the project
does not apply additional Dev Container Features. The image is published to
GitHub Container Registry. Consumers can add their own `features` alongside `image`.

## Published image

```text
ghcr.io/lbonjean/devcontainer:latest
```

The GitHub Actions workflow publishes a new image when the dev container
configuration changes and runs every Monday to incorporate upstream updates.
Immutable `sha-<commit>` tags are also published.

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

The Dockerfile retains PowerShell 7.6.5 and its seven configured modules, Node
22.22.2 with nvm/npm/Yarn/pnpm and native compilation dependencies, GitHub CLI,
Azure CLI and Bicep, the latest .NET LTS SDK plus the .NET 8 runtime, and Azure
Functions Core Tools with PowerShell worker 4.0.5362. The base already includes
the `vscode` user, sudo, git and zsh supplied by common-utils.

Versions are controlled by Dockerfile build arguments. Unpinned packages follow
their upstream repositories when the corresponding layer is rebuilt; use
`--pull --no-cache` when explicitly refreshing all upstream tools.

Downloads and package caches are removed in the RUN instruction that creates
them. The worker is compiled in a separate stage: source, NuGet cache, packaging
SDK and build-only modules are excluded from the final image. The normal .NET
SDK and node-gyp dependencies remain available for development. A `.dockerignore`
limits the build context to image inputs. Docker's local build cache is separate
from the published image and is intentionally left under the developer's control.

Removing Azure CLI's shipped Python bytecode saves space, but can increase CLI
startup time and expose upstream Python `SyntaxWarning` messages. The image smoke
test checks that Azure CLI and Bicep still work without this cache.

Dependabot checks the base image and GitHub Actions dependencies weekly.
