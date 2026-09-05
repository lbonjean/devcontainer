#!/usr/bin/env bash
set -euo pipefail

image="ghcr.io/${GITHUB_REPOSITORY,,}"
[[ "$VERSION" =~ ^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$ ]] || {
    echo 'Version must be MAJOR.MINOR.PATCH without a v prefix or leading zeros.' >&2
    exit 1
}
case "$OPERATION" in
    release)
        [[ "$SOURCE" =~ ^(staging|latest|build-[0-9]+-[0-9]+)$ ]] || {
            echo 'Select staging, latest, or a unique build tag.' >&2; exit 1;
        }
        ;;
    rollback) SOURCE="$VERSION" ;;
    *) echo 'Unknown operation.' >&2; exit 1 ;;
esac

# Resolve the registry digest, not the local image ID; resolve source only once.
digest_of() {
    local metadata digest_value
    metadata="$(docker buildx imagetools inspect "$1" --format '{{json .Manifest}}')" || return 1
    digest_value="$(jq -er '.digest' <<< "$metadata")" || return 1
    [[ "$digest_value" =~ ^sha256:[a-f0-9]{64}$ ]] || return 1
    printf '%s\n' "$digest_value"
}
digest="$(digest_of "$image:$SOURCE")"
resolved="$image@$digest"
# Ensure the computed digest is addressable before any mutation.
docker buildx imagetools inspect "$resolved" > /dev/null

if [[ "$OPERATION" == release ]]; then
    error_file="$(mktemp)"
    trap 'rm -f "$error_file"' EXIT
    if existing="$(digest_of "$image:$VERSION" 2> "$error_file")"; then
        [[ "$existing" == "$digest" ]] || {
            echo "Release $VERSION already exists with different content; refusing overwrite." >&2
            exit 1
        }
    elif grep -Eqi 'manifest unknown|MANIFEST_UNKNOWN|not found' "$error_file"; then
        docker buildx imagetools create --prefer-index=false --tag "$image:$VERSION" "$resolved"
    else
        cat "$error_file" >&2
        exit 1
    fi
    [[ "$(digest_of "$image:$VERSION")" == "$digest" ]]
fi

docker buildx imagetools create --prefer-index=false --tag "$image:stable" "$resolved"
[[ "$(digest_of "$image:stable")" == "$digest" ]]
{
    echo "### Image $OPERATION"
    echo "Version: $VERSION"
    echo "Source: $SOURCE"
    echo "Stable: $resolved"
    echo 'Existing devcontainers must be recreated to use this image.'
} >> "$GITHUB_STEP_SUMMARY"
