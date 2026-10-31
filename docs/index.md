# open-bookmarks docs

Status: 1.0 Draft, not yet published. Breaking changes are still
allowed before the 1.0 publication.

This is the documentation for open-bookmarks, a simple open format
for sharing bookmark packs. This page always describes the current
version. Past versions, when they exist, are listed in
[versions.md](versions.md).

Start with the [spec](../SPEC.md). It is short and it is the source
of truth for the format. The [README](../README.md) shows a small
example pack and how to run the converters. For a field by field
syntax guide, see [SYNTAX.md](SYNTAX.md). For every example pack,
see [EXAMPLES.md](EXAMPLES.md). For password encrypted packs,
see [ENCRYPTION.md](ENCRYPTION.md), or try the browser tool in
[ENCRYPT-TOOL.md](ENCRYPT-TOOL.md). For how this repo holds several
libraries side by side, see [MONOREPO.md](MONOREPO.md).

In short:

- A pack is a JSON file with folders and links.
- A folder can point at another pack with a `source` URL.
- Importing takes a snapshot. Remote packs only change your copy when
  you refresh on purpose.
- Only http and https links are allowed. Anything else is rejected.

## Versioning

The `format` field carries the version of the standard, as
`"open-bookmarks/1.0"`. Major changes break old readers, minor
changes are additive only, and patch changes are wording
clarifications that do not change the format value. Readers
accept the same major version, warn on a newer minor version,
and reject a different major version.

Separate from that, a pack can carry its own optional `version`
field, the author's version of that pack, for example `"1.2.0"`.
That field, with the updated date and a content diff by URL, is
how a reader offers an update on a manual refresh only. See
SPEC.md Section 12. No hash field is defined in this draft; that
was discussed and parked, not added.

See [versions.md](versions.md) for the version list, and
[CHANGELOG.md](../CHANGELOG.md) for release notes.

To publish these docs, see [DEPLOY.md](DEPLOY.md).
