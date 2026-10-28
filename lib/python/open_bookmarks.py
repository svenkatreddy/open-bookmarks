"""Small, dependency free library for open-bookmarks packs.

Functions:
  load_pack(data)      Accept a dict, a JSON string, or a file-like
                       object, and return the pack dict.
  format_version(pack) Return the pack format string, for example
                       open-bookmarks/1.0, or None if missing.
  pack_version(pack)   Return the author version of this pack, for
                       example 1.2.0, or None if missing. This is
                       not the format version. It is an optional
                       string, and a non-semantic version string
                       is still valid.
  validate_pack(pack)  Return a list of error strings, empty if valid.
                       A newer minor version is a warning, not an
                       error, see format_warnings.
  format_warnings(pack) Return a list of version warnings.
  flatten_urls(pack)   Return a flat list of dicts with title, url,
                       folder path, and custom-properties and icon
                       where the bookmark has them, in pack order.
  expand_remote(pack, fetch)  Return a new pack with remote folders
                       expanded, using fetch(source_url) supplied by
                       the caller. The library itself does no network
                       calls. fetch must return a pack dict, a JSON
                       string, or None. Depth is capped at 4 folder levels and a
                       source URL is expanded at most once per path
                       from the root, so cycles cannot loop forever.
"""

import json

MAX_DEPTH = 4
FORMAT = "open-bookmarks/1.0"


def _host_ok(value, scheme):
    rest = value[len(scheme):]
    if not rest or rest[0] in "/?#":
        return False
    host = rest.split("/")[0].split("?")[0].split("#")[0]
    return bool(host)


def _is_http_url(value):
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


def _is_https_url(value):
    if not isinstance(value, str):
        return False
    value = value.strip()
    if not value or " " in value:
        return False
    lowered = value.lower()
    if not lowered.startswith("https://"):
        return False
    return _host_ok(lowered, "https://")


import re as _re
_UPDATED_RE = _re.compile(
    r"^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])"
    r"(T([01]\d|2[0-3]):[0-5]\d(:[0-5]\d)?"
    r"(Z|[+-]([01]\d|2[0-3]):[0-5]\d)?)?$"
)


def _is_iso_date(value):
    return isinstance(value, str) and bool(_UPDATED_RE.match(value))


def load_pack(data):
    """Load a pack from a dict, a JSON string, bytes, or a file object."""
    if isinstance(data, dict):
        return data
    if isinstance(data, (bytes, bytearray)):
        data = data.decode("utf-8")
    if isinstance(data, str):
        return json.loads(data)
    if hasattr(data, "read"):
        return json.load(data)
    raise TypeError("load_pack needs a dict, JSON text, or a file object")


def format_version(pack):
    """Return the pack format string, or None if it is missing."""
    if isinstance(pack, dict):
        value = pack.get("format")
        return value if isinstance(value, str) else None
    return None


def pack_version(pack):
    """Return the author version of this pack, or None if missing.

    This is the pack version in the version field, not the format
    version in the format field. It is passed through unchanged
    by load_pack, because load_pack returns the pack dict as is.
    """
    if isinstance(pack, dict):
        value = pack.get("version")
        if isinstance(value, str) and value.strip():
            return value
    return None


def format_warnings(pack):
    """Return version warnings. A newer minor version warns, not fails."""
    value = format_version(pack)
    if value == FORMAT or value is None:
        return []
    if value.startswith("open-bookmarks/1."):
        rest = value[len("open-bookmarks/1."):]
        if rest.isdigit() and int(rest) > 0:
            return [
                "format is a newer minor version %r, "
                "reading the fields this library knows" % value
            ]
    return []


ICON_TYPES = ("image/png", "image/svg+xml", "image/x-icon",
                "image/webp", "image/gif", "image/jpeg")
_SIZES_RE = _re.compile(r"^(any|(\d+x\d+)( \d+x\d+)*)$")


def _is_icon_src(value):
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
    return _is_https_url(value)


def _check_icon(obj, where, errors):
    if not isinstance(obj, dict) or "icon" not in obj:
        return
    icon = obj["icon"]
    if not isinstance(icon, dict):
        errors.append("%s: icon must be an object" % where)
        return
    src = icon.get("src")
    if not isinstance(src, str) or not src.strip():
        errors.append("%s: icon src is missing or empty" % where)
    elif not _is_icon_src(src):
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


def _check_custom_properties(obj, where, errors):
    if isinstance(obj, dict) and "custom-properties" in obj:
        if not isinstance(obj["custom-properties"], dict):
            errors.append(
                "%s: custom-properties must be an object, got %r"
                % (where, obj["custom-properties"])
            )


