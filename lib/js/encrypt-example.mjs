// Example: encrypt and decrypt a pack with a password.
// Run from the repo root:
//   node lib/js/encrypt-example.mjs
//
// This uses a test password only. Never use a test password
// for a real pack.

import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import path from "node:path";
import { encryptPack, decryptPack } from "./encrypt.mjs";
import { validatePack } from "./open-bookmarks.mjs";

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const pack = JSON.parse(readFileSync(path.join(repoRoot, "packs", "examples", "simple.json"), "utf-8"));
const password = "test-password-do-not-use";

const encrypted = await encryptPack(pack, password);
console.log("encrypted format:", encrypted.format);
console.log("salt bytes:", encrypted.salt.length / 2);
console.log("iv bytes:", encrypted.iv.length / 2);

const decrypted = await decryptPack(encrypted, password);
console.log("decrypted title:", decrypted.title);
console.log("validation errors:", validatePack(decrypted));

try {
  await decryptPack(encrypted, "wrong-password");
  console.log("wrong password unexpectedly worked");
} catch (error) {
  console.log("wrong password:", error.message);
}
