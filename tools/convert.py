#!/usr/bin/env python3
"""Convert bookmarks into and out of the open-bookmarks format.

Dependency free, Python 3 standard library only.

Supported inputs (--from):
  netscape        Netscape Bookmark HTML, the file browsers export
  chrome          Chrome Bookmarks JSON (the profile Bookmarks file)
  firefox         Firefox JSON backup / export
  xbel            XBEL XML
  csv             CSV with title and url columns
  json            A simple list of title/url objects, or a dict with
                  a bookmarks / nodes / children list
  open-bookmarks  A pack already in the open-bookmarks format

Supported outputs (--to):
  open-bookmarks  The format in SPEC.md
  netscape        Netscape Bookmark HTML

Rules, shared by every converter:
  - Only http and https URLs are kept. Anything else is skipped
    with a warning on stderr.
  - Duplicate URLs are kept once, at the first place they appear.
  - Bad entries are skipped, never fatal. A bad link must not
    break a whole import.
  - Unknown fields are ignored.
  - Converters from old formats omit custom-properties, because
    those formats have no equivalent. Converting open-bookmarks
    to Netscape HTML drops custom-properties, because Netscape
    HTML has no place for it. Links and folders survive, custom
    properties do not.
  - Converters omit the pack version field, because old formats
    have no equivalent pack version. Do not invent a version
    for a converted pack; leave the field out, so the pack is
    still valid and a reader falls back to a content diff by URL
    for update guidance. The one exception is open-bookmarks to
    open-bookmarks, which preserves the input pack's description,
    source, updated, version, author, icon, and custom-properties, so a
    round trip does not lose them.
  - Icons: Netscape ICON_URI, when it is https, becomes an icon
    src, with type inferred from the file extension (.png, .svg,
    .ico, .webp, .gif, .jpg or .jpeg) when the extension is
    known, and type omitted otherwise. Netscape ICON alone, a
    base64 value with no MIME type, is skipped with a warning;
    no MIME type is invented for it. Firefox iconuri, when it is
    a data:image/ URI or an https URL, becomes an icon src, with
    type taken from the data URI header or inferred from the
    extension; any other scheme, including moz-anno:, is skipped
    with a warning. Exporting open-bookmarks to Netscape HTML
    writes an https icon src as ICON_URI, and a base64 data URI
    icon src as ICON holding only the base64 part after the
    comma; type and sizes are lost on that export, and folder
    icons and non-base64 data URI icons are dropped.
  - Depth: when converting to open-bookmarks, folders deeper
    than 4 levels are skipped with a warning, and their whole
    subtree is skipped, so converter output always conforms to
    the depth limit in SPEC.md. A url inside a folder at level 4
    is kept. This rule does not apply to Netscape HTML output,
    where depth is not an open-bookmarks rule.
"""

import argparse
import csv
import html
import json
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser


def warn(message):
    print("warning: " + message, file=sys.stderr)


def is_http_url(value):
    if not isinstance(value, str):
        return False
    value = value.strip()
    if not value or " " in value:
        return False
    lowered = value.lower()
    for scheme in ("http://", "https://"):
        if lowered.startswith(scheme):
            rest = lowered[len(scheme):]
            if not rest or rest[0] in "/?#":
                return False
            host = rest.split("/")[0].split("?")[0].split("#")[0]
            return bool(host)
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
    rest = lowered[len("https://"):]
    if not rest or rest[0] in "/?#":
        return False
    host = rest.split("/")[0].split("?")[0].split("#")[0]
    return bool(host)


def clean_title(value, fallback="Untitled"):
    if isinstance(value, str) and value.strip():
        return value.strip()
    return fallback


def dedupe_nodes(nodes, seen=None):
    """Remove duplicate URLs, keeping the first occurrence."""
    if seen is None:
        seen = set()
    out = []
    for node in nodes:
        if not isinstance(node, dict):
            continue
        node_type = node.get("type")
        if node_type == "url":
            url = node.get("url", "")
            if url in seen:
                continue
            seen.add(url)
            out.append(node)
        elif node_type == "folder":
            children = dedupe_nodes(node.get("nodes", []), seen)
            new_node = dict(node)
            new_node["nodes"] = children
            out.append(new_node)
        else:
            continue
    return out


def prune_depth(nodes, folder_depth=0):
    """Skip folders deeper than 4 levels, with a warning.

    folder_depth is the number of enclosing folders for this list.
    A folder in the top-level list is at level 1. A url inside a
    folder at level 4 is kept, because it is not a folder level.
    """
    out = []
    for node in nodes:
        if not isinstance(node, dict):
            continue
        if node.get("type") == "url":
            out.append(node)
        elif node.get("type") == "folder":
            folder_level = folder_depth + 1
            if folder_level > 4:
                warn(
                    "skipping folder deeper than 4 levels: %r"
                    % (node.get("title"),)
                )
                continue
            new_node = dict(node)
            if "nodes" in node:
                new_node["nodes"] = prune_depth(
                    node.get("nodes", []), folder_level
                )
            out.append(new_node)
    return out


