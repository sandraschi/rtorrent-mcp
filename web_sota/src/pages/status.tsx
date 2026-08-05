import { HardDrive, Link2, Server } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useRtorrentBridge } from "@/hooks/useRtorrentBridge";

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

export function Status() {
  const { health, rtStatus, torrents, loading, error } =
    useRtorrentBridge(5000);
  const connected = rtStatus?.connected === true;
  const list = torrents?.torrents ?? [];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white">
            Status
          </h2>
          <p className="text-slate-400">
            rTorrent XML-RPC via the same process as MCP. Throttle / upload
            totals are not exposed here yet; this page lists{" "}
            <strong className="text-slate-200">live torrent rows</strong> from{" "}
            <code className="text-xs">/api/rtorrent/torrents</code>.
          </p>
        </div>
      </div>

      {error ? (
        <div className="rounded-lg border border-rose-500/40 bg-rose-950/40 px-4 py-3 text-sm text-rose-100">
          {error}
        </div>
      ) : null}

      <div className="grid gap-4 md:grid-cols-3">
        <Card className="border-slate-800 bg-slate-950/50">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-200">
              Bridge
            </CardTitle>
            <Server className="h-4 w-4 text-emerald-500" />
          </CardHeader>
          <CardContent>
            <div className="text-xl font-bold text-white">
              {loading ? "…" : health?.ok ? "healthy" : "—"}
            </div>
            <p className="text-xs text-slate-500">
              rtorrent-mcp {health?.version ?? ""}
            </p>
          </CardContent>
        </Card>
        <Card className="border-slate-800 bg-slate-950/50">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-200">
              rTorrent
            </CardTitle>
            <Link2
              className={`h-4 w-4 ${connected ? "text-emerald-500" : "text-rose-400"}`}
            />
          </CardHeader>
          <CardContent>
            <div className="text-xl font-bold text-white">
              {loading ? "…" : connected ? "connected" : "offline"}
            </div>
            <p className="text-xs text-slate-500">
              {rtStatus?.host}:{rtStatus?.port}/RPC2
            </p>
          </CardContent>
        </Card>
        <Card className="border-slate-800 bg-slate-950/50">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-200">
              Torrents
            </CardTitle>
            <HardDrive className="h-4 w-4 text-slate-400" />
          </CardHeader>
          <CardContent>
            <div className="text-xl font-bold text-white">
              {loading ? "…" : list.length}
            </div>
            <p className="text-xs text-slate-500">in session</p>
          </CardContent>
        </Card>
      </div>

      <Card className="border-slate-800 bg-slate-950/50">
        <CardHeader>
          <CardTitle className="text-white">All torrents</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="max-h-[480px] overflow-auto rounded-md border border-slate-800">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="sticky top-0 bg-slate-900 text-xs uppercase text-slate-500">
                <tr>
                  <th className="p-3">Name</th>
                  <th className="p-3">State</th>
                  <th className="p-3">Progress</th>
                  <th className="p-3">Done</th>
                  <th className="p-3">Size</th>
                  <th className="p-3 font-mono text-[10px]">Hash</th>
                </tr>
              </thead>
              <tbody>
                {list.map((t) => (
                  <tr key={t.hash} className="border-t border-slate-800/80">
                    <td className="p-3 align-top break-all">{t.name}</td>
                    <td className="p-3 whitespace-nowrap">
                      <span className={STATE_LABELS[t.state]?.[1] ?? ""}>
                        {torrentStateLabel(t.state)}
                      </span>
                    </td>
                    <td className="p-3 whitespace-nowrap">
                      {t.progress?.toFixed?.(1) ?? "—"}%
                    </td>
                    <td className="p-3 whitespace-nowrap">
                      {fmtBytes(t.completed_bytes)}
                    </td>
                    <td className="p-3 whitespace-nowrap">
                      {fmtBytes(t.size_bytes)}
                    </td>
                    <td className="p-3 font-mono text-[10px] text-slate-500 break-all">
                      {t.hash}
                    </td>
                  </tr>
                ))}
                {!loading && list.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="p-6 text-center text-slate-500">
                      No torrents or cannot reach rTorrent. Check .env
                      RTORRENT_HOST / RTORRENT_PORT.
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
