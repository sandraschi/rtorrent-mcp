import { useState, type FormEvent } from "react";
import { Download, Tv, Search, Sparkles, CheckCircle, AlertCircle } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { addMagnet, searchPirateBay, type PirateBaySearchResult } from "@/lib/api";

export function PirateBaySearchPage() {
  const [query, setQuery] = useState("");
  const [resolution, setResolution] = useState("1080p");
  const [group, setGroup] = useState("MeGusta");
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<PirateBaySearchResult[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [addingTitle, setAddingTitle] = useState<string | null>(null);
  const [addMsg, setAddMsg] = useState<{ title: string; success: boolean } | null>(null);

  async function handleSearch(e?: FormEvent) {
    if (e) e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    setAddMsg(null);

    try {
      const res = await searchPirateBay(query.trim(), resolution, group);
      if (res.success && res.results) {
        setResults(res.results);
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

  async function handleAdd(item: PirateBaySearchResult) {
    if (!item.magnet) return;
    setAddingTitle(item.title);
    setAddMsg(null);

    try {
      const res = await addMagnet(item.magnet, "tv");
      if (res.status === "success" || res.hash) {
        setAddMsg({ title: item.title, success: true });
      } else {
        setAddMsg({ title: item.title, success: false });
      }
    } catch {
      setAddMsg({ title: item.title, success: false });
    } finally {
      setAddingTitle(null);
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="flex items-center gap-2 text-2xl font-bold tracking-tight text-slate-100">
            <Tv className="h-7 w-7 text-purple-400" />
            The Pirate Bay TV & Movie Search
          </h1>
          <p className="text-sm text-slate-400">
            Search TV series and movies with MeGusta release group optimization.
          </p>
        </div>
      </div>

      <Card className="border-slate-800 bg-slate-900/60 backdrop-blur-xl">
        <CardHeader className="pb-3">
          <CardTitle className="text-sm font-medium text-slate-300">
            Search Filters & Options
          </CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSearch} className="flex flex-wrap items-center gap-3">
            <div className="relative flex-1 min-w-[240px]">
              <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-500" />
              <input
                type="text"
                placeholder="Search TV show or movie (e.g. South Park S28E03, Severance)..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="w-full rounded-md border border-slate-800 bg-slate-950 py-2 pl-9 pr-4 text-sm text-slate-100 placeholder-slate-500 focus:border-purple-500 focus:outline-none"
              />
            </div>

            <select
              value={resolution}
              onChange={(e) => setResolution(e.target.value)}
              className="rounded-md border border-slate-800 bg-slate-950 px-3 py-2 text-sm text-slate-200 focus:border-purple-500 focus:outline-none"
            >
              <option value="1080p">1080p Quality</option>
              <option value="720p">720p Quality</option>
              <option value="4K">4K UHD</option>
            </select>

            <select
              value={group}
              onChange={(e) => setGroup(e.target.value)}
              className="rounded-md border border-slate-800 bg-slate-950 px-3 py-2 text-sm text-slate-200 focus:border-purple-500 focus:outline-none"
            >
              <option value="MeGusta">MeGusta (x265 TV)</option>
              <option value="RARBG">RARBG</option>
              <option value="EZTV">EZTV</option>
            </select>

            <button
              type="submit"
              disabled={loading || !query.trim()}
              className="flex items-center gap-2 rounded-md bg-purple-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-purple-500 disabled:opacity-50"
            >
              {loading ? "Searching..." : "Search Pirate Bay"}
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
              ? `Successfully added "${addMsg.title}" to rTorrent!`
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
              {loading ? "Fetching releases from The Pirate Bay..." : "No search results to display."}
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm text-slate-300">
                <thead className="border-b border-slate-800 text-xs font-semibold uppercase text-slate-400">
                  <tr>
                    <th className="pb-3 pt-2">Torrent Title</th>
                    <th className="pb-3 pt-2">Episode</th>
                    <th className="pb-3 pt-2">Group</th>
                    <th className="pb-3 pt-2">Score</th>
                    <th className="pb-3 pt-2">Size</th>
                    <th className="pb-3 pt-2">Seeds</th>
                    <th className="pb-3 pt-2 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {results.map((item, idx) => (
                    <tr key={idx} className="hover:bg-slate-800/40">
                      <td className="py-3 font-medium text-slate-100 max-w-md truncate">
                        {item.title}
                      </td>
                      <td className="py-3">
                        {item.episode_info?.episode_string ? (
                          <span className="rounded bg-purple-950/60 px-2 py-0.5 text-xs text-purple-300 border border-purple-800/50 font-mono">
                            {item.episode_info.episode_string}
                          </span>
                        ) : (
                          <span className="text-xs text-slate-500">—</span>
                        )}
                      </td>
                      <td className="py-3">
                        <span className="rounded bg-slate-800 px-2 py-0.5 text-xs text-slate-300 border border-slate-700">
                          {item.release_group || "MeGusta"}
                        </span>
                      </td>
                      <td className="py-3">
                        <span className="flex items-center gap-1 text-xs font-semibold text-emerald-400">
                          <Sparkles className="h-3 w-3" />
                          {item.quality_score}
                        </span>
                      </td>
                      <td className="py-3 text-slate-400 text-xs">{item.size}</td>
                      <td className="py-3 text-xs font-medium text-green-400">
                        {item.seeders}
                      </td>
                      <td className="py-3 text-right">
                        <button
                          type="button"
                          onClick={() => handleAdd(item)}
                          disabled={addingTitle === item.title || !item.magnet}
                          className="inline-flex items-center gap-1.5 rounded bg-purple-600/80 px-3 py-1 text-xs font-medium text-white transition-colors hover:bg-purple-500 disabled:opacity-50"
                        >
                          <Download className="h-3.5 w-3.5" />
                          {addingTitle === item.title ? "Adding..." : "Add"}
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
    </div>
  );
}

export default PirateBaySearchPage;
