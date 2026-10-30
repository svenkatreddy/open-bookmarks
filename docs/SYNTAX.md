# open-bookmarks syntax

Status: 1.0 Draft, not yet published. This document describes the
syntax of version 1.0. The full specification is
[../SPEC.md](../SPEC.md). If this document and the specification
disagree, the specification governs, and the disagreement should be
reported as a bug in this document.

## Conformance

The key words MUST, MUST NOT, REQUIRED, SHALL, SHALL NOT, SHOULD,
SHOULD NOT, RECOMMENDED, MAY, and OPTIONAL in this document are to
be interpreted as described in RFC 2119 [RFC2119] and clarified in
RFC 8174 [RFC8174] when, and only when, they appear in all capitals.
Words in lower case have no special meaning in this document.

Normative statements in this document use those capital keywords.
Examples and notes marked as informative, and every code example
labelled as non-normative, do not create rules. If an example and a
normative rule disagree, the normative rule governs.

The normative machine-readable definition is the JSON Schema in
[../schema/open-bookmarks.schema.json](../schema/open-bookmarks.schema.json),
using JSON Schema draft 2020-12. The prose in [../SPEC.md](../SPEC.md)
is the normative human-readable definition. The two are intended to
agree. One known difference in strength is stated where it
matters: the schema and the validator check the shape of
updated with a pattern, while the prose requires a real ISO 8601
date or date-time, so a shape-valid but impossible date like
2026-02-30 would pass the tools and still fail the prose rule.
In that case the prose rule governs.

## Terminology

A pack is a single JSON object that holds a collection of bookmarks
in folders. A node is one entry in a pack. A folder is a node that
holds other nodes. A url node is a node that holds a single link.
A remote folder is a folder that has a source field pointing at
another pack file. A snapshot is a copy of a pack made at import
time. A reader is software that reads a pack. A writer is software
that creates or converts a pack. A conformant pack, reader, or
writer is one that satisfies the conformance class for that role
in [../SPEC.md](../SPEC.md), Section 4.

## Normative references

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
- [JSONSCHEMA] JSON Schema, draft 2020-12, for the schema file.

## The smallest valid pack

A pack is a JSON object, as defined by [RFC8259]. JSON objects use
curly braces, string keys in double quotes, and values that are
strings, numbers, booleans, null, arrays, or objects. Open-bookmarks
uses only strings, arrays, and objects in its own fields, plus any
JSON value inside custom-properties.

Example, non-normative. This is the smallest pack that is valid:

```json
{
  "format": "open-bookmarks/1.0",
  "title": "My links",
  "nodes": []
}
```

It has exactly the three required pack fields: format, title, and
nodes. Everything else in this document adds optional fields or
nodes inside that list.

Example, non-normative. A pack with one folder and two links:

```json
{
  "format": "open-bookmarks/1.0",
  "title": "My links",
  "nodes": [
    {
      "type": "folder",
      "title": "News",
      "nodes": [
        {
          "type": "url",
          "title": "BBC News",
          "url": "https://www.bbc.com/news"
        },
        {
          "type": "url",
          "title": "Reuters",
          "url": "https://www.reuters.com/"
        }
      ]
    }
  ]
}
```

## Pack fields

Table 1 lists every pack field. No other pack field is required.
Readers MUST ignore unknown pack fields.

Table 1. Pack fields. Normative.

| Field | Required | Type |
| --- | --- | --- |
| format | Yes | String |
| title | Yes | String |
| author | No | String, the person or group that made this pack |
| description | No | String |
| source | No | String, https URL |
| updated | No | String, ISO 8601 date or date-time |
| version | No | String, the author's version of this pack |
| nodes | Yes | List of nodes |
| icon | No | Object, an image for the pack, see the icon section |
| custom-properties | No | JSON object |

### format

Type: string. Required: yes.

Rule: format MUST be exactly "open-bookmarks/1.0". The value
carries the version: major version 1, minor version 0.

