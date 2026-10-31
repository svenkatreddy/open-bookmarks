# Encrypted packs

An encrypted pack is a whole plain pack, encrypted with a
password, in a separate file format. It is not a plain pack
with an extra field, and a plain pack reader must not try to
read it as a pack. Decrypt it first, then validate the plain
pack inside, with the normal validator.

## Format

```json
{
  "format": "open-bookmarks/encrypted/1.0",
  "cipher": "AES-256-GCM",
  "kdf": "PBKDF2-HMAC-SHA-256",
  "iterations": 600000,
  "salt": "hex, 16 bytes",
  "iv": "hex, 12 bytes",
  "ciphertext": "hex, ciphertext plus the 16 byte GCM tag"
}
```

Parameters, fixed for version 1.0 of this encrypted format:

- Key derivation: PBKDF2 with SHA-256, 600,000 iterations,
  fixed for version 1.0, with no override in any encryptor
  or decryptor. That is the OWASP-recommended work factor
  for PBKDF2 with SHA-256, and PBKDF2 is the
  password-oriented choice in the native Web Crypto API,
  which is why it was chosen, not because it is stronger
  than Argon2, and not because Web Crypto has no other
  key derivation options. Web Crypto also supports HKDF,
  ECDH, and X25519, but those are not password based in
  the same way. Argon2 is stronger against GPU brute
  force, but it is not in Web Crypto, so a zero dependency
  JavaScript version cannot use it.
- Content encryption: AES-256-GCM. The GCM tag is appended
  to the ciphertext, as in Web Crypto and in Python's
  cryptography library, so the same bytes decrypt in both.
- Salt: 16 random bytes, fresh for every encryption.
- IV: 12 random bytes, fresh for every encryption.
- Encoding: hex for salt, IV, and ciphertext. Hex is twice
  the size of the raw bytes, but it has no padding and no
  encoding surprises across languages.

A decryptor must accept a flat payload with only salt, iv,
and ciphertext, with the version 1.0 defaults, because that
was the layout in the original prompt for this feature.
Encryptors must always write the full envelope above, so a
reader can tell what the file is and how it was made.
A decryptor must reject any present format, cipher, kdf,
or iterations field that differs from the values above,
including an explicit null, before any PBKDF2 work.

## What it is, and what it is not

Encryption here is confidentiality, and tamper evidence
under the password, because AES-GCM authentication fails
if the ciphertext is changed. It does not prove who made
the pack. Anyone with the password can encrypt a different
pack that decrypts just as well, and tamper evidence under
a shared password is not proof of authorship. If you need
to prove authorship, that needs a signature, which is a
separate feature, not defined here.

A lost password means a lost pack, by design. There is no
recovery, no back door, and no password reset. A weak
password also loses, because PBKDF2 at 600,000 iterations
slows brute force down, it does not stop it. Use a long,
unique password, and do not reuse an account password.

A remote update check cannot work on an encrypted pack
without decrypting it first. Version, updated date, and
diff are inside the encrypted part, on purpose, so they do
not leak. Update checking for encrypted packs is therefore
manual: decrypt, compare, then replace only after the
user confirms, as required in SPEC.md Section 12.

## Where each language runs

JavaScript and TypeScript: no npm dependencies, only the
native Web Crypto API, `globalThis.crypto.subtle`. This
runs in modern browsers and in Node.js 20 and later.
Functions are async, because Web Crypto is async:

```js
import { encryptPack, decryptPack } from "open-bookmarks/encrypt";
const encrypted = await encryptPack(pack, password);
const decrypted = await decryptPack(encrypted, password);
```

That import works only after publication, because the
`open-bookmarks` package is not yet published. Until then,
use the repo-relative file instead:

```js
import { encryptPack, decryptPack } from "./lib/js/encrypt.mjs";
```

A wrong password, or a corrupted payload, throws:

```
Decryption failed. Invalid password or corrupted payload
```

Python: the standard library has PBKDF2 and secure random
values, but it has no AES at all, and no AES-GCM. There is
no standard library fallback, and this project does not
write AES in pure Python to fake one. The Python tool
therefore needs the cryptography package:

```sh
python3 -m pip install cryptography
python3 tools/encrypt.py encrypt --input pack.json --output encrypted.json
python3 tools/encrypt.py decrypt --input encrypted.json --output pack.json
```

If `--password` is not given, it is asked for on the
terminal, so it does not appear in shell history. The
`--password` flag exists for scripts and tests only.

React Native: this JavaScript code does not run out of
the box in React Native, because Hermes has no
`crypto.subtle`. A React Native reader needs a different
engine behind the same payload format, for example a pure
JavaScript AES-GCM implementation, or a native crypto
library, and the payload above is designed so that engine
can interoperate with the web version. Until that engine
lands, a React Native reader should say an encrypted pack
is not supported, not try to decrypt it with a weaker
method.

## Public keys

This version is password only, by design, for simplicity
and for Web Crypto compatibility. A future version may add
public key recipients, but that is not defined here, and a
password pack from this version must keep decrypting with
a password after that version lands.

## Try it in your browser

No command line is needed to make one. The docs site has a
tool that encrypts a plain pack and decrypts an encrypted
pack, all in your browser, with nothing uploaded:
[Encrypt a pack](ENCRYPT-TOOL.md).

## Example file

`packs/examples/encrypted-template.json` is a structural
template only. Its salt, IV, and ciphertext are placeholder
hex values, not a real encrypted pack, and decrypting it
will fail, on purpose. Use the JavaScript example or the
Python tool to make a real encrypted pack from a real
plain pack.
