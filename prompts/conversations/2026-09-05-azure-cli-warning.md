# Azure CLI Python warning — 2026-09-05

## User request (verbatim)

```text
# Context from my IDE setup:

## Active file: .devcontainer/Dockerfile

## Open tabs:
- Dockerfile: .devcontainer/Dockerfile

## My request:
als ik de container start dan lukt dat, ik krijg eenpython melding als ik iets met az doe, zowel in bash als in pwsh shell:
bv az bicep version geeft: (met op de laatste lijn de verwachte output)
/opt/az/lib/python3.14/site-packages/azure/mgmt/resource/deploymentstacks/models/\_models.py:119: SyntaxWarning: "\\/" is an invalid escape sequence. Such sequences will not work in the future. Did you mean "\\\\/"? A raw string is also an option.
&#x20; following actions are automatically appended to 'excludedActions': '\*\\/read' and
Bicep CLI version 0.46.1 (545b338e2c)
```

## Decisions and changes

- Reproduced the exact upstream SyntaxWarning with `az bicep version` as vscode in the existing devcontainer:ubuntu26 image; command still exited successfully.
- Removed bytecode deletion from .devcontainer/Dockerfile. Retain Azure CLI's vendor-supplied bytecode, avoiding repeated compilation by the non-root user. No global warning suppression or SDK source modification.
- Updated .devcontainer/test-image.sh to reject SyntaxWarning output from `az bicep version` in Bash and PowerShell; removed the requirement that Azure CLI bytecode be absent.
- Updated README.md with the tradeoff: roughly 281 MB restored for Azure CLI 2.90.0. Corrected the earlier cache-removal lesson.
- Python documentation confirms unrecognized escapes emit SyntaxWarning during compilation: https://docs.python.org/3.12/reference/lexical_analysis.html .

## Validation

- Initial sandbox Docker access was denied; elevated Docker access succeeded.
- Bash syntax validation of the modified test script passed. `git diff --check` passed.
- Reinstalled the same Azure CLI 2.90.0 package inside a disposable local container, restoring the shipped bytecode. As vscode, both Bash and PowerShell returned Bicep CLI version 0.46.1 without SyntaxWarning; test process exited 0. Apt emitted noninteractive debconf frontend fallback notices only.
- No full image rebuild or full Functions suite was run for this focused change. The existing running user container is unchanged; rebuilding the image and recreating the devcontainer is required.
- Delivered Dutch explanation of cause, fix, size tradeoff, successful focused validation and rebuild requirement. Changes committed locally; nothing pushed or published.
