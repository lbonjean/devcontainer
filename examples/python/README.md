# Prebuilt dev container Python Functions example

This example uses the prebuilt image with an Azure Functions Python worker
project. The function app lives in `function` and uses the Python v2 programming
model.

Copy this folder to another repository, open it in VS Code, and run **Dev
Containers: Reopen in Container**. The image is published as
`ghcr.io/lbonjean/devcontainer:latest`.

The first run creates a local virtual environment and installs the Python
dependencies from `function/requirements.txt` before starting Core Tools.

If the GHCR package is private, authenticate Docker before opening the repository:

```sh
docker login ghcr.io
```

Run locally from the container:

```sh
cd function
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
func start
```

Then call the sample trigger:

```sh
curl 'http://localhost:7071/api/HelloWorld?name=Python'
```