# open-bookmarks

Status: 1.0 Draft, not yet published. Breaking changes are still
allowed before the 1.0 publication. See [docs/versions.md](docs/versions.md)
and [CHANGELOG.md](CHANGELOG.md).

A simple, open format for sharing bookmark packs. A pack is a JSON file
with folders and links. Anyone can write one, host it anywhere, and
share it by URL. No account, no server, no lock-in.

Any browser or tool can read it. The format does not belong to any
single app.

## A small example

```json
{
  "format": "open-bookmarks/1.0",
  "title": "News",
  "description": "A few news sites I check most mornings.",
  "nodes": [
    {
      "type": "folder",
      "title": "World",
      "nodes": [
        { "type": "url", "title": "BBC News", "url": "https://www.bbc.com/news" }
      ]
    },
    {
      "type": "folder",
      "title": "Tech News",
      "source": "https://example.com/tech-news.json"
    }
  ]
}
```

A folder can hold links directly, or it can point at another pack with
a `source` URL. That is how a pack stays small while still going deep.
Readers should only fetch that second file when someone opens the
folder, not up front.

The full rules are in [SPEC.md](SPEC.md), and the machine-readable
version is in [schema/open-bookmarks.schema.json](schema/open-bookmarks.schema.json).
For a field by field syntax guide with valid and invalid examples,
see [docs/SYNTAX.md](docs/SYNTAX.md).

## custom-properties

A pack, a folder, and a bookmark can each carry a
`custom-properties` object. The standard does not interpret what is
inside it. Clients use it for their own purposes, for example a UI
icon and colour, an analytics ID, or their own version tag:

```json
{
  "type": "url",
  "title": "BBC News",
  "url": "https://www.bbc.com/news",
  "custom-properties": {
    "icon": "globe",
    "accent": "#1f6feb"
  }
}
```

The value must be an object. Readers preserve it and include it in
flattened output for bookmarks that have it, and ignore keys inside
it they do not know. Converting to Netscape HTML drops it, because
Netscape HTML has no place for it. The full rules are in
[SPEC.md](SPEC.md).

## icon

A pack, a folder, and a bookmark can each carry an optional
`icon` object. It is different from the `icon` key inside
`custom-properties`, which is just a client name like "globe".
The standard `icon` points at an image:

```json
{
  "type": "url",
  "title": "BBC News",
  "url": "https://www.bbc.com/news",
  "icon": {
    "src": "https://www.bbc.com/favicon.ico",
    "type": "image/x-icon",
    "sizes": "16x16 32x32"
  }
}
```

Inside `icon`, `src` is required, `type` and `sizes` are
optional. `src` must be an https URL or an image data URI.
`type` must be one of image/png, image/svg+xml, image/x-icon,
image/webp, image/gif, or image/jpeg. Readers must support PNG
and SVG. Writers should use PNG or SVG, and should not fetch an
icon URL on import, only when the icon is shown. The full rules
are in [SPEC.md](SPEC.md) Section 7.1 and
[docs/SYNTAX.md](docs/SYNTAX.md).

## Versioning

The current version is 1.0 Draft, unpublished. The `format` field
carries the version of the standard, as `"open-bookmarks/1.0"`.
Major changes break old readers, minor changes are additive only,
and patch changes are wording clarifications that do not change
the format value. Readers accept the same major version, warn on
a newer minor version, and reject a different major version. See
[docs/versions.md](docs/versions.md)
and [CHANGELOG.md](CHANGELOG.md).

Separate from that, a pack can carry its own optional `version`
field, for example `"1.2.0"`. That is the author's version of
that pack, not the format version, and it is how a reader can
offer an update: on a manual refresh only, it compares the
stored version, the stored updated date, and a content diff by
URL, then shows an update option instead of replacing your copy
on its own. The full rules are in [SPEC.md](SPEC.md) Section 12.
No hash field is defined in this draft; that was discussed and
parked, not added.

## Import a pack

You have two ways in:

1. By URL: paste the URL of a pack JSON file into a reader that
   supports open-bookmarks.
2. By file: download the pack JSON, then import the file.

Importing takes a snapshot. If the author changes the pack later, your
copy does not change until you refresh it on purpose. That keeps a
shared pack from quietly swapping a link under you. On that manual
refresh, a reader compares version, updated date, and a content diff
by URL, as described in SPEC.md Section 12, and shows an update
option if anything changed.

## Convert your old bookmarks

The converters live in `tools/` and need only Python 3, nothing else
to install.

```sh
python3 tools/convert.py --from netscape --to open-bookmarks \
  --input bookmarks.html --output my-pack.json

python3 tools/convert.py --from chrome --to open-bookmarks \
  --input Bookmarks --output my-pack.json

python3 tools/convert.py --from open-bookmarks --to netscape \
  --input my-pack.json --output bookmarks.html
```

Supported inputs: Netscape Bookmark HTML, Chrome Bookmarks JSON,
Firefox JSON, XBEL XML, and a simple title/url CSV or JSON list.
Run `python3 tools/convert.py --help` for the full list.

Check a pack before you share it:

```sh
python3 tools/validate.py packs/examples/news.json
```

## Use it in code

There are three small libraries, all with no dependencies:

- Python: see [lib/python/README.md](lib/python/README.md)
- JavaScript (ESM): see [lib/js/README.md](lib/js/README.md)
- TypeScript: see [lib/ts/README.md](lib/ts/README.md)

All can load a pack, validate it, flatten it to a list of links,
and expand remote folders when you hand them a fetch function. They
do no network calls on their own.

## Install, not yet published

The libraries are prepared as packages, but they are not published
yet, so do not try these commands until a release is announced.
When they are published, they will be:

```sh
npm install open-bookmarks
pip install open-bookmarks
```

Until then, copy the library file from this repo, as described in
the library READMEs below. The package files are prepared in
lib/js/package.json and lib/python/pyproject.toml, with package
version 0.1.0, because the format itself is still 1.0 Draft and
unpublished. See lib/js/PUBLISHING.md and lib/python/PUBLISHING.md
for the manual publish steps that are still needed.

## Example packs

See [docs/EXAMPLES.md](docs/EXAMPLES.md) for every example pack,
what it shows, and a short snippet of each. The packs include:

- [packs/examples/news.json](packs/examples/news.json)
- [packs/examples/movies.json](packs/examples/movies.json)
- [packs/examples/simple.json](packs/examples/simple.json)
- [packs/examples/nested.json](packs/examples/nested.json)
- [packs/examples/remote.json](packs/examples/remote.json)
- [packs/examples/custom-properties.json](packs/examples/custom-properties.json)
- [packs/examples/icon.json](packs/examples/icon.json)
- [packs/examples/tech.json](packs/examples/tech.json)

## Monorepo

This repo is a monorepo: one repo holds the spec, schema, tools,
docs, example packs, and several libraries side by side. See
[docs/MONOREPO.md](docs/MONOREPO.md) for how the libraries are
published independently, how versioning works across them, and how
to add a new library without changing the spec.

## Docs

The docs are plain Markdown in `docs/`. To publish them, see
[docs/DEPLOY.md](docs/DEPLOY.md). It is a short GitHub Pages guide
with no build step.

## Licence

MIT. See [LICENSE](LICENSE).
