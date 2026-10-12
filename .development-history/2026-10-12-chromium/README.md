# Chromium dependencies and Windows Hello

- [Validation details](research/validation.md)
- [Conversation record](../../prompts/conversations/2026-10-12-chromium-webauthn.md)

The Ubuntu 24.04 image now declares the Linux libraries and fonts required by
headed Playwright Chromium. The consuming project still installs its
Playwright-pinned browser into the user cache; the shared image does not pin a
Chromium revision.

X11 can display the Linux Chromium window on the host, but does not expose the
Windows Hello platform authenticator to that browser. Use a browser running on
Windows, or a Windows RDP session whose server supports WebAuthn redirection.