Valid example, non-normative:

```json
"format": "open-bookmarks/1.0"
```

Invalid example, non-normative, and why it fails:

```json
"format": "1.0"
```

This fails because the value is not the exact string
"open-bookmarks/1.0". A missing format field also fails, for the
same reason: a reader cannot tell which version the pack claims.

Version note, normative: a reader MUST warn, not fail, on a newer
minor version such as "open-bookmarks/1.1" and still read the fields
it knows. A reader MUST reject, or clearly warn and refuse to trust
the pack, on a different major version, naming the version found.
The schema for 1.0 states format as a constant, so a 1.1 pack fails
the schema alone but passes the validator with a warning. That
difference is intentional and is documented in the specification.

### title

Type: string. Required: yes.

Rule: title MUST be non-empty after trimming surrounding
whitespace. It is the human-readable name shown for the pack, for
example "News".

Valid example, non-normative:

```json
"title": "News"
```

Invalid examples, non-normative, and why they fail:

```json
"title": ""
```

This fails because the string is empty.

```json
"title": "   "
```

This fails because the string is empty after trimming whitespace.
It passes a plain length check, but it fails the specification
rule and the validator, and the specification rule governs.

### author

Type: string. Required: no, on the pack only.

Rule: author, if present, MUST be a non-empty string after
trimming surrounding whitespace. It names the person or group
that made the pack, the curator, not the author of any linked
page. A reader SHOULD show it with the pack title, when it is
present. Nodes do not inherit it, and there is no author field
on a folder or on a url node in version 1.0.

Valid example, non-normative:

```json
"author": "FMHY"
```

Invalid example, non-normative, and why it fails:

```json
"author": "   "
```

This fails because author is only spaces, so after trimming
there is nothing left to show.

### description

Type: string. Required: no.

Rule: description, if present, MUST be a string. It SHOULD be one
or two sentences about what the pack is for. A reader MAY show it,
and MAY ignore it.

Valid example, non-normative:

```json
"description": "A few news sites I check most mornings."
```

Invalid example, non-normative, and why it fails:

```json
"description": 42
```

This fails because description is not a string.

### source

Type: string. Required: no.

Rule: source, if present, MUST be an https URL, as defined in the
URL rules below. It is the URL the pack was published at, if known.
It is not the same as a folder source field, although the URL rule
is the same: https only.

Valid example, non-normative:

```json
"source": "https://example.com/news.json"
```

Invalid example, non-normative, and why it fails:

```json
"source": "http://example.com/news.json"
```

This fails for a pack source because a pack source MUST be https,
even though http is allowed for a bookmark link itself. The two
fields have different rules, and this is the most common mistake
in this field.

### updated

Type: string. Required: no.

Rule: updated, if present, MUST be a string in ISO 8601 [ISO8601]
date or date-time form. A plain calendar date is enough for most
packs. A date-time MAY include a time and a time zone designator.

Valid examples, non-normative:

```json
"updated": "2026-10-27"
```

```json
"updated": "2026-10-27T15:00:00Z"
```

Invalid example, non-normative, and why it fails:

```json
"updated": "27 October 2026"
```

This fails because it is not an ISO 8601 date, even though a human
can read it. The schema and the validator both reject it, by
pattern, as well as the prose rule.

### version

Type: string. Required: no, on the pack only.

Rule: version, if present, MUST be a non-empty string after
trimming surrounding whitespace. It is the author's version of
this pack, and it is not the format version. The format field
carries the version of the standard, as "open-bookmarks/1.0".
The version field carries the version of this pack, for example
"1.2.0". Readers compare version as a plain string, and treat
any difference as a possible update, not as proof of change.

