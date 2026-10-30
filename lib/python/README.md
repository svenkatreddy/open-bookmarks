# open-bookmarks, Python library

No dependencies. Python 3 only, standard library only.

## Import it

The library is a single file, `open_bookmarks.py`. That is
deliberate, so you can use it without a package install.

Option 1, copy the file. Copy `open_bookmarks.py` into your
project, then:

```python
from open_bookmarks import load_pack, validate_pack, flatten_urls
```

Option 2, use it from this repo. Add `lib/python` to the Python
path, for example:

```sh
PYTHONPATH=lib/python python3 your-script.py
```

Or, in code:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path("lib/python").resolve()))
from open_bookmarks import load_pack
```

Option 3, package install, not yet published. A package file is
prepared in `pyproject.toml` in this folder, with package version
0.1.0, because the format itself is still 1.0 Draft and
unpublished. Do not try `pip install open-bookmarks` until a
release is announced. See `PUBLISHING.md` in this folder for the
manual publish steps that are still needed. After publication, the
import name stays `open_bookmarks`, as in Option 1.

## Load a pack from a string or a file

`load_pack` accepts a dict, a JSON string, bytes, or a file object,
and returns a pack dict. It does not validate. Always validate
after loading, as shown below.

From a file:

```python
import json
from open_bookmarks import load_pack, validate_pack, flatten_urls

with open("packs/examples/news.json", encoding="utf-8") as handle:
    pack = load_pack(handle)
```

From a string:

```python
text = '{"format": "open-bookmarks/1.0", "title": "My links", "nodes": []}'
pack = load_pack(text)
```

From a dict you already have, for example after `json.loads`:

```python
pack = load_pack({"format": "open-bookmarks/1.0", "title": "My links", "nodes": []})
```

If the text is not valid JSON, `load_pack` raises
`json.JSONDecodeError`. If you pass a value that is not a dict,
a string, bytes, or a file object, it raises `TypeError`. Catch
those at the point where you load, not inside the library.

## Validate it and handle errors

`validate_pack` returns a list of error strings. An empty list
means the pack is valid. A newer minor version is a warning, not
an error, so check warnings separately.

```python
from open_bookmarks import validate_pack, format_warnings, format_version

errors = validate_pack(pack)
if errors:
    raise SystemExit(errors)

for warning in format_warnings(pack):
    print("warning:", warning)

print("format:", format_version(pack))
```

What the validator checks, in short: the pack is a JSON object,
format is "open-bookmarks/1.0" or a newer minor version, title is
non-empty after trimming whitespace, nodes is a list, every node
has a known type and a non-empty title, every url is http or https,
every remote source is https, any custom-properties value is an
object, and no folder sits at level 5 or deeper. The depth limit
is 4 folder levels. A folder directly in the pack is level 1, and
a link inside a level 4 folder is allowed.

A different major version, for example "open-bookmarks/2.0", is an
error, not a warning. A malformed format value is also an error.

## Flatten it to links, with folder path

`flatten_urls` returns a flat list in pack order, deduped by URL,
keeping the first occurrence. Each entry has title, url, and path,
where path is the folder path joined with "/". A top-level link
has an empty path.

```python
for link in flatten_urls(pack):
    print(link["path"], link["title"], link["url"])
```

For the news pack, that prints the World folder links, with path
"World", and no Tech News links, because those live in a remote
folder that has not been expanded yet. See the next section for
remote folders.

## Read custom-properties from flattened output

If a bookmark has custom-properties, that object is included in
its flattened entry, unchanged, under the key "custom-properties".
Keys inside it are not interpreted. A bookmark without it
flattens exactly as before, with no custom-properties key.

```python
for link in flatten_urls(pack):
    props = link.get("custom-properties")
    if props:
        print(link["title"], "icon:", props.get("icon"), "accent:", props.get("accent"))
```

For the news pack, BBC News has custom-properties with an icon
and an accent. Reuters does not, so its entry has no
custom-properties key.

## Expand a remote folder

Remote folders only expand when you supply a fetch function. The
library itself never does network calls. The fetch function takes
a source URL and returns a pack dict, a JSON string, or None if
the source cannot be loaded. A source that fails to load is left
as an unexpanded folder.

```python
from open_bookmarks import expand_remote

def fetch(url):
    # Replace this with your own HTTP call.
    # Return a pack dict, a JSON string, or None.
    if url.endswith("tech.json"):
        with open("packs/examples/tech.json", encoding="utf-8") as handle:
            return handle.read()
    return None

expanded = expand_remote(pack, fetch)
for link in flatten_urls(expanded):
    print(link["path"], link["title"], link["url"])
```

With that fetch function, the news pack expands to five links:
the three World links, plus Hacker News and The Verge under
"Tech News". Expansion stops at the depth limit of 4 folder
levels, and a source URL is expanded at most once per path from the root, so
cycles stop safely.

## How version warnings work

`format_version` returns the format string, for example
"open-bookmarks/1.0", or None if it is missing.
`format_warnings` returns a list of version warnings. It returns
an empty list for "open-bookmarks/1.0" and for a missing format,
because a missing format is already an error in `validate_pack`.
It returns a warning for a newer minor version such as
"open-bookmarks/1.1", and the pack is still read with the fields
the library knows. It returns no warning for a different major
version, because that case is an error in `validate_pack`.

## Pack version

`pack_version` returns the author version of a pack, for
example "1.2.0", or None if the pack has no version field. This
is not the format version: `format_version` returns
"open-bookmarks/1.0", while `pack_version` returns the version
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

Run this from the repo root:

```sh
python3 lib/python/example.py
```

It loads `packs/examples/news.json`, validates it, prints the
flattened links, and shows custom-properties where present.

## Functions

- `load_pack(data)`: dict, JSON string, bytes, or file object in,
  pack dict out.
- `format_version(pack)`: the `format` string, for example
  `open-bookmarks/1.0`, or None if missing.
- `pack_author(pack)`: the person or group that made this pack, or None if missing. Pack level only, not the author of a linked page.
- `pack_version(pack)`: the author `version` of this pack, for
  example `1.2.0`, or None if missing. Not the format version.
- `format_warnings(pack)`: list of version warnings, empty for
  1.0. A newer minor version warns, a different major version
  does not warn here, because it is an error in `validate_pack`.
- `validate_pack(pack)`: list of error strings, empty if valid.
- `flatten_urls(pack)`: flat list of `title`, `url`, and `path`, plus `icon` when the bookmark has one
  (the folder path, joined with `/`), deduped by URL, in pack order.
  If a bookmark has `custom-properties`, that object is included
  in its flattened entry, unchanged.
- `expand_remote(pack, fetch)`: a copy of the pack with remote
  folders expanded. Depth is capped at 4 folder levels, and a
  source URL is expanded at most once per path from the root, so cycles stop
  safely.
