import { Box, ExternalLink, Loader2 } from "lucide-react";
import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { API_BASE } from "@/lib/api";

interface FleetApp {
  port: number;
  url: string;
  ok: boolean;
}

const SHORTCUTS = [
  {
    name: "This app (Vite)",
    port: 10911,
    description: "rtorrent-mcp web shell",
  },
  {
    name: "MCP HTTP (same machine)",
    port: 10910,
    description: "Streamable MCP path /mcp",
  },
];

export function Apps() {
  const [live, setLive] = useState<FleetApp[]>([]);
  const [scanning, setScanning] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    fetch(`${API_BASE}/api/fleet/apps`)
      .then((r) => r.json())
      .then((d) => {
        if (cancelled) return;
        setLive(d.apps ?? []);
        setScanning(false);
      })
      .catch(() => {
        if (cancelled) return;
        setError("Backend unreachable — fleet scan skipped.");
        setScanning(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const otherApps = live.filter((a) => a.port !== 10910 && a.port !== 10911);

  return (
    <div className="space-y-6" data-testid="apps-page">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white">
            App Hub
          </h2>
          <p className="text-slate-400">
            {scanning
              ? "Scanning the fleet webapp reservoir…"
              : `${otherApps.length} fleet app${otherApps.length === 1 ? "" : "s"} live on this machine.`}
          </p>
        </div>
        {scanning && <Loader2 className="h-5 w-5 animate-spin text-blue-400" />}
      </div>

      {error && (
        <Card className="border-red-900/60 bg-red-950/30">
          <CardContent className="py-3 text-sm text-red-300">
            {error}
          </CardContent>
        </Card>
      )}

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {SHORTCUTS.map((app) => (
          <Card
            key={app.name}
            className="border-slate-800 bg-slate-950/50 hover:bg-slate-900/50 transition-colors group cursor-pointer"
            onClick={() =>
              window.open(`http://127.0.0.1:${app.port}`, "_blank")
            }
          >
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-200">
                {app.name}
              </CardTitle>
              <Box className="h-4 w-4 text-blue-500 group-hover:scale-110 transition-transform" />
            </CardHeader>
            <CardContent>
              <p className="text-xs text-slate-400 mb-4">{app.description}</p>
              <div className="flex items-center text-xs text-blue-400 font-medium">
                <span>127.0.0.1:{app.port}</span>
                <ExternalLink className="h-3 w-3 ml-1" />
              </div>
            </CardContent>
          </Card>
        ))}

        {otherApps.map((app) => (
          <Card
            key={app.port}
            className="border-slate-800 bg-slate-950/50 hover:bg-slate-900/50 transition-colors group cursor-pointer"
            onClick={() => window.open(app.url, "_blank")}
          >
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-200">
                Fleet webapp :{app.port}
              </CardTitle>
              <Box className="h-4 w-4 text-emerald-500 group-hover:scale-110 transition-transform" />
            </CardHeader>
            <CardContent>
              <p className="text-xs text-slate-400 mb-4">
                Live peer discovered on the webapp reservoir.
              </p>
              <div className="flex items-center text-xs text-emerald-400 font-medium">
                <span>{app.url}</span>
                <ExternalLink className="h-3 w-3 ml-1" />
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {!scanning && otherApps.length === 0 && (
        <Card className="border-slate-800 bg-slate-950/50 border-dashed">
          <CardContent className="py-8 text-center text-sm text-slate-500">
            No other fleet webapps are live right now. Start another MCP webapp
            and re-visit this page to discover it.
          </CardContent>
        </Card>
      )}
    </div>
  );
}
