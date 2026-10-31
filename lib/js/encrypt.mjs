// Password based encryption for open-bookmarks packs.
// No npm dependencies. This module uses only the native Web
// Crypto API, globalThis.crypto.subtle, so it runs out of the
// box in modern browsers and in Node.js 20 and later.
//
// It does NOT run out of the box in React Native. Hermes has
// no crypto.subtle, so a React Native reader needs a different
// engine behind the same payload format, for example a pure
// JavaScript AES-GCM implementation, or a native crypto
// library. The payload format below is engine independent,
// so a pack encrypted here can be decrypted there, and the
// other way round, as long as the other engine uses the
// same parameters.
//
// encryptPack(jsonPack, password)  Encrypt a whole pack object.
// decryptPack(encryptedPackage, password)  Decrypt it back.
//
// Payload, the corrected version of the flat Gemini layout:
// the flat salt, iv, and ciphertext fields are kept, so a
// plain Gemini style payload still decrypts, but encryptPack
// always adds format, cipher, kdf, and iterations, so a
// reader can tell what this file is and how it was made,
// and a future change to those parameters does not break
// old files silently.
//
// {
//   "format": "open-bookmarks/encrypted/1.0",
//   "cipher": "AES-256-GCM",
//   "kdf": "PBKDF2-HMAC-SHA-256",
//   "iterations": 600000,
//   "salt": "hex, 16 bytes",
//   "iv": "hex, 12 bytes",
//   "ciphertext": "hex, ciphertext plus the 16 byte GCM tag"
// }
//
// Parameters, fixed for version 1.0 of this encrypted format:
// PBKDF2 with SHA-256, 600,000 iterations, a random 16 byte
// salt, a random 12 byte IV, and AES-256-GCM. The password is
// never used directly as a key, and salt and IV are never
// reused. A wrong password, or a corrupted payload, fails
// GCM authentication, and decryptPack throws a single clear
// error for both cases, so a caller cannot tell which one
// it was from the error alone.
//
// This is confidentiality only. It does not prove who made
// the pack. Anyone with the password can encrypt a different
// pack that decrypts just as well. A lost password means a
// lost pack, by design, there is no recovery.

export const ENCRYPTED_FORMAT = "open-bookmarks/encrypted/1.0";
export const ENCRYPTION_CIPHER = "AES-256-GCM";
export const ENCRYPTION_KDF = "PBKDF2-HMAC-SHA-256";
export const ENCRYPTION_ITERATIONS = 600000;
export const SALT_BYTES = 16;
export const IV_BYTES = 12;

function subtle() {
  const cryptoObject = globalThis.crypto;
  if (!cryptoObject || !cryptoObject.subtle) {
    throw new Error(
      "Web Crypto API is not available in this environment. " +
        "This module needs globalThis.crypto.subtle, as in a modern browser or Node.js 20 or later. " +
        "It does not run in React Native out of the box.",
    );
  }
  return cryptoObject.subtle;
}

function randomBytes(length) {
  const cryptoObject = globalThis.crypto;
  if (!cryptoObject || !cryptoObject.getRandomValues) {
    throw new Error("Secure random values are not available in this environment.");
  }
  return cryptoObject.getRandomValues(new Uint8Array(length));
}

function hexEncode(bytes) {
  return Array.from(bytes, (byte) => byte.toString(16).padStart(2, "0")).join("");
}

function hexDecode(value, field) {
  if (typeof value !== "string" || value.length % 2 !== 0 || !/^[0-9a-fA-F]*$/.test(value)) {
    throw new Error(`Decryption failed. Invalid password or corrupted payload`);
  }
  const bytes = new Uint8Array(value.length / 2);
  for (let i = 0; i < bytes.length; i += 1) {
    bytes[i] = parseInt(value.slice(i * 2, i * 2 + 2), 16);
  }
  if (field === "salt" && bytes.length !== SALT_BYTES) {
    throw new Error(`Decryption failed. Invalid password or corrupted payload`);
  }
  if (field === "iv" && bytes.length !== IV_BYTES) {
    throw new Error(`Decryption failed. Invalid password or corrupted payload`);
  }
  if (field === "ciphertext" && bytes.length === 0) {
    throw new Error(`Decryption failed. Invalid password or corrupted payload`);
  }
  return bytes;
}

