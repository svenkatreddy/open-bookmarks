# open-bookmarks format, version 1.0

Status: 1.0 Draft, not yet published. Breaking changes are still
allowed before the 1.0 publication. See [docs/versions.md](docs/versions.md)
and [CHANGELOG.md](CHANGELOG.md) for the version history.

## 1. Conformance

The key words MUST, MUST NOT, REQUIRED, SHALL, SHALL NOT, SHOULD,
SHOULD NOT, RECOMMENDED, MAY, and OPTIONAL in this document are to
be interpreted as described in RFC 2119 [RFC2119] and clarified in
RFC 8174 [RFC8174] when, and only when, they appear in all capitals.
Words in lower case have no special meaning in this document.

Sections 1 to 13 are normative, except for examples and notes that
are explicitly marked as informative. All examples in this document
are non-normative. They illustrate a rule; they do not create a new
rule. If an example and a normative rule disagree, the normative
rule governs.

The machine-readable definition in
[schema/open-bookmarks.schema.json](schema/open-bookmarks.schema.json)
is normative for the shape it covers. The prose in this document is
also normative. The two definitions are intended to agree. Where they
differ in strength, this document states the difference in the
relevant section. In particular, the schema is version-specific for
1.0 and covers shape only; depth, cycle, and some string checks are
defined in prose and enforced by code, not by the schema alone.

## 2. Terminology

A pack is a single JSON object that holds a collection of bookmarks
in folders. A node is one entry in a pack. A folder is a node that
holds other nodes. A url node is a node that holds a single link.
A remote folder is a folder that has a source field pointing at
another pack file, so its children come from that file in addition
to, or instead of, inline children. A snapshot is a copy of a pack
made at import time. A reader is software that reads a pack, for
example a browser or a library. A writer is software that creates
or converts a pack, for example a converter or an editor. A
conformant pack, reader, or writer is one that satisfies the
conformance class in Section 4 for that role.

## 3. Normative references

- [RFC2119] S. Bradner, "Key words for use in RFCs to Indicate
  Requirement Levels", RFC 2119, March 1997.
- [RFC8174] B. Leiba, "Ambiguity of Uppercase vs Lowercase in
  RFC 2119 Key Words", RFC 8174, May 2017.
- [RFC8259] T. Bray, "The JavaScript Object Notation (JSON) Data
  Interchange Format", RFC 8259, December 2017.
- [RFC3986] T. Berners-Lee, R. Fielding, and L. Masinter, "Uniform
  Resource Identifier (URI): Generic Syntax", RFC 3986, January 2005.
- [ISO8601] ISO 8601, "Date and time format", for dates and
  date-times in the updated field.
- [JSONSCHEMA] JSON Schema, draft 2020-12, for the machine-readable
  definition in schema/open-bookmarks.schema.json.

## 4. Conformance classes

### 4.1 Conformant pack

A conformant pack MUST satisfy all of the following:

- It MUST be a JSON object as defined by [RFC8259].
- Its format field MUST be exactly "open-bookmarks/1.0".
- Its title MUST be a non-empty string, where non-empty means
  non-empty after trimming surrounding whitespace.
- Its nodes field MUST be a list, which MAY be empty.
- Every node MUST have a type of "folder" or "url" and a non-empty
  title, with the same trimming rule.
- Every url node MUST have a url field that satisfies Section 8.
- Every source field MUST satisfy Section 8.
- Folder nesting MUST NOT exceed 4 levels, as counted in Section 9. A folder at level 5 MUST NOT be present.
- Any custom-properties field present, on the pack or on a node,
  MUST be a JSON object, as defined in Section 7.
- Any version field present, on the pack, MUST be a non-empty
  string, as defined in Section 12.
- Any icon field present, on the pack or on a node, MUST be an
  object with a required src, as defined in Section 7.1.

A pack that satisfies this list is conformant even if it contains
unknown fields. Readers MUST ignore unknown fields, as stated in
Section 5.

### 4.2 Conformant reader

