// Password based encryption for open-bookmarks packs, in TypeScript.
// Same payload and parameters as lib/js/encrypt.mjs, with types.
// No npm dependencies, only the native Web Crypto API.
//
// This file uses only erasable TypeScript syntax, so it can run
// under Node type stripping and can be type checked with a
// TypeScript compiler, like the main TypeScript library.
//
// It does NOT run out of the box in React Native. Hermes has
// no crypto.subtle, so a React Native reader needs a different
// engine behind the same payload format. See docs/ENCRYPTION.md.

import type { Pack } from "./open-bookmarks.ts";

export const ENCRYPTED_FORMAT = "open-bookmarks/encrypted/1.0";
export const ENCRYPTION_CIPHER = "AES-256-GCM";
export const ENCRYPTION_KDF = "PBKDF2-HMAC-SHA-256";
export const ENCRYPTION_ITERATIONS = 600000;
export const SALT_BYTES = 16;
export const IV_BYTES = 12;

export interface EncryptedPack {
  format?: string;
  cipher?: string;
  kdf?: string;
  iterations?: number;
  salt: string;
  iv: string;
  ciphertext: string;
}

type SubtleCrypto = {
  importKey: (...args: unknown[]) => Promise<unknown>;
  deriveKey: (...args: unknown[]) => Promise<unknown>;
  encrypt: (...args: unknown[]) => Promise<unknown>;
  decrypt: (...args: unknown[]) => Promise<unknown>;
};

function subtle(): SubtleCrypto {
  const cryptoObject = (globalThis as { crypto?: { subtle?: SubtleCrypto; getRandomValues?: (array: Uint8Array) => Uint8Array } }).crypto;
  if (!cryptoObject || !cryptoObject.subtle) {
    throw new Error(
      "Web Crypto API is not available in this environment. " +
        "This module needs globalThis.crypto.subtle, as in a modern browser or Node.js 20 or later. " +
        "It does not run in React Native out of the box.",
    );
  }
  return cryptoObject.subtle;
}

function randomBytes(length: number): Uint8Array {
  const cryptoObject = (globalThis as { crypto?: { getRandomValues?: (array: Uint8Array) => Uint8Array } }).crypto;
  if (!cryptoObject || !cryptoObject.getRandomValues) {
    throw new Error("Secure random values are not available in this environment.");
  }
  return cryptoObject.getRandomValues(new Uint8Array(length));
}

function hexEncode(bytes: Uint8Array): string {
  return Array.from(bytes, (byte) => byte.toString(16).padStart(2, "0")).join("");
}

function hexDecode(value: unknown, field: string): Uint8Array {
  if (typeof value !== "string" || value.length % 2 !== 0 || !/^[0-9a-fA-F]*$/.test(value)) {
    throw new Error("Decryption failed. Invalid password or corrupted payload");
  }
  const bytes = new Uint8Array(value.length / 2);
  for (let i = 0; i < bytes.length; i += 1) {
    bytes[i] = parseInt(value.slice(i * 2, i * 2 + 2), 16);
  }
  if (field === "salt" && bytes.length !== SALT_BYTES) {
    throw new Error("Decryption failed. Invalid password or corrupted payload");
  }
  if (field === "iv" && bytes.length !== IV_BYTES) {
    throw new Error("Decryption failed. Invalid password or corrupted payload");
  }
  if (field === "ciphertext" && bytes.length === 0) {
    throw new Error("Decryption failed. Invalid password or corrupted payload");
  }
  return bytes;
}

async function deriveKey(password: string, salt: Uint8Array, iterations: number): Promise<unknown> {
  const encoder = new TextEncoder();
  const cryptoSubtle = subtle();
  const baseKey = await cryptoSubtle.importKey("raw", encoder.encode(password), "PBKDF2", false, ["deriveKey"]);
  return cryptoSubtle.deriveKey(
    { name: "PBKDF2", salt, iterations, hash: "SHA-256" },
    baseKey,
    { name: "AES-GCM", length: 256 },
    false,
    ["encrypt", "decrypt"],
  );
}

export async function encryptPack(jsonPack: Pack, password: string): Promise<EncryptedPack> {
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
  const ciphertext = (await subtle().encrypt({ name: "AES-GCM", iv }, key, plaintext)) as ArrayBuffer;
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

export async function decryptPack(encryptedPackage: EncryptedPack, password: string): Promise<Pack> {
  if (!encryptedPackage || typeof encryptedPackage !== "object" || Array.isArray(encryptedPackage)) {
    throw new Error("Decryption failed. Invalid password or corrupted payload");
  }
  if (typeof password !== "string" || !password) {
    throw new Error("Decryption failed. Invalid password or corrupted payload");
  }
  if (encryptedPackage.format !== undefined && encryptedPackage.format !== ENCRYPTED_FORMAT) {
    throw new Error("Decryption failed. Invalid password or corrupted payload");
  }
  if (encryptedPackage.cipher !== undefined && encryptedPackage.cipher !== ENCRYPTION_CIPHER) {
    throw new Error("Decryption failed. Invalid password or corrupted payload");
  }
  if (encryptedPackage.kdf !== undefined && encryptedPackage.kdf !== ENCRYPTION_KDF) {
    throw new Error("Decryption failed. Invalid password or corrupted payload");
  }
  const iterations = encryptedPackage.iterations === undefined ? ENCRYPTION_ITERATIONS : encryptedPackage.iterations;
  if (!Number.isInteger(iterations) || iterations < 1) {
    throw new Error("Decryption failed. Invalid password or corrupted payload");
  }
  try {
    const salt = hexDecode(encryptedPackage.salt, "salt");
    const iv = hexDecode(encryptedPackage.iv, "iv");
    const ciphertext = hexDecode(encryptedPackage.ciphertext, "ciphertext");
    const key = await deriveKey(password, salt, iterations);
    const plaintext = (await subtle().decrypt({ name: "AES-GCM", iv }, key, ciphertext)) as ArrayBuffer;
    return JSON.parse(new TextDecoder().decode(plaintext)) as Pack;
  } catch (error) {
    if (error instanceof Error && error.message === "Decryption failed. Invalid password or corrupted payload") {
      throw error;
    }
    throw new Error("Decryption failed. Invalid password or corrupted payload");
  }
}

export function isEncryptedPack(value: unknown): boolean {
  return Boolean(
    value && typeof value === "object" && !Array.isArray(value) && typeof (value as EncryptedPack).ciphertext === "string",
  );
}
