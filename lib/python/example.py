"""Example: load the news pack, validate it, print its links.

Run from the repo root:
  python3 lib/python/example.py

It loads packs/examples/news.json, prints the flattened links,
and shows custom-properties where a bookmark has them. It uses
only the standard library, like the library itself.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from open_bookmarks import flatten_urls, load_pack, pack_version, validate_pack


def main():
    repo_root = Path(__file__).resolve().parents[2]
    pack_path = repo_root / "packs" / "examples" / "news.json"
    with open(pack_path, encoding="utf-8") as handle:
        pack = load_pack(handle)
    errors = validate_pack(pack)
    if errors:
        raise SystemExit(errors)
    print("pack version: %s" % (pack_version(pack),))
    for link in flatten_urls(pack):
        line = "%s %s %s" % (link["path"], link["title"], link["url"])
        props = link.get("custom-properties")
        if props:
            line += " custom-properties=%s" % (props,)
        print(line)


if __name__ == "__main__":
    main()
