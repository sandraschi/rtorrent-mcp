---
name: rtorrent-mcp
description: Automate rTorrent via XML-RPC with Nyaa search, legal (AT) checks, and portmanteau MCP tools.
---

# rTorrent MCP

## When to use

- Add/list/pause torrents against **rTorrent** (`RTORRENT_HOST`, `RTORRENT_PORT`, `/RPC2`).
- Search **nyaa.si** and other indexers through `search_management`.
- Check **Austrian legal** context with `legal_management` before risky operations.

## Tools (portmanteau)

| Tool | Role |
|------|------|
| `torrent_management` | add, list, pause, resume, delete, status, post-processing |
| `search_management` | anime, tv, movies, ebooks, metadata |
| `nlp_management` | natural language commands |
| `legal_management` | risk, check, advice |
| `system_management` | help, health, status |
| `workflow_management` | franchise / batch / schedule |
| `agentic_rtorrent_workflow` | LLM-driven multi-step flow (needs sampling) |

## Sampling

Server-side LLM defaults to **Ollama** at `RTORRENT_SAMPLING_BASE_URL`. Set `RTORRENT_SAMPLING_USE_CLIENT_LLM=1` to use the host LLM when supported.

## Safety

Do not expose rTorrent XML-RPC to the public internet. Keep RPC on localhost or a trusted network.