A conformant reader MUST do all of the following:

- Accept a conformant pack and read the fields it knows.
- Ignore unknown fields and unknown keys inside custom-properties,
  and MUST NOT reject a pack only because of an unknown field.
- Reject, or clearly warn and refuse to trust, a pack whose major
  version differs from the version it was built for, naming the
  version found.
- Warn, not fail, on a newer minor version, and still read the
  fields it knows.
- Apply the URL rules in Section 8, the depth and cycle rules in
  Section 9, and the remote folder rules in Section 6.
- Preserve custom-properties when loading a pack, and include it in
  flattened output for a bookmark that has it, as stated in
  Section 7.
- Fetch a remote source only when the user opens that folder, or
  when the user asks to import or refresh the pack, as stated in
  Section 6.
- Accept an optional pack version field, if present and a
  non-empty string, and MUST NOT reject a pack only because its
  version is not in semantic versioning form. Pack version
  handling is defined in Section 12.
- Preserve an icon field when loading a pack, and include it in
  flattened output for a bookmark that has it, as stated in
  Section 7.1. A reader MUST NOT fetch an icon URL on import;
  icon fetching is display only, as stated in Section 7.1.

### 4.3 Conformant writer

A conformant writer MUST do all of the following:

- Produce only conformant packs, as defined in Section 4.1.
- Write the format field exactly as "open-bookmarks/1.0".
- Write only http or https values in url fields, and only https
  values in source fields.
- Write custom-properties, if present, only as a JSON object.
- Write an icon field, if present, only as an object with a
  required src, as defined in Section 7.1.
- MUST NOT write a javascript:, data:, or file: URL in any url or
  source field. This rule does not ban a data URI as an icon
  src, which is allowed by Section 7.1 and is not a url or
  source field.

## 5. Pack

A pack is a single JSON object with the fields in Table 1.

Table 1. Pack fields. Normative.

| Field | Required | Type and rules |
| --- | --- | --- |
| format | Yes | String. MUST be exactly "open-bookmarks/1.0". |
| title | Yes | String. MUST be non-empty after trimming surrounding whitespace. |
| author | No | String. The person or group that made this pack. MUST be non-empty after trimming surrounding whitespace, if present. See below. |
| version | No | String. The author's version of this pack. See Section 12. |
| description | No | String. One or two sentences about what the pack is for. |
| source | No | String. The URL this pack was published at, if known. MUST be https, as defined in Section 8. |
| updated | No | String. An ISO 8601 [ISO8601] date or date-time, for example "2026-10-27". |
| nodes | Yes | List of nodes. MAY be empty. |
| icon | No | Object. An image for the pack. See Section 7.1. |
| custom-properties | No | JSON object for client use only. See Section 7. |

A reader MUST accept a pack even if description, source, updated,
version, icon, or author are missing. A reader MUST reject a pack if format is
wrong, title is missing or empty, or nodes is not a list, subject
to the minor version warning rule in Section 11.

Author, at pack level only: author names the person or group that
made the pack, the curator, not the author of any linked page.
A link in a pack can come from many different sites, so a pack
level author MUST NOT be read as the author of a link. Nodes do
not inherit author from the pack, and there is no author field
on a folder or on a url node in version 1.0. A reader SHOULD show
author with the pack title, when it is present, for example in a
pack list or a pack header. If a pack needs a link level author,
that belongs in custom-properties, or in a future field, not by
reusing the pack author.

Unknown fields at any level MUST be ignored. That rule is how the
format can grow later without breaking old readers. Readers MUST NOT
rely on unknown fields.

Note, informative: the schema and the validator both reject a
title that is only spaces, the schema by a pattern requiring a
non-space character and the validator by trimming. The prose rule
in this section governs if they ever disagree.

Note, informative: the schema and the validator both check that
updated, if present, matches an ISO 8601 date or date-time
pattern. The pattern checks the shape, month, day, and time
ranges, not the full calendar, so 2026-02-30 would pass the
pattern and still be a bad date. Authors SHOULD write a real
calendar date.

