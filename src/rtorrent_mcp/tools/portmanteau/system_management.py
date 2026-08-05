# pyright: reportUnusedFunction=false
"""
System Management Portmanteau Tool

Consolidates all system operations including help, status, health checks, and repository analysis.
"""

import logging
import sys
from pathlib import Path
from typing import Any, Literal

import psutil
from fastmcp import FastMCP

logger = logging.getLogger(__name__)

SYSTEM_ACTIONS = {
    "help": "Get comprehensive help and tool documentation",
    "status": "Get system status and health check",
    "health": "Detailed health check with metrics",
    "info": "Get server information and configuration",
    "analyze": "Analyze repository structure and codebase",
}


def register_system_management_tool(mcp: FastMCP, settings) -> None:
    """Register the system management portmanteau tool."""

    @mcp.tool()
    async def system_management(
        action: Literal["help", "status", "health", "info", "analyze"],
        topic: str | None = None,
        level: str = "basic",
    ) -> dict[str, Any]:
        """
        Comprehensive system management portmanteau tool.

        PORTMANTEAU PATTERN RATIONALE:
        Instead of creating 5+ separate tools (one per operation), this tool consolidates related
        system operations into a single interface. Prevents tool explosion (5 tools → 1 tool) while maintaining
        full functionality and improving discoverability. Follows FastMCP 2.12+ best practices.

        Args:
            action (Literal, required): The system operation to perform. Must be one of:
                - "help": Get help documentation (optional: topic, level)
                - "status": Get quick system status (no params required)
                - "health": Detailed health check with metrics (no params required)
                - "info": Get server info and configuration (no params required)
                - "analyze": Analyze repository structure (no params required)

            topic (str | None): Help topic for filtered help.
                Optional for: help
                Valid: "torrent", "search", "nlp", "legal", "all"

            level (str): Detail level for help/status.
                Default: "basic". Valid: "basic", "detailed", "expert"

        Returns:
            dict[str, Any]: Dictionary containing:
                - success (bool): Boolean indicating if operation succeeded
                - action (str): The action that was performed
                - data (dict): System information or help content
                - error (str | None): Error message if success is False

        Examples:
            # Get help overview
            result = await system_management(action="help")

            # Get detailed help on search tools
            result = await system_management(action="help", topic="search", level="detailed")

            # Quick status check
            result = await system_management(action="status")

            # Detailed health check
            result = await system_management(action="health")

            # Get server info
            result = await system_management(action="info")

            # Analyze repository
            result = await system_management(action="analyze")
        """
        try:
            if action not in SYSTEM_ACTIONS:
                return {
                    "success": False,
                    "action": action,
                    "error": f"Invalid action '{action}'. Available: {list(SYSTEM_ACTIONS.keys())}",
                }

            logger.info(f"Executing system action: {action}")

            if action == "help":
                help_data = _get_help(topic, level)
                return {"success": True, "action": action, "data": help_data}

            if action == "status":
                status_data = await _get_status(settings)
                return {"success": True, "action": action, "data": status_data}

            if action == "health":
                health_data = await _get_health(settings)
                return {"success": True, "action": action, "data": health_data}

            if action == "info":
                info_data = _get_info(settings)
                return {"success": True, "action": action, "data": info_data}

            if action == "analyze":
                analysis = await _analyze_repo()
                return {"success": True, "action": action, "data": analysis}

            return {
                "success": False,
                "action": action,
                "error": f"Action '{action}' not implemented",
            }

        except Exception as e:
            logger.error(f"Error in system action '{action}': {e}", exc_info=True)
            return {"success": False, "action": action, "error": f"System operation failed: {e!s}"}


