# Dev container

Reusable VS Code development container for PowerShell and Azure development.
The image includes the Dev Container Features configured in
`.devcontainer/devcontainer.json` and is published to GitHub Container Registry.

## Published image

```text
ghcr.io/lbonjean/devcontainer:latest
```

The GitHub Actions workflow publishes a new image when the dev container
configuration changes and runs every Monday to incorporate upstream updates.
Immutable `sha-<commit>` tags are also published.

To use the image from another repository, start from the configuration in
`examples/prebuilt-devcontainer/devcontainer.json`. If the package is private,
authenticate first with `docker login ghcr.io`.

Dependabot checks the base image and GitHub Actions dependencies weekly.