Semantic versioning is RECOMMENDED, not required. An author
SHOULD use major.minor.patch, with major for a breaking or large
removal of links, minor for added links, and patch for small
fixes. A non-semantic version string is still valid, as long as
it is a non-empty string. Authors SHOULD bump version when the
links change, but readers MUST NOT rely on version alone, because
an author may forget to bump it. The content comparison in the
reader update guidance below is the stronger signal.

Valid examples, non-normative:

```json
"version": "1.2.0"
```

```json
"version": "autumn-2026"
```

The second example is valid even though it is not semantic
versioning, because the rule for this field is a non-empty
string, not a semantic version.

Invalid examples, non-normative, and why they fail:

```json
"version": 12
```

This fails because version is a number, not a string. A reader
comparing versions as strings cannot compare a number here
without inventing a conversion.

```json
"version": ""
```

This fails because the string is empty.

```json
"version": "   "
```

This fails because the string is empty after trimming
whitespace. It passes a plain length check, but it fails the
specification rule and the validator, and the specification rule
governs.

Confused example, non-normative, and why it is a mistake:

```json
"version": "open-bookmarks/1.0"
```

This is the format version, not a pack version. It belongs in
the format field, not here. A pack version should look like
"1.2.0", or another string the author uses for this pack. The
validator checks only that version is a non-empty string, so it
does not catch this confusion on its own. Authors SHOULD check
by hand that they have not put the format string in the version
field.

### icon

Type: object. Required: no, on a pack, on a folder, and on a url
node. The rules are the same in all three places. A pack or node
with no icon is valid.

Rule: icon, if present, MUST be an object. Inside icon, src is
required, type and sizes are optional. src MUST be an https URL
with a host, or a data URI for an image. type, if present, MUST
be one of image/png, image/svg+xml, image/x-icon, image/webp,
image/gif, or image/jpeg. sizes, if present, MUST be "any", or
one or more sizes like "32x32" separated by single spaces, for
example "16x16 32x32".

This icon field is distinct from custom-properties. A
custom-properties key called "icon" is a client-defined name,
for example "globe". It is a string, and the standard does not
interpret it. The icon field here is a standard object that
points at an image. The two MAY appear together, and neither
replaces the other.

Readers MUST support PNG and SVG, SHOULD support ICO and WebP,
and MAY support GIF and JPEG. Writers SHOULD use PNG or SVG,
SHOULD NOT use JPEG, because JPEG has no transparency, and
SHOULD NOT use animated GIFs. Data URIs SHOULD stay small,
about 64 KB or less, because they bloat the pack file, and
writers SHOULD prefer an https URL for a shared pack.

Privacy guidance, informative: a reader SHOULD NOT fetch an
icon URL on import. It SHOULD fetch an icon only when the icon
is about to be shown, and SHOULD prefer a site favicon derived
from the bookmark URL itself over a third-party icon host where
possible. A data URI icon needs no fetch at all.

Valid examples, non-normative, an https PNG icon:

```json
"icon": {
  "src": "https://example.com/icons/news.png",
  "type": "image/png",
  "sizes": "32x32"
}
```

Valid example, non-normative, an SVG data URI icon:

```json
"icon": {
  "src": "data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20viewBox='0%200%2016%2016'%3E%3Ccircle%20cx='8'%20cy='8'%20r='8'%20fill='%231f6feb'/%3E%3C/svg%3E",
  "type": "image/svg+xml",
  "sizes": "any"
}
```

Valid example, non-normative, an ICO icon with two sizes:

```json
"icon": {
  "src": "https://example.com/favicon.ico",
  "type": "image/x-icon",
  "sizes": "16x16 32x32"
}
```

Invalid examples, non-normative, and why they fail:

```json
"icon": "globe"
```

This fails because icon MUST be an object, not a string. The
string "globe" is valid inside custom-properties, not here.

```json
"icon": { "type": "image/png", "sizes": "32x32" }
```

This fails because src is missing. src is required when icon
is present.

```json
"icon": { "src": "http://example.com/icon.png" }
```