## 6. Nodes

Every node MUST have a type. There are two node types in version
1.0: "folder" and "url". There is no separate "remote" node type
in version 1.0. A remote folder is a folder with a source field,
as defined below.

### 6.1 url node

A url node is a single bookmark.

Example, non-normative:

```json
{ "type": "url", "title": "BBC News", "url": "https://www.bbc.com/news" }
```

Table 2. url node fields. Normative.

| Field | Required | Type and rules |
| --- | --- | --- |
| type | Yes | String. MUST be "url". |
| title | Yes | String. MUST be non-empty after trimming surrounding whitespace. |
| url | Yes | String. MUST be http or https, as defined in Section 8. |
| icon | No | Object. An image for the bookmark. See Section 7.1. |
| custom-properties | No | JSON object for client use only. See Section 7. |

### 6.2 folder node

A folder node holds other nodes.

Example, non-normative:

```json
{
  "type": "folder",
  "title": "World",
  "nodes": [
    { "type": "url", "title": "BBC News", "url": "https://www.bbc.com/news" }
  ]
}
```

Table 3. Folder node fields. Normative.

| Field | Required | Type and rules |
| --- | --- | --- |
| type | Yes | String. MUST be "folder". |
| title | Yes | String. MUST be non-empty after trimming surrounding whitespace. |
| nodes | No | List of child nodes. If absent, it defaults to an empty list. |
| source | No | String. See remote folders below. MUST be https, as defined in Section 8. |
| icon | No | Object. An image for the folder. See Section 7.1. |
| custom-properties | No | JSON object for client use only. See Section 7. |

A folder MAY have nodes, a source, or both. If it has both, readers
SHOULD show the inline nodes first, then expand the remote source
when the folder is opened.

### 6.3 Remote folders

A remote folder is written as a folder with a source field, not as
a separate node type, so that a folder can mix inline links and one
remote source.

Example, non-normative:

```json
{
  "type": "folder",
  "title": "Tech News",
  "source": "https://example.com/tech-news.json"
}
```

When a reader expands a remote folder, it MUST fetch the pack at
source, take that pack's top-level nodes, and show them as the
children of this folder. The remote pack's own title MUST NOT be
used as a folder name; the local folder title stays.

Remote folders are lazy. A reader MUST only fetch a remote source
when the user opens that folder, or when the user asks to import or
refresh the whole pack. A reader MUST NOT fetch remote sources in
the background, on app start, or just because a pack was listed.

Snapshot by default. Importing a pack MUST copy the links at that
moment. Later changes to the remote file MUST NOT change the
imported copy. A reader MAY offer a manual Refresh, which re-fetches
the sources the user asks for and replaces the snapshot for those
folders. Refresh MUST always be an explicit user action.

Cycle protection. A pack MAY point at itself, or two packs MAY
point at each other, but a reader MUST keep a set of source URLs
already visited while expanding one tree, and MUST stop expanding
a source that has been seen before. Expanding MUST also stop at
the depth limit in Section 9, even if no cycle is found.

## 7. custom-properties

A pack, a folder, and a url node MAY each carry a field called
custom-properties. Its value, when present, MUST be a JSON object.
Keys inside it are client-defined, and values MAY be any JSON value.
The standard does not interpret, validate, or require any key inside
it. It does not assign meaning to any key inside it.

Clients use it for their own purposes.

Example, non-normative:

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

Example, non-normative:

```json
{
  "type": "url",
  "title": "IMDb",
  "url": "https://www.imdb.com/",
  "custom-properties": {
    "icon": "film",
    "accent": "#f5c518",
    "client-version": "example-client-1"
  }
}
```

Other uses are just as valid: an analytics ID a client uses to count
opens, a UI element it wants to show, a version tag for its own
bookmarks, or anything else that is specific to that client and not
part of the shared format.

Rules for readers and writers, normative:

