// Example: load the news pack, validate it, print its links.
//
// Run from the repo root:
//   node lib/js/example.mjs
//
// It loads packs/examples/news.json, prints the flattened links,
// and shows custom-properties where a bookmark has them.

import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import path from "node:path";
import { loadPack, validatePack, flattenUrls, packVersion } from "./open-bookmarks.mjs";

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const packPath = path.join(repoRoot, "packs", "examples", "news.json");
const pack = loadPack(readFileSync(packPath, "utf-8"));
const errors = validatePack(pack);
if (errors.length) throw new Error(errors.join("\n"));
console.log(`pack version: ${packVersion(pack)}`);
for (const link of flattenUrls(pack)) {
  let line = `${link.path} ${link.title} ${link.url}`;
  if (link["custom-properties"]) {
    line += ` custom-properties=${JSON.stringify(link["custom-properties"])}`;
  }
  console.log(line);
}