def validate_pack(pack):
    """Return a list of errors. An empty list means the pack is valid."""
    errors = []

    def check_nodes(nodes, folder_depth, path, seen_sources):
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
            _check_custom_properties(node, where, errors)
            _check_icon(node, where, errors)
            if not isinstance(title, str) or not title.strip():
                errors.append("%s: title is missing or empty" % where)
            if node_type == "url" and not _is_http_url(node.get("url")):
                errors.append(
                    "%s: url is not http or https: %r" % (where, node.get("url"))
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
                if source is not None and not _is_https_url(source):
                    errors.append(
                        "%s: remote source is not https: %r" % (where, source)
                    )
                elif source is not None and source in seen_sources:
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
                check_nodes(children or [], folder_level, where, next_seen)

    if not isinstance(pack, dict):
        return ["pack is not a JSON object"]
    if pack.get("format") != FORMAT and not format_warnings(pack):
        errors.append(
            "format must be %s, got %r" % (FORMAT, pack.get("format"))
        )
    _check_custom_properties(pack, "pack", errors)
    _check_icon(pack, "pack", errors)
    if "description" in pack and not isinstance(pack["description"], str):
        errors.append("description must be a string")
    if "source" in pack and not _is_https_url(pack["source"]):
        errors.append("source must be https")
    if "updated" in pack and not _is_iso_date(pack["updated"]):
        errors.append("updated must be an ISO 8601 date or date-time")
    if "version" in pack:
        version = pack["version"]
        if not isinstance(version, str) or not version.strip():
            errors.append("version must be a non-empty string")
    if not isinstance(pack.get("title"), str) or not pack["title"].strip():
        errors.append("title is missing or empty")
    if not isinstance(pack.get("nodes"), list):
        errors.append("nodes is missing or not a list")
        return errors
    check_nodes(pack["nodes"], 0, "nodes", set())
    return errors


def flatten_urls(pack, _nodes=None, _path=None, _seen=None):
    """Flatten a pack to title/url/folder-path entries, in order."""
    if _nodes is None:
        nodes = pack.get("nodes", []) if isinstance(pack, dict) else []
        _path = []
        _seen = set()
    else:
        nodes = _nodes
    out = []
    for node in nodes or []:
        if not isinstance(node, dict):
            continue
        if node.get("type") == "url":
            url = node.get("url", "")
            if url in _seen:
                continue
            _seen.add(url)
            entry = {
                "title": node.get("title", ""),
                "url": url,
                "path": "/".join(_path),
            }
            if "custom-properties" in node:
                entry["custom-properties"] = node["custom-properties"]
            if "icon" in node:
                entry["icon"] = node["icon"]
            out.append(entry)
        elif node.get("type") == "folder":
            out.extend(
                flatten_urls(
                    pack,
                    node.get("nodes", []),
                    _path + [node.get("title", "")],
                    _seen,
                )
            )
    return out


def expand_remote(pack, fetch, _folder_depth=0, _seen=None):
    """Return a copy of pack with remote folders expanded.

    fetch is a function taking a source URL and returning a pack
    dict, a JSON string, or None if the source cannot be loaded.
    A source that fails to load is left as an unexpanded folder.
    """
    if _seen is None:
        _seen = set()
    if not isinstance(pack, dict):
        return pack

    def expand_nodes(nodes, folder_depth, seen):
        out = []
        for node in nodes or []:
            if not isinstance(node, dict):
                continue
            new_node = dict(node)
            if node.get("type") == "folder":
                folder_level = folder_depth + 1
                if folder_level > MAX_DEPTH:
                    out.append(new_node)
                    continue
                source = node.get("source")
                children = list(node.get("nodes", []) or [])
                if source and source not in seen and _is_https_url(source):
                    try:
                        remote = fetch(source)
                    except Exception:
                        remote = None
                    if remote is not None:
                        try:
                            remote_pack = load_pack(remote)
                        except Exception:
                            remote_pack = None
                        if isinstance(remote_pack, dict):
                            remote_nodes = remote_pack.get("nodes", [])
                            if isinstance(remote_nodes, list):
                                children = children + remote_nodes
                    new_node["nodes"] = expand_nodes(
                        children, folder_level, seen | {source}
                    )
                else:
                    new_node["nodes"] = expand_nodes(
                        children, folder_level, seen
                    )
            out.append(new_node)
        return out

    result = dict(pack)
    result["nodes"] = expand_nodes(pack.get("nodes", []), _folder_depth, _seen)
    return result
