# Validation — 2026-10-05

Scope: the existing Linux amd64 Ubuntu 24.04.5 development container and local
workflow logic. The user confirmed that the image build had already succeeded
and prohibited Dockerfile changes. No fresh image build was performed.

| Check | Result |
| --- | --- |
| `bash .devcontainer/test-image.sh` | Passed |
| `python3 -m unittest discover -s .github/scripts -p 'test_*.py'` | 16 tests passed |
| Bash syntax for image/release scripts | Passed |
| Workflow YAML and skip/publish conditions | Passed |
| actionlint 1.7.12, modified build workflow | Passed; external ShellCheck disabled |
| Dockerfile diff against HEAD | Empty |
| `git diff --check`, staged whitespace check | Passed |
| setup-doctor | One pre-existing Codex entrypoint failure; other checks passed |
| Live GitHub run inspection | Unavailable without a usable forwarded credential |

The image test verified Ubuntu/user/locale/sudo, Node 22.22.2, package managers,
SWA and native keytar, Oh My Posh, interactive shell configuration, real manual
pages, GitHub CLI, Azure CLI/Bicep without Python SyntaxWarnings, .NET SDK
10.0.401 and runtime 8.0.31, Core Tools 4.14.0, development tools, Python/PyYAML,
module availability/imports, writable directories and image cache cleanliness.
All seven configured user PowerShell modules imported successfully. A real
HTTP invocation returned the expected HelloWorld response and worker version
7.6.5, without Azure credentials or Azurite.

PR-reuse tests cover exact success, missing runs, new commits, mismatching events,
branches/repositories/SHAs, failed/cancelled/skipped/running/queued runs, fork and
deleted repositories, pagination, explicit API failure and step-output/summary
contents. Existing eight release safeguard tests remain green.

Initial failures were corrected: locally missing jq; apt installation lists
contaminating image-cleanliness checks; executable named bwrap rather than its
package name bubblewrap. The editor test tool found no unittest tests, so the
existing command-line runner was used. actionlint was missing, so its release
binary was downloaded temporarily and verified against the release checksum.
Noninteractive Bash job-control notices are expected and did not fail tests.

Automatic PowerShell profile/history loading remains intentionally disabled.
No authenticated Azure operations, deployment, registry publishing, fresh
Docker build or live GitHub push/PR execution was performed.