async function deriveKey(password, salt, iterations) {
  const encoder = new TextEncoder();
  const baseKey = await subtle().importKey("raw", encoder.encode(password), "PBKDF2", false, ["deriveKey"]);
  return subtle().deriveKey(
    { name: "PBKDF2", salt, iterations, hash: "SHA-256" },
    baseKey,
    { name: "AES-GCM", length: 256 },
    false,
    ["encrypt", "decrypt"],
  );
}

export async function encryptPack(jsonPack, password) {
  if (!jsonPack || typeof jsonPack !== "object" || Array.isArray(jsonPack)) {
    throw new TypeError("encryptPack needs a bookmark pack object, not a string or an array.");
  }
  if (typeof password !== "string" || !password) {
    throw new TypeError("encryptPack needs a non-empty password string.");
  }
  const salt = randomBytes(SALT_BYTES);
  const iv = randomBytes(IV_BYTES);
  const key = await deriveKey(password, salt, ENCRYPTION_ITERATIONS);
  const plaintext = new TextEncoder().encode(JSON.stringify(jsonPack));
  const ciphertext = await subtle().encrypt({ name: "AES-GCM", iv }, key, plaintext);
  return {
    format: ENCRYPTED_FORMAT,
    cipher: ENCRYPTION_CIPHER,
    kdf: ENCRYPTION_KDF,
    iterations: ENCRYPTION_ITERATIONS,
    salt: hexEncode(salt),
    iv: hexEncode(iv),
    ciphertext: hexEncode(new Uint8Array(ciphertext)),
  };
}

export async function decryptPack(encryptedPackage, password) {
  if (!encryptedPackage || typeof encryptedPackage !== "object" || Array.isArray(encryptedPackage)) {
    throw new Error("Decryption failed. Invalid password or corrupted payload");
  }
  if (typeof password !== "string" || !password) {
    throw new Error("Decryption failed. Invalid password or corrupted payload");
  }
  // A payload with a format field must be this encrypted
  // format, and a payload with cipher or kdf fields must
  // name the algorithms this module supports. A flat
  // Gemini style payload, with only salt, iv, and
  // ciphertext, is accepted with the version 1.0 defaults,
  // so packs made by the original prompt still decrypt.
  if (encryptedPackage.format !== undefined && encryptedPackage.format !== ENCRYPTED_FORMAT) {
    throw new Error("Decryption failed. Invalid password or corrupted payload");
  }
  if (encryptedPackage.cipher !== undefined && encryptedPackage.cipher !== ENCRYPTION_CIPHER) {
    throw new Error("Decryption failed. Invalid password or corrupted payload");
  }
  if (encryptedPackage.kdf !== undefined && encryptedPackage.kdf !== ENCRYPTION_KDF) {
    throw new Error("Decryption failed. Invalid password or corrupted payload");
  }
  const iterations =
    encryptedPackage.iterations === undefined ? ENCRYPTION_ITERATIONS : encryptedPackage.iterations;
  if (!Number.isInteger(iterations) || iterations < 1) {
    throw new Error("Decryption failed. Invalid password or corrupted payload");
  }
  try {
    const salt = hexDecode(encryptedPackage.salt, "salt");
    const iv = hexDecode(encryptedPackage.iv, "iv");
    const ciphertext = hexDecode(encryptedPackage.ciphertext, "ciphertext");
    const key = await deriveKey(password, salt, iterations);
    const plaintext = await subtle().decrypt({ name: "AES-GCM", iv }, key, ciphertext);
    return JSON.parse(new TextDecoder().decode(plaintext));
  } catch (error) {
    if (error instanceof Error && error.message === "Decryption failed. Invalid password or corrupted payload") {
      throw error;
    }
    throw new Error("Decryption failed. Invalid password or corrupted payload");
  }
}

export function isEncryptedPack(value) {
  return Boolean(
    value && typeof value === "object" && !Array.isArray(value) && typeof value.ciphertext === "string",
  );
}
