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

Logging correction: the first commit attempt was denied access to .git/index.lock by the sandbox. An authorized escalation succeeded (38bfccc); no auto-review rejection occurred.

## Follow-up user request (verbatim)

# Context from my IDE setup:

## Active file: .devcontainer/test-image.ps1

## Open tabs:
- test-image.ps1: .devcontainer/test-image.ps1

## My request:
1. latest de laatst geteste
2. aparte staging branch
3. handmatig

## Delivered implementation

- Confirmed latest as the newest successful main build, a separate staging branch/channel, and manual semantic version releases.
- Updated .github/workflows/devcontainer.yml to build the Dockerfile explicitly, smoke-test before any push, publish unique build/run-attempt tags, retain branch tags, and update latest/staging only on the matching branches. Scheduled/manual main builds now update latest. Branch pushes exclude Git tag pushes. Builds refresh upstream inputs with --pull --no-cache. Per-branch publishing is serialized.
- Added .github/workflows/image-release.yml and .github/scripts/image-release.sh for main-only manual release/rollback, digest-preserving promotion without rebuilding, input validation, version overwrite refusal, idempotent same-content release retries, and registry failure handling. Release and rollback share a concurrency group. This creates image versions, not Git tags/GitHub Releases. No image deletion or remote publication performed.
- Added eight offline registry-mock tests in .github/scripts/test_image_release.py and execute them in build CI. Updated README with channel meanings, versioning, operation steps, retention, pinning, and devcontainer recreation requirements.
- Validation: all eight release safety tests passed in WSL; actionlint passed via a temporary Docker container; Bash syntax check and git diff --check passed. The exact CI smoke-test invocation passed against the existing devcontainer:optimized image, including the Functions HTTP invocation. No fresh full image build or live GHCR promotion was run. Known non-failing Bash terminal/job-control warnings and Azure CLI Python SyntaxWarning appeared.
- Environment: WSL/Docker were initially inaccessible in the sandbox; authorized escalation enabled validation. actionlint was absent locally and run from its container image; no devcontainer dependency changes were needed. Shell profile emitted an unrelated unapproved-verbs warning.
- Changes committed on dev-optimisation; local staging branch created at the implementation commit. Remote activation still requires pushing/merging workflows into main and pushing staging. Manual Actions require the workflow on the default branch.
