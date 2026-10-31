#!/usr/bin/env python3
"""Validate an open-bookmarks pack. Dependency free.

Usage:
  python3 tools/validate.py pack.json

Checks, in plain language:
  - the file is JSON and a pack object
  - format is open-bookmarks/1.0, or a newer minor version
    (warned, not failed), or a different major version (failed)
  - title is present and nodes is a list
  - every node has a known type and a title
  - every url is http or https, every remote source is https
  - any custom-properties present, on the pack or on a node,
    is a JSON object, not a string, number, array, or null
  - any version present, on the pack, is a non-empty string
  - any author present, on the pack, is a non-empty string
  - any icon present, on the pack or on a node, is an object
    with a required src that is an https URL or an image data
    URI, an optional type from a fixed list, and optional sizes
  - folder nesting is no deeper than 4 folder levels
  - remote sources in the same file do not form a simple cycle
    (a source URL repeated on the path from the root to a folder)

Exit code 0 means valid, 1 means one or more errors were found.
Warnings do not fail validation.
"""

import argparse
import json
import re as _re
import sys

MAX_DEPTH = 4


def _host_ok(value, scheme):
    # value is already stripped, scheme is "http://" or "https://".
    rest = value[len(scheme):]
    if not rest or rest[0] in "/?#":
        return False
    host = rest.split("/")[0].split("?")[0].split("#")[0]
    return bool(host)


def is_http_url(value):
    if not isinstance(value, str):
        return False
    value = value.strip()
    if not value or " " in value:
        return False
    lowered = value.lower()
    for scheme in ("http://", "https://"):
        if lowered.startswith(scheme):
            return _host_ok(lowered, scheme)
    return False


def is_https_url(value):
    if not isinstance(value, str):
        return False
    value = value.strip()
    if not value or " " in value:
        return False
    lowered = value.lower()
    if not lowered.startswith("https://"):
        return False
    return _host_ok(lowered, "https://")


_UPDATED_RE = _re.compile(
    r"^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])"
    r"(T([01]\d|2[0-3]):[0-5]\d(:[0-5]\d)?"
    r"(Z|[+-]([01]\d|2[0-3]):[0-5]\d)?)?$"
)


def is_iso_date(value):
    return isinstance(value, str) and bool(_UPDATED_RE.match(value))


ICON_TYPES = ("image/png", "image/svg+xml", "image/x-icon",
                "image/webp", "image/gif", "image/jpeg")
_SIZES_RE = _re.compile(r"^(any|(\d+x\d+)( \d+x\d+)*)$")


def is_icon_src(value):
    if not isinstance(value, str):
        return False
    value = value.strip()
    if not value or " " in value:
        return False
    if value.startswith("data:"):
        rest = value[len("data:"):]
        if "," not in rest:
            return False
        header, data = rest.split(",", 1)
        if not data:
            return False
        mime = header.split(";")[0]
        return mime in ICON_TYPES
    return is_https_url(value)


def check_icon(obj, where, errors):
    if "icon" not in obj:
        return
    icon = obj["icon"]
    if not isinstance(icon, dict):
        errors.append("%s: icon must be an object" % where)
        return
    src = icon.get("src")
    if not isinstance(src, str) or not src.strip():
        errors.append("%s: icon src is missing or empty" % where)
    elif not is_icon_src(src):
        errors.append(
            "%s: icon src is not an https URL or an image data URI: %r"
            % (where, src)
        )
    if "type" in icon and icon["type"] not in ICON_TYPES:
        errors.append(
            "%s: icon type must be one of %s, got %r"
            % (where, ", ".join(ICON_TYPES), icon["type"])
        )
    if "sizes" in icon:
        sizes = icon["sizes"]
        if not isinstance(sizes, str) or not _SIZES_RE.match(sizes.strip()):
            errors.append(
                '%s: icon sizes must be like "32x32", "16x16 32x32", '
                'or "any", got %r' % (where, sizes)
            )


def check_custom_properties(obj, where, errors):
    if "custom-properties" in obj:
        value = obj["custom-properties"]
        if not isinstance(value, dict):
            errors.append(
                "%s: custom-properties must be an object, got %r"
                % (where, value)
            )


