import { useCallback, useEffect, useState } from "react";
import { API_BASE } from "@/lib/api";

export type HealthPayload = {
  ok?: boolean;
  service?: string;
  version?: string;
};

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
    // Each endpoint fails independently: rTorrent (the wrapped host app)
    // being offline must not report our own backend as down too, and vice
    // versa - they're separate failure domains (see docs/ONBOARDING.md).
    const [healthResult, statusResult, torrentsResult] =
      await Promise.allSettled([
        fetch(`${API_BASE}/api/health`).then((r) =>
          r.ok ? r.json() : Promise.reject(new Error(`health ${r.status}`)),
        ),
        fetch(`${API_BASE}/api/rtorrent/status`).then((r) => r.json()),
        fetch(`${API_BASE}/api/rtorrent/torrents`).then((r) => r.json()),
      ]);

    setHealth(healthResult.status === "fulfilled" ? healthResult.value : null);
    setRtStatus(
      statusResult.status === "fulfilled" ? statusResult.value : null,
    );
    setTorrents(
      torrentsResult.status === "fulfilled" ? torrentsResult.value : null,
    );

    if (healthResult.status === "rejected") {
      const reason = healthResult.reason;
      setError(
        reason instanceof Error ? reason.message : "Failed to reach backend",
      );
    } else {
      setError(null);
    }
    setLoading(false);
  }, []);

  useEffect(() => {
    void refresh();
    if (pollMs <= 0) return;
    const id = window.setInterval(() => void refresh(), pollMs);
    return () => window.clearInterval(id);
  }, [pollMs, refresh]);

  return { health, rtStatus, torrents, loading, error, refresh };
}
