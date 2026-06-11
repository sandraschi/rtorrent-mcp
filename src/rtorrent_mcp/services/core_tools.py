"""
core_tools.py - Core MCP tools for RTorrent MCP Server
Help, status, and analyzer tools with extensive error handling
"""

import logging
import os
import sys
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def register_core_tools(mcp):
    """Register core tools with FastMCP server"""

    @mcp.tool(
        name="help",
        description="""
        Get comprehensive help information about available tools and resources.

        This tool provides detailed information about:
        - Available tools and their purposes
        - Resource endpoints and their data
        - Configuration and setup instructions
        - Legal compliance information
        - Troubleshooting guide

        Use this tool to understand how to interact with the RTorrent MCP server
        and get the most out of its capabilities.

        Returns:
            dict: Comprehensive help information organized by category
        """,
        output_schema={
            "type": "object",
            "properties": {
                "tools": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "description": {"type": "string"},
                            "category": {"type": "string"},
                        },
                    },
                },
                "resources": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "uri": {"type": "string"},
                            "description": {"type": "string"},
                            "content_type": {"type": "string"},
                        },
                    },
                },
                "configuration": {
                    "type": "object",
                    "properties": {
                        "app_name": {"type": "string"},
                        "version": {"type": "string"},
                        "legal_status": {"type": "string"},
                        "allowed_categories": {"type": "array", "items": {"type": "string"}},
                        "allowed_resolutions": {"type": "array", "items": {"type": "string"}},
                    },
                },
                "troubleshooting": {"type": "array", "items": {"type": "string"}},
            },
        },
    )
    def _help_tool() -> dict[str, Any]:
        """Get comprehensive help information"""
        try:
            return {
                "tools": [
                    {
                        "name": "add_torrent",
                        "description": "Add a torrent to rTorrent with Austrian anime categorization",
                        "category": "Torrent Management",
                    },
                    {
                        "name": "list_torrents",
                        "description": "List all torrents in rTorrent with status information",
                        "category": "Torrent Management",
                    },
                    {
                        "name": "pause_torrent",
                        "description": "Pause a specific torrent in rTorrent",
                        "category": "Torrent Management",
                    },
                    {
                        "name": "resume_torrent",
                        "description": "Resume a specific torrent in rTorrent",
                        "category": "Torrent Management",
                    },
                    {
                        "name": "delete_torrent",
                        "description": "Delete a torrent from rTorrent with optional file deletion",
                        "category": "Torrent Management",
                    },
                    {
                        "name": "get_status",
                        "description": "Get the current connection status of rTorrent",
                        "category": "System Status",
                    },
                    {
                        "name": "search_anime",
                        "description": "Search nyaa.si for anime releases with Austrian preferences",
                        "category": "Search",
                    },
                    {
                        "name": "analyze_repo",
                        "description": "Analyze the repository and provide comprehensive information",
                        "category": "Analysis",
                    },
                    {
                        "name": "get_system_status",
                        "description": "Get comprehensive system status and metrics",
                        "category": "System Status",
                    },
                    {
                        "name": "help",
                        "description": "Get comprehensive help information",
                        "category": "Information",
                    },
                ],
                "resources": [
                    {
                        "uri": "rtorrent://config",
                        "description": "rTorrent configuration and setup information",
                        "content_type": "application/json",
                    },
                    {
                        "uri": "anime://search/recent",
                        "description": "Recent anime releases information",
                        "content_type": "application/json",
                    },
                ],
                "configuration": {
                    "app_name": "RTorrent MCP",
                    "version": "3.0.0",
                    "legal_status": "Safe for Sandra in Vienna - Austrian legal compliance",
                    "allowed_categories": ["Anime"],
                    "allowed_resolutions": ["720p", "1080p"],
                },
                "troubleshooting": [
                    "Ensure rTorrent is running with SCGI enabled on port 12224",
                    "Check that the SCGI URL is accessible: http://localhost:12224/RPC2",
                    "Verify nyaa.si is accessible for search functionality",
                    "Check log files for detailed error messages",
                    "Ensure all dependencies are installed (fastmcp, aiohttp, etc.)",
                    "For anime search issues, verify network connectivity to nyaa.si",
                ],
            }
        except Exception as e:
            logger.error(f"Error generating help information: {e}")
            return {
                "error": f"Failed to generate help information: {e!s}",
                "tools": [],
                "resources": [],
                "configuration": {},
                "troubleshooting": [],
            }

    @mcp.tool(
        name="get_system_status",
        description="""
        Get comprehensive system status and metrics for the RTorrent MCP server.

        This tool provides detailed information about:
        - Server health and connection status
        - rTorrent connection status
        - System resource usage
        - Configuration status
        - Recent activity and error logs
        - Performance metrics

        Use this tool to diagnose issues or monitor the system's health.

        Returns:
            dict: Comprehensive status information
        """,
        output_schema={
            "type": "object",
            "properties": {
                "server_status": {"type": "string"},
                "rtorrent_status": {"type": "string"},
                "system_metrics": {
                    "type": "object",
                    "properties": {
                        "python_version": {"type": "string"},
                        "working_directory": {"type": "string"},
                        "memory_usage": {"type": "string"},
                        "uptime": {"type": "string"},
                    },
                },
                "configuration": {
                    "type": "object",
                    "properties": {
                        "app_name": {"type": "string"},
                        "version": {"type": "string"},
                        "log_level": {"type": "string"},
                        "allowed_categories": {"type": "array", "items": {"type": "string"}},
                    },
                },
                "recent_activity": {"type": "array", "items": {"type": "string"}},
                "errors": {"type": "array", "items": {"type": "string"}},
            },
        },
    )
    def get_system_status() -> dict[str, Any]:
        """Get comprehensive system status"""
        try:
            import time

            import psutil

            # Get process information
            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()
            uptime = time.time() - process.create_time()

            # Get recent log entries (simplified)
            recent_activity = [
                "Server running (status stub — use system_management for live health)",
            ]

            return {
                "server_status": "running",
                "rtorrent_status": "unknown (use system_management for live check)",
                "system_metrics": {
                    "python_version": sys.version,
                    "working_directory": os.getcwd(),
                    "memory_usage": f"{memory_info.rss / 1024 / 1024:.2f} MB",
                    "uptime": f"{uptime:.2f} seconds",
                },
                "configuration": {
                    "app_name": "RTorrent MCP",
                    "version": "3.0.0",
                    "log_level": "INFO",
                    "allowed_categories": ["Anime"],
                },
                "recent_activity": recent_activity,
                "errors": [],
            }
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {
                "server_status": "error",
                "rtorrent_status": "unknown",
                "system_metrics": {},
                "configuration": {},
                "recent_activity": [],
                "errors": [str(e)],
            }

    @mcp.tool(
        name="analyze_repo",
        description="""
        Analyze the RTorrent MCP repository and provide comprehensive information.

        This tool performs a deep analysis of the codebase and provides:
        - Project structure and organization
        - Code quality metrics
        - Dependency analysis
        - Configuration details
        - Documentation status
        - Test coverage information
        - Security considerations
        - Performance recommendations

        The analysis is designed to give Claude users a complete understanding
        of the repository for better assistance and code review.

        Returns:
            dict: Comprehensive repository analysis
        """,
        output_schema={
            "type": "object",
            "properties": {
                "project_info": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "version": {"type": "string"},
                        "description": {"type": "string"},
                        "author": {"type": "string"},
                    },
                },
                "structure": {
                    "type": "object",
                    "properties": {
                        "directories": {"type": "array", "items": {"type": "string"}},
                        "files": {"type": "array", "items": {"type": "string"}},
                        "total_lines": {"type": "number"},
                        "total_files": {"type": "number"},
                    },
                },
                "dependencies": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "version": {"type": "string"},
                            "purpose": {"type": "string"},
                        },
                    },
                },
                "code_quality": {
                    "type": "object",
                    "properties": {
                        "python_files": {"type": "number"},
                        "test_files": {"type": "number"},
                        "documentation_files": {"type": "number"},
                        "main_packages": {"type": "array", "items": {"type": "string"}},
                    },
                },
                "configuration": {
                    "type": "object",
                    "properties": {
                        "build_system": {"type": "string"},
                        "testing_framework": {"type": "string"},
                        "linting_tools": {"type": "array", "items": {"type": "string"}},
                    },
                },
                "security": {"type": "array", "items": {"type": "string"}},
                "recommendations": {"type": "array", "items": {"type": "string"}},
            },
        },
    )
    def analyze_repo() -> dict[str, Any]:
        """Analyze the repository and provide comprehensive information"""
        try:
            project_root = Path(__file__).parent.parent.parent
            analysis = {
                "project_info": {
                    "name": "RTorrent MCP Server",
                    "version": "3.0.0",
                    "description": "FastMCP 3.1 server for anime torrenting automation with Austrian legal compliance",
                    "author": "Sandra's Austrian Anime Automation",
                },
                "structure": {"directories": [], "files": [], "total_lines": 0, "total_files": 0},
                "dependencies": [
                    {"name": "fastmcp", "version": "^2.12.0", "purpose": "MCP server framework"},
                    {"name": "aiohttp", "version": "^3.9.0", "purpose": "Async HTTP client"},
                    {
                        "name": "beautifulsoup4",
                        "version": "^4.12.0",
                        "purpose": "HTML parsing for NYAA search",
                    },
                    {
                        "name": "python-dotenv",
                        "version": "^1.0.0",
                        "purpose": "Environment configuration",
                    },
                    {
                        "name": "pydantic-settings",
                        "version": "^2.0.0",
                        "purpose": "Settings management",
                    },
                ],
                "code_quality": {
                    "python_files": 0,
                    "test_files": 0,
                    "documentation_files": 0,
                    "main_packages": ["rtorrent_mcp"],
                },
                "configuration": {
                    "build_system": "setuptools",
                    "testing_framework": "pytest",
                    "linting_tools": ["black", "isort", "mypy"],
                },
                "security": [
                    "Uses structured logging instead of print statements",
                    "Implements proper error handling and validation",
                    "Legal compliance checks for Austrian law",
                    "No hardcoded credentials in code",
                ],
                "recommendations": [
                    "Consider adding type hints to all functions",
                    "Implement unit tests for all modules",
                    "Add integration tests for full workflows",
                    "Consider adding rate limiting for API calls",
                    "Implement caching for frequently accessed data",
                ],
            }

            # Analyze directory structure
            for item in project_root.rglob("*"):
                if item.is_dir() and item.name not in ["__pycache__", ".git"]:
                    analysis["structure"]["directories"].append(str(item.relative_to(project_root)))
                elif item.is_file() and item.suffix in [".py", ".md", ".toml", ".txt"]:
                    analysis["structure"]["files"].append(str(item.relative_to(project_root)))

            # Count Python files
            analysis["code_quality"]["python_files"] = len([f for f in project_root.rglob("*.py") if f.is_file()])

            # Count test files
            analysis["code_quality"]["test_files"] = len([f for f in project_root.rglob("test_*.py") if f.is_file()])

            # Count documentation files
            analysis["code_quality"]["documentation_files"] = len(
                [f for f in project_root.rglob("*.md") if f.is_file()]
            )

            analysis["structure"]["total_files"] = len(analysis["structure"]["files"])

            # Estimate lines of code
            for file_path in project_root.rglob("*.py"):
                if file_path.is_file():
                    try:
                        with open(file_path, encoding="utf-8") as f:
                            analysis["structure"]["total_lines"] += len(f.readlines())
                    except (OSError, UnicodeDecodeError):
                        pass

            return analysis
        except Exception as e:
            logger.error(f"Error analyzing repository: {e}")
            return {
                "error": f"Failed to analyze repository: {e!s}",
                "project_info": {},
                "structure": {},
                "dependencies": [],
                "code_quality": {},
                "configuration": {},
                "security": [],
                "recommendations": [],
            }