This fails because an icon src MUST be https, not http.

```json
"icon": { "src": "javascript:alert(1)" }
```

This fails because javascript: is not an https URL or an image
data URI.

```json
"icon": { "src": "https://example.com/icon.png", "type": "image/bmp" }
```

This fails because image/bmp is not in the allowed type list.

```json
"icon": { "src": "https://example.com/icon.png", "sizes": "large" }
```

This fails because sizes MUST be "any" or sizes like "32x32",
not a word like "large".

```json
"icon": { "src": "data:text/plain,hello" }
```

This fails because the data URI is not an image data URI.

### nodes

Type: list of nodes. Required: yes.

Rule: nodes MUST be a list. It MAY be empty. Each entry in the list
MUST be a node, as defined in the node fields section below. A
missing nodes field fails. A nodes field that is not a list, for
example a single object, fails.

Valid example, non-normative:

```json
"nodes": []
```

Invalid example, non-normative, and why it fails:

```json
"nodes": { "type": "url", "title": "BBC News", "url": "https://www.bbc.com/news" }
```

This fails because nodes is an object, not a list. The single
bookmark must be inside a list, even if it is the only one.

### custom-properties at pack level

Type: JSON object. Required: no.

Rule: custom-properties, if present on a pack, MUST be a JSON
object. The rules for its contents are the same as for a bookmark
in the custom-properties section below. The standard does not
interpret any key inside it.

Valid example, non-normative:

```json
"custom-properties": { "icon": "newspaper" }
```

Invalid example, non-normative, and why it fails:

```json
"custom-properties": "newspaper"
```

This fails because the value is a string, not an object.

## Node fields

Every node is a JSON object. The type field decides which other
fields are required.

Table 2. Node fields by type. Normative.

| Field | url node | Folder node |
| --- | --- | --- |
| type | Required, "url" | Required, "folder" |
| title | Required, non-empty string | Required, non-empty string |
| url | Required, http or https URL | Must not be used as the link field for a folder |
| nodes | Not used | Optional, list of nodes, defaults to empty |
| source | Not used | Optional, https URL for a remote folder |
| icon | Optional, object, see the icon section | Optional, object, see the icon section |
| custom-properties | Optional, JSON object | Optional, JSON object |

There is no separate "remote" node type in version 1.0. A remote
folder is a folder node with a source field. If a writer uses
"type": "remote", the pack is invalid, because the type is unknown.

### type

Type: string. Required: yes, on every node.

Rule: type MUST be exactly "folder" or "url". Any other value,
including "link", "bookmark", or "remote", MUST be rejected by a
validator.

Valid examples, non-normative: "folder", "url".

Invalid example, non-normative, and why it fails:

```json
{ "type": "link", "title": "BBC News", "url": "https://www.bbc.com/news" }
```

This fails because "link" is not a known node type, even though
the rest of the node looks like a bookmark.

### title on a node

Type: string. Required: yes, on every node.

Rule: title MUST be non-empty after trimming surrounding
whitespace, with the same rule as pack title. For a url node it
is the link text to show. For a folder node it is the folder name
to show.

Valid example, non-normative:

```json
"title": "BBC News"
```

Invalid example, non-normative, and why it fails:

```json
"title": ""
```

This fails because the title is empty. A node without a usable
title cannot be shown in a list.

### url

Type: string. Required: yes, on a url node only.

Rule: url MUST be an http or https URL, as defined in the URL
rules below. A url node without a url field fails. A url field on
a folder node is not a link and MUST NOT be treated as one; a
folder shows its children, not a url field.

Valid example, non-normative:

```json
"url": "https://www.bbc.com/news"
```

Invalid examples, non-normative, and why they fail:

```json
"url": "javascript:alert(1)"
```

This fails because only http and https are allowed.

```json
"url": "www.bbc.com/news"
```

This fails because the URL has no scheme. The scheme must be
written out, as "https://www.bbc.com/news".

