import { Download, Pause, Play, Wrench } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const PORTMANTEAU = [
  {
    name: "torrent_management",
    desc: "Torrent add/list/pause/resume/delete, post-processing hooks",
  },
  { name: "search_management", desc: "Nyaa, mirrors, metadata search actions" },
  { name: "nlp_management", desc: "Natural language helpers" },
  { name: "legal_management", desc: "Austrian compliance / risk messaging" },
  { name: "system_management", desc: "Help, status, health, info" },
  { name: "workflow_management", desc: "Multi-step download workflows" },
];

export function Tools() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white">
            MCP tools (reference)
          </h2>
          <p className="text-slate-400">
            Portmanteau tools exposed by the server — names match the MCP, not
            this UI.
          </p>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {PORTMANTEAU.slice(0, 3).map((t) => (
          <Card key={t.name} className="border-slate-800 bg-slate-950/50">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-200 font-mono">
                {t.name}
              </CardTitle>
              <Play className="h-4 w-4 text-emerald-500" />
            </CardHeader>
            <CardContent>
              <p className="text-xs text-slate-400">{t.desc}</p>
            </CardContent>
          </Card>
        ))}
        {PORTMANTEAU.slice(3).map((t) => (
          <Card key={t.name} className="border-slate-800 bg-slate-950/50">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-200 font-mono">
                {t.name}
              </CardTitle>
              {t.name.includes("workflow") ? (
                <Pause className="h-4 w-4 text-purple-500" />
              ) : (
                <Download className="h-4 w-4 text-blue-500" />
              )}
            </CardHeader>
            <CardContent>
              <p className="text-xs text-slate-400">{t.desc}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card className="border-slate-800 bg-slate-950/50">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Wrench className="h-4 w-4 text-slate-400" />
            Invoking tools
          </CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-slate-400">
          Call these from your MCP client (Cursor, Claude Desktop, etc.). This
          page is documentation layout only — it does not invoke Python.
        </CardContent>
      </Card>
    </div>
  );
}
