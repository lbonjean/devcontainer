#!/usr/bin/env bash
set -euo pipefail

if ! command -v npm >/dev/null 2>&1; then
    echo 'npm-global-packages: npm must already be installed and available on PATH.' >&2
    exit 1
fi

packages="${PACKAGES:-@openai/codex @fission-ai/openspec@latest}"
packages="${packages//$'\n'/ }"
read -r -a package_list <<< "$packages" || true

if [ "${#package_list[@]}" -eq 0 ]; then
    echo 'npm-global-packages: no packages requested.'
    exit 0
fi

npm_command="$(command -v npm)"
npm_prefix="$(npm prefix -g)"

if [ "$(id -u)" -eq 0 ]; then
    prefix_owner="$(stat -c %U "$npm_prefix")"
    if [ "$prefix_owner" != root ]; then
        if ! command -v runuser >/dev/null 2>&1; then
            echo 'npm-global-packages: runuser is required to install into a non-root-owned npm prefix.' >&2
            exit 1
        fi
        runuser -u "$prefix_owner" -- "$npm_command" install -g -- "${package_list[@]}"
        exit 0
    fi
fi

"$npm_command" install -g -- "${package_list[@]}"
