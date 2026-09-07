# Installing rtorrent-mcp

> **New here?** Read [`docs/ONBOARDING.md`](docs/ONBOARDING.md) first — it covers
> starting the rTorrent container and (optional) registering an Anna's Archive
> account so e-book searches and downloads work.

## Prerequisites

Install these if you don't have them already:

| Tool | Purpose | Install |
|------|---------|---------|
| Claude Desktop | Required host | [download](https://claude.ai/download) |
| Docker Desktop | Runs rTorrent (recommended) | [download](https://www.docker.com/products/docker-desktop/) |
| Git | Clone repo (Option C/D only) | `winget install Git.Git` |
| uv | Run server (Option C/D only) | `winget install astral-sh.uv` |
| Node.js | mcpb CLI (Option B only) | `winget install OpenJS.NodeJS` |
| just | Dev recipes (Option D only) | `winget install Casey.Just` |

> Windows: all installs via [winget](https://learn.microsoft.com/en-us/windows/package-manager/winget/).
> macOS: use `brew install` equivalents. Linux: use your distro package manager.
> After any winget install: close and reopen your terminal — PATH doesn't refresh in-place.

## Step 0 — Get rTorrent running (required, once)

rtorrent-mcp drives rTorrent; it doesn't include one. The bundled Docker
Compose stack is the fastest way to get one:

```powershell
docker compose up -d
```

This starts `crazymax/rtorrent-rutorrent` with XML-RPC on `12224` and the
ruTorrent WebUI on `12222`. Full setup, plugins, and troubleshooting:
[docs/RTORRENT_SETUP.md](docs/RTORRENT_SETUP.md). First-timer checklist
(including the optional Anna's Archive account): [docs/ONBOARDING.md](docs/ONBOARDING.md).

## Option A — Drag and Drop (Recommended)

1. Go to [Releases](https://github.com/sandraschi/rtorrent-mcp/releases/latest)
2. Download `rtorrent-mcp-{version}.mcpb`
3. Open Claude Desktop → drag the file onto the window
   *Or*: Settings → MCP Servers → Install from file

No Python, uv, git, or Node required.

## Option B — mcpb CLI

```bash
# Requires Node.js (see Prerequisites)
npx @anthropic-ai/mcpb install https://github.com/sandraschi/rtorrent-mcp
```

## Option C — Manual Configuration

1. Clone: `git clone https://github.com/sandraschi/rtorrent-mcp`
2. Install deps: `cd rtorrent-mcp && uv sync`
3. Add to Claude Desktop config:

```json
{
  "mcpServers": {
    "rtorrent-mcp": {
      "command": "uv",
      "args": ["--directory", "C:\\path\\to\\rtorrent-mcp", "run", "rtorrent-mcp"],
      "env": { "RTORRENT_HOST": "localhost", "RTORRENT_PORT": "12224" }
    }
  }
}
```

Config file location:
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`

4. Restart Claude Desktop. Full variable list: [docs/CONFIGURATION.md](docs/CONFIGURATION.md).

## Option D — Developer Mode

For contributing or running from source with live reload:

```powershell
just bootstrap   # install all dependencies
just serve       # start the backend
just web         # start the frontend (web_sota/)
```

See [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) for tests, linting, and the
build pipeline.

## LLM for the agentic workflow (optional)

`agentic_rtorrent_workflow` needs an LLM to plan multi-step tasks. Two tiers,
pick one:

| Tier | Setup | Config |
|------|-------|--------|
| **Local (Ollama)** — default | `winget install Ollama.Ollama` then `ollama pull llama3.2` | Nothing to set — defaults to `http://127.0.0.1:11434/v1` |
| **Cloud / client LLM** | No local install needed | Set `RTORRENT_SAMPLING_USE_CLIENT_LLM=1` to use the MCP host's own LLM instead |

Every other tool works with no LLM configured at all — this only affects the
one agentic workflow tool.

## Verify Installation

After installing, open Claude Desktop and type:
> "Check rTorrent status"

You should see a health/connection summary from `system_management`. If it
reports rTorrent as unreachable, revisit Step 0 above.

## Troubleshooting

| Issue | Fix |
|---|---|
| `just` not found (Option D) | Install via `winget install Casey.Just`, `scoop install just`, or `brew install just` |
| Port conflict | Run `just kill-all` to clear fleet ports (10700–11000) |
| Dependencies out of sync | `uv sync --all-extras` |
| rTorrent unreachable | See [docs/RTORRENT_SETUP.md](docs/RTORRENT_SETUP.md) |
| Something else | See [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) or [open a GitHub issue](https://github.com/sandraschi/rtorrent-mcp/issues) |

---

*See the main [README](README.md) for feature overview and documentation.*
