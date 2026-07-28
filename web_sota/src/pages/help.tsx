import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Book, Cable, Database, Info, Server } from "lucide-react";

export function Help() {
  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-white">
          Help — rTorrent &amp; BitTorrent
        </h2>
        <p className="text-slate-400 mt-1">
          Repository <strong className="text-slate-200">rtorrent-mcp</strong>{" "}
          (Python import{" "}
          <code className="text-xs text-slate-300">rtorrent_mcp</code>). The old
          name <code className="text-xs text-slate-500">qbtmcp</code> /
          qBittorrent prototype is{" "}
          <strong className="text-amber-200/90">historic only</strong>.
        </p>
      </div>

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
          </ul>
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
