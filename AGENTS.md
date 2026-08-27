# Repository instructions for Codex

These instructions apply to all work under this directory structure.

## Persistent conversation log

Maintain a durable session log in `prompts/conversations/`.

- At the start of a session, continue the most recent relevant conversation file or create `YYYY-MM-DD-<short-topic>.md`.
- Before completing each user request, append the user's request verbatim and a concise but complete account of the delivered response, decisions, changed files, and validation results.
- Put verbatim user messages in a clearly marked section or companion `*.user-prompts.md` file. Preserve spelling, formatting, code blocks, and error payloads.
- Assistant responses may be summarized faithfully.
- Clearly mark reconstructed or incomplete history. Never pretend unavailable or compacted conversation text is verbatim.
- Do not record hidden reasoning, chain-of-thought, raw tool traces, access tokens, passwords, secret values, or other credentials.
- If a user message itself contains a credential or secret value, replace only that value with `[REDACTED]` and state that a redaction was made.
- Redact sensitive personal or customer information that is not needed to understand the engineering work.
- Record failures and corrections because they are useful project history.
- Conversation logging does not authorize commits, pushes, deployments, or messages to external systems.

## Lessons learned

Maintain cumulative, reusable technical knowledge in `prompts/LESSONS_LEARNED.md`.

- Read it before making project changes.
- Append only durable findings, constraints, failure modes, conventions, and verified fixes.
- Include the date and enough context to apply the lesson later.
- Correct outdated lessons explicitly; do not silently erase useful history.
- Do not duplicate the complete conversation or store secrets.

## Cooperation

- We rely heavily on devcontainers, if some tools  (apt packges, powershell modules) are missing for the agent to function properly, let me know so that we can add them to devcontainer.json

## Code

- All code should be idempotent
- if resources like storage tables, queues etc do not exist, create them
- git commit when you finished a request

## Good to know

- Azurite is available trough vscode

## Validation

- Run `git diff --check`.
- Report validation warnings and failures honestly.