- If custom-properties is present, it MUST be an object. A string,
  number, array, or null value is invalid.
- Readers MUST preserve it when loading a pack, and MUST include it
  in flattened output for a bookmark that has it.
- Readers MUST ignore keys inside it they do not know. They MUST
  never reject a pack just because of a key inside it.
- Converters from old formats that have no equivalent field omit
  it. That is not an error; the converted pack simply has no custom
  properties.
- Exporting an open-bookmarks pack to Netscape HTML drops
  custom-properties, because Netscape HTML has no place to put it.
  The links and folders survive that export, the custom properties
  do not. Writers MUST NOT invent a Netscape encoding for it.

## 7.1 Icon

A pack, a folder, and a url node MAY each carry a field called
icon. It is optional everywhere. A pack or node with no icon is
valid, and a reader MUST NOT require one.

Icon is distinct from custom-properties. A custom-properties key
called "icon" is a client-defined name, for example "globe" or
"film". It is a string chosen by a client, and the standard does
not interpret it. The icon field in this section is different: it
is a standard object that points at an image file. The two MAY
appear together, and neither replaces the other. A reader MUST
NOT treat a custom-properties icon string as a standard icon
image, and MUST NOT treat a standard icon object as a
custom-properties name.

Table 4. Icon fields. Normative.

| Field | Required | Type and rules |
| --- | --- | --- |
| src | Yes, when icon is present | String. MUST be an https URL with a host, or an image data URI. See below. |
| type | No | String. If present, MUST be one of image/png, image/svg+xml, image/x-icon, image/webp, image/gif, or image/jpeg. |
| sizes | No | String. If present, MUST be "any", or one or more sizes like "32x32" separated by single spaces, for example "16x16 32x32". |

Rules, normative:

- If icon is present, it MUST be an object. A string, number,
  array, or null value is invalid. In particular, a string icon
  such as "globe" is invalid as an icon field, even though the
  same string is valid inside custom-properties.
- src, when icon is present, MUST be present and MUST be a
  non-empty string after trimming surrounding whitespace.
- src MUST be either an https URL with a host, or a data URI
  for an image. An http URL, a javascript: URL, a file: URL, a
  host-less URL, and a data URI that is not an image are all
  invalid as an icon src.
- A data URI src MUST start with "data:", followed by an image
  MIME type from the type list above, followed by a comma that
  separates the header from the data, followed by non-empty
  data. The header MAY include ";base64" for base64 data, or a
  charset for URL-encoded SVG, for example
  "data:image/svg+xml,%3Csvg%20...". Writers and readers MUST
  NOT validate the actual image bytes, only the MIME type and
  the comma separator, as stated here.
- type, if present, MUST be exactly one of the six MIME types
  in Table 4. A type that does not match the image at src is a
  writer error, but readers SHOULD use the type as a hint and
  fall back to the image itself when they disagree.
- sizes, if present, MUST be "any" or a space separated list of
  width by height sizes, each written as digits, "x", digits.
  "any" is for scalable images, normally SVG. A sizes value
  such as "large" or "32" is invalid.
- Readers MUST support PNG and SVG icons. Readers SHOULD support
  ICO (image/x-icon) and WebP icons. Readers MAY support GIF
  and JPEG icons.
- Writers SHOULD use PNG or SVG for icons. Writers SHOULD NOT
  use JPEG for icons, because JPEG has no transparency and loses
  quality when resized. Writers SHOULD NOT use animated GIFs
  for icons, because animation distracts and the files are large.
- Data URIs SHOULD stay small, about 64 KB or less, because a
  data URI is stored inside the pack file itself and bloats it.
  For a shared pack, writers SHOULD prefer an https URL for the
  icon, and use a data URI only for a small custom icon.
- Exporting an open-bookmarks pack to Netscape HTML preserves
  an icon src only, and drops type and sizes, because Netscape
  HTML has no place for them. An https icon src becomes an
  ICON_URI attribute. A base64 data URI icon src becomes an
  ICON attribute holding only the base64 part after the comma.
  A non-base64 data URI icon is dropped on Netscape export,
  because Netscape ICON expects base64 data. Folder icons are
  dropped on Netscape export, because a Netscape folder heading
  has no standard icon attribute.

