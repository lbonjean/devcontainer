#!/usr/bin/env bash
set -euo pipefail

if ! command -v npm >/dev/null 2>&1; then
    echo 'npm-global-packages: npm must already be installed and available on PATH.' >&2
    exit 1
fi

feature_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
package_lines="$(node -e '
const fs = require("node:fs");
const packages = JSON.parse(fs.readFileSync(process.argv[1], "utf8"));
if (!Array.isArray(packages) || packages.some(pkg =>
    typeof pkg !== "string" || !pkg.trim() || pkg !== pkg.trim() || /[\r\n]/.test(pkg))) {
    console.error("npm-global-packages: packages.json must contain an array of non-empty package specs.");
    process.exit(1);
}
for (const pkg of packages) console.log(pkg);
' "$feature_dir/packages.json")"

if [ -z "$package_lines" ]; then
    echo 'npm-global-packages: no packages requested.'
    exit 0
fi
mapfile -t package_list <<< "$package_lines"

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
