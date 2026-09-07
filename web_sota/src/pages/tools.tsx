import { Download, Pause, Play, Wrench } from "lucide-react";
import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { normalizeFilename } from "@/lib/api";

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

      <FilenameNormalizerTester />
    </div>
  );
}

function FilenameNormalizerTester() {
  const [inputName, setInputName] = useState(
    "[SubsPlease] Boku no Hero Academia - 139 (1080p) [C5819381].mkv",
  );
  const [category, setCategory] = useState("anime");
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  async function handleTest() {
    if (!inputName.trim()) return;
    setLoading(true);
    try {
      const res = await normalizeFilename(inputName.trim(), category);
      if (res.success && res.normalized) {
        setResult(res.normalized);
      }
    } catch {
      setResult(null);
    } finally {
      setLoading(false);
    }
  }

  return (
    <Card className="border-slate-800 bg-slate-950/50">
      <CardHeader>
        <CardTitle className="text-white flex items-center gap-2 text-sm font-medium">
          <Wrench className="h-4 w-4 text-blue-400" />
          Filename Normalizer & Plex Path Tester
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex flex-wrap items-center gap-3">
          <input
            type="text"
            value={inputName}
            onChange={(e) => setInputName(e.target.value)}
            placeholder="Paste raw torrent filename..."
            className="flex-1 min-w-[280px] rounded-md border border-slate-800 bg-slate-900 px-3 py-2 text-sm text-slate-100 placeholder-slate-500 focus:border-blue-500 focus:outline-none"
          />
          <select
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            className="rounded-md border border-slate-800 bg-slate-900 px-3 py-2 text-sm text-slate-200 focus:border-blue-500 focus:outline-none"
          >
            <option value="anime">Anime</option>
            <option value="tv">TV Shows</option>
            <option value="movies">Movies</option>
          </select>
          <button
            type="button"
            onClick={handleTest}
            disabled={loading}
            className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-blue-500 disabled:opacity-50"
          >
            {loading ? "Normalizing..." : "Test Normalizer"}
          </button>
        </div>

        {result && (
          <div className="rounded-md border border-slate-800 bg-slate-900/80 p-4 space-y-2 text-xs font-mono">
            <div className="text-slate-400">
              <span className="text-slate-500">Normalized File:</span>{" "}
              <span className="text-green-400 font-semibold">
                {result.normalized_filename}
              </span>
            </div>
            <div className="text-slate-400">
              <span className="text-slate-500">Plex Target Path:</span>{" "}
              <span className="text-blue-300">{result.relative_plex_path}</span>
            </div>
            <div className="text-slate-400">
              <span className="text-slate-500">Extracted Title:</span>{" "}
              <span className="text-slate-200">{result.title}</span>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
