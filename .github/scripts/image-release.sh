#!/usr/bin/env bash
set -euo pipefail

image="ghcr.io/${GITHUB_REPOSITORY,,}"
# New releases use a real calendar date and a daily sequence from 01 to 99.
# Rollback also accepts the legacy three-component version tags.
valid_calendar_version() {
    [[ "$VERSION" =~ ^([0-9]{4})\.([0-9]{2})\.([0-9]{2})\.(0[1-9]|[1-9][0-9])$ ]] || return 1
    local release_date="${BASH_REMATCH[1]}-${BASH_REMATCH[2]}-${BASH_REMATCH[3]}"
    [[ "$(date -u --date="$release_date" +%Y-%m-%d 2>/dev/null)" == "$release_date" ]]
}
if ! valid_calendar_version; then
    if [[ "$OPERATION" != rollback || ! "$VERSION" =~ ^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$ ]]; then
        echo 'Version must be YYYY.MM.DD.NN with a valid date and sequence 01-99 (e.g. 2026.11.24.01). Legacy versions are accepted only for rollback.' >&2
        exit 1
    fi
fi
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