Privacy guidance, informative, not a validity rule: a reader
SHOULD NOT fetch an icon URL when a pack is imported, listed, or
refreshed. It SHOULD fetch an icon only when the icon is about
to be shown. Where a reader can, it SHOULD prefer a site favicon
derived from the bookmark URL itself over a third-party icon
host, because fetching from a third-party host tells that host
the reader holds that bookmark. A data URI icon needs no fetch
at all, which is its privacy advantage, at the cost of pack size.

Example, non-normative:

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

Example, non-normative, an SVG data URI icon:

```json
{
  "type": "url",
  "title": "Example",
  "url": "https://example.com/",
  "icon": {
    "src": "data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20viewBox='0%200%2016%2016'%3E%3Ccircle%20cx='8'%20cy='8'%20r='8'%20fill='%231f6feb'/%3E%3C/svg%3E",
    "type": "image/svg+xml",
    "sizes": "any"
  }
}
```

## 8. URL rules

These rules apply to every url field and every source field:

- Only http and https are allowed in a url field.
- Only https is allowed in a source field.
- javascript:, data:, file:, and any other scheme MUST be rejected
  in a url field or a source field. A data URI is allowed only
  as an icon src, as defined in Section 7.1, and nowhere else.
- A URL with no scheme, or with spaces, MUST be rejected.
- Readers SHOULD keep the URL exactly as written, apart from
  trimming surrounding whitespace. They SHOULD NOT add tracking
  parameters.

URLs are URIs as defined by [RFC3986], with the scheme restrictions
in this section added by open-bookmarks. The scheme check is
case-insensitive for the purpose of accepting http, https, and
HTTPS spellings, and the stored URL is otherwise kept as written.

Converters MUST apply the same rules: skip a bad URL, warn about
it, and keep converting the rest. A single bad link MUST NOT break
a whole import.

## 9. Limits

These limits keep a pack safe to open, even if the author is
unknown:

- Max depth: 4 levels of folders. Depth is counted by folder
  levels below the pack root. A folder directly in the pack nodes
  list is at level 1. A folder inside a level 1 folder is at level
  2, and so on. A pack MAY contain folders nested up to 4 levels
  deep. A url MAY sit inside a folder at level 4. A folder at
  level 5 MUST NOT be present, and a pack with a folder at level 5
  is invalid. Such a folder MUST be rejected by the validator and
  SHOULD be skipped by a reader.
- Max nodes: readers SHOULD refuse or truncate a pack with more
  than 10,000 nodes in total after expansion. The exact behaviour is
  up to the reader, but it MUST NOT hang or run out of memory.
- Max file size: 1 MB for a single pack file is a sensible cap for
  readers to enforce. Larger files SHOULD be rejected with a clear
  message, not loaded and then failed halfway. This cap is a
  recommendation, not a pack validity rule, and the validator does
  not enforce it.
- Dedupe: when importing, readers and converters SHOULD dedupe by
  URL, keeping the first occurrence. The same URL MAY appear in two
  folders in a source file, but it SHOULD appear once after import,
  in the first folder where it was found. Dedupe is an import and
  flattening rule, not a pack validity rule: a pack with a repeated
  URL is not invalid on that ground alone.

## 10. Validation

A pack is valid if all of the following hold:

1. It is a JSON object with format set to "open-bookmarks/1.0",
   subject to the minor version warning rule in Section 11.
2. title is a non-empty string, after trimming surrounding
   whitespace, and nodes is a list.
3. Every node has a known type ("folder" or "url") and a
   non-empty title, after trimming surrounding whitespace.
4. Every url node has an http or https URL, and every source field
   is an https URL.
5. No folder is present at level 5 or deeper, as counted in
   Section 9. A folder at level 5 is invalid, even if it contains
   no links.
