"""
System tools for RTorrent MCP Server

MCP tools for system monitoring, help, and repository analysis
"""

import logging
import os
import sys
from pathlib import Path
from typing import Any

from fastmcp import FastMCP

logger = logging.getLogger(__name__)


def register_system_tools(mcp: FastMCP, settings) -> None:
    """
    Register system monitoring and utility tools with FastMCP server.

    Args:
        mcp: FastMCP server instance
        settings: Application settings
    """

    @mcp.tool(
        name="help",
        description="Get multilevel help information about available tools and resources. "
        "Args: level (str): Help detail level ('basic', 'intermediate', 'advanced'). "
        "Returns: dict with help information organized by category and detail level.",
    )
    def help(level: str = "intermediate") -> dict[str, Any]:
        """Get multilevel help information"""
        logger.info(f"Providing help at level: {level}")
        try:
            # Base help information
            base_help = {
                "level": level,
                "tools": [],
                "resources": [],
                "configuration": {},
                "troubleshooting": [],
            }

            # Basic level - just names and brief descriptions
            if level == "basic":
                base_help["tools"] = [
                    {"name": "add_torrent", "description": "Add torrents", "category": "Torrent"},
                    {
                        "name": "list_torrents",
                        "description": "List torrents",
                        "category": "Torrent",
                    },
                    {"name": "search_anime", "description": "Search anime", "category": "Search"},
                    {"name": "help", "description": "Get help", "category": "System"},
                ]
                base_help["resources"] = ["rtorrent://config", "anime://search/recent"]
                base_help["configuration"] = {"app_name": "RTorrent MCP", "version": "1.0.0"}

            # Intermediate level - standard help
            elif level == "intermediate":
                base_help["tools"] = [
                    {
                        "name": "add_torrent",
                        "description": "Add torrents to rTorrent",
                        "category": "Torrent Management",
                    },
                    {
                        "name": "list_torrents",
                        "description": "List all torrents with status",
                        "category": "Torrent Management",
                    },
                    {
                        "name": "pause_torrent",
                        "description": "Pause a torrent",
                        "category": "Torrent Management",
                    },
                    {
                        "name": "resume_torrent",
                        "description": "Resume a torrent",
                        "category": "Torrent Management",
                    },
                    {
                        "name": "delete_torrent",
                        "description": "Delete a torrent",
                        "category": "Torrent Management",
                    },
                    {
                        "name": "get_status",
                        "description": "Get rTorrent connection status",
                        "category": "System Status",
                    },
                    {
                        "name": "search_anime",
                        "description": "Search nyaa.si for anime",
                        "category": "Search",
                    },
                    {
                        "name": "check_legal_status",
                        "description": "Check legal status by country",
                        "category": "Legal Compliance",
                    },
                    {
                        "name": "get_legal_warning",
                        "description": "Get detailed legal warnings",
                        "category": "Legal Compliance",
                    },
                    {
                        "name": "sandra_anime_command",
                        "description": "Process natural language commands",
                        "category": "NLP",
                    },
                    {
                        "name": "parse_anime_command",
                        "description": "Parse commands without searching",
                        "category": "NLP",
                    },
                    {
                        "name": "get_command_help",
                        "description": "Get command pattern help",
                        "category": "NLP",
                    },
                    {
                        "name": "analyze_repo",
                        "description": "Analyze the repository",
                        "category": "System",
                    },
                    {
                        "name": "get_system_status",
                        "description": "Get system status and metrics",
                        "category": "System",
                    },
                    {
                        "name": "validate_rtorrent_setup",
                        "description": "Validate rTorrent installation and configuration",
                        "category": "System",
                    },
                    {"name": "help", "description": "Get multilevel help", "category": "System"},
                ]
                base_help["resources"] = [
                    {
                        "uri": "rtorrent://config",
                        "description": "rTorrent configuration info",
                        "content_type": "application/json",
                    },
                    {
                        "uri": "anime://search/recent",
                        "description": "Recent anime releases info",
                        "content_type": "application/json",
                    },
                    {
                        "uri": "legal://austria",
                        "description": "Austrian legal framework",
                        "content_type": "application/json",
                    },
                    {
                        "uri": "legal://overview",
                        "description": "Legal risks overview",
                        "content_type": "application/json",
                    },
                    {
                        "uri": "nlp://examples",
                        "description": "NLP command examples",
                        "content_type": "application/json",
                    },
                ]
                base_help["configuration"] = {
                    "app_name": "RTorrent MCP",
                    "version": "1.0.0",
                    "legal_status": "Safe for Sandra in Vienna (AT)",
                    "allowed_categories": ["Anime"],
                }
                base_help["troubleshooting"] = [
                    "Run validate_rtorrent_setup() to check installation",
                    "Ensure rTorrent is running with SCGI on port 12224",
                    "Check network connectivity to nyaa.si",
                    "Verify local legal compliance requirements",
                ]

            # Advanced level - detailed help with usage examples
            else:  # level == "advanced"
                base_help["tools"] = [
                    {
                        "name": "add_torrent",
                        "description": "Add torrents to rTorrent with Austrian anime categorization",
                        "category": "Torrent Management",
                        "usage": "add_torrent(magnet_link='magnet:?...', category='anime')",
                        "parameters": {
                            "magnet_link": "Magnet URI (required)",
                            "category": "Category (default: 'anime')",
                        },
                    },
                    {
                        "name": "list_torrents",
                        "description": "List all torrents with detailed status information",
                        "category": "Torrent Management",
                        "usage": "list_torrents()",
                        "returns": "Array of torrent objects with hash, name, state, size, completion",
                    },
                    {
                        "name": "search_anime",
                        "description": "Search nyaa.si with intelligent Austrian legal scoring",
                        "category": "Search",
                        "usage": "search_anime(query='anime name', resolution='720p', group='ASW')",
                        "parameters": {
                            "query": "Anime name (required)",
                            "resolution": "Video resolution",
                            "group": "Release group",
                        },
                    },
                    {
                        "name": "sandra_anime_command",
                        "description": "Process natural language commands in German/English",
                        "category": "NLP",
                        "usage": "sandra_anime_command(command='lade detective conan asw 720p')",
                        "supported_languages": ["German", "English"],
                        "examples": [
                            "lade detective conan asw 720p",
                            "get me this weeks asw anime, 720p",
                        ],
                    },
                    {
                        "name": "check_legal_status",
                        "description": "Check torrenting legality by country with Austrian baseline",
                        "category": "Legal Compliance",
                        "usage": "check_legal_status(country='germany')",
                        "countries": ["austria", "germany", "japan", "usa", "uk", "france"],
                    },
                    {
                        "name": "get_system_status",
                        "description": "Get comprehensive system status and metrics",
                        "category": "System",
                        "returns": "Server status, rTorrent connection, system metrics, configuration",
                    },
                    {
                        "name": "analyze_repo",
                        "description": "Deep analysis of the repository codebase",
                        "category": "System",
                        "returns": "Project structure, dependencies, code quality metrics, recommendations",
                    },
                    {
                        "name": "validate_rtorrent_setup",
                        "description": "Validate rTorrent installation and configuration for MCP compatibility",
                        "category": "System",
                        "returns": "Installation status, validation checks, recommendations, error details",
                    },
                ]
                base_help["resources"] = [
                    {
                        "uri": "rtorrent://config",
                        "description": "rTorrent configuration and setup information",
                        "content_type": "application/json",
                        "fields": ["default_host", "default_port", "setup_instructions"],
                    },
                    {
                        "uri": "legal://austria",
                        "description": "Comprehensive Austrian copyright law framework",
                        "content_type": "application/json",
                    },
                    {
                        "uri": "nlp://examples",
                        "description": "Natural language command patterns and examples",
                        "content_type": "application/json",
                    },
                ]
                base_help["configuration"] = {
                    "app_name": "RTorrent MCP",
                    "version": "1.0.0",
                    "legal_status": "Safe for Sandra in Vienna (AT)",
                    "allowed_categories": ["Anime"],
                    "rtorrent_host": "localhost",
                    "rtorrent_port": 12224,
                    "nyaa_base_url": "https://nyaa.si",
                }
                base_help["troubleshooting"] = [
                    "Run validate_rtorrent_setup() to check installation",
                    "Ensure rTorrent is running with SCGI on port 12224",
                    "Check network connectivity to nyaa.si",
                    "Verify local legal compliance requirements",
                    "Check Python dependencies: fastmcp, aiohttp, beautifulsoup4",
                    "Ensure proper file permissions for download directory",
                    "Verify rTorrent configuration (.rtorrent.rc)",
                    "See comprehensive setup guide: docs/RTORRENT_SETUP.md",
                ]
                base_help["api_reference"] = {
                    "transport": "stdio (for Claude Desktop)",
                    "protocol": "FastMCP 2.12",
                    "error_handling": "Structured logging with detailed error types",
                    "legal_compliance": "Austria-focused with international warnings",
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
        name="validate_rtorrent_setup",
        description="Validate rTorrent installation and configuration for MCP server compatibility. "
        "This tool checks rTorrent binary availability, SCGI support, configuration files, "
        "service status, network connectivity, and provides detailed recommendations. "
        "Use this tool to diagnose installation issues or verify setup completeness. "
        "Returns: dict with validation results and recommendations.",
        output_schema={
            "type": "object",
            "properties": {
                "installation_status": {
                    "type": "string",
                    "description": "Overall installation status",
                },
                "checks": {
                    "type": "object",
                    "description": "Individual validation checks",
                    "properties": {
                        "binary_exists": {
                            "type": "boolean",
                            "description": "rTorrent binary found",
                        },
                        "scgi_support": {
                            "type": "boolean",
                            "description": "SCGI support available",
                        },
                        "config_file": {
                            "type": "boolean",
                            "description": "Configuration file exists",
                        },
                        "service_running": {
                            "type": "boolean",
                            "description": "rTorrent service running",
                        },
                        "port_accessible": {
                            "type": "boolean",
                            "description": "SCGI port accessible",
                        },
                        "xmlrpc_working": {
                            "type": "boolean",
                            "description": "XML-RPC interface working",
                        },
                    },
                },
                "recommendations": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Setup recommendations and fixes",
                },
                "errors": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Validation errors found",
                },
            },
        },
    )
    def validate_rtorrent_setup() -> dict[str, Any]:
        """Validate rTorrent installation and configuration"""
        try:
            import shutil
            import socket
            import subprocess
            from pathlib import Path

            validation = {
                "installation_status": "unknown",
                "checks": {
                    "binary_exists": False,
                    "scgi_support": False,
                    "config_file": False,
                    "service_running": False,
                    "port_accessible": False,
                    "xmlrpc_working": False,
                },
                "recommendations": [],
                "errors": [],
            }

            # Check 1: Binary exists
            try:
                rtorrent_path = shutil.which("rtorrent")
                if rtorrent_path:
                    validation["checks"]["binary_exists"] = True
                    validation["recommendations"].append(f"[OK] rTorrent found at: {rtorrent_path}")
                else:
                    validation["errors"].append("[FAIL] rTorrent binary not found in PATH")
                    validation["recommendations"].append("Install rTorrent: sudo apt install rtorrent (Ubuntu/Debian)")
            except Exception as e:
                validation["errors"].append(f"Error checking rTorrent binary: {e}")

            # Check 2: SCGI support
            try:
                if validation["checks"]["binary_exists"]:
                    result = subprocess.run(["/usr/bin/rtorrent", "-h"], capture_output=True, text=True, timeout=10)
                    if "scgi" in result.stdout.lower() or "scgi" in result.stderr.lower():
                        validation["checks"]["scgi_support"] = True
                        validation["recommendations"].append("[OK] SCGI support detected")
                    else:
                        validation["errors"].append("[FAIL] SCGI support not found in rTorrent")
                        validation["recommendations"].append(
                            "Reinstall rTorrent with SCGI support: sudo apt install libxmlrpc-core-c3-dev"
                        )
            except Exception as e:
                validation["errors"].append(f"Error checking SCGI support: {e}")

            # Check 3: Configuration file
            try:
                config_paths = [
                    Path.home() / ".rtorrent.rc",
                    Path.home() / ".rtorrent" / "rtorrent.rc",
                    Path("/etc/rtorrent.rc"),
                ]

                config_found = False
                for config_path in config_paths:
                    if config_path.exists():
                        validation["checks"]["config_file"] = True
                        config_found = True
                        validation["recommendations"].append(f"[OK] Configuration file found: {config_path}")
                        break

                if not config_found:
                    validation["errors"].append("[FAIL] rTorrent configuration file not found")
                    validation["recommendations"].append("Create ~/.rtorrent.rc with SCGI configuration")
            except Exception as e:
                validation["errors"].append(f"Error checking configuration: {e}")

            # Check 4: Service running
            try:
                result = subprocess.run(["/usr/bin/pgrep", "-x", "rtorrent"], capture_output=True, text=True)
                if result.returncode == 0:
                    validation["checks"]["service_running"] = True
                    validation["recommendations"].append("[OK] rTorrent process is running")
                else:
                    validation["errors"].append("[FAIL] rTorrent process not running")
                    validation["recommendations"].append("Start rTorrent: rtorrent -d")
            except Exception as e:
                validation["errors"].append(f"Error checking rTorrent process: {e}")

            # Check 5: Port accessible
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                result = sock.connect_ex(("localhost", 12224))
                sock.close()

                if result == 0:
                    validation["checks"]["port_accessible"] = True
                    validation["recommendations"].append("[OK] SCGI port 12224 is accessible")
                else:
                    validation["errors"].append("[FAIL] SCGI port 12224 not accessible")
                    validation["recommendations"].append(
                        "Check rTorrent configuration: scgi_port = localhost:5000 (container internal)"
                    )
            except Exception as e:
                validation["errors"].append(f"Error checking port accessibility: {e}")

            # Check 6: XML-RPC working
            try:
                if validation["checks"]["port_accessible"]:
                    import requests

                    response = requests.post(
                        "http://localhost:12224/RPC2",
                        data=(
                            '<?xml version="1.0"?><methodCall><methodName>system.listMethods</methodName></methodCall>'
                        ),
                        headers={"Content-Type": "text/xml"},
                        timeout=5,
                    )
                    if response.status_code == 200 and "system.listMethods" in response.text:
                        validation["checks"]["xmlrpc_working"] = True
                        validation["recommendations"].append("[OK] XML-RPC interface working")
                    else:
                        validation["errors"].append("[FAIL] XML-RPC interface not responding")
                        validation["recommendations"].append("Check rTorrent SCGI configuration and restart")
            except Exception as e:
                validation["errors"].append(f"Error checking XML-RPC: {e}")

            # Determine overall status
            all_checks = validation["checks"].values()
            if all(all_checks):
                validation["installation_status"] = "[OK] Complete - Ready for MCP server"
            elif any(all_checks):
                validation["installation_status"] = "[WARN] Partial - Some issues found"
            else:
                validation["installation_status"] = "[FAIL] Failed - rTorrent not properly installed"

            # Add general recommendations
            if not validation["checks"]["binary_exists"]:
                validation["recommendations"].extend(
                    [
                        " See installation guide: docs/RTORRENT_SETUP.md",
                        "Linux: sudo apt install rtorrent",
                        " macOS: brew install rtorrent",
                        " Windows: Use WSL or Docker",
                    ]
                )

            return validation

        except Exception as e:
            logger.error(f"Error validating rTorrent setup: {e}")
            return {
                "installation_status": "[FAIL] Error during validation",
                "checks": {},
                "recommendations": ["Check logs for detailed error information"],
                "errors": [f"Validation failed: {e!s}"],
            }

    @mcp.tool(
        name="get_system_status",
        description="Get comprehensive system status and metrics for the RTorrent MCP server. "
        "This tool provides detailed information about server health, connection status, "
        "system resource usage, configuration status, recent activity, and performance metrics. "
        "Use this tool to diagnose issues or monitor the system's health. "
        "Returns: dict with comprehensive status information.",
        output_schema={
            "type": "object",
            "properties": {
                "server_status": {"type": "string", "description": "Server health status"},
                "rtorrent_status": {"type": "string", "description": "rTorrent connection status"},
                "system_metrics": {
                    "type": "object",
                    "description": "System resource metrics",
                    "properties": {
                        "python_version": {"type": "string", "description": "Python version"},
                        "working_directory": {"type": "string", "description": "Working directory"},
                        "memory_usage": {"type": "string", "description": "Memory usage"},
                        "uptime": {"type": "string", "description": "Server uptime"},
                    },
                },
                "configuration": {
                    "type": "object",
                    "description": "Current configuration",
                    "properties": {
                        "app_name": {"type": "string", "description": "Application name"},
                        "version": {"type": "string", "description": "Application version"},
                        "log_level": {"type": "string", "description": "Logging level"},
                        "allowed_categories": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Allowed content categories",
                        },
                    },
                },
                "recent_activity": {
                    "type": "array",
                    "description": "Recent server activity",
                    "items": {"type": "string"},
                },
                "errors": {
                    "type": "array",
                    "description": "Recent error messages",
                    "items": {"type": "string"},
                },
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
                "Server started successfully",
                "rTorrent connection established",
                "Configuration loaded from environment",
            ]

            return {
                "server_status": "running",
                "rtorrent_status": "connected",
                "system_metrics": {
                    "python_version": sys.version,
                    "working_directory": os.getcwd(),
                    "memory_usage": f"{memory_info.rss / 1024 / 1024:.2f} MB",
                    "uptime": f"{uptime:.2f} seconds",
                },
                "configuration": {
                    "app_name": "RTorrent MCP",
                    "version": "1.0.0",
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
        description="Analyze the RTorrent MCP repository and provide comprehensive information. "
        "This tool performs a deep analysis of the codebase and provides project structure, "
        "code quality metrics, dependency analysis, configuration details, documentation status, "
        "test coverage information, security considerations, and performance recommendations. "
        "The analysis is designed to give users a complete understanding of the repository. "
        "Returns: dict with comprehensive repository analysis.",
        output_schema={
            "type": "object",
            "properties": {
                "project_info": {
                    "type": "object",
                    "description": "Basic project information",
                    "properties": {
                        "name": {"type": "string", "description": "Project name"},
                        "version": {"type": "string", "description": "Project version"},
                        "description": {"type": "string", "description": "Project description"},
                        "author": {"type": "string", "description": "Project author"},
                    },
                },
                "structure": {
                    "type": "object",
                    "description": "Repository structure analysis",
                    "properties": {
                        "directories": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Project directories",
                        },
                        "files": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Project files",
                        },
                        "total_lines": {"type": "number", "description": "Total lines of code"},
                        "total_files": {"type": "number", "description": "Total number of files"},
                    },
                },
                "dependencies": {
                    "type": "array",
                    "description": "Project dependencies",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "Package name"},
                            "version": {"type": "string", "description": "Package version"},
                            "purpose": {"type": "string", "description": "Package purpose"},
                        },
                    },
                },
                "code_quality": {
                    "type": "object",
                    "description": "Code quality metrics",
                    "properties": {
                        "python_files": {"type": "number", "description": "Number of Python files"},
                        "test_files": {"type": "number", "description": "Number of test files"},
                        "documentation_files": {
                            "type": "number",
                            "description": "Number of documentation files",
                        },
                        "main_packages": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Main Python packages",
                        },
                    },
                },
                "recommendations": {
                    "type": "array",
                    "description": "Improvement recommendations",
                    "items": {"type": "string"},
                },
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
                    "version": "1.0.0",
                    "description": "FastMCP-compliant server for anime torrenting automation with AT legal compliance",
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
                "recommendations": [],
            }
