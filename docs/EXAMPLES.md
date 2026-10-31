# Example packs

All plain packs below are in [packs/examples/](https://github.com/svenkatreddy/open-bookmarks/tree/main/packs/examples).
Every plain pack passes `python3 tools/validate.py <file>`. Each snippet
below is a short excerpt, not the whole file. Open the linked file
for the full pack. The encrypted template at the end of this page
is not a plain pack, and it does not pass that validator, by design.

## News

File: [packs/examples/news.json](https://raw.githubusercontent.com/svenkatreddy/open-bookmarks/main/packs/examples/news.json)

What it shows: a normal pack with an inline folder and a remote
folder. World news is inline. Tech News points at a second pack
file, so the first file stays small. It also carries pack
version "1.2.0", the author's version of this pack, distinct
from the format version "open-bookmarks/1.0". BBC News also
carries a standard icon, an https ICO favicon, alongside its
custom-properties icon name "globe", to show that the two fields
are different and can appear together.

Snippet:

```json
{
  "format": "open-bookmarks/1.0",
  "title": "News",
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
      "source": "https://raw.githubusercontent.com/svenkatreddy/open-bookmarks/main/packs/examples/tech.json"
    }
  ]
}
```

## Movies

File: [packs/examples/movies.json](https://raw.githubusercontent.com/svenkatreddy/open-bookmarks/main/packs/examples/movies.json)

What it shows: two folders, Reviews and Listings, and a bookmark
with custom-properties for an icon, an accent, and a client version
tag. The standard does not interpret those keys. The pack also
carries pack version "1.1.0".

Snippet:

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

## Tech

File: [packs/examples/tech.json](https://raw.githubusercontent.com/svenkatreddy/open-bookmarks/main/packs/examples/tech.json)

What it shows: the remote half of the News pack. It is a plain pack
with two links and no folders. A reader fetches it only when someone
opens the Tech News folder in News.

Snippet:

```json
{
  "format": "open-bookmarks/1.0",
  "title": "Tech News",
  "nodes": [
    { "type": "url", "title": "Hacker News", "url": "https://news.ycombinator.com/" },
    { "type": "url", "title": "The Verge", "url": "https://www.theverge.com/" }
  ]
}
```

## Simple

File: [packs/examples/simple.json](https://raw.githubusercontent.com/svenkatreddy/open-bookmarks/main/packs/examples/simple.json)

What it shows: the smallest useful pack. One folder, two links,
and pack version "1.0.0". Copy this file when you write your
first pack by hand, then change the title and the links. The
Nested, Remote, and Custom properties packs below carry no
version field, to show that it is optional.

Snippet:

```json
{
  "format": "open-bookmarks/1.0",
  "title": "Simple",
  "nodes": [
    {
      "type": "folder",
      "title": "Reading",
      "nodes": [
        { "type": "url", "title": "BBC News", "url": "https://www.bbc.com/news" },
        { "type": "url", "title": "Reuters", "url": "https://www.reuters.com/" }
      ]
    }
  ]
}
```

## Nested

File: [packs/examples/nested.json](https://raw.githubusercontent.com/svenkatreddy/open-bookmarks/main/packs/examples/nested.json)

What it shows: folders nested four levels deep. Collections holds
Topics, which holds Technology, which holds Programming, which holds
a Python link. It also shows that a link can sit at a higher level
in the same tree, next to a nested folder.

Snippet:

```json
{
  "type": "folder",
  "title": "Collections",
  "nodes": [
    {
      "type": "folder",
      "title": "Topics",
      "nodes": [
        {
          "type": "folder",
          "title": "Technology",
          "nodes": [
            {
              "type": "folder",
              "title": "Programming",
              "nodes": [
                { "type": "url", "title": "Python", "url": "https://www.python.org/" }
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

The depth limit is 4 levels, so four levels is valid. See
[SYNTAX.md](SYNTAX.md) for how depth is counted.

## Depth

Valid at exactly 4 levels: [packs/examples/nested.json](https://raw.githubusercontent.com/svenkatreddy/open-bookmarks/main/packs/examples/nested.json).
Collections is level 1, Topics is level 2, Technology is level 3,
and Programming is level 4. The Python link sits inside the level
4 folder, and that is allowed, because a link is not a folder level.

Invalid at 5 levels: a pack that adds one more folder inside
Programming, for example a folder called Level5 holding a link.
That pack is not in packs/examples, because every file there must
pass validation. It is kept as a test fixture instead, at
[../tools/tests/fixtures/invalid-depth.json](../tools/tests/fixtures/invalid-depth.json).

Run the validator on that fixture, from the repo root:

```sh
python3 tools/validate.py tools/tests/fixtures/invalid-depth.json
```

It fails with exit code 1 and this error:

```
error: nodes[0][0][0][0][0]: folder at level 5 exceeds max depth 4
```

The count is folder levels below the pack root, not links. A
folder at level 5 is invalid even if it contains no links.

## Remote

File: [packs/examples/remote.json](https://raw.githubusercontent.com/svenkatreddy/open-bookmarks/main/packs/examples/remote.json)

What it shows: a pack that uses a remote folder on purpose, with
both a local folder and a remote folder side by side. The remote
URL in this example is an example only. Replace it with the URL of
a real pack before importing, and fetch it only when you open the
folder.

Snippet:

```json
{
  "type": "folder",
  "title": "Remote links",
  "source": "https://example.com/remote-pack.json"
}
```

The full file also says, in its description, that the remote URL
is an example only, so the warning survives even if only the file
itself is shared.

## Custom properties

File: [packs/examples/custom-properties.json](https://raw.githubusercontent.com/svenkatreddy/open-bookmarks/main/packs/examples/custom-properties.json)

What it shows: custom-properties at three levels. The pack itself
carries a pack icon and a client tag. A folder carries an accent.
Two bookmarks carry an icon, an accent, and a client version tag.
All client names in this file are generic examples only.

Snippet:

```json
{
  "type": "url",
  "title": "BBC News",
  "url": "https://www.bbc.com/news",
  "custom-properties": {
    "icon": "globe",
    "accent": "#1f6feb",
    "client-version": "example-client-1"
  }
}
```

The standard does not interpret any key inside
custom-properties. A reader that does not know a key must ignore
that key and keep the rest. See [SYNTAX.md](SYNTAX.md) for the
full rules.

## Icons

File: [packs/examples/icon.json](https://raw.githubusercontent.com/svenkatreddy/open-bookmarks/main/packs/examples/icon.json)

What it shows: the standard icon field at all three levels, all
optional. The pack itself has an https PNG icon. The News folder
has an https SVG icon. Inside the folder, BBC News has an https
ICO icon with two sizes, Example Site has a PNG data URI icon,
and Reuters has an SVG data URI icon with sizes "any". Type and
sizes are optional inside icon, and a pack or node with no icon
is still valid.

Snippet:

```json
{
  "type": "url",
  "title": "BBC News",
  "url": "https://www.bbc.com/news",
  "icon": {
    "src": "https://example.com/favicon.ico",
    "type": "image/x-icon",
    "sizes": "16x16 32x32"
  }
}
```

See [SYNTAX.md](SYNTAX.md) for the full icon rules, including
the invalid cases: a string icon, a missing src, an http src, a
javascript: src, a bad type, and a bad sizes value.

## Encrypted template

File: [packs/examples/encrypted-template.json](https://raw.githubusercontent.com/svenkatreddy/open-bookmarks/main/packs/examples/encrypted-template.json)

What it shows: the shape of an encrypted pack envelope, and
nothing else. It is not a plain pack, it has no title or nodes,
and it must not be used as a pack. Its salt, IV, and ciphertext
are placeholder hex values, not a real encryption, so decrypting
it will fail, on purpose, and the plain pack validator will
reject it with a single clear message: decrypt it first.

Snippet, the whole file, because it is only an envelope:

```json
{
  "cipher": "AES-256-GCM",
  "ciphertext": "0000000000000000000000000000000000000000000000000000000000000000",
  "format": "open-bookmarks/encrypted/1.0",
  "iterations": 600000,
  "iv": "000000000000000000000000",
  "kdf": "PBKDF2-HMAC-SHA-256",
  "salt": "00000000000000000000000000000000"
}
```

The envelope structure is defined in
[../schema/open-bookmarks-encrypted.schema.json](../schema/open-bookmarks-encrypted.schema.json).
That schema checks structure only, so this placeholder template
passes the schema and still fails to decrypt, which is expected.
To make a real encrypted pack, use the browser tool in
[ENCRYPT-TOOL.md](ENCRYPT-TOOL.md), the JavaScript or
TypeScript `encryptPack` function, or the Python tool in
`tools/encrypt.py`, as described in [ENCRYPTION.md](ENCRYPTION.md).

## How to check an example

Run the validator on any plain file above, from the repo root:

```sh
python3 tools/validate.py packs/examples/simple.json
```

A valid pack prints "valid:" followed by the file name. A pack
that fails prints each error on its own line and exits with a
non-zero code. Do not run that validator on
`packs/examples/encrypted-template.json` expecting a valid pack.
It will print that it is an encrypted pack, not a plain pack,
and exit with a non-zero code, which is the correct result.
