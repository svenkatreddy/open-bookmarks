// Small, dependency free library for open-bookmarks packs.
// Same behaviour as lib/python/open_bookmarks.py and
// lib/js/open-bookmarks.mjs. This file uses only erasable
// TypeScript syntax, so it can run under Node type stripping
// and can be type checked with a TypeScript compiler.
//
// loadPack(data)      Accept an object or a JSON string, return the pack.
// formatVersion(pack) Return the pack format string, or null.
// packVersion(pack)   Return the author version of this pack, or
//                     null if missing. This is not the format
//                     version. It is an optional string, and a
//                     non-semantic version string is still valid.
// validatePack(pack)  Return a list of error strings, empty if valid.
//                     A newer minor version is a warning, not an
//                     error, see formatWarnings.
// formatWarnings(pack) Return a list of version warnings.
// flattenUrls(pack)   Return a flat list of title, url, folder path,
//                     and custom-properties where the bookmark has it.
// expandRemote(pack, fetch)  Return a new pack with remote folders
//                     expanded, using the fetch function supplied by
//                     the caller. This module itself does no network
//                     calls. fetch must return a pack object, a JSON
//                     string, or null. Depth is capped at 4 folder
//                     levels and a source URL is expanded at most
//                     once per path from the root.

export const MAX_DEPTH = 4;
export const FORMAT = "open-bookmarks/1.0";

export type CustomProperties = Record<string, unknown>;

export interface UrlNode {
  type: "url";
  title: string;
  url: string;
  "custom-properties"?: CustomProperties;
}

export interface FolderNode {
  type: "folder";
  title: string;
  nodes?: PackNode[];
  source?: string;
  "custom-properties"?: CustomProperties;
}

export type PackNode = UrlNode | FolderNode;

export interface Pack {
  format: string;
  title: string;
  description?: string;
  source?: string;
  updated?: string;
  version?: string;
  nodes: PackNode[];
  "custom-properties"?: CustomProperties;
}

export interface FlatLink {
  title: string;
  url: string;
  path: string;
  "custom-properties"?: CustomProperties;
}

export type FetchFunction = (url: string) => unknown;

function hostOk(lowered: string, scheme: string): boolean {
  const rest = lowered.slice(scheme.length);
  if (!rest || rest[0] === "/" || rest[0] === "?" || rest[0] === "#") return false;
  const host = rest.split("/")[0].split("?")[0].split("#")[0];
  return host.length > 0;
}

function isHttpUrl(value: unknown): value is string {
  if (typeof value !== "string") return false;
  const trimmed = value.trim();
  if (!trimmed || trimmed.includes(" ")) return false;
  const lowered = trimmed.toLowerCase();
  for (const scheme of ["http://", "https://"]) {
    if (lowered.startsWith(scheme)) return hostOk(lowered, scheme);
  }
  return false;
}

function isHttpsUrl(value: unknown): value is string {
  if (typeof value !== "string") return false;
  const trimmed = value.trim();
  if (!trimmed || trimmed.includes(" ")) return false;
  const lowered = trimmed.toLowerCase();
  if (!lowered.startsWith("https://")) return false;
  return hostOk(lowered, "https://");
}

const UPDATED_RE = /^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])(T([01]\d|2[0-3]):[0-5]\d(:[0-5]\d)?(Z|[+-]([01]\d|2[0-3]):[0-5]\d)?)?$/;

function isIsoDate(value: unknown): boolean {
  return typeof value === "string" && UPDATED_RE.test(value);
}

export function loadPack(data: unknown): Pack {
  if (data && typeof data === "object") return data as Pack;
  if (typeof data === "string") return JSON.parse(data) as Pack;
  throw new TypeError("loadPack needs an object or a JSON string");
}

export function formatVersion(pack: unknown): string | null {
  if (pack && typeof pack === "object" && typeof (pack as Pack).format === "string") {
    return (pack as Pack).format;
  }
  return null;
}

export function packVersion(pack: unknown): string | null {
  if (pack && typeof pack === "object" && typeof (pack as Pack).version === "string" && (pack as Pack).version.trim()) {
    return (pack as Pack).version;
  }
  return null;
}

export function formatWarnings(pack: unknown): string[] {
  const value = formatVersion(pack);
  if (value === FORMAT || value === null) return [];
  if (value.startsWith("open-bookmarks/1.")) {
    const rest = value.slice("open-bookmarks/1.".length);
    if (/^\d+$/.test(rest) && parseInt(rest, 10) > 0) {
      return [`format is a newer minor version ${JSON.stringify(value)}, reading the fields this library knows`];
    }
  }
  return [];
}

function checkCustomProperties(obj: unknown, where: string, errors: string[]): void {
  if (obj && typeof obj === "object" && "custom-properties" in obj) {
    const value = (obj as Record<string, unknown>)["custom-properties"];
    if (!value || typeof value !== "object" || Array.isArray(value)) {
      errors.push(`${where}: custom-properties must be an object, got ${JSON.stringify(value)}`);
    }
  }
}