def url_node(title, url):
    url = url.strip() if isinstance(url, str) else ""
    if not is_http_url(url):
        warn("skipping non-http URL: %r" % (url,))
        return None
    return {"type": "url", "title": clean_title(title), "url": url}


def folder_node(title, nodes=None, source=None):
    node = {"type": "folder", "title": clean_title(title)}
    if nodes:
        node["nodes"] = nodes
    if source and is_https_url(source):
        node["source"] = source.strip()
    elif source:
        warn("skipping non-https remote source: %r" % (source,))
    return node


ICON_TYPES = {
    "image/png", "image/svg+xml", "image/x-icon",
    "image/webp", "image/gif", "image/jpeg",
}
_EXT_TO_TYPE = {
    ".png": "image/png",
    ".svg": "image/svg+xml",
    ".ico": "image/x-icon",
    ".webp": "image/webp",
    ".gif": "image/gif",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
}


def infer_icon_type(src):
    lowered = src.strip().lower()
    lowered = lowered.split("?")[0].split("#")[0]
    for ext, mime in _EXT_TO_TYPE.items():
        if lowered.endswith(ext):
            return mime
    return None


def icon_from_src(src):
    """Return an icon dict for a valid src, or None with a warning."""
    if not isinstance(src, str) or not src.strip():
        return None
    src = src.strip()
    if src.startswith("data:"):
        rest = src[len("data:"):]
        if "," not in rest:
            warn("skipping icon data URI with no comma: %r" % (src[:60],))
            return None
        header, data = rest.split(",", 1)
        mime = header.split(";")[0]
        if mime not in ICON_TYPES or not data:
            warn("skipping non-image icon data URI: %r" % (src[:60],))
            return None
        return {"src": src, "type": mime}
    if is_https_url(src):
        icon = {"src": src}
        mime = infer_icon_type(src)
        if mime:
            icon["type"] = mime
        return icon
    warn("skipping icon src that is not https or an image data URI: %r" % (src,))
    return None


def attach_icon(node, src):
    if node is None:
        return None
    icon = icon_from_src(src)
    if icon is not None:
        node["icon"] = icon
    return node


# Netscape HTML


class NetscapeParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.root = []
        self.stack = [self.root]
        self.pending_folder = None
        self.in_h3 = False
        self.pending_link = None
        self.in_a = False

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        attrs = {k.lower(): v for k, v in attrs}
        if tag == "dl":
            if self.pending_folder is not None:
                folder = self.pending_folder
                self.pending_folder = None
                self.stack[-1].append(folder)
                self.stack.append(folder["nodes"])
        elif tag == "h3":
            self.in_h3 = True
            self.pending_folder = {"type": "folder", "title": "", "nodes": []}
        elif tag == "a":
            self.in_a = True
            self.pending_link = {
                "href": attrs.get("href", ""),
                "title": "",
                "icon_uri": attrs.get("icon_uri", ""),
                "icon": attrs.get("icon", ""),
            }

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag == "h3":
            self.in_h3 = False
            if self.pending_folder is not None:
                self.pending_folder["title"] = clean_title(
                    self.pending_folder["title"]
                )
        elif tag == "a":
            self.in_a = False
            if self.pending_link is not None:
                node = url_node(
                    self.pending_link["title"], self.pending_link["href"]
                )
                if node is not None:
                    icon_uri = self.pending_link.get("icon_uri", "")
                    if icon_uri:
                        attach_icon(node, icon_uri)
                    elif self.pending_link.get("icon"):
                        warn(
                            "skipping Netscape ICON with no MIME type for %r; "
                            "use ICON_URI with an https URL instead"
                            % (self.pending_link["title"],)
                        )
                    self.stack[-1].append(node)
                self.pending_link = None
        elif tag == "dl":
            if len(self.stack) > 1:
                self.stack.pop()
        elif tag == "dt":
            # A folder heading with no child list still counts.
            if self.pending_folder is not None:
                self.stack[-1].append(self.pending_folder)
                self.pending_folder = None

    def handle_data(self, data):
        if self.in_h3 and self.pending_folder is not None:
            self.pending_folder["title"] += data
        elif self.in_a and self.pending_link is not None:
            self.pending_link["title"] += data


def parse_netscape(text):
    parser = NetscapeParser()
    parser.feed(text)
    return "Imported bookmarks", parser.root


# Chrome JSON


