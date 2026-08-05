# rTorrent MCP - GitHub Copilot Instructions

You have access to the rtorrent-mcp MCP server for torrent management and media search.

## Before starting work
1. Check server health: `system_management(action="health")`
2. Review current torrents: `torrent_management(action="list")`

## At end of work
- Run a legal risk check for non-Anime content: `legal_management(action="risk")`
- Manage post-processing loops with `torrent_management(action="start_processing" | "stop_processing")`
