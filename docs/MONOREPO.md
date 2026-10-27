# Monorepo: one repo, several libraries

Yes, this repo already is a monorepo. One repo holds the spec,
the schema, the tools, the docs, the example packs, and several
libraries side by side. That is deliberate, and it is how the
project is meant to stay for now.

## What lives here

- Spec and schema: `SPEC.md` at the repo root, and
  `schema/open-bookmarks.schema.json`. These are shared. No
  library defines the format on its own.
- Tools: `tools/convert.py` and `tools/validate.py`, with test
  fixtures in `tools/tests/fixtures/`. These are shared test
  material for every library.
- Docs: `docs/`, including `SYNTAX.md`, `EXAMPLES.md`,
  `DEPLOY.md`, `versions.md`, and the HTML entry page
  `index.html`.
- Example packs: `packs/examples/`, including News, Movies, Tech,
  Simple, Nested, Remote, and Custom properties. Every library is
  tested against the same packs, so a change in one library can
  be checked against the same files as a change in another.
- Libraries, each in its own folder under `lib/`:
  - Python: `lib/python/`, single file `open_bookmarks.py`,
    package file `pyproject.toml`, README, example, and
    publishing note.
  - JavaScript: `lib/js/`, single file `open-bookmarks.mjs`,
    type declarations `open-bookmarks.d.ts`, package file
    `package.json`, README, example, and publishing note.
  - TypeScript: `lib/ts/`, single file `open-bookmarks.ts`,
    README, and example. It uses only erasable TypeScript syntax,
    so it can run under Node type stripping and can be type
    checked with a TypeScript compiler.

A Go library is not in this repo yet. Go was planned, but the Go
toolchain is not available in the environment where this scaffold
was built, so a Go library was not added untested. When a Go
library is added, it should follow the same pattern: a folder
under `lib/go/`, a `go.mod` file, a README, and a runnable example
that loads the news pack and prints the same flattened links as
the other libraries. Until then, do not list Go as a shipped
library. The pattern below is written so a future Go library fits
without changing the spec.

## How each library is published independently

Each library lives in its own folder with its own package
manifest, and is published independently from that folder. That
is the whole point of the monorepo layout here: npm, PyPI, and a
future Go module do not need separate repos.

- Node: publish from `lib/js`, using `lib/js/package.json`.
  See `lib/js/PUBLISHING.md`.
- Python: publish from `lib/python`, using
  `lib/python/pyproject.toml`. See `lib/python/PUBLISHING.md`.
- TypeScript: the TypeScript source in `lib/ts/` is for projects
  that want typed source directly. The Node package in `lib/js/`
  already ships type declarations, so most TypeScript users can
  use the Node package and do not need a separate TypeScript
  package. If a separate TypeScript package is wanted later, it
  should be published from `lib/ts/` with its own package file,
  following the same pattern, and that decision should be made
  explicitly, not by accident.

Shared parts are never published as part of a library package,
except where a package manifest lists them. The npm package
lists only its own library files. The Python package lists only
its own module. The spec, schema, tools, docs, and example packs
stay in the repo for everyone to read, and are not bundled into
every library release.

## Versioning in the monorepo

There are two kinds of version in this repo, and they are not the
same thing.

- Format version: shared. It lives in the `format` field of every
  pack, currently "open-bookmarks/1.0", status Draft, unpublished.
  It changes only when the format itself changes, as defined in
  `SPEC.md`.
- Package version: per library. Each package starts at 0.1.0
  until the format is published, because the package itself has
  not had a 1.0 release yet. That is why a package can be 0.1.0
  while the format it implements is called 1.0 Draft. The two
  numbers are related, not identical.

Rules for later releases:

- A bug fix in one language alone bumps only that package. For
  example, a fix in the Python library alone bumps only the
  Python package version, and the other packages stay where they
  are.
- A format change bumps all libraries together, because every
  library must implement the new format, or clearly state which
  format version it implements. A format change also updates the
  spec, the schema, the validator, the converters, and the
  example packs, in the same change, so the libraries are never
  left implementing different formats without a note saying so.
- A change to docs, tools, or examples alone, with no format
  change and no library code change, does not need a package
  version bump. Record it in the changelog instead.

## Adding a new library

Adding a new library means adding a new folder under `lib/`, with
no change to the spec itself, unless the new library uncovers a
bug in the spec, in which case fix the spec first and record it
in the changelog.

Steps:

1. Create a folder under `lib/`, named for the language, for
   example `lib/go/` for Go.
2. Add the library code, with no external dependencies unless
   there is a clear reason, and document any dependency in the
   library README.
3. Add a README in that folder, with the same usage sections as
   the other libraries: load from a string or a file, validate
   and handle errors, flatten to links with folder path, expand
   a remote folder with a caller-supplied fetch function, read
   custom-properties from flattened output, and how version
   warnings work.
4. Add a runnable example in that folder that loads
   `packs/examples/news.json` and prints the same flattened links
   as the Python and JavaScript examples.
5. Add the library's own manifest in that folder, for example
   `package.json`, `pyproject.toml`, or `go.mod`, with the same
   package version rule as above, and a publishing note if the
   library is meant to be published.
6. Add the library to the list in this file, and to the list in
   the repo README, and run the validator and the library examples
   against the shared example packs before calling the library
   done.

## What this monorepo deliberately does not use

This repo does not use npm workspaces, pnpm workspaces, Turborepo,
Nx, or Lerna, and it should not add them in this change. Those
tools are overkill for a handful of dependency-free libraries.
They would add configuration, a build step, and a new tool to
learn, without benefit at this size. Each library is a single
file or a small set of files, with no dependencies and no build
step, so there is nothing for a workspace tool to coordinate.
If the repo grows to many libraries with shared build steps or
shared dependencies, that decision can be revisited then, with a
clear reason, not by default.

## Folder names, and a possible future cleanup

The libraries live under `lib/`, not under `packages/`. That is
the existing layout, and it is kept in this change. A rename to
`packages/` is a possible future cleanup if the owner wants it,
but it is not done now, because it would break links already
documented in the README, in the docs, and in the library READMEs,
and it would change every import path in the examples. If that
rename is ever made, it must be done in one change, with every
link and example updated in the same change, and recorded in the
changelog.
