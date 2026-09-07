# Installation

> **New here?** Read [`docs/ONBOARDING.md`](docs/ONBOARDING.md) first — it covers
> starting the rTorrent container and (optional) registering an Anna's Archive
> account so e-book searches and downloads work.

## 🚀 Quick Start (recommended)

```powershell
# Install just if you don't have it
winget install Casey.Just    # Windows
# scoop install just          # Windows (alternative)
# brew install just           # macOS
# sudo apt install just       # Debian/Ubuntu
# cargo install just          # Linux (Rust)

git clone https://github.com/sandraschi/rtorrent-mcp
cd rtorrent-mcp
just
```

The interactive recipe dashboard opens in your browser. From there:

```powershell
just bootstrap   # install all dependencies
just serve       # start the server
just web         # start the frontend (if applicable)
```

> **Why not `pip install`?** MCP servers bundle webapps, configs, project scaffolding, and tooling that a flat Python package can't deliver. PyPI offers no safety advantage — it doesn't audit packages either. `just` gives you the complete, ready-to-run stack.

---

## 🐌 Traditional Setup

If you prefer not to use `just`:

1. Install [Python 3.13+](https://python.org) and [uv](https://docs.astral.sh/uv/)
2. Clone and enter the repo:
   ```powershell
   git clone https://github.com/sandraschi/rtorrent-mcp
   cd rtorrent-mcp
   ```
3. Install dependencies:
   ```powershell
   uv sync --all-extras
   ```
4. Start the server:
   ```powershell
   # stdio mode (for MCP clients like Claude Desktop)
   uv run python -m rtorrent_mcp.server

   # HTTP mode (for web dashboard)
   uv run uvicorn rtorrent_mcp.server:app --port 10910
   ```
5. Open `http://localhost:10912` or the frontend URL.

---

## 🔌 Claude Desktop Configuration

Add this to your `claude_desktop_config.json`
(`%APPDATA%\Claude\claude_desktop_config.json` on Windows,
`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS,
`~/.config/Claude/claude_desktop_config.json` on Linux):

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

Replace the path with your actual clone location, then restart Claude Desktop.
Full variable list: [docs/CONFIGURATION.md](docs/CONFIGURATION.md).

## 🤖 LLM for the agentic workflow (optional)

`agentic_rtorrent_workflow` needs an LLM to plan multi-step tasks. Two tiers,
pick one:

| Tier | Setup | Config |
|------|-------|--------|
| **Local (Ollama)** — default | `winget install Ollama.Ollama` then `ollama pull llama3.2` | Nothing to set — defaults to `http://127.0.0.1:11434/v1` |
| **Cloud / client LLM** | No local install needed | Set `RTORRENT_SAMPLING_USE_CLIENT_LLM=1` to use the MCP host's own LLM instead |

Every other tool works with no LLM configured at all — this only affects the
one agentic workflow tool.

---

## ❓ Troubleshooting

| Issue | Fix |
|---|---|
| `just` not found | Install via `winget install Casey.Just`, `scoop install just`, or `brew install just` |
| Port conflict | Run `just kill-all` to clear fleet ports (10700–11000) |
| Dependencies out of sync | `uv sync --all-extras` |
| Something else | [Open a GitHub issue](https://github.com/sandraschi/rtorrent-mcp/issues) |

---

*See the main [README](README.md) for feature overview and documentation.*