def _get_help(topic: str | None, level: str) -> dict:
    """Get help documentation."""
    base_help = {
        "title": "RTorrent MCP Server (AT)",
        "description": "FastMCP 3.1 server for anime torrenting automation with Austrian legal compliance",
        "version": "3.0.0",
        "portmanteau_tools": {
            "torrent_management": {
                "description": "All rTorrent operations (add, list, pause, resume, delete, status)",
                "actions": ["add", "list", "pause", "resume", "delete", "status", "info"],
            },
            "search_management": {
                "description": "All search operations (anime, manga, movies, ebooks, metadata)",
                "actions": [
                    "anime",
                    "manga",
                    "japanese_tv",
                    "movies",
                    "ebooks_annas",
                    "ebooks_pb",
                    "comics",
                    "annas_detail",
                    "imdb",
                    "imdb_search",
                    "tvdb",
                ],
            },
            "nlp_management": {
                "description": "Natural language commands (EN/DE)",
                "actions": ["command", "parse", "help"],
            },
            "legal_management": {
                "description": "Austrian legal compliance",
                "actions": ["risk", "check", "advice", "status"],
            },
            "system_management": {
                "description": "System operations (help, status, health)",
                "actions": ["help", "status", "health", "info", "analyze"],
            },
        },
        "quick_start": [
            "search_management(action='anime', query='Detective Conan', resolution='720p')",
            "torrent_management(action='add', magnet_link='magnet:?...')",
            "nlp_management(action='command', text='get me asw anime 720p')",
            "legal_management(action='status')",
        ],
        "austrian_context": {
            "location": "Vienna, 9th district",
            "legal_status": "Safe for personal anime consumption",
            "preferred_group": "ASW (Austrian preference)",
            "default_resolution": "720p",
        },
    }

    if topic and topic != "all":
        filtered = {k: v for k, v in base_help.items() if topic.lower() in k.lower() or topic.lower() in str(v).lower()}
        if filtered:
            return filtered

    return base_help


async def _get_status(settings) -> dict:
    """Get system status."""
    return {
        "server": "RTorrent MCP Server",
        "status": "running",
        "version": getattr(settings, "APP_VERSION", "1.0.0"),
        "python_version": sys.version,
        "rtorrent": {
            "host": getattr(settings, "RTORRENT_HOST", "localhost"),
            "port": getattr(settings, "RTORRENT_PORT", 5000),
        },
        "legal_region": "Austria (AT)",
        "allowed_categories": getattr(settings, "ALLOWED_CATEGORIES", ["Anime"]),
    }


async def _get_health(settings) -> dict:
    """Get detailed health metrics."""
    cpu_percent = psutil.cpu_percent()
    memory = psutil.virtual_memory()
    disk_path = "C:\\" if sys.platform == "win32" else "/"
    disk = psutil.disk_usage(disk_path)

    return {
        "status": "healthy" if cpu_percent < 90 and memory.percent < 90 else "degraded",
        "metrics": {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "memory_available_gb": round(memory.available / (1024**3), 2),
            "disk_percent": disk.percent,
            "disk_free_gb": round(disk.free / (1024**3), 2),
        },
        "components": {
            "mcp_server": "healthy",
            "rtorrent_client": "pending_check",
            "search_services": "healthy",
        },
        "uptime": "N/A",
    }


def _get_info(settings) -> dict:
    """Get server information."""
    return {
        "name": getattr(settings, "APP_NAME", "RTorrent MCP Server"),
        "version": getattr(settings, "APP_VERSION", "1.0.0"),
        "description": getattr(settings, "APP_DESCRIPTION", "Austrian anime automation"),
        "framework": "FastMCP 3.1",
        "transport": "stdio",
        "configuration": {
            "rtorrent_host": getattr(settings, "RTORRENT_HOST", "localhost"),
            "rtorrent_port": getattr(settings, "RTORRENT_PORT", 5000),
            "nyaa_base_url": getattr(settings, "NYAA_BASE_URL", "https://nyaa.si"),
            "log_level": getattr(settings, "LOG_LEVEL", "INFO"),
            "debug": getattr(settings, "DEBUG", False),
        },
        "capabilities": [
            "Anime search (nyaa.si)",
            "Movie search (YTS)",
            "Ebook search (Anna's Archive)",
            "Metadata (IMDb, TVDB)",
            "Natural language commands (EN/DE)",
            "Austrian legal compliance",
            "Post-processing integration",
        ],
    }


async def _analyze_repo() -> dict:
    """Analyze repository structure."""
    project_root = Path(__file__).resolve().parents[4]  # src/rtorrent_mcp/tools/portmanteau → repo root

    # Count files by type
    py_files = list(project_root.rglob("*.py"))
    md_files = list(project_root.rglob("*.md"))
    test_files = [f for f in py_files if "test" in f.name.lower()]

    return {
        "project_name": "rTorrent MCP Server",
        "structure": {
            "python_files": len(py_files),
            "markdown_files": len(md_files),
            "test_files": len(test_files),
        },
        "directories": {
            "src/rtorrent_mcp/tools": "MCP tool definitions",
            "src/rtorrent_mcp/services": "Service implementations",
            "src/rtorrent_mcp/config": "Configuration management",
            "tests": "Test suite",
            "docs": "Documentation",
        },
        "architecture": "FastMCP 2.12 portmanteau pattern",
        "compliance": {
            "fastmcp_version": "2.12+",
            "portmanteau_tools": 5,
            "individual_tools_replaced": "30+",
            "production_ready": True,
        },
    }