```json
"url": "https://www.bbc.com/news page"
```

This fails because the URL contains a space.

### nodes on a folder

Type: list of nodes. Required: no, on a folder node only.

Rule: nodes, if present on a folder, MUST be a list. If absent,
it defaults to an empty list, so a folder with only a source field
is valid. Each entry in the list MUST be a node.

Valid example, non-normative:

```json
"nodes": [
  { "type": "url", "title": "BBC News", "url": "https://www.bbc.com/news" }
]
```

Invalid example, non-normative, and why it fails:

```json
"nodes": "https://www.bbc.com/news"
```

This fails because nodes is a string, not a list of nodes.

### source on a folder

Type: string. Required: no, on a folder node only.

Rule: source, if present, MUST be an https URL, as defined in the
URL rules below. A folder MAY have nodes, a source, or both. If it
has both, readers SHOULD show the inline nodes first, then expand
the remote source when the folder is opened.

When a reader expands a remote folder, it MUST fetch the pack at
source, take that pack's top-level nodes, and show them as the
children of this folder. The remote pack's own title MUST NOT be
used as a folder name; the local folder title stays.

A reader MUST only fetch a remote source when the user opens that
folder, or when the user asks to import or refresh the whole pack.
A reader MUST NOT fetch remote sources in the background, on app
start, or just because a pack was listed.

Valid example, non-normative:

```json
{
  "type": "folder",
  "title": "Tech News",
  "source": "https://example.com/tech-news.json"
}
```

Invalid example, non-normative, and why it fails:

```json
{
  "type": "folder",
  "title": "Tech News",
  "source": "http://example.com/tech-news.json"
}
```

This fails because a remote source MUST be https, not http.

### custom-properties on a node

Type: JSON object. Required: no.

Rule: custom-properties, if present on a node, MUST be a JSON
object. Keys inside it are client-defined, and values MAY be any
JSON value. The standard does not interpret, validate, or require
any key inside it.

Valid example, non-normative:

```json
"custom-properties": {
  "icon": "globe",
  "accent": "#1f6feb",
  "client-version": "example-client-1"
}
```

In that example, "icon" and "accent" are UI hints for a client,
and "client-version" is a version tag for that client's own use.
Another client MAY use completely different keys, for example an
analytics ID, and the pack is still valid.

Invalid examples, non-normative, and why they fail:

```json
"custom-properties": ["globe"]
```

This fails because the value is an array, not an object.

```json
"custom-properties": null
```

This fails because null is not an object for this field. Omitting
the field entirely is valid; setting it to null is not.

Readers MUST preserve custom-properties when loading a pack, and
MUST include it in flattened output for a bookmark that has it.
Readers MUST ignore keys inside it they do not know, and MUST NOT
reject a pack only because of a key inside it. Converters from old
formats that have no equivalent field omit it, which is not an
error. Exporting to Netscape HTML drops it, because Netscape HTML
has no place to put it, and writers MUST NOT invent a Netscape
encoding for it.

### icon on a node

Type: object. Required: no, on a folder node and on a url node.

Rule: the same as the icon section under Pack fields above.
icon, if present, MUST be an object with a required src that is
an https URL or an image data URI, an optional type from the
fixed list, and optional sizes. A string icon, a missing src, an
http src, a javascript: src, a bad type, and a bad sizes value
all fail, for the reasons given in that section. Readers MUST
include icon in flattened output for a bookmark that has it,
just as they include custom-properties.

## URL rules

URLs are URIs as defined by [RFC3986], with the scheme
restrictions added by open-bookmarks in this section. Those
restrictions are normative.

- A url field MUST use http or https.
- A source field, on a pack or on a folder, MUST use https.
- javascript:, data:, file:, and any other scheme MUST be
  rejected.
