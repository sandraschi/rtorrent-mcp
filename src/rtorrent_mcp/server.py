#!/usr/bin/env python3
"""
rTorrent MCP Server (Python package: ``rtorrent_mcp``)
FastMCP 3.1 server: portmanteau tools, prompts, bundled skills, sampling, agentic workflows.

Repository: **rtorrent-mcp**. Early development targeted qBittorrent (no usable API); the **historic**
PyPI/import name was ``qbtmcp``. This codebase is **rTorrent-first** (XML-RPC to ``/RPC2``).

v3.0.0:
- FastMCP 3.1: sampling (OpenAI-compatible LLM), ``agentic_rtorrent_workflow`` (sample_step + tools)
- Skills: ``SkillsDirectoryProvider`` on ``src/rtorrent_mcp/skills/``
- Prompts: parameterized templates for search, legal, workflows
"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from fastmcp import FastMCP
from fastmcp.server.providers.skills import SkillsDirectoryProvider

# Load environment variables from .env file
load_dotenv()

# Add the project root directory to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import application settings
from rtorrent_mcp.config.settings import get_settings, settings
from rtorrent_mcp.sampling import RTorrentSamplingHandler

from .transport import run_server_async

# Configure structured logging
logger = logging.getLogger(__name__)

# Version info
__version__ = "3.0.0"
__fastmcp_version__ = "3.1"

_USE_CLIENT_SAMPLING = os.getenv("RTORRENT_SAMPLING_USE_CLIENT_LLM", "").lower() in (
    "1",
    "true",
    "yes",
)
_SKILLS_ROOT = Path(__file__).resolve().parent / "skills"
_BUNDLED_SKILL_PROVIDERS: list[SkillsDirectoryProvider] = []
if _SKILLS_ROOT.is_dir():
    _BUNDLED_SKILL_PROVIDERS.append(SkillsDirectoryProvider(roots=[_SKILLS_ROOT]))


class RTorrentMCPServer(FastMCP):
    """
    rTorrent MCP Server (FastMCP 3.1): portmanteau tools, prompts, skills, sampling.

    PORTMANTEAU TOOLS (6) plus **agentic_rtorrent_workflow** (sampling with tools):
    1. torrent_management - Torrent ops + post-processing (12 actions)
    2. search_management - All search operations (13 actions)
    3. nlp_management - Natural language processing (3 actions)
    4. legal_management - Legal compliance (4 actions)
    5. system_management - System operations (5 actions)
    6. workflow_management - Complex multi-step workflows (8 actions)
    7. agentic_rtorrent_workflow - LLM-orchestrated multi-step flows (requires sampling)

    PROMPT TEMPLATES:
    - anime_search_prompt - Search anime with Austrian preferences
    - franchise_download_prompt - Download entire anime franchise
    - legal_check_prompt - Check legal status
    - tv_show_search_prompt - Search Western TV shows
    - ebook_search_prompt - Search ebooks (Anna's Archive)
    - torrent_workflow_prompt - Standard torrent workflow
    - system_status_prompt - System status check
    """

    def __init__(self, config_path: str | None = None):
        """
        Initialize the rTorrent MCP server (FastMCP 3.1: sampling, skills, prompts).

        Args:
            config_path: Optional path to .env configuration file
        """
        # Load settings
        if config_path and os.path.exists(config_path):
            self._settings = get_settings(env_file=config_path)
        else:
            self._settings = settings
        if self._settings.LOG_LEVEL:
            os.environ["FASTMCP_LOG_LEVEL"] = self._settings.LOG_LEVEL

        self._sampling_handler = RTorrentSamplingHandler(config=self._settings)

        super().__init__(
            name=self._settings.APP_NAME,
            instructions=self._get_instructions(),
            version=__version__,
            providers=_BUNDLED_SKILL_PROVIDERS or None,
            sampling_handler=self._sampling_handler,
            sampling_handler_behavior="fallback" if _USE_CLIENT_SAMPLING else "always",
            strict_input_validation=True,
            on_duplicate="replace",
        )

        self.logger = logging.getLogger(__name__)

    def _get_instructions(self) -> str:
        """Generate server instructions with MCPB pattern."""
        return f"""
{self._settings.APP_DESCRIPTION}

## FastMCP 3.1

### Portmanteau tools (6) + agentic_rtorrent_workflow
1. **torrent_management** - Add, list, pause, resume, delete, status, info,
   check_completed, process, start_processing, stop_processing, normalize
2. **search_management** - Anime, manga, japanese_tv, movies, tv_shows, tv_smart,
   ebooks_annas, ebooks_pb, comics, annas_detail, imdb, imdb_search, tvdb
3. **nlp_management** - Command processing, parsing, help
4. **legal_management** - Risk assessment, legal checks, advice, status
5. **system_management** - Help, status, health, info, analyze
6. **workflow_management** - Franchise downloads, batch series, scheduling
7. **agentic_rtorrent_workflow** - LLM-orchestrated multi-step flows

### Sampling
Default: OpenAI-compatible HTTP at RTORRENT_SAMPLING_BASE_URL (Ollama localhost).
Set RTORRENT_SAMPLING_USE_CLIENT_LLM=1 to prefer the MCP host LLM.

### Skills
Bundled skills under skill:// (see skills/rtorrent-mcp/SKILL.md).

### Prompt templates
anime_search_prompt, franchise_download_prompt, legal_check_prompt,
tv_show_search_prompt, ebook_search_prompt, torrent_workflow_prompt,
system_status_prompt

### Legal hints (AT)
Tool output may include Austria-oriented risk context; users must verify local law.
"""

    def setup(self):
        """Setup the server with SOTA components: tools + prompts"""
        # Log configuration
        self.logger.info(
            "Starting %s v%s (FastMCP %s)",
            self._settings.APP_NAME,
            __version__,
            __fastmcp_version__,
        )
        self.logger.info("Configuration loaded from: %s", os.getenv("ENV_FILE", "default settings"))
        self.logger.info("Legal hints: AT-oriented defaults in tools (not legal advice)")
        self.logger.info(
            "Focus: %s",
            ", ".join(self._settings.ALLOWED_CATEGORIES) + " @ " + "/".join(self._settings.ALLOWED_RESOLUTIONS),
        )

        self.logger.info("Mode: FastMCP 3.1 — 6 portmanteau tools + agentic_rtorrent_workflow")

        # Register all portmanteau tools + agentic workflow
        from rtorrent_mcp.tools import register_all_tools

        register_all_tools(self, self._settings)

        # Register prompt templates
        from rtorrent_mcp.prompts import register_prompts

        register_prompts(self)

        self.logger.info("Prompt templates registered")

        from rtorrent_mcp.api.web_routes import register_web_api

        register_web_api(self, app_version=__version__)
        self.logger.info("HTTP REST API registered: /api/health, /api/info, /api/rtorrent/*")

        if hasattr(self, "_app") and self._app is not None:
            from starlette.middleware.cors import CORSMiddleware

            self._app.add_middleware(
                CORSMiddleware,
                allow_origins=[
                    "tauri://localhost",
                    "http://tauri.localhost",
                    "https://tauri.localhost",
                ],
                allow_origin_regex=r"https?://(?:[a-zA-Z0-9-]+\.ts\.net|.*?\.tail-[a-f0-9]+\.ts\.net|tauri\.localhost|localhost|127\.0\.0\.1|192\.168\.\d{1,3}\.\d{1,3}|10\.\d{1,3}\.\d{1,3}\.\d{1,3}|100\.\d{1,3}\.\d{1,3}\.\d{1,3})(?::\d+)?$|^tauri://localhost$",
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )

        self.logger.info("[OK] Server setup complete")


def main(config_path: str | None = None):
    """Initialize and start the rTorrent MCP server"""
    import argparse

    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="rTorrent MCP Server — FastMCP 3.1 (rTorrent + search + workflows)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
v{__version__} (FastMCP {__fastmcp_version__}):
  6 Portmanteau Tools + agentic_rtorrent_workflow
  7 Prompt Templates
  Bundled skills (skill://)
  Sampling (RTORRENT_SAMPLING_*)

Portmanteau tools:
  1. torrent_management  - Torrent + post-processing (12 actions)
  2. search_management   - All searches (13 actions)
  3. nlp_management      - NLP processing (3 actions)
  4. legal_management    - Legal compliance (4 actions)
  5. system_management   - System ops (5 actions)
  6. workflow_management - Complex workflows (8 actions)
  7. agentic_rtorrent_workflow - LLM + tools (sampling)

Examples:
  python -m rtorrent_mcp.server                    # stdio (default)
  python -m rtorrent_mcp.server --transport http   # HTTP transport
  python -m rtorrent_mcp.server --config .env.prod # Custom config
        """,
    )
    parser.add_argument("--config", type=str, default=".env", help="Path to configuration file (.env)")
    parser.add_argument(
        "--transport",
        type=str,
        default="stdio",
        choices=["stdio", "http"],
        help="Transport protocol (stdio or http)",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"rTorrent MCP {__version__} (FastMCP {__fastmcp_version__})",
    )
    args = parser.parse_args()

    # Use provided config_path if available, otherwise use args.config
    final_config_path = config_path if config_path is not None else args.config

    # Build a namespace for the transport so it does not re-parse argv (avoids
    # "unrecognized arguments: --config .env --transport stdio" when run from Cursor).
    class TransportArgs:
        pass

    transport_args = TransportArgs()
    transport_args.stdio = args.transport == "stdio"
    transport_args.http = args.transport == "http"
    transport_args.sse = False
    transport_args.host = None
    transport_args.port = None
    transport_args.path = None
    transport_args.debug = False

    # Create and start the server
    try:
        server = RTorrentMCPServer(config_path=final_config_path)
        server.setup()
        import asyncio

        try:
            asyncio.run(run_server_async(server, args=transport_args, server_name="rtorrent-mcp"))
        except RuntimeError:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(run_server_async(server, args=transport_args, server_name="rtorrent-mcp"))
    except Exception as e:
        logger.error("[FAIL] Failed to start server: %s", str(e), exc_info=True)
        sys.exit(1)


class _UvicornASGIApp:
    """Lazy ASGI callable for ``uvicorn rtorrent_mcp.server:app`` (web_sota / Glama).

    Building the Starlette app is deferred until the first request so
    ``from rtorrent_mcp.server import RTorrentMCPServer`` does not run ``setup()`` twice.
    """

    __slots__ = ("_inner",)

    def __init__(self) -> None:
        self._inner = None

    async def __call__(self, scope, receive, send):
        if self._inner is None:
            try:
                srv = RTorrentMCPServer()
                srv.setup()
                path = os.environ.get("MCP_PATH", "/mcp")
                if not path.startswith("/"):
                    path = "/" + path
                self._inner = srv.http_app(path=path)
            except Exception:
                logger.exception("Failed to build ASGI app")
                from starlette.responses import Response

                resp = Response(
                    content='{"ok":false,"error":"Failed to initialize server"}',
                    status_code=500,
                    media_type="application/json",
                    headers={"content-type": "application/json"},
                )
                await resp(scope, receive, send)
                return
        return await self._inner(scope, receive, send)


app = _UvicornASGIApp()


if __name__ == "__main__":
    main()
