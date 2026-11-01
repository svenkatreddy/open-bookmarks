# Encrypt a pack in your browser

Use this tool to turn a plain pack into an encrypted pack, or to check
an encrypted pack by decrypting it. Everything runs in your browser.
Your pack and password never leave this page, and nothing is uploaded.

The encrypted output uses the same format as
[Encrypted packs](ENCRYPTION.md): `open-bookmarks/encrypted/1.0`,
PBKDF2 with SHA-256 at 600,000 iterations, and AES-256-GCM. A reader
that supports encrypted packs can decrypt the output with the same
password.

<EncryptTool />