export function validatePack(pack: unknown): string[] {
  const errors: string[] = [];

  function checkNodes(nodes: unknown, folderDepth: number, path: string, seenSources: Set<string>): void {
    if (!Array.isArray(nodes)) {
      errors.push(`${path}: nodes is not a list`);
      return;
    }
    nodes.forEach((node: unknown, index: number) => {
      const where = `${path}[${index}]`;
      if (!node || typeof node !== "object") {
        errors.push(`${where}: node is not an object`);
        return;
      }
      const typed = node as PackNode;
      if (typed.type !== "folder" && typed.type !== "url") {
        errors.push(`${where}: unknown node type ${JSON.stringify((typed as { type?: unknown }).type)}`);
        return;
      }
      checkCustomProperties(node, where, errors);
      if (typeof typed.title !== "string" || !typed.title.trim()) {
        errors.push(`${where}: title is missing or empty`);
      }
      if (typed.type === "url" && !isHttpUrl(typed.url)) {
        errors.push(`${where}: url is not http or https: ${JSON.stringify(typed.url)}`);
      }
      if (typed.type === "folder") {
        const folderLevel = folderDepth + 1;
        if (folderLevel > MAX_DEPTH) {
          errors.push(`${where}: folder at level ${folderLevel} exceeds max depth ${MAX_DEPTH}`);
          return;
        }
        const source = typed.source;
        if (source !== undefined && source !== null && !isHttpsUrl(source)) {
          errors.push(`${where}: remote source is not https: ${JSON.stringify(source)}`);
        } else if (source && seenSources.has(source)) {
          errors.push(`${where}: remote source cycle: ${source} already seen above`);
        }
        const children = typed.nodes || [];
        if (typed.nodes !== undefined && typed.nodes !== null && !Array.isArray(typed.nodes)) {
          errors.push(`${where}: nodes is not a list`);
          return;
        }
        const nextSeen = new Set(seenSources);
        if (source) nextSeen.add(source);
        checkNodes(children, folderLevel, where, nextSeen);
      }
    });
  }

  if (!pack || typeof pack !== "object") {
    return ["pack is not a JSON object"];
  }
  const typedPack = pack as Pack;
  if (typedPack.format !== FORMAT && formatWarnings(pack).length === 0) {
    errors.push(`format must be ${FORMAT}, got ${JSON.stringify(typedPack.format)}`);
  }
  checkCustomProperties(pack, "pack", errors);
  if ("description" in typedPack && typeof typedPack.description !== "string") {
    errors.push("description must be a string");
  }
  if ("source" in typedPack && !isHttpsUrl(typedPack.source)) {
    errors.push("source must be https");
  }
  if ("updated" in typedPack && !isIsoDate(typedPack.updated)) {
    errors.push("updated must be an ISO 8601 date or date-time");
  }
  if ("version" in typedPack && (typeof typedPack.version !== "string" || !typedPack.version.trim())) {
    errors.push("version must be a non-empty string");
  }
  if (typeof typedPack.title !== "string" || !typedPack.title.trim()) {
    errors.push("title is missing or empty");
  }
  if (!Array.isArray(typedPack.nodes)) {
    errors.push("nodes is missing or not a list");
    return errors;
  }
  checkNodes(typedPack.nodes, 0, "nodes", new Set<string>());
  return errors;
}

export function flattenUrls(pack: Pack, nodes?: PackNode[], path?: string[], seen?: Set<string>): FlatLink[] {
  const list = nodes !== undefined ? nodes : (pack && Array.isArray(pack.nodes) ? pack.nodes : []);
  const currentPath = path || [];
  const seenSet = seen || new Set<string>();
  const out: FlatLink[] = [];
  for (const node of list) {
    if (!node || typeof node !== "object") continue;
    if (node.type === "url") {
      if (seenSet.has(node.url)) continue;
      seenSet.add(node.url);
      const entry: FlatLink = { title: node.title || "", url: node.url || "", path: currentPath.join("/") };
      if ("custom-properties" in node) entry["custom-properties"] = node["custom-properties"];
      out.push(entry);
    } else if (node.type === "folder") {
      out.push(...flattenUrls(pack, node.nodes || [], [...currentPath, node.title || ""], seenSet));
    }
  }
  return out;
}

export function expandRemote(pack: Pack, fetch: FetchFunction, folderDepth?: number, seen?: Set<string>): Pack {
  const currentFolderDepth = folderDepth || 0;
  const seenSet = seen || new Set<string>();
  if (!pack || typeof pack !== "object") return pack;

  function expandNodes(nodes: PackNode[], enclosingFolderDepth: number, nodeSeen: Set<string>): PackNode[] {
    const out: PackNode[] = [];
    for (const node of nodes || []) {
      if (!node || typeof node !== "object") continue;
      const newNode: PackNode = { ...node } as PackNode;
      if (node.type === "folder") {
        const folderLevel = enclosingFolderDepth + 1;
        if (folderLevel > MAX_DEPTH) {
          out.push(newNode);
          continue;
        }
        const source = node.source;
        let children: PackNode[] = [...(node.nodes || [])];
        if (source && !nodeSeen.has(source) && isHttpsUrl(source)) {
          let remote: unknown = null;
          try {
            remote = fetch(source);
          } catch {
            remote = null;
          }
          if (remote !== null && remote !== undefined) {
            let remotePack: Pack | null = null;
            try {
              remotePack = loadPack(remote);
            } catch {
              remotePack = null;
            }
            if (remotePack && Array.isArray(remotePack.nodes)) {
              children = children.concat(remotePack.nodes);
            }
          }
          newNode.nodes = expandNodes(children, folderLevel, new Set([...nodeSeen, source]));
        } else {
          newNode.nodes = expandNodes(children, folderLevel, nodeSeen);
        }
      }
      out.push(newNode);
    }
    return out;
  }

  return { ...pack, nodes: expandNodes(pack.nodes || [], currentFolderDepth, seenSet) };
}
