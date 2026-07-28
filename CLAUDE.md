## Session Context (rTorrent MCP)

You have access to a BitTorrent automation server with rTorrent XML-RPC, multi-source search (nyaa, piratebay, annas-archive, YTS), media integration (Plex/Jellyfin), and Austrian legal compliance tools.

**Before starting work:**
1. Check server health: system_management(operation="health")
2. List current torrents: torrent_management(operation="list")
3. Check search availability: system_management(operation="status")

**Key tools:**
- `torrent_management` — manage torrent lifecycle (13 actions)
- `search_management` — search anime, TV, movies, ebooks (13 actions)
- `system_management` — health, status, diagnostics (5 actions)
- `agentic_rtorrent_workflow` — multi-step LLM-orchestrated workflows

**Config:** `.env` for credentials. rTorrent runs in Docker on port 12224. Backend on 10910, frontend on 10911.
