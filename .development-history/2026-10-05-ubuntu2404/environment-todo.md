# Environment prerequisites

- The current container has no Docker client, daemon or mounted socket. The
  local devcontainer now includes Docker-outside-of-Docker; rebuild it with Docker
  available on the host to enable local image build/run commands. This Feature
  is not part of the published image and was not applied to this running container.
- jq was absent and installed locally with user approval for release safeguard
  tests. GitHub Ubuntu runners supply jq. Dockerfile remains unchanged, so future
  local containers must install jq separately before running those tests.
- actionlint and ShellCheck were absent. Validation used a temporary,
  checksum-verified actionlint 1.7.12 binary without external ShellCheck.
- Existing GitHub CLI/host credential forwarding supplied no usable credential.
  Restore forwarding if live Actions inspection is needed; no login was started.
- setup-doctor reported: `/home/vscode/.codex/AGENTS.md does not resolve to
  /home/vscode/.agents/AGENTS.md`. Fix separately if the Codex entrypoint is needed;
  no unrelated instruction links were changed.
