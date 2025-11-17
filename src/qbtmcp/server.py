#!/usr/bin/env python3
"""
RTorrent MCP Server
FastMCP 2.12 compliant server for anime torrenting automation with Austrian legal compliance
"""

import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from fastmcp import FastMCP

# Load environment variables from .env file
load_dotenv()

# Add the project root directory to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import application settings
from qbtmcp.config.settings import settings  # noqa: E402

# Configure structured logging
logger = logging.getLogger(__name__)

class RTorrentMCPServer(FastMCP):
    """RTorrent MCP Server implementation using FastMCP 2.12"""

    def __init__(self, config_path: str | None = None):
        """Initialize the RTorrent MCP server with optional config path"""
        # Load settings
        if config_path and os.path.exists(config_path):
            os.environ["ENV_FILE"] = config_path

        # Initialize FastMCP server with settings
        super().__init__(
            name=settings.APP_NAME,
            instructions=settings.APP_DESCRIPTION,
            log_level=settings.LOG_LEVEL
        )

        self.logger = logging.getLogger(__name__)
        self._settings = settings

    def setup(self):
        """Setup the server and register all tools"""
        # Log configuration
        self.logger.info("🎌 Starting %s v%s", self._settings.APP_NAME, self._settings.APP_VERSION)
        self.logger.info("🔧 Configuration loaded from: %s",
                        os.getenv("ENV_FILE", "default settings"))
        self.logger.info("🇦🇹 Legal Status: Safe for Sandra in Vienna")
        self.logger.info("🎯 Focus: %s",
                        ", ".join(self._settings.ALLOWED_CATEGORIES) + " @ " +
                        "/".join(self._settings.ALLOWED_RESOLUTIONS))

        # Register all MCP tools using the tools package
        from qbtmcp.tools import register_all_tools

        register_all_tools(self, self._settings)

        self.logger.info("✅ Server setup complete")

def main(config_path: str | None = None):
    """Initialize and start the RTorrent MCP server"""
    import argparse

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="RTorrent MCP Server")
    parser.add_argument("--config", type=str, default=".env",
                      help="Path to configuration file (.env)")
    parser.add_argument("--transport", type=str, default="stdio",
                      choices=["stdio", "http"],
                      help="Transport protocol (stdio or http)")
    args = parser.parse_args()

    # Use provided config_path if available, otherwise use args.config
    final_config_path = config_path if config_path is not None else args.config

    # Create and start the server
    try:
        server = RTorrentMCPServer(config_path=final_config_path)
        server.setup()
        if args.transport == "stdio":
            import asyncio
            asyncio.run(server.run_stdio_async())
        else:
            server.run()
    except Exception as e:
        logger.error("❌ Failed to start server: %s", str(e), exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
