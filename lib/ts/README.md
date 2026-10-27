# open-bookmarks, TypeScript library

No dependencies. Typed definitions and the same behaviour as the
JavaScript library, in a single TypeScript file,
`open-bookmarks.ts`. It uses only erasable TypeScript syntax, so
it can run under Node type stripping and can be type checked with
a TypeScript compiler, without a build step for the example below.

## Import it

Copy `open-bookmarks.ts` into your project, then import it by
relative path:

```ts
import { loadPack, validatePack, flattenUrls } from "./open-bookmarks.ts";
```

If your project uses a TypeScript compiler, include the file in
your sources and use the same import, without the `.ts` extension
if your compiler setup prefers that. The exported types are
`Pack`, `PackNode`, `UrlNode`, `FolderNode`, `FlatLink`, and
`CustomProperties`, plus `FetchFunction` for remote expansion.

There is no CommonJS version. If your project uses `require`,
use a dynamic `import()` instead.

## Load a pack from a string or a file

`loadPack` accepts an object or a JSON string, and returns a pack
object. It does not validate. Always validate after loading.

From a file, in Node:

```ts
import { readFileSync } from "node:fs";
import { loadPack, validatePack, flattenUrls } from "./open-bookmarks.ts";

const pack = loadPack(readFileSync("packs/examples/news.json", "utf-8"));
```

From a string:

```ts
const pack = loadPack('{"format": "open-bookmarks/1.0", "title": "My links", "nodes": []}');
```

If the text is not valid JSON, `loadPack` throws a `SyntaxError`.
If you pass a value that is not an object or a string, it throws
a `TypeError`.

## Validate it and handle errors

`validatePack` returns a list of error strings. An empty list
means the pack is valid. A newer minor version is a warning, not
an error, so check warnings separately.

```ts
const errors = validatePack(pack);
if (errors.length) throw new Error(errors.join("\n"));

for (const warning of formatWarnings(pack)) {
  console.log("warning:", warning);
}

console.log("format:", formatVersion(pack));
```

The checks are the same as in the JavaScript library: format is
"open-bookmarks/1.0" or a newer minor version, title is non-empty
after trimming whitespace, nodes is a list, every node has a known
type and a non-empty title, every url is http or https, every
remote source is https, any custom-properties value is an object,
and no folder sits at level 5 or deeper. The depth limit is 4
folder levels. A folder directly in the pack is level 1, and a link
inside a level 4 folder is allowed. A different major version is
an error, not a warning.

## Flatten it to links, with folder path

`flattenUrls` returns a flat list in pack order, deduped by URL,
keeping the first occurrence. Each entry has title, url, and path,
where path is the folder path joined with "/". A top-level link
has an empty path.

```ts
for (const link of flattenUrls(pack)) {
  console.log(link.path, link.title, link.url);
}
```

For the news pack, that prints the World folder links, with path
"World", and no Tech News links, because those live in a remote
folder that has not been expanded yet.

## Read custom-properties from flattened output

If a bookmark has custom-properties, that object is included in
its flattened entry, unchanged, under the key "custom-properties".
Keys inside it are not interpreted. A bookmark without it
flattens exactly as before, with no custom-properties key.

```ts
for (const link of flattenUrls(pack)) {
  const props = link["custom-properties"];
  if (props) {
    console.log(link.title, props);
  }
}
```

For the news pack, BBC News has custom-properties with an icon
and an accent. Reuters does not, so its entry has no
custom-properties key.

## Expand a remote folder

Remote folders only expand when you supply a fetch function. The
library itself never does network calls. The fetch function takes
a source URL and returns a pack object, a JSON string, or null if
the source cannot be loaded. A source that fails to load is left
as an unexpanded folder.

```ts
import { expandRemote } from "./open-bookmarks.ts";
import { readFileSync } from "node:fs";

const expanded = expandRemote(pack, (url) => {
  if (url.endsWith("tech.json")) {
    return readFileSync("packs/examples/tech.json", "utf-8");
  }
  return null;
});

for (const link of flattenUrls(expanded)) {
  console.log(link.path, link.title, link.url);
}
```

With that fetch function, the news pack expands to five links:
the three World links, plus Hacker News and The Verge under
"Tech News". Expansion stops at the depth limit of 4 folder
levels, and a source URL is expanded at most once per path from the root, so
cycles stop safely.

## How version warnings work

`formatVersion` returns the format string, for example
"open-bookmarks/1.0", or null if it is missing.
`formatWarnings` returns a list of version warnings. It returns
an empty list for "open-bookmarks/1.0" and for a missing format,
because a missing format is already an error in `validatePack`.
It returns a warning for a newer minor version such as
"open-bookmarks/1.1", and the pack is still read with the fields
the library knows. It returns no warning for a different major
version, because that case is an error in `validatePack`.

## Pack version

`packVersion` returns the author version of a pack, for
example "1.2.0", or null if the pack has no version field. This
is not the format version: `formatVersion` returns
"open-bookmarks/1.0", while `packVersion` returns the version
of that single pack. The field is optional, and its value is a
non-empty string. Semantic versioning is recommended for authors
but is not a validity rule, so a non-semantic string is still
valid, and a reader compares versions as plain strings. Version
alone is not proof that links changed, so for update guidance
see SPEC.md Section 12: a reader stores the source URL, the
version it saw, the updated date it saw, and the local copy, and
on a manual refresh only, it compares version, updated, and a
content diff by URL, then shows an update option instead of
replacing the copy on its own.

## Runnable example

Run this from the repo root, with Node type stripping:

```sh
node lib/ts/example.ts
```

It loads `packs/examples/news.json`, validates it, prints the
flattened links, and shows custom-properties where present.

## Functions

- `loadPack(data)`: object or JSON string in, pack object out.
- `formatVersion(pack)`: the `format` string, for example
  `open-bookmarks/1.0`, or null if missing.
- `packVersion(pack)`: the author `version` of this pack, for
  example `1.2.0`, or null if missing. Not the format version.
- `formatWarnings(pack)`: list of version warnings, empty for
  1.0. A newer minor version warns, a different major version
  does not warn here, because it is an error in `validatePack`.
- `validatePack(pack)`: list of error strings, empty if valid.
- `flattenUrls(pack)`: flat list of `title`, `url`, and `path`
  (the folder path, joined with `/`), deduped by URL, in pack order.
  If a bookmark has `custom-properties`, that object is included
  in its flattened entry, unchanged.
- `expandRemote(pack, fetch)`: a copy of the pack with remote
  folders expanded. Depth is capped at 4 folder levels, and a
  source URL is expanded at most once per path from the root, so cycles stop
  safely.
