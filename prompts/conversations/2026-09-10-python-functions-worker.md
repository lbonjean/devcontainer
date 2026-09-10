# Python Functions worker — 2026-09-10

## User request (verbatim)

```text
ik zou naast de powershell worker ook graag de python worker voor azure functions willen toevoegen aan deze container.
In de examples zou ik graag een extra voorbeeld hebben met de python worker ipv de powershell worker.
```

## Delivered response

- Added Python development tooling to `.devcontainer/Dockerfile`: `python-is-python3`, `python3-dev`, `python3-pip` and `python3-venv`, alongside the existing Python interpreter.
- Added `examples/python` with a prebuilt-image devcontainer configuration, VS Code Azure Functions/Python settings and tasks, and a Python v2 Azure Functions HTTP trigger project under `function`.
- Kept `azure-functions-worker` out of `requirements.txt`; only the app SDK `azure-functions` is listed, because Core Tools/the platform manages the Python worker.
- Extended `.devcontainer/test-image.sh` to check Python, pip and venv, then run the Python Functions sample through `func start` and an HTTP invocation after the existing PowerShell worker smoke test.
- Updated `README.md` to describe the image as PowerShell, Python and Azure focused, point to the Python example, and document Python worker smoke-test coverage.
- Added a durable lesson in `prompts/LESSONS_LEARNED.md` for Python Functions worker dependency and smoke-test conventions.

## Validation

- `bash -n .devcontainer/test-image.sh`: passed.
- `git diff --check`: passed before and after documentation updates.
- Docker engine was reachable on Linux amd64 through Docker Desktop 4.73.0.
- Docker image `devcontainer:python-worker-local` was built successfully.
- `docker run --rm --user vscode --mount type=bind,source="${PWD}",target=/src,readonly devcontainer:python-worker-local bash /src/.devcontainer/test-image.sh`: passed. Relevant output included `Functions PowerShell runtime: 7.6.5`, `Functions Python runtime smoke test passed.`, and `Image smoke tests passed.`