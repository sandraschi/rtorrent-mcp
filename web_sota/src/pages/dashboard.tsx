import {
  Activity,
  ArrowDownToLine,
  Download,
  Link2,
  ListTree,
  RotateCw,
  Search,
  Server,
  Tv,
  Wifi,
  WifiOff,
} from "lucide-react";
import { type FormEvent, useState } from "react";
import { Link } from "react-router-dom";
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

function StatusPill({
  ok,
  label,
  testid,
}: {
  ok: boolean;
  label: string;
  testid?: string;
}) {
  return (
    <span
      data-testid={testid}
      className={`inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-medium ${
        ok
          ? "border-emerald-500/30 bg-emerald-500/10 text-emerald-300"
          : "border-rose-500/30 bg-rose-500/10 text-rose-300"
      }`}
    >
      {ok ? <Wifi className="h-3 w-3" /> : <WifiOff className="h-3 w-3" />}
      {label}
    </span>
  );
}

export function Dashboard() {
  const { health, rtStatus, torrents, loading, error, refresh } =
    useRtorrentBridge(10000);
  const [magnet, setMagnet] = useState("");
  const [magnetBusy, setMagnetBusy] = useState(false);
  const [magnetMsg, setMagnetMsg] = useState<string | null>(null);
  const [retrying, setRetrying] = useState(false);

  const connected = rtStatus?.connected === true;
  const count = torrents?.count ?? torrents?.torrents?.length ?? 0;

  const list = torrents?.torrents ?? [];
  const downloading = list.filter((t) => t.state === 1).length;
  const seeding = list.filter((t) => t.state === 2).length;
  const stopped = list.filter((t) => t.state === 0).length;
  const complete = list.filter((t) => (t.progress ?? 0) >= 100).length;
  const totalSize = list.reduce((a, t) => a + (t.size_bytes || 0), 0);

  async function reconnect() {
    setRetrying(true);
    await refresh();
    setRetrying(false);
  }

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
      {/* Hero */}
      <section className="rounded-2xl border border-emerald-500/20 bg-gradient-to-br from-emerald-950/40 via-slate-950 to-slate-950 p-8">
        <div className="flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
          <div className="max-w-2xl">
            <div className="mb-3 flex flex-wrap items-center gap-2">
              <StatusPill
                ok={Boolean(health?.ok)}
                label={health?.ok ? "Backend up" : "Backend down"}
                testid="status-backend"
              />
              <StatusPill
                ok={connected}
                label={connected ? "rTorrent connected" : "rTorrent offline"}
                testid="status-rtorrent"
              />
            </div>
            <h1 className="text-4xl font-extrabold tracking-tight text-white">
              rTorrent MCP
            </h1>
            <p className="mt-3 text-lg text-slate-400">
              Search, add and manage torrents from one shell — anime, TV &amp;
              movies via the Python bridge, with MCP tools for everything else.
            </p>
            <div className="mt-6 flex flex-wrap gap-3">
              <Link
                to="/nyaa"
                className="inline-flex items-center gap-2 rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-500"
              >
                <Search className="h-4 w-4" />
                Search anime (Nyaa)
              </Link>
              <Link
                to="/bay"
                className="inline-flex items-center gap-2 rounded-lg border border-slate-700 bg-slate-900/60 px-4 py-2 text-sm font-medium text-slate-200 hover:bg-slate-800"
              >
                <Tv className="h-4 w-4" />
                Search TV / movies
              </Link>
              <a
                href="#add-magnet"
                className="inline-flex items-center gap-2 rounded-lg border border-slate-700 bg-slate-900/60 px-4 py-2 text-sm font-medium text-slate-200 hover:bg-slate-800"
              >
                <ArrowDownToLine className="h-4 w-4" />
                Add torrent
              </a>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3 text-center md:grid-cols-1">
            <button
              type="button"
              onClick={() => void reconnect()}
              disabled={retrying}
              className="inline-flex items-center justify-center gap-2 rounded-lg border border-slate-700 bg-slate-900/60 px-4 py-2 text-sm font-medium text-slate-200 hover:bg-slate-800 disabled:opacity-50"
            >
              <RotateCw
                className={`h-4 w-4 ${retrying ? "animate-spin" : ""}`}
              />
              {retrying ? "Reconnecting…" : "Reconnect"}
            </button>
            <div className="rounded-lg border border-slate-800 bg-slate-900/40 px-4 py-3 text-xs text-slate-500">
              MCP HTTP <code className="text-emerald-300/90">/mcp</code>
              <br />
              REST <code className="text-emerald-300/90">/api/*</code>
            </div>
          </div>
        </div>
      </section>

      {/* Host App Status Card — first visible element (HOST_APP_LIFECYCLE §VI) */}
      <Card
        className="border-slate-800 bg-slate-950/50"
        data-testid="host-app-status"
      >
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium text-slate-200">
            Host app — rTorrent (XML-RPC)
          </CardTitle>
          <Activity
            className={`h-4 w-4 ${connected ? "text-emerald-500" : "text-amber-400"}`}
          />
        </CardHeader>
        <CardContent>
          {connected ? (
            <div className="flex flex-wrap items-center gap-4">
              <span className="inline-flex items-center gap-2 text-emerald-300">
                <span className="relative flex h-2.5 w-2.5">
                  <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75" />
                  <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-emerald-500" />
                </span>
                READY
              </span>
              <span className="text-sm text-slate-400">
                {rtStatus?.host}:{rtStatus?.port}
                <span className="text-slate-600"> /RPC2</span>
              </span>
              <span className="text-xs text-slate-500">
                {count} torrents tracked
              </span>
            </div>
          ) : (
            <div>
              <div className="flex items-center gap-2 text-amber-300">
                <span className="inline-flex h-2.5 w-2.5 rounded-full bg-amber-400" />
                UNREACHABLE — rTorrent not answering on{" "}
                {rtStatus?.host ?? "localhost"}:{rtStatus?.port ?? 12224}
              </div>
              {rtStatus?.error ? (
                <p className="mt-2 text-sm text-rose-300">{rtStatus.error}</p>
              ) : (
                <p className="mt-2 text-sm text-slate-400">
                  Start the rTorrent container or run{" "}
                  <code className="text-xs text-emerald-300/90">start.ps1</code>
                  , then retry.
                </p>
              )}
              <button
                type="button"
                onClick={() => void reconnect()}
                disabled={retrying}
                className="mt-4 inline-flex items-center gap-2 rounded-lg border border-amber-700 bg-amber-950/40 px-4 py-2 text-sm font-medium text-amber-200 hover:bg-amber-950/60 disabled:opacity-50"
              >
                <RotateCw
                  className={`h-4 w-4 ${retrying ? "animate-spin" : ""}`}
                />
                {retrying ? "Reconnecting…" : "Retry connection"}
              </button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Backend error banner with reconnect */}
      {error ? (
        <div
          className="flex flex-wrap items-center gap-4 rounded-lg border border-rose-500/40 bg-rose-950/40 px-4 py-3 text-sm text-rose-100"
          data-testid="backend-error-banner"
        >
          <span>
            Bridge unreachable: {error}. Ensure the backend is running on port
            10910.
          </span>
          <button
            type="button"
            onClick={() => void reconnect()}
            disabled={retrying}
            data-testid="reconnect-backend"
            className="inline-flex items-center gap-2 rounded-lg border border-rose-600 bg-rose-900/40 px-3 py-1.5 text-xs font-medium text-rose-100 hover:bg-rose-900/60 disabled:opacity-50"
          >
            <RotateCw
              className={`h-3.5 w-3.5 ${retrying ? "animate-spin" : ""}`}
            />
            {retrying ? "Reconnecting…" : "Reconnect backend"}
          </button>
        </div>
      ) : null}

      {/* KPI cards */}
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

      {/* Derived torrent stats (real data, not fabricated) */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card className="border-slate-800 bg-slate-950/50">
          <CardContent className="pt-4">
            <div className="text-xs uppercase tracking-wider text-slate-500">
              Downloading
            </div>
            <div className="mt-1 text-2xl font-bold text-blue-400">
              {downloading}
            </div>
          </CardContent>
        </Card>
        <Card className="border-slate-800 bg-slate-950/50">
          <CardContent className="pt-4">
            <div className="text-xs uppercase tracking-wider text-slate-500">
              Seeding
            </div>
            <div className="mt-1 text-2xl font-bold text-green-400">
              {seeding}
            </div>
          </CardContent>
        </Card>
        <Card className="border-slate-800 bg-slate-950/50">
          <CardContent className="pt-4">
            <div className="text-xs uppercase tracking-wider text-slate-500">
              Complete
            </div>
            <div className="mt-1 text-2xl font-bold text-emerald-400">
              {complete}
            </div>
          </CardContent>
        </Card>
        <Card className="border-slate-800 bg-slate-950/50">
          <CardContent className="pt-4">
            <div className="text-xs uppercase tracking-wider text-slate-500">
              Stopped / total size
            </div>
            <div className="mt-1 text-2xl font-bold text-slate-300">
              {stopped} / {fmtBytes(totalSize)}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Add magnet */}
      <Card
        className="border-slate-800 bg-slate-950/50"
        data-testid="add-magnet-card"
      >
        <div id="add-magnet">
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
                  className="inline-flex items-center gap-2 rounded-md bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-500 disabled:opacity-50"
                >
                  <Download className="h-4 w-4" />
                  {magnetBusy ? "Adding…" : "Add to rTorrent"}
                </button>
                {magnetMsg ? (
                  <span className="text-sm text-slate-400">{magnetMsg}</span>
                ) : null}
              </div>
            </form>
          </CardContent>
        </div>
      </Card>

      {/* Torrent list */}
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
                {list.slice(0, 12).map((t) => (
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
                {!loading && list.length === 0 ? (
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
