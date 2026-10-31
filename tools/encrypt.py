#!/usr/bin/env python3
"""Encrypt and decrypt an open-bookmarks pack with a password.

Usage, from the repo root:
  python3 tools/encrypt.py encrypt --input packs/examples/simple.json \
    --output /tmp/encrypted.json
  python3 tools/encrypt.py decrypt --input /tmp/encrypted.json \
    --output /tmp/decrypted.json

If --password is not given, the password is asked for on the
terminal, with getpass, so it does not appear in shell history
or in a process list. --password exists for scripts and tests
only, and using it in a normal shell is not recommended, for
exactly that reason.

Requirements, stated plainly, because the original prompt asked
for a standard library only tool and that is not possible:
Python's standard library has PBKDF2, in hashlib, and secure
random values, in secrets, but it has no AES at all, and no
AES-GCM. There is no clean standard library fallback, and
writing AES-GCM in pure Python to fake one would be slow,
unaudited, and easy to get wrong. This tool therefore needs
the cryptography package, and it refuses to run without it:

  python3 -m pip install cryptography

With that package, the payload is byte for byte compatible
with lib/js/encrypt.mjs and lib/ts/encrypt.ts: PBKDF2 with
SHA-256, 600,000 iterations, a random 16 byte salt, a random
12 byte IV, AES-256-GCM, hex encoded salt, IV, and ciphertext,
where ciphertext includes the 16 byte GCM tag at the end, as
in Web Crypto and in cryptography's AESGCM, so a pack
encrypted in JavaScript decrypts here, and the other way round.

Payload, the same envelope as the JavaScript module:
  {
    "format": "open-bookmarks/encrypted/1.0",
    "cipher": "AES-256-GCM",
    "kdf": "PBKDF2-HMAC-SHA-256",
    "iterations": 600000,
    "salt": "hex, 16 bytes",
    "iv": "hex, 12 bytes",
    "ciphertext": "hex, ciphertext plus tag"
  }

Decrypt also accepts a flat payload with only salt, iv, and
ciphertext, with the version 1.0 defaults, so packs made by
the original flat layout still decrypt.

This is confidentiality only. It does not prove who made the
pack, and a lost password means a lost pack, by design.
"""

import argparse
import getpass
import hashlib
import json
import secrets
import sys

ENCRYPTED_FORMAT = "open-bookmarks/encrypted/1.0"
ENCRYPTION_CIPHER = "AES-256-GCM"
ENCRYPTION_KDF = "PBKDF2-HMAC-SHA-256"
ENCRYPTION_ITERATIONS = 600000
SALT_BYTES = 16
IV_BYTES = 12

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.exceptions import InvalidTag
except ImportError:  # pragma: no cover - tested by the error path
    AESGCM = None
    InvalidTag = None


def require_cryptography():
    if AESGCM is None:
        print(
            "error: the cryptography package is required, "
            "Python's standard library has no AES-GCM. "
            "Install it with: python3 -m pip install cryptography",
            file=sys.stderr,
        )
        raise SystemExit(2)


def get_password(args):
    # An explicitly empty --password is an error, not a prompt.
    # Only an omitted --password, which is None, prompts.
    if args.password is not None:
        if not args.password:
            print("error: password must not be empty", file=sys.stderr)
            raise SystemExit(2)
        return args.password
    try:
        password = getpass.getpass("Password: ")
    except (EOFError, KeyboardInterrupt):
        print("error: password must not be empty", file=sys.stderr)
        raise SystemExit(2)
    if not password:
        print("error: password must not be empty", file=sys.stderr)
        raise SystemExit(2)
    return password


def derive_key(password, salt, iterations):
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, iterations, dklen=32
    )


def load_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def encrypt_pack(pack, password):
    require_cryptography()
    if not isinstance(pack, dict):
        print("error: encrypt needs a bookmark pack object", file=sys.stderr)
        raise SystemExit(2)
    if not password:
        print("error: password must not be empty", file=sys.stderr)
        raise SystemExit(2)
    salt = secrets.token_bytes(SALT_BYTES)
    iv = secrets.token_bytes(IV_BYTES)
    key = derive_key(password, salt, ENCRYPTION_ITERATIONS)
    iterations = ENCRYPTION_ITERATIONS
    plaintext = json.dumps(pack, ensure_ascii=False).encode("utf-8")
    ciphertext = AESGCM(key).encrypt(iv, plaintext, None)
    return {
        "format": ENCRYPTED_FORMAT,
        "cipher": ENCRYPTION_CIPHER,
        "kdf": ENCRYPTION_KDF,
        "iterations": iterations,
        "salt": salt.hex(),
        "iv": iv.hex(),
        "ciphertext": ciphertext.hex(),
    }


