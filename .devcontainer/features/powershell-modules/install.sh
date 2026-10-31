#!/usr/bin/env bash
set -euo pipefail

if ! command -v pwsh >/dev/null 2>&1; then
    echo 'powershell-modules: PowerShell must already be installed and available on PATH.' >&2
    exit 1
fi

feature_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
pwsh -NoLogo -NoProfile -NonInteractive -File "$feature_dir/install.ps1"
