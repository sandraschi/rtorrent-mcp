import { Book, Cable, Database, Info, Server, ShieldAlert } from "lucide-react";
import { ShellHonestyBanner } from "@/components/layout/shell-honesty-banner";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export function Help() {
  return (
    <div className="space-y-6 max-w-4xl">
      <ShellHonestyBanner />
      <Card
        className="border-red-900/60 bg-red-950/30"
        data-testid="legal-stance-banner"
      >
        <CardHeader>
          <div className="flex items-center gap-2">
            <ShieldAlert className="h-5 w-5 text-red-400" />
            <CardTitle className="text-white">Not for piracy</CardTitle>
          </div>
        </CardHeader>
        <CardContent className="text-sm text-slate-400 space-y-2">
          <p>
            <strong className="text-slate-200">
              This software does not help with copyright infringement.
            </strong>{" "}
            No infringing sources, no sourcing help, no configuration for
            infringing purposes. BitTorrent is neutral infrastructure with real
            lawful uses — this repo is for those.
          </p>
          <p>
            Read first:{" "}
            <code className="text-xs text-slate-300">docs/LEGAL_NOTICE.md</code>{" "}
            (stance + issue policy) ·{" "}
            <code className="text-xs text-slate-300">
              docs/LEGAL_SOURCING.md
            </code>{" "}
            (lawful uses) ·{" "}
            <code className="text-xs text-slate-300">
              docs/SAFETY_TORRENTING.md
            </code>{" "}
            (swarm visibility, VPN limits, seeding liability) ·{" "}
            <code className="text-xs text-slate-300">
              docs/LEGAL_COUNTRIES.md
            </code>{" "}
            (Austria, Germany, USA, UK, Japan).
          </p>
          <p>
            In-app risk help: the{" "}
            <code className="text-xs text-slate-300">legal_management</code>{" "}
            tool (<code className="text-xs text-slate-300">risk</code>,{" "}
            <code className="text-xs text-slate-300">check</code>,{" "}
            <code className="text-xs text-slate-300">advice</code>,{" "}
            <code className="text-xs text-slate-300">status</code>) describes
            download risk with Austrian context. It describes risk — it does not
            grant permission.
          </p>
        </CardContent>
      </Card>
      <Card
        className="border-slate-800 bg-slate-950/50"
        data-testid="noseed-mode-card"
      >
        <CardHeader>
          <div className="flex items-center gap-2">
            <Info className="h-5 w-5 text-amber-500" />
            <CardTitle className="text-white">No-seed mode (default)</CardTitle>
          </div>
        </CardHeader>
        <CardContent className="text-sm text-slate-400 space-y-2">
          <p>
            This stack does not seed. Two settings enforce it: rTorrent stops
            every torrent the instant it completes (
            <code className="text-xs text-slate-300">
              method.set_key =
              event.download.finished,stop_completed,&quot;d.stop=&quot;
            </code>{" "}
            in{" "}
            <code className="text-xs text-slate-300">config/rtorrent.rc</code>
            ), and the post-processor removes the stopped torrent after handling
            files (
            <code className="text-xs text-slate-300">
              DELETE_TORRENT_AFTER_COMPLETE=true
            </code>
            ). A finished download therefore never sits seeding while waiting
            for processing.
          </p>
          <p>
            Honest limit: piece-uploads <em>during</em> the download are
            unavoidable — that is the protocol, not a setting. Small files
            barely upload before finishing; multi-GB packs measurably do.
            Details:{" "}
            <code className="text-xs text-slate-300">
              docs/POST_PROCESSING_SETUP.md
            </code>{" "}
            and{" "}
            <code className="text-xs text-slate-300">
              docs/SAFETY_TORRENTING.md
            </code>{" "}
            §3.
          </p>
        </CardContent>
      </Card>
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-white">
          Help — rTorrent &amp; BitTorrent
        </h2>
        <p className="text-slate-400 mt-1">
          Repository <strong className="text-slate-200">rtorrent-mcp</strong>{" "}
          (Python import{" "}
          <code className="text-xs text-slate-300">rtorrent_mcp</code>). Dual
          backend since v3.1:{" "}
          <code className="text-xs text-slate-300">
            TORRENT_BACKEND=rtorrent
          </code>{" "}
          (Docker, default) or{" "}
          <code className="text-xs text-slate-300">qbittorrent</code> (native
          exe via WebUI API — the old prototype is back, properly this time).
        </p>
      </div>

      <Card
        className="border-slate-800 bg-slate-950/50"
        data-testid="backend-card"
      >
        <CardHeader>
          <div className="flex items-center gap-2">
            <Server className="h-5 w-5 text-emerald-500" />
            <CardTitle className="text-white">Torrent backend</CardTitle>
          </div>
        </CardHeader>
        <CardContent className="text-sm text-slate-400 space-y-2">
          <p>
            One tool surface, two clients.{" "}
            <strong className="text-slate-200">rTorrent</strong> (XML-RPC
            through the Docker stack) is the default;{" "}
            <strong className="text-slate-200">qBittorrent</strong> (native
            WebUI API v2, cookie session with re-login, API-key ready for ≥
            v5.2.0) is selected with{" "}
            <code className="text-xs text-slate-300">
              TORRENT_BACKEND=qbittorrent
            </code>{" "}
            plus <code className="text-xs text-slate-300">QBITTORRENT_URL</code>{" "}
            and credentials. Post-processing, Plex handoff, and no-seed
            enforcement work identically above either backend. Details:{" "}
            <code className="text-xs text-slate-300">
              docs/DUAL_BACKEND_SPEC.md
            </code>
            .
          </p>
        </CardContent>
      </Card>

      <Card className="border-slate-800 bg-slate-950/50">
        <CardHeader>
          <div className="flex items-center gap-2">
            <Server className="h-5 w-5 text-emerald-500" />
            <CardTitle className="text-white">What rTorrent is</CardTitle>
          </div>
        </CardHeader>
        <CardContent className="text-sm text-slate-400 space-y-3">
          <p>
            <strong className="text-slate-200">rTorrent</strong> is a
            lightweight, scriptable{" "}
            <strong className="text-slate-200">BitTorrent</strong> client. It is
            controlled via <strong className="text-slate-200">XML-RPC</strong>{" "}
            (this MCP uses the HTTP endpoint{" "}
            <code className="text-xs text-slate-300">/RPC2</code>).
          </p>
          <p>
            In Docker setups (e.g. crazymax/rtorrent-rutorrent),{" "}
            <strong>nginx</strong> forwards HTTP to rTorrent&apos;s socket —
            typical MCP settings use{" "}
            <code className="text-xs">RTORRENT_HOST=localhost</code> and{" "}
            <code className="text-xs">RTORRENT_PORT=12224</code> (adjust to your
            compose).
          </p>
        </CardContent>
      </Card>

      <Card className="border-slate-800 bg-slate-950/50">
        <CardHeader>
          <div className="flex items-center gap-2">
            <Cable className="h-5 w-5 text-blue-500" />
            <CardTitle className="text-white">
              How the MCP talks to rTorrent
            </CardTitle>
          </div>
        </CardHeader>
        <CardContent className="text-sm text-slate-400 space-y-3 font-mono text-xs">
          <p className="text-slate-500 font-sans text-sm">
            The server uses Python XML-RPC against:
          </p>
          <pre className="rounded-md border border-slate-800 bg-slate-900/80 p-3 text-emerald-300/90 overflow-x-auto">
            http://&lt;RTORRENT_HOST&gt;:&lt;RTORRENT_PORT&gt;/RPC2
          </pre>
          <p className="text-slate-400 font-sans text-sm">
            List methods with{" "}
            <code className="text-xs">system.listMethods</code>; torrent
            operations use the standard rTorrent XML-RPC API (
            <code className="text-xs">d.*</code>,{" "}
            <code className="text-xs">download_list</code>, etc.).
          </p>
        </CardContent>
      </Card>

      <Card className="border-slate-800 bg-slate-950/50">
        <CardHeader>
          <div className="flex items-center gap-2">
            <Database className="h-5 w-5 text-violet-500" />
            <CardTitle className="text-white">
              Key environment variables
            </CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          <table className="w-full text-sm text-left text-slate-400 border-collapse">
            <thead>
              <tr className="border-b border-slate-800 text-slate-300">
                <th className="py-2 pr-4 font-medium">Variable</th>
                <th className="py-2 font-medium">Purpose</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              <tr>
                <td className="py-2 font-mono text-xs text-slate-300">
                  RTORRENT_HOST
                </td>
                <td className="py-2">XML-RPC host (often localhost)</td>
              </tr>
              <tr>
                <td className="py-2 font-mono text-xs text-slate-300">
                  RTORRENT_PORT
                </td>
                <td className="py-2">Port for /RPC2 (e.g. 12224 in Docker)</td>
              </tr>
              <tr>
                <td className="py-2 font-mono text-xs text-slate-300">
                  RTORRENT_PATH
                </td>
                <td className="py-2">Session path (container path)</td>
              </tr>
              <tr>
                <td className="py-2 font-mono text-xs text-slate-300">
                  NYAA_BASE_URL
                </td>
                <td className="py-2">Indexer base for search tools</td>
              </tr>
            </tbody>
          </table>
          <p className="text-xs text-slate-500 mt-3">
            Full list:{" "}
            <code className="text-xs">src/rtorrent_mcp/config/settings.py</code>
          </p>
        </CardContent>
      </Card>

      <Card className="border-slate-800 bg-slate-950/50">
        <CardHeader>
          <div className="flex items-center gap-2">
            <Book className="h-5 w-5 text-amber-500" />
            <CardTitle className="text-white">
              Documentation in the repo
            </CardTitle>
          </div>
        </CardHeader>
        <CardContent className="text-sm text-slate-400 space-y-2">
          <ul className="list-disc list-inside space-y-1">
            <li>
              <code className="text-xs text-slate-300">
                docs/RTORRENT_REFERENCE.md
              </code>{" "}
              — short architecture (this page mirrors it).
            </li>
            <li>
              <code className="text-xs text-slate-300">
                docs/RTORRENT_SETUP.md
              </code>{" "}
              — Docker, plugins, RSS, ruTorrent, troubleshooting.
            </li>
            <li>
              <code className="text-xs text-slate-300">README.md</code> —
              install, MCP config, legal context (Austria).
            </li>
            <li>
              <code className="text-xs text-slate-300">
                docs/LEGAL_NOTICE.md
              </code>{" "}
              — not-for-piracy stance, lawful-use scope, sourcing-question issue
              policy.
            </li>
            <li>
              <code className="text-xs text-slate-300">
                docs/LEGAL_SOURCING.md
              </code>{" "}
              ·{" "}
              <code className="text-xs text-slate-300">
                docs/SAFETY_TORRENTING.md
              </code>{" "}
              ·{" "}
              <code className="text-xs text-slate-300">
                docs/LEGAL_COUNTRIES.md
              </code>{" "}
              — lawful uses, safety, country specifics.
            </li>
          </ul>
        </CardContent>
      </Card>

      <Card className="border-slate-800 bg-slate-950/50">
        <CardHeader>
          <div className="flex items-center gap-2">
            <Book className="h-5 w-5 text-amber-500" />
            <CardTitle className="text-white">
              Anna&apos;s Archive: Bulk Torrents &amp; Quality Notes (*Caveat
              Downloador*)
            </CardTitle>
          </div>
        </CardHeader>
        <CardContent className="text-sm text-slate-400 space-y-3">
          <p>
            <strong className="text-slate-200">
              Bulk Torrents vs Single Items
            </strong>
            : Anna&apos;s Archive hosts both individual book mirrors and massive
            bulk torrent dumps (ranging from ~5TB collections to multi-terabyte
            / 100TB+ full catalog archives). AI corporations famously used these
            bulk dumps to train LLMs (triggering copyright litigation). For
            day-to-day reading, use{" "}
            <code className="text-xs">ebooks_annas</code> to fetch individual
            books rather than dataset archives.
          </p>
          <p>
            <strong className="text-slate-200">
              Duplicates &amp; Format Variances
            </strong>
            : Anna&apos;s Archive aggregates LibGen, Z-Library, Sci-Hub, and
            Internet Archive. Expect duplicate entries for popular titles with
            varying scan quality—ranging from pristine vector digital{" "}
            <code className="text-xs">.epub</code> /{" "}
            <code className="text-xs">.pdf</code> files to raw bitmap scans
            packed in <code className="text-xs">.cbz</code>. Check file format
            and size in <code className="text-xs">annas_detail</code> before
            downloading!
          </p>
          <p>
            <strong className="text-slate-200">
              Fast vs. Slow Mirrors &amp; Single Books
            </strong>
            : Fast partner downloads require donor membership/account
            registration. Free Slow partner mirrors (LibGen, Z-Lib, IPFS)
            require no account signup, but have brief queue timers (10-60s). For
            single e-books (a few megabytes), <em>ignore paid Fast options</em>-
            free Slow mirrors or P2P magnets download almost instantly.
          </p>
          <p>
            <strong className="text-slate-200">
              Registration now required (anti-bot)
            </strong>
            : Anna&apos;s Archive now gates even the slow downloads behind an
            account. Register once at{" "}
            <code className="text-xs">annas-archive.is</code> (a burner email is
            fine), then paste your session cookie in{" "}
            <strong className="text-slate-200">
              Settings &gt; Anna&apos;s Archive session
            </strong>{" "}
            (or set <code className="text-xs">ANNAS_SESSION_COOKIE</code> in{" "}
            <code className="text-xs">.env</code>). Search stays open; only
            downloads need this.
          </p>
        </CardContent>
      </Card>

      <Card className="border-slate-800 bg-slate-950/50">
        <CardHeader>
          <div className="flex items-center gap-2">
            <Info className="h-5 w-5 text-slate-500" />
            <CardTitle className="text-white">This web UI</CardTitle>
          </div>
        </CardHeader>
        <CardContent className="text-sm text-slate-500">
          The Vite shell does not control rTorrent directly. Use MCP tools from
          your agent (e.g. <code className="text-xs">torrent_management</code>,{" "}
          <code className="text-xs">system_management</code>
          ).
        </CardContent>
      </Card>
    </div>
  );
}