6. Remote sources do not form a cycle when expanded, as checked
   along the path from the root to a folder.
7. Any custom-properties present, on the pack or on a node, is a
   JSON object. Other values are invalid.
8. Any icon present, on the pack or on a node, is an object with
   a required src that is an https URL or an image data URI, an
   optional type from the list in Section 7.1, and optional
   sizes in the form in Section 7.1. Other values are invalid.

The JSON Schema in schema/open-bookmarks.schema.json covers items
1 to 4 and the shape of nodes. Depth and cycle checks need code, so
they live in tools/validate.py and in the libraries, not in the
schema alone. The schema is version-specific for 1.0: it states
format as a constant "open-bookmarks/1.0". A newer minor version
therefore fails the schema alone but passes the validator with a
warning, as stated in Section 11. That difference is intentional
and is documented here so it is not mistaken for an error.

## 11. Versioning

Current version: 1.0, status Draft, not yet published. Breaking
changes are still allowed before the 1.0 publication. The version
history lives in [docs/versions.md](docs/versions.md), and release
notes live in [CHANGELOG.md](CHANGELOG.md).

The format field carries the version, as "open-bookmarks/1.0"
(major.minor). Patch-level changes are spec wording clarifications
only and do not change the format value.

- Major version change: breaking. Removing or renaming a required
  field, or changing a node type in a way old readers cannot handle.
  Example, non-normative: "open-bookmarks/2.0".
- Minor version change: additive only. New optional fields, or new
  node types that old readers can safely ignore. Example,
  non-normative: "open-bookmarks/1.1".
- Patch: wording clarifications in the spec or docs only. The
  format value stays the same.

Reader compatibility rule, normative:

- A reader MUST accept the same major version it was built for.
- A reader MUST ignore unknown fields.
- A reader MUST warn, not fail, on a newer minor version, and still
  read the fields it knows.
- A reader MUST reject, or clearly warn and refuse to trust the
  pack, on a different major version, with a message that names the
  version found.

The validator follows the same rule: it accepts
"open-bookmarks/1.0", warns on a newer minor version such as
"open-bookmarks/1.1" and still checks the rest of the pack, and
rejects any other major version or a malformed format value.

This section is only about the format version. The version of a
single pack, set by its author, is a separate optional field,
defined in Section 12. Do not confuse the two.

## 12. Pack version and reader update guidance

This section is about the version of a pack, not the version of
the format. The two are different, and confusing them is the most
common mistake in this section.

- format is the version of the standard. In this draft it is
  exactly "open-bookmarks/1.0", as defined in Section 11. It
  tells a reader which rules the pack was written under.
- version is the version of this pack, set by the pack author.
  It tells a reader whether this copy of the pack may be newer
  than a copy it already has. It is optional, and it is not the
  format version.

### 12.1 Pack version field

Type: string. Required: no, on the pack only. There is no version
field on a folder or on a url node in version 1.0.

Rule, normative: version, if present, MUST be a non-empty string
after trimming surrounding whitespace. A number, an empty string,
a string that is only spaces, or a null value is invalid. A
version value of "open-bookmarks/1.0" is a mistake, not a pack
version: that string belongs in the format field, not here.

Example, non-normative:

```json
{
  "format": "open-bookmarks/1.0",
  "title": "News",
  "version": "1.2.0",
  "nodes": []
}
```

Semantic versioning is RECOMMENDED, not required. An author SHOULD
use major.minor.patch, for example "1.2.0", with major for a
breaking or large removal of links, minor for added links, and
patch for small fixes. That recommendation is not a validity rule:
a reader MUST accept a pack with a non-semantic version string,
for example "autumn-2026", as long as it is a non-empty string,
and MUST compare it as a string, not as a number or as a parsed
semantic version.

Version alone is not proof of change. Authors may forget to bump
it, bump it with no content change, or bump it in a way that does
not sort in the order a reader expects. A reader MUST NOT treat a
version difference as proof that links changed, and MUST NOT
treat equal versions as proof that links did not change. The
content comparison in Section 12.2 is the check that matters.