- A URL with no scheme, or with spaces, MUST be rejected.
- Readers SHOULD keep a URL exactly as written, apart from
  trimming surrounding whitespace. Readers SHOULD NOT add tracking
  parameters.
- The scheme check is case-insensitive for accepting http, https,
  and HTTPS spellings. The stored URL is otherwise kept as written.

Converters MUST apply the same rules: skip a bad URL, warn about
it, and keep converting the rest. A single bad link MUST NOT break
a whole import.

## Date rules

The updated field, if present, MUST be a string in ISO 8601
[ISO8601] date or date-time form. A plain date such as
"2026-10-27" is valid. A date-time such as "2026-10-27T15:00:00Z"
is valid. A human-readable date such as "27 October 2026" is not
valid under this rule. The schema and the validator both reject
it by pattern, as well as the prose rule. The pattern checks
shape, not the full calendar, so an impossible date like
2026-02-30 would still pass the tools and fail the prose rule.

## Reader update guidance

This section is guidance for any reader, not for a single app.
Checking for updates, showing an update option, and replacing a
local copy are reader duties. The format only defines the fields
a reader can compare: version, updated, and the links themselves.
The full normative rules are in [../SPEC.md](../SPEC.md),
Section 12. This section restates them in short form.

A reader that imports a pack SHOULD store, alongside its local
copy, the source URL it imported from, the version it saw, the
updated date it saw, and the local copy of the content itself.
If the pack had no version and no updated date, the reader stores
that fact, and the content comparison below is still available.

Refresh MUST always be an explicit user action. A reader MUST NOT
check for pack updates in the background, on app start, or just
because a pack was listed.

On a manual refresh, a reader SHOULD fetch the pack from its
stored source URL, then compare version as a plain string,
updated as a plain string, and the links by URL. Added means a
URL in the fetched pack that is not in the stored copy. Removed
means a URL in the stored copy that is not in the fetched pack.
Changed means the same URL is in both, but its title or folder
path differs.

Then, normative in short form:

- Version differs, or updated differs, or the diff is not empty:
  show an update option, with the version change if there is
  one, and a short summary of the diff.
- Version is the same but the diff is not empty: still show the
  update option. The author may have forgotten to bump version.
- Version differs but the diff is empty: say there is no
  meaningful content change, and let the user keep the local copy.
- Version and updated are both missing: the diff alone is the
  update signal. If the diff is empty, there is no update to offer.

A reader MUST NOT replace the local copy without a user action.
Imported packs are treated as read-only collections for this
guidance: updating means replacing the whole snapshot, after the
user accepts, not silently merging edits. A user who wants their
own edited copy SHOULD save it as a new pack of their own, with
its own title and version.

No hash field is defined in this draft. That choice is
deliberate: a hash was discussed and parked, not added, so this
guidance uses version, updated, and content diff only.

## Nesting, depth, and limits

Folders MAY nest inside folders. The depth limit is normative.
Depth is counted by folder levels below the pack root. A folder
directly in the pack nodes list is at level 1. A folder inside a
level 1 folder is at level 2, and so on. A pack MAY contain folders
nested up to 4 levels deep. A url MAY sit inside a folder at level
4. A folder at level 5 MUST NOT be present, and a pack with a
folder at level 5 is invalid. Such a folder MUST be rejected by
the validator and SHOULD be skipped by a reader.

Two limits are recommendations, not pack validity rules, and the
validator does not enforce them:

- Readers SHOULD refuse or truncate a pack with more than 10,000
  nodes in total after expansion, and MUST NOT hang or run out of
  memory on a large pack.
- A single pack file SHOULD be no larger than 1 MB. Larger files
  SHOULD be rejected with a clear message, not loaded and then
  failed halfway.

Dedupe is an import and flattening rule, not a validity rule.
When importing, readers and converters SHOULD dedupe by URL,
keeping the first occurrence. A pack that repeats a URL in two
folders is not invalid on that ground alone; after import it SHOULD
appear once, in the first folder where it was found.

