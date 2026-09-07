import {
  AlertCircle,
  AlertTriangle,
  CheckCircle,
  Download,
  ExternalLink,
  Library,
  Save,
  Search,
} from "lucide-react";
import { type FormEvent, useEffect, useMemo, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  type AnnasDetail,
  type AnnasSearchResult,
  addMagnet,
  annasConfig,
  annasDetail,
  downloadToDepot,
  searchAnnas,
} from "@/lib/api";

export function AnnasSearchPage() {
  const [query, setQuery] = useState("");
  const [contentType, setContentType] = useState("books");
  const [maxResults, setMaxResults] = useState("20");
  const [loading, setLoading] = useState(false);
  const [detailLoading, setDetailLoading] = useState<string | null>(null);
  const [results, setResults] = useState<AnnasSearchResult[]>([]);
  const [detail, setDetail] = useState<AnnasDetail | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [adding, setAdding] = useState<string | null>(null);
  const [addMsg, setAddMsg] = useState<{
    title: string;
    success: boolean;
  } | null>(null);
  const [depotBusy, setDepotBusy] = useState<string | null>(null);
  const [depotMsg, setDepotMsg] = useState<{
    label: string;
    success: boolean;
    detail?: string;
  } | null>(null);
  const [authState, setAuthState] = useState<"checking" | "yes" | "no">(
    "checking",
  );

  useEffect(() => {
    let cancelled = false;
    void (async () => {
      try {
        const cfg = await annasConfig();
        if (!cancelled) setAuthState(cfg.authenticated ? "yes" : "no");
      } catch {
        if (!cancelled) setAuthState("no");
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  async function handleSearch(e?: FormEvent) {
    if (e) e.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    setError(null);
    setAddMsg(null);
    setDetail(null);
    setDetailLoading(null);
    try {
      const res = await searchAnnas(
        query.trim(),
        contentType,
        Number(maxResults) || 20,
      );
      if (res.success && res.results) {
        setResults(
          res.results.filter(
            (r) =>
              !r.error &&
              r.title &&
              !/^(No records|Search performed)/i.test(r.title) &&
              Boolean(r.detail_url),
          ),
        );
      } else {
        setError(res.error || "No results found");
        setResults([]);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Search failed");
      setResults([]);
    } finally {
      setLoading(false);
    }
  }

  async function handleDetail(item: AnnasSearchResult) {
    if (!item.detail_url) return;
    setDetailLoading(item.title);
    setError(null);
    try {
      const res = await annasDetail(item.detail_url);
      if (res.success && res.result) {
        setDetail(res.result);
      } else {
        setDetail(res.result ?? null);
        setError(res.error || res.result?.error || "Could not load detail");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Detail fetch failed");
    } finally {
      setDetailLoading(null);
    }
  }

  async function handleAdd(magnet: string, title: string) {
    if (!magnet) return;
    setAdding(title + magnet);
    setAddMsg(null);
    try {
      const res = await addMagnet(magnet, "books");
      const ok = res.status === "success" || Boolean(res.hash);
      setAddMsg({ title, success: ok });
    } catch {
      setAddMsg({ title, success: false });
    } finally {
      setAdding(null);
    }
  }

  async function handleDepot(url: string, label: string) {
    if (!url) return;
    setDepotBusy(url);
    setDepotMsg(null);
    try {
      const res = await downloadToDepot(url);
      setDepotMsg({
        label,
        success: Boolean(res.success),
        detail: res.success
          ? `Saved ${res.filename} (${(res.size_bytes ?? 0).toLocaleString()} bytes) to depot.`
          : res.error || "Download failed",
      });
    } catch (err) {
      setDepotMsg({
        label,
        success: false,
        detail: err instanceof Error ? err.message : "Download failed",
      });
    } finally {
      setDepotBusy(null);
    }
  }

  const directDownloads = useMemo(
    () => detail?.direct_downloads ?? [],
    [detail],
  );

  return (
    <div className="space-y-6">
      <div>
        <h1 className="flex items-center gap-2 text-2xl font-bold tracking-tight text-slate-100">
          <Library className="h-7 w-7 text-amber-400" />
          Anna&apos;s Archive
        </h1>
        <p className="text-sm text-slate-400">
          Search and download a single book or paper, not bulk datasets.
        </p>
      </div>

      <Card className="border-amber-700/40 bg-amber-950/30">
        <CardHeader className="flex flex-row items-center gap-2 pb-2">
          <AlertTriangle className="h-5 w-5 text-amber-400" />
          <CardTitle className="text-sm font-medium text-amber-200">
            Single-book downloads only - avoid the bulk torrent dumps
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm text-amber-100/80">
          <p>
            Use this page to find{" "}
            <strong className="text-amber-200">one book/paper</strong> and grab
            just that item - via a free Slow mirror (LibGen / Z-Lib / IPFS) or a
            small single-book magnet.
          </p>
          <p>
            <strong className="text-amber-200">Do NOT grab:</strong> bulk
            torrent / dataset archives (5TB to 100TB+). Those are training
            corpora, not something to seed to rTorrent.
          </p>
          <p className="text-xs text-amber-200/70">
            Free beats paid here: a single e-book is a few MB. Skip the paid
            Fast mirrors - a Slow mirror or tiny magnet downloads almost
            instantly. Anna&apos;s Archive now gates the slow downloads behind
            an account (anti-bot); set the session cookie to enable them.
          </p>
        </CardContent>
      </Card>

      {authState === "no" ? (
        <div
          className="rounded-md border border-slate-700 bg-slate-900/40 p-4 text-sm text-slate-400"
          data-testid="annas-auth-hint"
        >
          <span className="font-medium text-slate-300">
            Downloads need a session.
          </span>{" "}
          Register once at{" "}
          <code className="text-xs text-emerald-300/90">annas-archive.is</code>,
          copy the session cookie, and set{" "}
          <code className="text-xs text-emerald-300/90">
            ANNAS_SESSION_COOKIE
          </code>{" "}
          in the backend&apos;s env. Search works without it; download links
          only appear once authenticated.
        </div>
      ) : null}

      <Card className="border-slate-800 bg-slate-900/60 backdrop-blur-xl">
        <CardHeader className="pb-3">
          <CardTitle className="text-sm font-medium text-slate-300">
            Search books / papers
          </CardTitle>
        </CardHeader>
        <CardContent>
          <form
            onSubmit={handleSearch}
            className="flex flex-wrap items-center gap-3"
          >
            <div className="relative flex-1 min-w-[240px]">
              <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-500" />
              <input
                type="text"
                placeholder="Title, author or ISBN (e.g. Dune, Orwell 1984)..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="w-full rounded-md border border-slate-800 bg-slate-950 py-2 pl-9 pr-4 text-sm text-slate-100 placeholder-slate-500 focus:border-amber-500 focus:outline-none"
              />
            </div>

            <select
              value={contentType}
              onChange={(e) => setContentType(e.target.value)}
              className="rounded-md border border-slate-800 bg-slate-950 px-3 py-2 text-sm text-slate-200 focus:border-amber-500 focus:outline-none"
            >
              <option value="books">Books</option>
              <option value="papers">Papers</option>
            </select>

            <select
              value={maxResults}
              onChange={(e) => setMaxResults(e.target.value)}
              className="rounded-md border border-slate-800 bg-slate-950 px-3 py-2 text-sm text-slate-200 focus:border-amber-500 focus:outline-none"
            >
              <option value="10">10 results</option>
              <option value="20">20 results</option>
              <option value="50">50 results</option>
            </select>

            <button
              type="submit"
              disabled={loading || !query.trim()}
              className="flex items-center gap-2 rounded-md bg-amber-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-amber-500 disabled:opacity-50"
            >
              {loading ? "Searching..." : "Search Anna's Archive"}
            </button>
          </form>
        </CardContent>
      </Card>

      {addMsg && (
        <div
          className={`flex items-center gap-2 rounded-md border p-3 text-sm ${
            addMsg.success
              ? "border-green-800/50 bg-green-950/30 text-green-300"
              : "border-red-800/50 bg-red-950/30 text-red-300"
          }`}
        >
          {addMsg.success ? (
            <CheckCircle className="h-4 w-4 text-green-400" />
          ) : (
            <AlertCircle className="h-4 w-4 text-red-400" />
          )}
          <span>
            {addMsg.success
              ? `Dispatched "${addMsg.title}" to rTorrent.`
              : `Failed to add "${addMsg.title}" to rTorrent.`}
          </span>
        </div>
      )}

      {error && (
        <div className="rounded-md border border-red-800/50 bg-red-950/30 p-4 text-sm text-red-400">
          {error}
        </div>
      )}

      <Card className="border-slate-800 bg-slate-900/60 backdrop-blur-xl">
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <CardTitle className="text-sm font-medium text-slate-300">
            Search Results ({results.length})
          </CardTitle>
        </CardHeader>
        <CardContent>
          {results.length === 0 ? (
            <div className="py-12 text-center text-sm text-slate-500">
              {loading
                ? "Fetching from Anna's Archive..."
                : "No search results to display."}
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm text-slate-300">
                <thead className="border-b border-slate-800 text-xs font-semibold uppercase text-slate-400">
                  <tr>
                    <th className="pb-3 pt-2">Title</th>
                    <th className="pb-3 pt-2">Author</th>
                    <th className="pb-3 pt-2">Format</th>
                    <th className="pb-3 pt-2">Size</th>
                    <th className="pb-3 pt-2 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {results.map((item) => (
                    <tr
                      key={item.detail_url ?? item.title}
                      className="hover:bg-slate-800/40"
                    >
                      <td className="py-3 font-medium text-slate-100 max-w-md truncate">
                        {item.title}
                      </td>
                      <td className="py-3 text-slate-400 max-w-[160px] truncate">
                        {item.author || "—"}
                      </td>
                      <td className="py-3 text-xs text-slate-400">
                        {item.format ?? "—"}
                      </td>
                      <td className="py-3 text-xs text-slate-400">
                        {item.size ?? "—"}
                      </td>
                      <td className="py-3 text-right">
                        <button
                          type="button"
                          onClick={() => handleDetail(item)}
                          disabled={detailLoading === item.title}
                          className="inline-flex items-center gap-1.5 rounded bg-amber-600/80 px-3 py-1 text-xs font-medium text-white transition-colors hover:bg-amber-500 disabled:opacity-50"
                        >
                          {detailLoading === item.title
                            ? "Loading..."
                            : "Details"}
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      {detail && (
        <Card className="border-amber-700/40 bg-slate-900/60">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-slate-300">
              {detail.title || "Release detail"}
            </CardTitle>
            {detail.detail_url ? (
              <a
                href={detail.detail_url}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-1.5 rounded border border-slate-700 px-2 py-1 text-xs text-slate-400 hover:bg-slate-800"
              >
                <ExternalLink className="h-3 w-3" />
                Open page
              </a>
            ) : null}
          </CardHeader>
          <CardContent className="text-sm text-slate-400 space-y-3">
            <p>
              Size:{" "}
              <span className="text-slate-200">{detail.size ?? "unknown"}</span>
            </p>
            {directDownloads.length > 0 ? (
              <div>
                <p className="mb-2 text-xs font-semibold uppercase text-slate-500">
                  Direct download to depot (no rTorrent)
                </p>
                <div className="space-y-2">
                  {directDownloads.map((d) => (
                    <div
                      key={d.url}
                      className="flex items-center gap-2 rounded-md border border-slate-800 bg-slate-950/60 p-2"
                    >
                      <span className="flex-1 truncate text-xs text-slate-300">
                        {d.label}
                      </span>
                      <button
                        type="button"
                        onClick={() => handleDepot(d.url, d.label)}
                        disabled={depotBusy === d.url}
                        className="inline-flex shrink-0 items-center gap-1.5 rounded bg-emerald-600/80 px-3 py-1 text-xs font-medium text-white hover:bg-emerald-500 disabled:opacity-50"
                      >
                        <Save className="h-3 w-3" />
                        {depotBusy === d.url ? "Saving..." : "Save to depot"}
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            ) : null}

            {depotMsg && (
              <div
                className={`flex items-start gap-2 rounded-md border p-3 text-xs ${
                  depotMsg.success
                    ? "border-green-800/50 bg-green-950/30 text-green-300"
                    : "border-amber-800/50 bg-amber-950/30 text-amber-300"
                }`}
              >
                {depotMsg.success ? (
                  <CheckCircle className="h-4 w-4 shrink-0 text-green-400" />
                ) : (
                  <AlertTriangle className="h-4 w-4 shrink-0 text-amber-400" />
                )}
                <span>
                  <strong>{depotMsg.label}</strong>:{" "}
                  {depotMsg.success
                    ? depotMsg.detail
                    : `${depotMsg.detail} Some mirrors need a JS unlock (10-60s) or obscura-mcp. Check the opened page for a direct link.`}
                </span>
              </div>
            )}

            {(detail.magnets?.length ?? 0) > 0 ? (
              <div>
                <p className="mb-2 text-xs font-semibold uppercase text-slate-500">
                  Magnets — push to rTorrent ({detail.magnets?.length})
                </p>
                <div className="space-y-2 max-h-64 overflow-auto">
                  {detail.magnets?.map((m) => (
                    <div
                      key={m}
                      className="flex items-center gap-2 rounded-md border border-slate-800 bg-slate-950/60 p-2"
                    >
                      <code className="flex-1 break-all text-[11px] text-emerald-300/90 line-clamp-2">
                        {m}
                      </code>
                      <button
                        type="button"
                        onClick={() => handleAdd(m, detail.title ?? "book")}
                        disabled={adding === (detail.title ?? "book") + m}
                        className="inline-flex shrink-0 items-center gap-1.5 rounded bg-blue-600/80 px-3 py-1 text-xs font-medium text-white hover:bg-blue-500 disabled:opacity-50"
                      >
                        <Download className="h-3 w-3" />
                        {adding === (detail.title ?? "book") + m
                          ? "Adding..."
                          : "Add"}
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <p className="text-slate-500">
                No magnets found — check the site for a .torrent link.
              </p>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}

export default AnnasSearchPage;
