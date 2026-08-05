import { Activity, Link2, ListTree, Server } from "lucide-react";
import { type FormEvent, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useRtorrentBridge } from "@/hooks/useRtorrentBridge";
import { API_BASE } from "@/lib/api";

function fmtBytes(n: number) {
  if (!Number.isFinite(n) || n < 0) return "—";
  const u = ["B", "KB", "MB", "GB", "TB"];
  let v = n;
  let i = 0;
  while (v >= 1024 && i < u.length - 1) {
    v /= 1024;
    i++;
  }
  return `${v.toFixed(i === 0 ? 0 : 1)} ${u[i]}`;
}

const STATE_LABELS: Record<number, [string, string]> = {
  0: ["stopped", "text-red-400"],
  1: ["downloading", "text-blue-400"],
  2: ["seeding", "text-green-400"],
  3: ["hashing", "text-yellow-400"],
};

function torrentStateLabel(state: number | undefined): string {
  const entry = STATE_LABELS[state ?? -1];
  if (!entry) return "—";
  return entry[0];
}

export function Dashboard() {
  const { health, rtStatus, torrents, loading, error, refresh } =
    useRtorrentBridge(10000);
  const [magnet, setMagnet] = useState("");
  const [magnetBusy, setMagnetBusy] = useState(false);
  const [magnetMsg, setMagnetMsg] = useState<string | null>(null);

  const connected = rtStatus?.connected === true;
  const count = torrents?.count ?? torrents?.torrents?.length ?? 0;

  async function submitMagnet(e: FormEvent) {
    e.preventDefault();
    setMagnetMsg(null);
    const m = magnet.trim();
    if (!m.startsWith("magnet:")) {
      setMagnetMsg("Paste a magnet URI (starts with magnet:?)");
      return;
    }
    setMagnetBusy(true);
    try {
      const r = await fetch(`${API_BASE}/api/rtorrent/magnet`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ magnet: m, category: "anime" }),
      });
      const j = await r.json();
      if (r.ok && (j.status === "success" || j.hash)) {
        setMagnetMsg(`Added: ${j.hash ?? "ok"}`);
        setMagnet("");
        void refresh();
      } else {
        setMagnetMsg(j.error || j.message || `HTTP ${r.status}`);
      }
    } catch (err) {
      setMagnetMsg(err instanceof Error ? err.message : "Request failed");
    } finally {
      setMagnetBusy(false);
    }
  }

  return (
    <div className="space-y-6" data-testid="dashboard">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white">
            Overview
          </h2>
          <p className="text-slate-400">
            Live data from the Python bridge:{" "}
            <code className="text-xs text-emerald-300/90">/api/*</code> on the
            same host as MCP (see{" "}
            <code className="text-xs">web_sota/start.ps1</code>).
          </p>
        </div>
        <button
          type="button"
          onClick={() => void refresh()}
          className="rounded-md border border-slate-700 bg-slate-900 px-3 py-1.5 text-sm text-slate-200 hover:bg-slate-800"
        >
          Refresh
        </button>
      </div>

      {error ? (
        <div className="rounded-lg border border-rose-500/40 bg-rose-950/40 px-4 py-3 text-sm text-rose-100">
          Bridge unreachable: {error}. Start backend (port 10910) and ensure
          Vite proxies <code>/api</code>.
        </div>
      ) : null}

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card
          className="border-slate-800 bg-slate-950/50"
          data-testid="kpi-api"
        >
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-200">
              API
            </CardTitle>
            <Server className="h-4 w-4 text-emerald-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">
              {loading ? "…" : health?.ok ? "OK" : "—"}
            </div>
            <p className="text-xs text-slate-500">v{health?.version ?? "—"}</p>
          </CardContent>
        </Card>

        <Card
          className="border-slate-800 bg-slate-950/50"
          data-testid="kpi-rtorrent"
        >
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-200">
              rTorrent RPC
            </CardTitle>
            <Activity
              className={`h-4 w-4 ${connected ? "text-emerald-500" : "text-rose-400"}`}
            />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">
              {loading ? "…" : connected ? "Up" : "Down"}
            </div>
            <p className="text-xs text-slate-500">
              {rtStatus?.host}:{rtStatus?.port}
              {rtStatus?.error ? ` — ${rtStatus.error}` : ""}
            </p>
          </CardContent>
        </Card>

        <Card
          className="border-slate-800 bg-slate-950/50"
          data-testid="kpi-torrents"
        >
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-200">
              Torrents
            </CardTitle>
            <ListTree className="h-4 w-4 text-blue-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">
              {loading ? "…" : count}
            </div>
            <p className="text-xs text-slate-500">from download_list</p>
          </CardContent>
        </Card>

        <Card
          className="border-slate-800 bg-slate-950/50"
          data-testid="kpi-mcp"
        >
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-200">
              MCP
            </CardTitle>
            <Link2 className="h-4 w-4 text-purple-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">/mcp</div>
            <p className="text-xs text-slate-500">
              Agents use streamable HTTP here
            </p>
          </CardContent>
        </Card>
      </div>

      <Card className="border-slate-800 bg-slate-950/50">
        <CardHeader>
          <CardTitle className="text-white">Add magnet (XML-RPC)</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={submitMagnet} className="space-y-3">
            <textarea
              value={magnet}
              onChange={(e) => setMagnet(e.target.value)}
              placeholder="magnet:?xt=urn:btih:…"
              rows={3}
              className="w-full rounded-md border border-slate-700 bg-slate-900/80 p-3 font-mono text-xs text-slate-200"
            />
            <div className="flex items-center gap-3">
              <button
                type="submit"
                disabled={magnetBusy}
                className="rounded-md bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-500 disabled:opacity-50"
              >
                {magnetBusy ? "Adding…" : "Add to rTorrent"}
              </button>
              {magnetMsg ? (
                <span className="text-sm text-slate-400">{magnetMsg}</span>
              ) : null}
            </div>
          </form>
        </CardContent>
      </Card>

      <Card className="border-slate-800 bg-slate-950/50">
        <CardHeader>
          <CardTitle className="text-white">Torrent list (first 12)</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="max-h-[320px] overflow-auto font-mono text-xs border border-slate-800 rounded-md bg-slate-900/50">
            <table className="w-full text-left text-slate-300">
              <thead className="sticky top-0 bg-slate-900 text-slate-500">
                <tr>
                  <th className="p-2">Name</th>
                  <th className="p-2">State</th>
                  <th className="p-2">Progress</th>
                  <th className="p-2">Size</th>
                </tr>
              </thead>
              <tbody>
                {(torrents?.torrents ?? []).slice(0, 12).map((t) => (
                  <tr key={t.hash} className="border-t border-slate-800/80">
                    <td className="p-2 align-top break-all">{t.name}</td>
                    <td className="p-2 whitespace-nowrap">
                      <span className={STATE_LABELS[t.state]?.[1] ?? ""}>
                        {torrentStateLabel(t.state)}
                      </span>
                    </td>
                    <td className="p-2 whitespace-nowrap">
                      {t.progress?.toFixed?.(1) ?? "—"}%
                    </td>
                    <td className="p-2 whitespace-nowrap">
                      {fmtBytes(t.size_bytes)}
                    </td>
                  </tr>
                ))}
                {!loading && (torrents?.torrents?.length ?? 0) === 0 ? (
                  <tr>
                    <td colSpan={4} className="p-4 text-slate-500">
                      No torrents (or rTorrent unreachable).
                    </td>
                  </tr>
                ) : null}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
