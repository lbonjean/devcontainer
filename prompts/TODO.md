# TODO

## Devcontainer

- [ ] Add the official `ghcr.io/devcontainers/features/docker-outside-of-docker:1` Feature.
  This should install the Docker CLI and forward the Docker Desktop host socket so
  Codex can run a complete `devcontainer build --workspace-folder /workspace`.
  Review and accept the host Docker daemon access implications before enabling it.
