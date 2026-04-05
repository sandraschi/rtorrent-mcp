import { useEffect, useState } from "react";

export type McpBackendStatus = "checking" | "reachable" | "unreachable";

/**
 * Prefer the REST health endpoint (same process as MCP); fall back to GET /mcp.
 */
export function useMcpBackendStatus(): McpBackendStatus {
  const [status, setStatus] = useState<McpBackendStatus>("checking");

  useEffect(() => {
    let cancelled = false;
    fetch("/api/health", { method: "GET" })
      .then((r) => {
        if (!cancelled) setStatus(r.ok ? "reachable" : "unreachable");
      })
      .catch(() => {
        fetch("/mcp", { method: "GET" })
          .then(() => {
            if (!cancelled) setStatus("reachable");
          })
          .catch(() => {
            if (!cancelled) setStatus("unreachable");
          });
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return status;
}
