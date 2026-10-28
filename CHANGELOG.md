# Changelog

Entries are added per release. Versions follow the policy in
SPEC.md: major changes break old readers, minor changes are
additive only, patch changes are wording clarifications that do
not change the `format` value.

## 1.0 - Draft, unpublished - 2026-10-27

Not yet published. Breaking changes are still allowed before the
1.0 publication.

Added:

- Pack format `open-bookmarks/1.0`, with folder, url, and remote
  folder nodes, and snapshot import by default.
- URL rules: http and https only, https only for remote sources,
  depth limit of 4 folder levels, dedupe by URL, cycle protection for remote
  folders.
- `custom-properties`: an object allowed on the pack, on folders,
  and on url bookmarks, for client use only. The standard does not
  interpret any key inside it. Export to Netscape HTML drops it,
  because Netscape HTML has no place for it.
- Converters from Netscape Bookmark HTML, Chrome Bookmarks JSON,
  Firefox JSON, XBEL XML, and simple title/url CSV or JSON lists,
  and export from open-bookmarks back to Netscape HTML.
- A dependency free validator, and dependency free Python,
  JavaScript, and TypeScript libraries for loading, validating,
  flattening, and expanding remote folders. A Go library was
  planned but not added, because the Go toolchain was not
  available to test it in the build environment.
- Example packs for News, Movies, Tech, Simple, Nested, Remote,
  and Custom properties, with a docs page listing every pack.
- Syntax docs with formal conformance language, normative
  references, and valid and invalid examples for every field.
- Package files prepared, not published: a Node package in
  lib/js and a Python package in lib/python, both version 0.1.0
  while the format is 1.0 Draft, with publishing notes. No npm,
  PyPI, or Vercel publish has been made.
- Docs publishing routes for GitHub Pages and for Vercel, with
  an HTML entry page in docs, in the same repo, not a new repo.
- Monorepo docs: one repo holding the spec, schema, tools, docs,
  example packs, and several libraries side by side, each
  published independently from its own folder.
- Pack `version` field, added to the 1.0 draft: an optional
  non-empty string at pack root, the author's version of that
  pack, for example "1.2.0", distinct from the `format` field,
  which carries the standard version "open-bookmarks/1.0".
  Semantic versioning is recommended but not a validity rule,
  and version alone is not proof of change. Reader update
  guidance is defined in SPEC.md Section 12: a reader stores
  source URL, version, updated date, and local copy, and on a
  manual refresh only, compares version, updated, and a content
  diff by URL, then shows an update option instead of replacing
  the copy on its own. No hash field was added: a hash was
  discussed and explicitly parked, not implemented. The format
  version is unchanged.
- Standard `icon` field, added to the 1.0 draft after the first
  push, not yet pushed again: an optional object on the pack, on
  folders, and on url nodes, with a required src that must be an
  https URL or an image data URI, an optional type from
  image/png, image/svg+xml, image/x-icon, image/webp, image/gif,
  or image/jpeg, and optional sizes like "32x32" or "any".
  Readers must support PNG and SVG. Icon is distinct from the
  custom-properties icon name, which is unchanged. The validator
  and the Python, JavaScript, and TypeScript libraries validate
  icon the same way, and flattening includes icon when a
  bookmark has it. Converters map Netscape ICON_URI and Firefox
  iconuri to icon, skip a bare Netscape ICON with no MIME type,
  and export an https icon as ICON_URI and a base64 data URI
  icon as ICON, dropping type and sizes. No tags field, no
  added field, and no hash field were added with icon. The
  format version is unchanged.
- Honest review fixes, before first push: the open-bookmarks to
  open-bookmarks converter now preserves description, source,
  updated, version, and custom-properties, instead of dropping
  them; the converter's remote source check now requires https,
  not just http; the validator and all three libraries now reject
  a URL with no host, a pack source that is not https, a
  description that is not a string, and an updated value that is
  not an ISO 8601 date or date-time, all of which the spec
  already required; packVersion now returns null for a
  whitespace-only version, matching validation; the expand
  wording now says once per path from the root, not once per
  tree, which matches the actual cycle protection; the schema
  now patterns title and version to reject whitespace-only
  values, and updated to reject non-ISO shapes.