def decrypt_pack(payload, password):
    require_cryptography()
    if not isinstance(payload, dict):
        print("error: Decryption failed. Invalid password or corrupted payload", file=sys.stderr)
        raise SystemExit(1)
    # Presence, not just value: an explicit null is not the
    # same as an omitted legacy field, and must fail.
    if "format" in payload and payload["format"] != ENCRYPTED_FORMAT:
        print("error: Decryption failed. Invalid password or corrupted payload", file=sys.stderr)
        raise SystemExit(1)
    if "cipher" in payload and payload["cipher"] != ENCRYPTION_CIPHER:
        print("error: Decryption failed. Invalid password or corrupted payload", file=sys.stderr)
        raise SystemExit(1)
    if "kdf" in payload and payload["kdf"] != ENCRYPTION_KDF:
        print("error: Decryption failed. Invalid password or corrupted payload", file=sys.stderr)
        raise SystemExit(1)
    # Version 1.0 fixes iterations at exactly 600,000. A
    # payload with no iterations field is the legacy flat
    # layout, and gets that value. Any other value, including
    # a bool, which is an int subclass in Python, is rejected
    # before any PBKDF2 work.
    if "iterations" in payload:
        iterations = payload["iterations"]
        if type(iterations) is not int or iterations != ENCRYPTION_ITERATIONS:
            print("error: Decryption failed. Invalid password or corrupted payload", file=sys.stderr)
            raise SystemExit(1)
    else:
        iterations = ENCRYPTION_ITERATIONS
    if not password:
        print("error: Decryption failed. Invalid password or corrupted payload", file=sys.stderr)
        raise SystemExit(1)
    try:
        salt = bytes.fromhex(payload["salt"])
        iv = bytes.fromhex(payload["iv"])
        ciphertext = bytes.fromhex(payload["ciphertext"])
    except (KeyError, TypeError, ValueError):
        print("error: Decryption failed. Invalid password or corrupted payload", file=sys.stderr)
        raise SystemExit(1)
    if len(salt) != SALT_BYTES or len(iv) != IV_BYTES or not ciphertext:
        print("error: Decryption failed. Invalid password or corrupted payload", file=sys.stderr)
        raise SystemExit(1)
    key = derive_key(password, salt, iterations)
    try:
        plaintext = AESGCM(key).decrypt(iv, ciphertext, None)
    except InvalidTag:
        print("error: Decryption failed. Invalid password or corrupted payload", file=sys.stderr)
        raise SystemExit(1)
    try:
        return json.loads(plaintext.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        print("error: Decryption failed. Invalid password or corrupted payload", file=sys.stderr)
        raise SystemExit(1)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Encrypt or decrypt an open-bookmarks pack with a password.")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("encrypt", "decrypt"):
        cmd = sub.add_parser(name)
        cmd.add_argument("--input", required=True, help="Input JSON file")
        cmd.add_argument("--output", required=True, help="Output JSON file")
        cmd.add_argument("--password", help="Password. If omitted, it is asked for on the terminal.")
    args = parser.parse_args(argv)
    password = get_password(args)
    try:
        data = load_json(args.input)
    except OSError as exc:
        print("error: cannot read input: %s" % exc, file=sys.stderr)
        return 2
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        if args.command == "decrypt":
            print("error: Decryption failed. Invalid password or corrupted payload", file=sys.stderr)
            return 1
        print("error: cannot read input: %s" % exc, file=sys.stderr)
        return 2
    try:
        if args.command == "encrypt":
            save_json(args.output, encrypt_pack(data, password))
        else:
            save_json(args.output, decrypt_pack(data, password))
    except OSError as exc:
        print("error: cannot write output: %s" % exc, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
