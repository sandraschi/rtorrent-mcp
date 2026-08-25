import { useState, type FormEvent } from "react";
import { BookOpen, Search, Download, Sparkles, ExternalLink, ShieldCheck, HeartHandshake } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { addMagnet, searchGutenberg, type GutenbergSearchResult } from "@/lib/api";

export function GutenbergSearchPage() {
  const [query, setQuery] = useState("");
  const [topic, setTopic] = useState("");
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<GutenbergSearchResult[]>([]);
  const [searched, setSearched] = useState(false);
  const [dispatchStatus, setDispatchStatus] = useState<Record<string, string>>({});

  const handleSearch = async (e: FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setSearched(true);
    try {
      const res = await searchGutenberg(query.trim(), topic.trim() || undefined);
      if (res.success) {
        setResults(res.results || []);
      } else {
        setResults([]);
      }
    } catch {
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const handleDispatchEPUB = async (book: GutenbergSearchResult) => {
    const key = `book-${book.id}`;
    setDispatchStatus((prev) => ({ ...prev, [key]: "dispatching" }));
    try {
      const res = await addMagnet(book.download_url, "ebooks");
      if (res.status === "success" || res.status === "ok") {
        setDispatchStatus((prev) => ({ ...prev, [key]: "success" }));
      } else {
        setDispatchStatus((prev) => ({ ...prev, [key]: `error: ${res.error || "Failed"}` }));
      }
    } catch (err: any) {
      setDispatchStatus((prev) => ({ ...prev, [key]: `error: ${err.message || "Failed"}` }));
    }
  };

  return (
    <div className="space-y-6 max-w-6xl">
      <div>
        <div className="flex items-center gap-3">
          <BookOpen className="h-7 w-7 text-amber-400" />
          <h2 className="text-2xl font-bold tracking-tight text-white">
            Project Gutenberg E-Book Search
          </h2>
        </div>
        <p className="text-slate-400 mt-1">
          70,000+ free public domain e-books (ideal for pre-1900 classics like Austen, Dickens, Wilde, and Conan Doyle). 100% legal, DRM-free.
        </p>
      </div>

      {/* Search Card */}
      <Card className="border-slate-800 bg-slate-950/50">
        <CardHeader>
          <CardTitle className="text-white text-lg flex items-center gap-2">
            <Search className="h-5 w-5 text-amber-400" /> Search Gutenberg Public Domain Books
          </CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSearch} className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div className="sm:col-span-2">
                <label htmlFor="search-title-author" className="text-xs text-slate-400 block mb-1">
                  Title, Author, or Keyword
                </label>
                <input
                  id="search-title-author"
                  type="text"
                  placeholder="e.g. Pride and Prejudice, Sherlock Holmes, Mark Twain..."
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-800 rounded-md px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-amber-500"
                />
              </div>

              <div>
                <label htmlFor="search-topic" className="text-xs text-slate-400 block mb-1">
                  Topic / Subject (Optional)
                </label>
                <input
                  id="search-topic"
                  type="text"
                  placeholder="e.g. Fiction, History, Science..."
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-800 rounded-md px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-amber-500"
                />
              </div>
            </div>

            <div className="flex justify-end">
              <button
                type="submit"
                disabled={loading || !query.trim()}
                className="flex items-center gap-2 bg-amber-600 hover:bg-amber-500 disabled:opacity-50 text-white text-sm font-medium px-5 py-2 rounded-md transition-colors"
              >
                {loading ? (
                  <Sparkles className="h-4 w-4 animate-spin" />
                ) : (
                  <Search className="h-4 w-4" />
                )}
                Search Gutenberg
              </button>
            </div>
          </form>
        </CardContent>
      </Card>

      {/* Quick Search Chips */}
      <div className="flex flex-wrap gap-2 text-xs">
        <span className="text-slate-500 py-1">Popular Classics:</span>
        {["Pride and Prejudice", "Frankenstein", "Dracula", "Sherlock Holmes", "The Great Gatsby", "Moby Dick"].map((chip) => (
          <button
            key={chip}
            type="button"
            onClick={() => { setQuery(chip); }}
            className="bg-slate-900 hover:bg-slate-800 text-slate-300 px-2.5 py-1 rounded-full border border-slate-800 transition-colors"
          >
            {chip}
          </button>
        ))}
      </div>

      {/* Results */}
      {searched && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-medium text-slate-300">
              Found {results.length} Public Domain Book{results.length === 1 ? "" : "s"}
            </h3>
          </div>

          {results.length === 0 && !loading && (
            <Card className="border-slate-800 bg-slate-950/30 p-8 text-center text-slate-500">
              No public domain books found matching &quot;{query}&quot;. Try broadening your keywords.
            </Card>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {results.map((book) => {
              const statusKey = `book-${book.id}`;
              const currentStatus = dispatchStatus[statusKey];

              return (
                <Card
                  key={book.id}
                  className="border-slate-800 bg-slate-950/60 hover:border-slate-700 transition-colors flex flex-col justify-between"
                >
                  <CardHeader className="pb-3">
                    <div className="flex gap-4">
                      {book.cover_url && (
                        <img
                          src={book.cover_url}
                          alt={book.title}
                          className="w-16 h-24 object-cover rounded shadow-md border border-slate-800 shrink-0 bg-slate-900"
                          onError={(e) => { (e.target as HTMLElement).style.display = "none"; }}
                        />
                      )}
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <span className="text-[10px] font-mono bg-amber-950/80 text-amber-300 px-1.5 py-0.5 rounded border border-amber-800/50">
                            ID #{book.id}
                          </span>
                          <span className="text-[10px] font-mono bg-emerald-950/80 text-emerald-300 px-1.5 py-0.5 rounded border border-emerald-800/50 flex items-center gap-1">
                            <ShieldCheck className="h-3 w-3" /> Public Domain
                          </span>
                        </div>
                        <h4 className="font-semibold text-white text-base leading-snug line-clamp-2">
                          {book.title}
                        </h4>
                        <p className="text-xs text-amber-300/90 font-medium">
                          {book.author}
                        </p>
                        <p className="text-xs text-slate-400 flex items-center gap-1">
                          <HeartHandshake className="h-3 w-3 text-slate-500" />
                          {book.download_count.toLocaleString()} downloads
                        </p>
                      </div>
                    </div>
                  </CardHeader>

                  <CardContent className="space-y-3 pt-0">
                    {book.subjects && book.subjects.length > 0 && (
                      <div className="flex flex-wrap gap-1">
                        {book.subjects.slice(0, 3).map((sub, i) => (
                          <span
                            key={i}
                            className="text-[10px] bg-slate-900 text-slate-400 px-2 py-0.5 rounded-full border border-slate-800 line-clamp-1"
                          >
                            {sub}
                          </span>
                        ))}
                      </div>
                    )}

                    <div className="flex items-center justify-between pt-2 border-t border-slate-800/80">
                      <a
                        href={book.gutenberg_url}
                        target="_blank"
                        rel="noreferrer"
                        className="text-xs text-slate-400 hover:text-slate-200 flex items-center gap-1"
                      >
                        <ExternalLink className="h-3 w-3" /> Gutenberg Web Page
                      </a>

                      <div className="flex items-center gap-2">
                        <a
                          href={book.download_url}
                          target="_blank"
                          rel="noreferrer"
                          className="flex items-center gap-1 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs px-3 py-1.5 rounded transition-colors"
                        >
                          <Download className="h-3.5 w-3.5" /> Direct EPUB
                        </a>
                        <button
                          type="button"
                          onClick={() => handleDispatchEPUB(book)}
                          disabled={currentStatus === "dispatching"}
                          className="flex items-center gap-1 bg-amber-600 hover:bg-amber-500 text-white text-xs font-medium px-3 py-1.5 rounded transition-colors disabled:opacity-50"
                        >
                          <Download className="h-3.5 w-3.5" /> Send to rTorrent
                        </button>
                      </div>
                    </div>

                    {currentStatus && (
                      <div className="text-xs text-slate-300">
                        {currentStatus === "dispatching" && (
                          <span className="text-amber-400">Dispatching EPUB to rTorrent...</span>
                        )}
                        {currentStatus === "success" && (
                          <span className="text-emerald-400">Sent EPUB download to rTorrent queue!</span>
                        )}
                        {currentStatus.startsWith("error") && (
                          <span className="text-rose-400">{currentStatus}</span>
                        )}
                      </div>
                    )}
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
