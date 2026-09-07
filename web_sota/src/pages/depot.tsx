import { Archive, File as FileIcon, Folder, RefreshCw } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { type DepotEntry, listDepot } from "@/lib/api";

function fmtBytes(n: number | null) {
  if (n === null || !Number.isFinite(n) || n < 0) return "—";
  const u = ["B", "KB", "MB", "GB", "TB"];
  let v = n;
  let i = 0;
  while (v >= 1024 && i < u.length - 1) {
    v /= 1024;
    i++;
  }
  return `${v.toFixed(i === 0 ? 0 : 1)} ${u[i]}`;
}

function fmtDate(iso: string) {
  try {
    const d = new Date(iso);
    return d.toLocaleString();
  } catch {
    return iso;
  }
}

export function Depot() {
  const [entries, setEntries] = useState<DepotEntry[]>([]);
  const [depotPath, setDepotPath] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await listDepot();
      if (res.success) {
        setEntries(res.entries ?? []);
        setDepotPath(res.depot_path ?? null);
      } else {
        setEntries([]);
        setDepotPath(res.depot_path ?? null);
        setError(res.error || "Failed to load depot");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load depot");
      setEntries([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const totalFiles = entries.filter((e) => e.type === "file").length;
  const totalSize = entries.reduce<number>(
    (a, e) => a + (e.size_bytes ?? 0),
    0,
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="flex items-center gap-2 text-2xl font-bold tracking-tight text-slate-100">
            <Archive className="h-7 w-7 text-sky-400" />
            Download Depot
          </h1>
          <p className="text-sm text-slate-400">
            Completed media deposited in the output folder
            {depotPath ? (
              <>
                {" "}
                (
                <code className="text-xs text-emerald-300/90">{depotPath}</code>
                )
              </>
            ) : (
              ""
            )}
            .
          </p>
        </div>
        <button
          type="button"
          onClick={() => void load()}
          disabled={loading}
          className="inline-flex items-center gap-2 rounded-md border border-slate-700 bg-slate-900 px-3 py-1.5 text-sm text-slate-200 hover:bg-slate-800 disabled:opacity-50"
        >
          <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
          Refresh
        </button>
      </div>

      {error ? (
        <div className="rounded-md border border-amber-800/50 bg-amber-950/30 p-4 text-sm text-amber-300">
          {error}
        </div>
      ) : null}

      <div className="grid gap-4 md:grid-cols-3">
        <Card className="border-slate-800 bg-slate-950/50">
          <CardContent className="pt-4">
            <div className="text-xs uppercase tracking-wider text-slate-500">
              Total items
            </div>
            <div className="mt-1 text-2xl font-bold text-white">
              {loading ? "…" : entries.length}
            </div>
          </CardContent>
        </Card>
        <Card className="border-slate-800 bg-slate-950/50">
          <CardContent className="pt-4">
            <div className="text-xs uppercase tracking-wider text-slate-500">
              Files
            </div>
            <div className="mt-1 text-2xl font-bold text-sky-400">
              {loading ? "…" : totalFiles}
            </div>
          </CardContent>
        </Card>
        <Card className="border-slate-800 bg-slate-950/50">
          <CardContent className="pt-4">
            <div className="text-xs uppercase tracking-wider text-slate-500">
              Total size
            </div>
            <div className="mt-1 text-2xl font-bold text-emerald-400">
              {loading ? "…" : fmtBytes(totalSize)}
            </div>
          </CardContent>
        </Card>
      </div>

      <Card className="border-slate-800 bg-slate-950/50">
        <CardHeader>
          <CardTitle className="text-white">Depot contents</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="max-h-[420px] overflow-auto font-mono text-xs border border-slate-800 rounded-md bg-slate-900/50">
            <table className="w-full text-left text-slate-300">
              <thead className="sticky top-0 bg-slate-900 text-slate-500">
                <tr>
                  <th className="p-2">Name</th>
                  <th className="p-2">Type</th>
                  <th className="p-2">Size</th>
                  <th className="p-2">Modified</th>
                </tr>
              </thead>
              <tbody>
                {entries.map((e) => (
                  <tr
                    key={e.path}
                    className="border-t border-slate-800/80 hover:bg-slate-900/40"
                  >
                    <td className="p-2 break-all flex items-center gap-2">
                      {e.type === "dir" ? (
                        <Folder className="h-3.5 w-3.5 text-amber-400 shrink-0" />
                      ) : (
                        <FileIcon className="h-3.5 w-3.5 text-slate-500 shrink-0" />
                      )}
                      {e.name}
                    </td>
                    <td className="p-2 whitespace-nowrap">
                      {e.type === "dir" ? (
                        <span className="rounded bg-amber-950/40 border border-amber-800/40 px-2 py-0.5 text-[10px] text-amber-300">
                          dir
                        </span>
                      ) : (
                        <span className="rounded bg-slate-800 px-2 py-0.5 text-[10px] text-slate-400">
                          file
                        </span>
                      )}
                    </td>
                    <td className="p-2 whitespace-nowrap">
                      {fmtBytes(e.size_bytes)}
                    </td>
                    <td className="p-2 whitespace-nowrap text-slate-500">
                      {fmtDate(e.modified)}
                    </td>
                  </tr>
                ))}
                {!loading && entries.length === 0 ? (
                  <tr>
                    <td colSpan={4} className="p-4 text-slate-500">
                      No deposited media yet.
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

export default Depot;
