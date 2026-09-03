#!/bin/bash
set -euo pipefail

readonly WORKER_VERSION="4.0.5362"
readonly CORE_TOOLS_DIR="/usr/lib/azure-functions-core-tools"

if [[ ! -x "$(command -v pwsh)" ]]; then
    echo "PowerShell must be installed before the worker feature." >&2
    exit 1
fi

if [[ ! -d "$CORE_TOOLS_DIR" ]]; then
    echo "Azure Functions Core Tools must be installed before the worker feature." >&2
    exit 1
fi

work_dir="$(mktemp -d)"
trap 'rm -rf "$work_dir"' EXIT
wget --quiet --output-document="$work_dir/worker.tar.gz" "https://github.com/Azure/azure-functions-powershell-worker/archive/refs/tags/v${WORKER_VERSION}.tar.gz"
tar --extract --gzip --file="$work_dir/worker.tar.gz" --directory="$work_dir"
cd "$work_dir/azure-functions-powershell-worker-${WORKER_VERSION}"

pwsh ./build.ps1 -bootstrap -deploy -coretoolsdir "$CORE_TOOLS_DIR"
