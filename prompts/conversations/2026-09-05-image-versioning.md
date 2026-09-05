# Image versioning proposal — 2026-09-05

## User request (verbatim)

# Context from my IDE setup:

## Active file: .devcontainer/test-image.ps1

## Open tabs:
- test-image.ps1: .devcontainer/test-image.ps1

## My request:
ik zou graag via github actions het versiebeheer/tagging van de images beter willen doen.

- ik wil een stable version --> main branch?
- ik wel een latest version
- ik wil een staging version.
- versie nummers?
- manier om te failbacken

heb je hiermee voldoende info? indien meer info nodig, vraag info aub.

## Response and decisions

Inspected the workflow, README, devcontainer configuration, smoke test, and cumulative lessons. Current latest is updated on main pushes; scheduled/manual builds reuse sha tags. Proposed main as integration branch, latest as its newest tested build, staging as an explicitly selected release candidate, stable as an approved versioned release. Proposed semantic versions, unique build tags including run ID/attempt, digest-based promotion without rebuilding, and manual rollback by selecting a retained release. Asked whether latest should track main or stable, whether staging needs a separate branch, and whether versioned releases should be manual or automatic. These are design questions; no workflow implementation or remote changes made.

Docker and GitHub official documentation checked for tag/digest semantics and GHCR publishing. Only session log and a correction to lessons changed. Validation: git diff --check passed before commit. No build tests needed for documentation-only changes.
