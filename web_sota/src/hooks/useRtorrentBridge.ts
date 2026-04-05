import { useCallback, useEffect, useState } from "react";

export type HealthPayload = { ok?: boolean; service?: string; version?: string };

export type RtorrentStatusPayload = {
  connected?: boolean;
  host?: string;
  port?: number;
  error?: string;
};

export type TorrentsPayload = {
  success?: boolean;
  count?: number;
  torrents?: Array<{
    hash: string;
    name: string;
    state: number;
    size_bytes: number;
    completed_bytes: number;
    progress: number;
  }>;
  error?: string;
};

export function useRtorrentBridge(pollMs = 8000) {
  const [health, setHealth] = useState<HealthPayload | null>(null);
  const [rtStatus, setRtStatus] = useState<RtorrentStatusPayload | null>(null);
  const [torrents, setTorrents] = useState<TorrentsPayload | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setError(null);
    try {
      const [h, s, t] = await Promise.all([
        fetch("/api/health").then((r) => (r.ok ? r.json() : Promise.reject(new Error(`health ${r.status}`)))),
        fetch("/api/rtorrent/status").then((r) => r.json()),
        fetch("/api/rtorrent/torrents").then((r) => r.json()),
      ]);
      setHealth(h);
      setRtStatus(s);
      setTorrents(t);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load bridge API");
      setHealth(null);
      setRtStatus(null);
      setTorrents(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
    if (pollMs <= 0) return;
    const id = window.setInterval(() => void refresh(), pollMs);
    return () => window.clearInterval(id);
  }, [pollMs, refresh]);

  return { health, rtStatus, torrents, loading, error, refresh };
}