def walk_chrome_node(node):
    if not isinstance(node, dict):
        return None
    node_type = node.get("type")
    if node_type == "url":
        return url_node(node.get("name"), node.get("url", ""))
    if node_type == "folder":
        children = []
        for child in node.get("children", []):
            walked = walk_chrome_node(child)
            if walked is not None:
                children.append(walked)
        return folder_node(node.get("name"), children)
    return None


def parse_chrome(data):
    nodes = []
    roots = data.get("roots", {}) if isinstance(data, dict) else {}
    if roots:
        for key in ("bookmark_bar", "other", "synced"):
            root = roots.get(key)
            if not isinstance(root, dict):
                continue
            children = []
            for child in root.get("children", []):
                walked = walk_chrome_node(child)
                if walked is not None:
                    children.append(walked)
            if children:
                nodes.append(folder_node(root.get("name", key), children))
        if not nodes:
            # Fall back to a flat walk of every root.
            for root in roots.values():
                if isinstance(root, dict):
                    for child in root.get("children", []):
                        walked = walk_chrome_node(child)
                        if walked is not None:
                            nodes.append(walked)
    elif isinstance(data, dict) and data.get("children"):
        for child in data["children"]:
            walked = walk_chrome_node(child)
            if walked is not None:
                nodes.append(walked)
    return "Imported bookmarks", nodes


# Firefox JSON and generic tree JSON


def walk_generic_node(node):
    if not isinstance(node, dict):
        return None
    node_type = str(node.get("type", ""))
    # Firefox uses text/x-moz-place and text/x-moz-place-container.
    if node_type in ("url", "text/x-moz-place") or "uri" in node:
        url = node.get("uri") or node.get("url", "")
        node_out = url_node(node.get("title") or node.get("name"), url)
        iconuri = node.get("iconuri") or node.get("icon_uri")
        if iconuri:
            attach_icon(node_out, iconuri)
        return node_out
    if node_type in ("folder", "text/x-moz-place-container") or (
        "children" in node or "nodes" in node
    ):
        children = []
        for child in node.get("children", []) or node.get("nodes", []):
            walked = walk_generic_node(child)
            if walked is not None:
                children.append(walked)
        return folder_node(node.get("title") or node.get("name"), children)
    return None


def parse_firefox(data):
    nodes = []
    if isinstance(data, dict):
        items = data.get("children") or data.get("nodes") or []
        if not items and data.get("type"):
            walked = walk_generic_node(data)
            if walked is not None:
                nodes.append(walked)
        else:
            for item in items:
                walked = walk_generic_node(item)
                if walked is not None:
                    nodes.append(walked)
    elif isinstance(data, list):
        for item in data:
            walked = walk_generic_node(item)
            if walked is not None:
                nodes.append(walked)
    return "Imported bookmarks", nodes


# XBEL XML


def walk_xbel(element):
    tag = element.tag.split("}")[-1]
    if tag == "bookmark":
        title_el = element.find("title")
        title = title_el.text if title_el is not None else ""
        return url_node(title, element.get("href", ""))
    if tag == "folder":
        title_el = element.find("title")
        title = title_el.text if title_el is not None else ""
        children = []
        for child in element:
            walked = walk_xbel(child)
            if walked is not None:
                children.append(walked)
        return folder_node(title, children)
    return None


def parse_xbel(text):
    root = ET.fromstring(text)
    nodes = []
    for child in root:
        walked = walk_xbel(child)
        if walked is not None:
            nodes.append(walked)
    return "Imported bookmarks", nodes


# CSV and simple JSON list


def parse_csv(text):
    lines = text.splitlines()
    if not lines:
        return "Imported bookmarks", []
    reader = csv.reader(lines)
    rows = list(reader)
    if not rows:
        return "Imported bookmarks", []
    header = [c.strip().lower() for c in rows[0]]
    has_header = "url" in header or "link" in header or "href" in header
    start = 1 if has_header else 0
    title_idx = 0
    url_idx = 1
    if has_header:
        for name in ("title", "name"):
            if name in header:
                title_idx = header.index(name)
                break
        for name in ("url", "link", "href"):
            if name in header:
                url_idx = header.index(name)
                break
    nodes = []
    for row in rows[start:]:
        if len(row) <= max(title_idx, url_idx):
            continue
        node = url_node(row[title_idx], row[url_idx])
        if node is not None:
            nodes.append(node)
    return "Imported bookmarks", nodes


def parse_json_list(data):
    items = []
    if isinstance(data, list):
        items = data
    elif isinstance(data, dict):
        items = (
            data.get("bookmarks")
            or data.get("nodes")
            or data.get("children")
            or []
        )
    nodes = []
    for item in items:
        if not isinstance(item, dict):
            continue
        if item.get("type") in ("folder", "url") and "url" not in item:
            walked = walk_generic_node(item)
            if walked is not None:
                nodes.append(walked)
            continue
        title = item.get("title") or item.get("name") or ""
        url = item.get("url") or item.get("link") or item.get("href") or ""
        node = url_node(title, url)
        if node is not None:
            nodes.append(node)
    return "Imported bookmarks", nodes


