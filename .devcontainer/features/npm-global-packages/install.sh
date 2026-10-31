#!/usr/bin/env bash
set -euo pipefail

if ! command -v npm >/dev/null 2>&1; then
    echo 'npm-global-packages: npm must already be installed and available on PATH.' >&2
    exit 1
fi

packages="${PACKAGES:-}"
if [ -z "${packages//[[:space:]]/}" ]; then
    echo 'npm-global-packages: no packages requested.'
    exit 0
fi

if [[ "$packages" =~ ,[[:space:]]*$ ]]; then
    echo 'npm-global-packages: packages must not end with a comma.' >&2
    exit 1
fi

IFS=',' read -r -a package_list <<< "$packages"
for i in "${!package_list[@]}"; do
    package="${package_list[$i]}"
    package="${package#"${package%%[![:space:]]*}"}"
    package="${package%"${package##*[![:space:]]}"}"
    if [ -z "$package" ]; then
        echo 'npm-global-packages: packages must not contain empty entries.' >&2
        exit 1
    fi
    package_list[$i]="$package"
done

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
