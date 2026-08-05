import { useEffect, useState } from "react";
import { API_BASE } from "@/lib/api";

export type McpBackendStatus = "checking" | "reachable" | "unreachable";

const BACKOFF_MS = [1000, 2000, 4000, 8000, 16000];

/**
 * Backend connection status: prefers the REST health endpoint, falls back to
 * GET /mcp, and listens for the Tauri "backend-status" event when running
 * inside the native shell (NSIS WebView). Uses exponential backoff polling.
 */
export function useMcpBackendStatus(): McpBackendStatus {
  const [status, setStatus] = useState<McpBackendStatus>("checking");

  useEffect(() => {
    let cancelled = false;
    let attempt = 0;

    const check = async (): Promise<boolean> => {
      try {
        const r = await fetch(`${API_BASE}/api/health`, { method: "GET" });
        if (r.ok) return true;
      } catch {
        /* fall through to /mcp probe */
      }
      try {
        const r = await fetch("/mcp", { method: "GET" });
        return r.ok || r.status === 405;
      } catch {
        return false;
      }
    };

    const poll = async (): Promise<void> => {
      if (cancelled) return;
      const ok = await check();
      if (cancelled) return;
      setStatus(ok ? "reachable" : "unreachable");
      if (!ok) {
        const delay = BACKOFF_MS[Math.min(attempt, BACKOFF_MS.length - 1)];
        attempt += 1;
        setTimeout(poll, delay);
      } else {
        attempt = 0;
        setTimeout(poll, 10000);
      }
    };

    void poll();

    let unlisten: (() => void) | undefined;
    (async () => {
      try {
        const { listen } = await import("@tauri-apps/api/event");
        unlisten = await listen<string>("backend-status", (event) => {
          if (cancelled) return;
          if (event.payload === "ready") {
            setStatus("reachable");
          } else if (
            typeof event.payload === "string" &&
            event.payload.startsWith("error:")
          ) {
            setStatus("unreachable");
          }
        });
      } catch {
        // Not inside Tauri — HTTP polling handles it
      }
    })();

    return () => {
      cancelled = true;
      if (unlisten) unlisten();
    };
  }, []);

  return status;
}
