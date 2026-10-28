export const MAX_DEPTH: number;
export const FORMAT: string;
export type CustomProperties = Record<string, unknown>;
export interface Icon {
  src: string;
  type?: string;
  sizes?: string;
}
export interface UrlNode {
  type: "url";
  title: string;
  url: string;
  icon?: Icon;
  "custom-properties"?: CustomProperties;
}
export interface FolderNode {
  type: "folder";
  title: string;
  nodes?: PackNode[];
  source?: string;
  icon?: Icon;
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
  icon?: Icon;
  "custom-properties"?: CustomProperties;
}
export interface FlatLink {
  title: string;
  url: string;
  path: string;
  icon?: Icon;
  "custom-properties"?: CustomProperties;
}
export type FetchFunction = (url: string) => unknown;
export function loadPack(data: unknown): Pack;
export function formatVersion(pack: unknown): string | null;
export function packVersion(pack: unknown): string | null;
export function formatWarnings(pack: unknown): string[];
export function validatePack(pack: unknown): string[];
export function flattenUrls(pack: Pack, nodes?: PackNode[], path?: string[], seen?: Set<string>): FlatLink[];
export function expandRemote(pack: Pack, fetch: FetchFunction, folderDepth?: number, seen?: Set<string>): Pack;
