/// <reference types="vite/client" />

const API_BASE =
  (import.meta.env.VITE_API_BASE as string | undefined)?.replace(/\/$/, "") ??
  "http://127.0.0.1:10910";

export interface NyaaSearchResult {
  title: string;
  magnet: string;
  seeders: number;
  leechers: number;
  size: string;
  quality_score: number;
  release_group: string;
}

export interface PirateBaySearchResult {
  title: string;
  magnet: string;
  seeders: number;
  leechers: number;
  size: string;
  uploaded: string;
  quality_score: number;
  release_group: string;
  episode_info?: {
    season: number | null;
    episode: number | null;
    episode_string: string | null;
    format: string | null;
  };
}

export interface GutenbergSearchResult {
  id: number;
  title: string;
  author: string;
  authors: string[];
  languages: string[];
  subjects: string[];
  download_count: number;
  download_url: string;
  cover_url: string;
  gutenberg_url: string;
  copyright: boolean;
}

export async function searchNyaa(
  query: string,
  resolution = "1080p",
  group = "ASW",
): Promise<{ success: boolean; results: NyaaSearchResult[]; error?: string }> {
  const params = new URLSearchParams({ query, resolution, group });
  const resp = await fetch(`${API_BASE}/api/search/nyaa?${params.toString()}`);
  return resp.json();
}

export async function searchPirateBay(
  query: string,
  category = "tv",
): Promise<{ success: boolean; results: PirateBaySearchResult[]; error?: string }> {
  const params = new URLSearchParams({ query, category });
  const resp = await fetch(`${API_BASE}/api/search/piratebay?${params.toString()}`);
  return resp.json();
}

export async function searchGutenberg(
  query: string,
  topic?: string,
): Promise<{ success: boolean; results: GutenbergSearchResult[]; error?: string }> {
  const params = new URLSearchParams({ query });
  if (topic) params.append("topic", topic);
  const resp = await fetch(`${API_BASE}/api/search/gutenberg?${params.toString()}`);
  return resp.json();
}

export async function addMagnet(
  magnet: string,
  category = "anime",
): Promise<{ status: string; hash?: string; error?: string }> {
  const resp = await fetch(`${API_BASE}/api/rtorrent/magnet`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ magnet, category }),
  });
  return resp.json();
}

export async function normalizeFilename(
  filename: string,
  category = "anime",
): Promise<{ success: boolean; normalized?: Record<string, any>; error?: string }> {
  const resp = await fetch(`${API_BASE}/api/normalize/filename`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ filename, category }),
  });
  return resp.json();
}

export async function getPlexStatus(): Promise<{
  success: boolean;
  configured: boolean;
  plex_url?: string;
  link_mode?: string;
}> {
  const resp = await fetch(`${API_BASE}/api/plex/status`);
  return resp.json();
}

export async function scanPlex(section_id?: string): Promise<{ success: boolean; result?: any; error?: string }> {
  const resp = await fetch(`${API_BASE}/api/plex/scan`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ section_id }),
  });
  return resp.json();
}

export async function triggerPlexIngest(): Promise<{
  success: boolean;
  completed_found?: number;
  processed?: any[];
  error?: string;
}> {
  const resp = await fetch(`${API_BASE}/api/plex/ingest`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
  });
  return resp.json();
}

export { API_BASE };
export default API_BASE;
