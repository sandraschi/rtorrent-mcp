/**
 * Explains how the SPA relates to MCP vs the new REST bridge.
 */
export function ShellHonestyBanner() {
  return (
    <div
      className="rounded-lg border border-emerald-500/25 bg-emerald-950/30 px-4 py-3 text-sm text-emerald-100/90"
      role="status"
    >
      <p className="font-medium text-emerald-200/95">
        Two ways to control the same server
      </p>
      <p className="mt-1 text-emerald-100/85">
        <strong className="text-emerald-100">MCP</strong> (Cursor / Claude):
        streamable HTTP on{" "}
        <code className="rounded bg-slate-900/80 px-1 py-0.5 text-xs">
          /mcp
        </code>
        . <strong className="text-emerald-100">This UI</strong> uses the REST
        bridge{" "}
        <code className="rounded bg-slate-900/80 px-1 py-0.5 text-xs">
          /api/*
        </code>{" "}
        served by the same uvicorn process — live rTorrent list, status, and
        magnet add. Advanced workflows remain in MCP tools.
      </p>
    </div>
  );
}
