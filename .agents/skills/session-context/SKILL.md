---
name: session-context
description: Lightweight rtorrent-mcp session-start prompt — health check, torrent review, legal save action
---

## Session Context (rTorrent MCP)

You can manage rTorrent torrents and search anime/TV sources (nyaa.si, Pirate Bay, YTS, Anna's Archive) with Austrian legal checks.

**Before starting work:**
1. Check connection + health: system_management(action="health")
2. Review current torrents: torrent_management(action="list")

**At end of work:**
- Verify legal status for non-Anime content: legal_management(action="risk")
- Resume/pause processing loops: torrent_management(action="start_processing")
