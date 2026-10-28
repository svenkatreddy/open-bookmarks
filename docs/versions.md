# open-bookmarks versions

This page lists every version of the format, newest first. The docs
in `docs/index.md` always describe the current version. When a new
version is published, add a row here and a matching entry in
`CHANGELOG.md` at the repo root. Do not rewrite the current docs
to describe an old version; old versions are recorded here for
reference.

| Version | Status | Date | What it contains |
| --- | --- | --- | --- |
| 1.0 | Draft, unpublished | 2026-10-27 | Pack format with folder, url, and remote folder nodes, snapshot import, https only URLs, depth limit of 4 folder levels, cycle limits, converters from Netscape HTML, Chrome JSON, Firefox JSON, XBEL, and simple lists, export back to Netscape HTML, Python, JavaScript, and TypeScript libraries, the `custom-properties` object for client use, the optional pack `version` field for reader update guidance, and the optional standard `icon` object on packs, folders, and url nodes. No hash field is defined in this draft; a hash was discussed and parked, not added. No tags field and no added field were added with icon. |

Versioning rules, in short:

- Major change: breaking, for example removing or renaming a
  required field, or changing a node type old readers cannot handle.
- Minor change: additive only, for example a new optional field or
  a new node type old readers can safely ignore.
- Patch change: wording clarifications in the spec or docs only.
  The `format` value does not change.

Readers accept the same major version, ignore unknown fields, warn
on a newer minor version and still read the fields they know, and
reject or clearly warn on a different major version.

While 1.0 is a draft, breaking changes are still allowed before
publication. Once 1.0 is published, the rules above apply in full.

Draft note, 2026-10-27: the pack `version` field was added to
the draft, as an optional string distinct from the `format`
field. The format version did not change. A hash field was
explicitly not added at the same time; it remains parked.

Draft note, 2026-10-27: the standard `icon` field was added to
the draft after the first push, as an optional object on packs,
folders, and url nodes. The format version did not change. Tags
and added were not added with icon, and a hash field remains
parked. This icon update has not been pushed again yet.