Note, informative: the schema and the validator both reject a
version that is only spaces, the schema by a pattern requiring a
non-space character and the validator by trimming. The prose
rule in this section governs if they ever disagree. No hash field is defined in this
draft. That choice is deliberate: a hash was discussed and parked,
not added, so readers MUST NOT expect a hash field in a 1.0 pack,
and writers MUST NOT invent one as part of this format.

### 12.2 Reader update guidance

This guidance is for any reader, not for a single app. Checking
for updates, showing an update option, and replacing a copy are
reader duties, not format duties. The format only defines the
fields a reader can compare.

A reader that imports a pack SHOULD store, alongside its local
copy, the source URL it imported from, the version it saw, the
updated date it saw, and the local copy of the content itself.
Those four stored values are what a later refresh compares
against. If the pack had no version and no updated date, the
reader stores that fact, and the content comparison below is
still available.

Refresh MUST always be an explicit user action. A reader MUST NOT
check for pack updates in the background, on app start, or just
because a pack was listed. That rule matches the remote folder
rule in Section 6.3, and it keeps a refresh from quietly telling
a pack host that a reader still holds that pack.

On a manual refresh, a reader SHOULD fetch the pack from its
stored source URL, then compare, in this order:

1. Version: does the fetched version differ from the stored
   version, as a plain string comparison?
2. Updated: does the fetched updated date differ from the stored
   updated date?
3. Content diff by URL: which links were added, removed, or
   changed? Added means a URL in the fetched pack that is not in
   the stored copy. Removed means a URL in the stored copy that
   is not in the fetched pack. Changed means the same URL is in
   both, but its title or folder path differs.

The reader SHOULD then show an update option to the user, and
MUST NOT replace the local copy without that user action. The
cases are:

- Version differs, or updated differs, or the diff is not empty:
  show an update option, with the version change if there is
  one, and a short summary of the diff, for example how many
  links were added, changed, and removed.
- Version is the same but the diff is not empty: still show the
  update option. The author may have forgotten to bump the
  version, and the diff is the stronger signal.
- Version differs but the diff is empty: say there is no
  meaningful content change, and let the user keep the local
  copy. Do not present it as a new set of links.
- Version and updated are both missing: the diff alone is the
  update signal. If the diff is empty, there is no update to
  offer.

A reader SHOULD NOT try to merge a fetched pack into a local
copy the user has edited, unless it can show the user exactly
what would be kept and what would be lost. For a first version
of this guidance, imported packs are treated as read-only
collections: updating means replacing the whole snapshot, after
the user accepts, not silently merging edits. A user who wants
their own edited copy SHOULD save it as a new pack of their own,
with its own title and version, rather than editing an imported
pack in place and then expecting a clean update.

## 13. Relation to other formats, informative

This section is informative. It does not add a rule.

Netscape Bookmark HTML is the long-standing cross-browser export
format: an HTML file with a NETSCAPE-Bookmark-file-1 doctype,
nested lists for folders, and links for bookmarks. Open-bookmarks
borrows its folder and link idea and its plain, portable spirit,
but it does not copy its syntax. Netscape HTML is HTML, not JSON,
and it has no place for remote folders or custom-properties.

Chrome Bookmarks JSON stores bookmarks as a JSON tree with roots,
folders with children, and url nodes with a name and a url. Firefox
JSON backups store a similar tree in Firefox's own form. XBEL is an
XML format for sharing bookmarks, with folders and bookmarks in XML.
Open-bookmarks borrows the tree idea from all of them, and the JSON
encoding most closely from Chrome, but it defines its own field
names, its own format version field, its own remote folder rule,
and its own custom-properties rule. A Chrome, Firefox, or XBEL file
is therefore not an open-bookmarks pack, and an open-bookmarks pack
is not a Chrome, Firefox, or XBEL file. The converters in tools/
exist to translate between them.