def format_warnings(pack):
    """Return warnings for the format field, empty if it is 1.0."""
    value = pack.get("format") if isinstance(pack, dict) else None
    if value == "open-bookmarks/1.0":
        return []
    if isinstance(value, str) and value.startswith("open-bookmarks/1."):
        rest = value[len("open-bookmarks/1."):]
        if rest.isdigit() and int(rest) > 0:
            return [
                "format is a newer minor version %r, "
                "reading the fields this validator knows" % value
            ]
    return []


def validate_nodes(nodes, errors, folder_depth, path, seen_sources):
    # folder_depth is the number of enclosing folders for this list.
    # A folder in the top-level list is at level 1, and so on.
    if not isinstance(nodes, list):
        errors.append("%s: nodes is not a list" % path)
        return
    for index, node in enumerate(nodes):
        where = "%s[%d]" % (path, index)
        if not isinstance(node, dict):
            errors.append("%s: node is not an object" % where)
            continue
        node_type = node.get("type")
        title = node.get("title")
        if node_type not in ("folder", "url"):
            errors.append("%s: unknown node type %r" % (where, node_type))
            continue
        check_custom_properties(node, where, errors)
        check_icon(node, where, errors)
        if not isinstance(title, str) or not title.strip():
            errors.append("%s: title is missing or empty" % where)
        if node_type == "url":
            if not is_http_url(node.get("url")):
                errors.append(
                    "%s: url is not http or https: %r"
                    % (where, node.get("url"))
                )
        if node_type == "folder":
            folder_level = folder_depth + 1
            if folder_level > MAX_DEPTH:
                errors.append(
                    "%s: folder at level %d exceeds max depth %d"
                    % (where, folder_level, MAX_DEPTH)
                )
                continue
            source = node.get("source")
            if source is not None:
                if not is_https_url(source):
                    errors.append(
                        "%s: remote source is not https: %r"
                        % (where, source)
                    )
                elif source in seen_sources:
                    errors.append(
                        "%s: remote source cycle: %s already seen above"
                        % (where, source)
                    )
            children = node.get("nodes", [])
            if children is not None and not isinstance(children, list):
                errors.append("%s: nodes is not a list" % where)
                continue
            next_seen = set(seen_sources)
            if source:
                next_seen.add(source)
            validate_nodes(
                children or [], errors, folder_level, where, next_seen
            )


def validate_pack(pack):
    errors = []
    if not isinstance(pack, dict):
        return ["pack is not a JSON object"]
    if pack.get("format") == "open-bookmarks/encrypted/1.0":
        return [
            "this is an encrypted pack, not a plain pack: "
            "decrypt it first, then validate the plain pack inside"
        ]
    if pack.get("format") != "open-bookmarks/1.0" and not format_warnings(
        pack
    ):
        errors.append(
            "format must be open-bookmarks/1.0, got %r" % (pack.get("format"),)
        )
    check_custom_properties(pack, "pack", errors)
    check_icon(pack, "pack", errors)
    if "description" in pack and not isinstance(pack["description"], str):
        errors.append("description must be a string")
    if "source" in pack and not is_https_url(pack["source"]):
        errors.append("source must be https")
    if "updated" in pack and not is_iso_date(pack["updated"]):
        errors.append("updated must be an ISO 8601 date or date-time")
    if "version" in pack:
        version = pack["version"]
        if not isinstance(version, str) or not version.strip():
            errors.append("version must be a non-empty string")
    if "author" in pack:
        author = pack["author"]
        if not isinstance(author, str) or not author.strip():
            errors.append("author must be a non-empty string")
    if not isinstance(pack.get("title"), str) or not pack["title"].strip():
        errors.append("title is missing or empty")
    if not isinstance(pack.get("nodes"), list):
        errors.append("nodes is missing or not a list")
        return errors
    validate_nodes(pack["nodes"], errors, 0, "nodes", set())
    return errors


def main(argv=None):
    parser = argparse.ArgumentParser(description="Validate an open-bookmarks pack.")
    parser.add_argument("input", help="Pack JSON file to check")
    args = parser.parse_args(argv)
    try:
        with open(args.input, "r", encoding="utf-8") as handle:
            pack = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        print("error: cannot read pack: %s" % exc, file=sys.stderr)
        return 1
    errors = validate_pack(pack)
    if errors:
        for error in errors:
            print("error: " + error, file=sys.stderr)
        return 1
    for warning in format_warnings(pack):
        print("warning: " + warning, file=sys.stderr)
    print("valid: %s" % args.input)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
