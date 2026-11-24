#!/usr/bin/env bash
set -euo pipefail

image="ghcr.io/${GITHUB_REPOSITORY,,}"
# New releases use a real calendar date and a daily sequence from 01 to 99.
# Rollback also accepts the legacy three-component version tags.
valid_calendar_version() {
    [[ "$1" =~ ^([0-9]{4})\.([0-9]{2})\.([0-9]{2})\.(0[1-9]|[1-9][0-9])$ ]] || return 1
    local release_date="${BASH_REMATCH[1]}-${BASH_REMATCH[2]}-${BASH_REMATCH[3]}"
    [[ "$(date -u --date="$release_date" +%Y-%m-%d 2>/dev/null)" == "$release_date" ]]
}
if [[ "$OPERATION" != publish ]] && ! valid_calendar_version "$VERSION"; then
    if [[ "$OPERATION" != rollback || ! "$VERSION" =~ ^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$ ]]; then
        echo 'Version must be YYYY.MM.DD.NN with a valid date and sequence 01-99 (e.g. 2026.11.24.01). Legacy versions are accepted only for rollback.' >&2
        exit 1
    fi
fi
case "$OPERATION" in
    publish)
        [[ "$GITHUB_REF" == refs/heads/main && "$GITHUB_EVENT_NAME" != pull_request ]] || {
            echo 'Automatic version publication requires a main-branch build.' >&2; exit 1;
        }
        [[ "$SOURCE" =~ ^build-[0-9]+-[0-9]+$ ]] || {
            echo 'Automatic publication requires a unique build tag.' >&2; exit 1;
        }
        ;;
    release)
        [[ "$SOURCE" =~ ^(staging|latest|build-[0-9]+-[0-9]+)$ ]] || valid_calendar_version "$SOURCE" || {
            echo 'Select staging, latest, a calendar release, or a unique build tag.' >&2; exit 1;
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

error_file="$(mktemp)"
trap 'rm -f "$error_file"' EXIT

if [[ "$OPERATION" == publish ]]; then
    release_date="$(date -u +%Y.%m.%d)"
    VERSION=''
    # Main builds and manual release/rollback share one workflow concurrency group.
    # Never delete/recycle date tags. A retry reuses the same digest's date tag.
    for sequence in $(seq 1 99); do
        candidate="${release_date}.$(printf '%02d' "$sequence")"
        if existing="$(digest_of "$image:$candidate" 2> "$error_file")"; then
            if [[ "$existing" == "$digest" ]]; then
                VERSION="$candidate"
                break
            fi
        elif grep -Eqi 'manifest unknown|MANIFEST_UNKNOWN|not found' "$error_file"; then
            VERSION="$candidate"
            break
        else
            cat "$error_file" >&2
            exit 1
        fi
    done
    [[ -n "$VERSION" ]] || {
        echo 'All 99 calendar release slots for today are already used.' >&2; exit 1;
    }
fi

if [[ "$OPERATION" == release || "$OPERATION" == publish ]]; then
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

channel=stable
if [[ "$OPERATION" == publish ]]; then channel=latest; fi
docker buildx imagetools create --prefer-index=false --tag "$image:$channel" "$resolved"
[[ "$(digest_of "$image:$channel")" == "$digest" ]]
{
    echo "### Image $OPERATION"
    echo "Version: $VERSION"
    echo "Source: $SOURCE"
    echo "Channel: $image:$channel"
    echo "Digest: $resolved"
    echo 'Existing devcontainers must be recreated to use this image.'
} >> "$GITHUB_STEP_SUMMARY"
