import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Box, ExternalLink } from "lucide-react";

/** Optional bookmarks only — not scanned or discovered at runtime */
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
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white">
            Local shortcuts
          </h2>
          <p className="text-slate-400">
            Manual links — <strong className="text-amber-200/90">no</strong>{" "}
            fleet auto-discovery.
          </p>
        </div>
      </div>

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
      </div>

      <Card className="border-slate-800 bg-slate-950/50 border-dashed">
        <CardContent className="py-8 text-center text-sm text-slate-500">
          Add other MCP webapps to this list by editing{" "}
          <code className="text-xs text-slate-400">apps.tsx</code> — nothing
          polls the network.
        </CardContent>
      </Card>
    </div>
  );
}