def parse_open_bookmarks(data):
    if not isinstance(data, dict):
        warn("open-bookmarks input is not a JSON object")
        return "Imported bookmarks", []
    title = data.get("title") or "Imported bookmarks"
    nodes = data.get("nodes", [])
    if not isinstance(nodes, list):
        warn("open-bookmarks nodes is not a list")
        nodes = []
    return title, nodes


# Output: Netscape HTML


def nodes_to_netscape(nodes, indent=0):
    pad = "    " * indent
    lines = [pad + "<DL><p>"]
    for node in nodes:
        if node.get("type") == "url":
            icon_attrs = ""
            icon = node.get("icon")
            if isinstance(icon, dict) and isinstance(icon.get("src"), str):
                src = icon["src"].strip()
                if src.startswith("https://"):
                    icon_attrs = ' ICON_URI="%s"' % html.escape(src, quote=True)
                elif src.startswith("data:"):
                    rest = src[len("data:"):]
                    if "," in rest:
                        header, data = rest.split(",", 1)
                        if ";base64" in header and data:
                            icon_attrs = ' ICON="%s"' % html.escape(data, quote=True)
            lines.append(
                '%s<DT><A HREF="%s"%s>%s</A>'
                % (
                    pad,
                    html.escape(node.get("url", ""), quote=True),
                    icon_attrs,
                    html.escape(node.get("title", "")),
                )
            )
        elif node.get("type") == "folder":
            lines.append(
                "%s<DT><H3>%s</H3>"
                % (pad, html.escape(node.get("title", "")))
            )
            children = node.get("nodes", [])
            if node.get("source") and not children:
                # Keep the remote link visible in a plain export.
                children = [
                    {
                        "type": "url",
                        "title": node.get("title", "") + " (pack)",
                        "url": node["source"],
                    }
                ]
            lines.extend(nodes_to_netscape(children, indent + 1))
    lines.append(pad + "</DL><p>")
    return lines


def to_netscape(title, nodes):
    lines = [
        "<!DOCTYPE NETSCAPE-Bookmark-file-1>",
        "<META HTTP-EQUIV=\"Content-Type\" CONTENT=\"text/html; charset=UTF-8\">",
        "<TITLE>%s</TITLE>" % html.escape(title),
        "<H1>%s</H1>" % html.escape(title),
    ]
    lines.extend(nodes_to_netscape(nodes))
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Convert bookmarks to and from open-bookmarks."
    )
    parser.add_argument(
        "--from",
        dest="from_format",
        required=True,
        choices=[
            "netscape",
            "chrome",
            "firefox",
            "xbel",
            "csv",
            "json",
            "open-bookmarks",
        ],
        help="Input format",
    )
    parser.add_argument(
        "--to",
        dest="to_format",
        required=True,
        choices=["open-bookmarks", "netscape"],
        help="Output format",
    )
    parser.add_argument("--input", required=True, help="Input file path")
    parser.add_argument(
        "--output",
        help="Output file path. Writes to stdout if omitted.",
    )
    args = parser.parse_args(argv)

    with open(args.input, "r", encoding="utf-8", errors="replace") as handle:
        text = handle.read()

    from_format = args.from_format
    if from_format == "netscape":
        title, nodes = parse_netscape(text)
    elif from_format == "xbel":
        title, nodes = parse_xbel(text)
    elif from_format == "csv":
        title, nodes = parse_csv(text)
    else:
        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            print("error: input is not valid JSON: %s" % exc, file=sys.stderr)
            return 1
        if isinstance(data, dict) and data.get("format") == "open-bookmarks/encrypted/1.0":
            print(
                "error: input is an encrypted pack, not a plain pack: "
                "decrypt it first, then convert the plain pack inside",
                file=sys.stderr,
            )
            return 1
        if from_format == "chrome":
            title, nodes = parse_chrome(data)
        elif from_format == "firefox":
            title, nodes = parse_firefox(data)
        elif from_format == "json":
            title, nodes = parse_json_list(data)
        else:
            title, nodes = parse_open_bookmarks(data)

    nodes = dedupe_nodes(nodes)

    if args.to_format == "open-bookmarks":
        nodes = prune_depth(nodes)
        pack = {
            "format": "open-bookmarks/1.0",
            "title": title,
            "nodes": nodes,
        }
        if from_format == "open-bookmarks" and isinstance(data, dict):
            for field in ("description", "source", "updated", "version", "author", "icon", "custom-properties"):
                if field in data:
                    pack[field] = data[field]
        output = json.dumps(pack, indent=2, ensure_ascii=False) + "\n"
    else:
        output = to_netscape(title, nodes)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(output)
    else:
        sys.stdout.write(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
