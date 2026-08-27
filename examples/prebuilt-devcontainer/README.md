# Prebuilt dev container example

Copy `devcontainer.json` to the `.devcontainer` folder of another repository to
use the prebuilt image without a local Dockerfile or Features build.

The image is published as `ghcr.io/lbonjean/devcontainer:latest`.

The `--pull=always` run argument checks GHCR for a newer `latest` image whenever
VS Code creates or rebuilds the container. An already running container is not
replaced automatically. Run **Dev Containers: Rebuild Container** to recreate it
from the newest image.

If the GHCR package is private, authenticate Docker before opening the repository:

```sh
docker login ghcr.io
```