Cycle protection is normative for readers. A reader MUST keep a set
of source URLs already visited while expanding one tree, and MUST
stop expanding a source that has been seen before. Expanding MUST
also stop at the depth limit, even if no cycle is found.

## Writing a pack, step by step

Informative. This section is a checklist, not a new rule.

1. Start with format, title, and an empty nodes list.
2. Add a folder for each group, with a short title.
3. Inside each folder, add url nodes with a title and an http or
   https url.
4. Add description, source, updated, version, and icon only
   if you have them, using the forms in the field sections
   above. Remember that icon is optional everywhere, and that
   it is an object, not a string.
   Remember that version is the version of this pack, not the
   format version, which already lives in the format field.
5. Add custom-properties only as an object, and only for client
   use. Do not put a link, a password, or a secret in it.
6. Run the validator before sharing the pack:
   `python3 tools/validate.py my-pack.json`
7. Check that the validator prints "valid:" and no errors. Fix
   the first error it names, then run it again.

## Relation to other formats

Informative. This section does not add a rule.

Netscape Bookmark HTML is the long-standing cross-browser export
format: an HTML file with a NETSCAPE-Bookmark-file-1 doctype,
nested lists for folders, and links for bookmarks. Open-bookmarks
borrows its folder and link idea and its plain, portable spirit,
but it does not copy its syntax. Netscape HTML is HTML, not JSON,
and it has no place for remote folders or custom-properties.

Chrome Bookmarks JSON stores bookmarks as a JSON tree with roots,
folders with children, and url nodes with a name and a url.
Firefox JSON backups store a similar tree in Firefox's own form.
XBEL is an XML format for sharing bookmarks, with folders and
bookmarks in XML. Open-bookmarks borrows the tree idea from all of
them, and the JSON encoding most closely from Chrome, but it
defines its own field names, its own format version field, its own
remote folder rule, and its own custom-properties rule.

What is borrowed: a tree of folders and links, titles for folders
and links, and the idea that a pack is a portable file, not an
account. What is new: the format field with a version, the remote
folder rule with lazy fetching and snapshot import, the
custom-properties object that the standard deliberately does not
interpret, and the explicit http and https only rule with https
only for remote sources. A Chrome, Firefox, or XBEL file is
therefore not an open-bookmarks pack, and an open-bookmarks pack
is not a Chrome, Firefox, or XBEL file. The converters in tools/
exist to translate between them.

## Common mistakes

Informative. Each item below fails for the reason given, and the
field section above states the rule.

- Missing format, or format written as "1.0" instead of
  "open-bookmarks/1.0".
- nodes written as a single object instead of a list.
- A node type written as "link", "bookmark", or "remote" instead
  of "folder" or "url".
- A bookmark url written without a scheme, or with a javascript:
  scheme.
- A remote source written with http instead of https.
- custom-properties written as a string or an array instead of an
  object, or set to null instead of omitted.
- updated written as "27 October 2026" instead of an ISO 8601 date.
- A title that is only spaces, which passes a plain length check
  but fails the trimming rule.
- version written as a number, as an empty string, or as
  "open-bookmarks/1.0", which is the format version, not a pack
  version.
- icon written as a string instead of an object, or with a
  missing src, an http src, or a type outside the allowed list.
- A custom-properties icon string mistaken for a standard icon
  image. The two are different fields, as explained in the icon
  section.

## See also

- [../SPEC.md](../SPEC.md): the full specification, and the source
  of truth if this document and the specification disagree.
- [../schema/open-bookmarks.schema.json](../schema/open-bookmarks.schema.json):
  the machine-readable definition, JSON Schema draft 2020-12.
- [EXAMPLES.md](EXAMPLES.md): every example pack, what it shows,
  and a short snippet of each.
- [versions.md](versions.md): the version history.
- [../README.md](../README.md): a short introduction and the
  converter commands.
