#!/usr/bin/env python3
"""
qBTMCP - qBittorrent MCP Server
FastMCP 2.10 compliant server for anime torrenting automation with Austrian legal compliance
"""

import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import Optional

from fastmcp import FastMCP, FastMCPServer
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the project root directory to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import application settings
from qbtmcp.config.settings import settings

# Configure logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
    ]
)
logger = logging.getLogger(__name__)

# Import services after logging is configured
from qbtmcp.services.nyaa_search import register_anime_search_tools
from qbtmcp.services.qbittorrent_client import register_qbittorrent_tools
from qbtmcp.services.legal_compliance import register_legal_tools
from qbtmcp.services.natural_language import register_nlp_tools

class QBTMCPServer(FastMCPServer):
    """qBTMCP Server implementation using FastMCP 2.10"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the qBTMCP server with optional config path"""
        # Load settings
        if config_path and os.path.exists(config_path):
            os.environ["ENV_FILE"] = config_path
        
        # Initialize FastMCP server with settings
        super().__init__(
            name=settings.APP_NAME,
            version=settings.APP_VERSION,
            description=settings.APP_DESCRIPTION,
            log_level=settings.LOG_LEVEL,
            host=settings.HOST,
            port=settings.PORT,
            debug=settings.DEBUG
        )
        
        self.logger = logging.getLogger(__name__)
        self.settings = settings
    
    def setup(self):
        """Setup the server and register all tools"""
        # Log configuration
        self.logger.info("🎌 Starting %s v%s", self.settings.APP_NAME, self.settings.APP_VERSION)
        self.logger.info("🔧 Configuration loaded from: %s", 
                        os.getenv("ENV_FILE", "default settings"))
        self.logger.info("🇦🇹 Legal Status: Safe for Sandra in Vienna")
        self.logger.info("🎯 Focus: %s", 
                        ", ".join(self.settings.ALLOWED_CATEGORIES) + " @ " + 
                        "/".join(self.settings.ALLOWED_RESOLUTIONS))
        self.logger.info("📱 Inspector: http://%s:%d/inspector", 
                        self.settings.HOST, self.settings.PORT)
        
        # Register all tool modules with settings
        register_anime_search_tools(self, settings=self.settings)
        register_qbittorrent_tools(self, settings=self.settings)
        register_legal_tools(self, settings=self.settings)
        register_nlp_tools(self, settings=self.settings)
        
        self.logger.info("✅ Server setup complete")

def main():
    """Initialize and start the qBTMCP server"""
    import argparse
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="qBTMCP - qBittorrent MCP Server")
    parser.add_argument("--config", type=str, default=".env",
                      help="Path to configuration file (.env)")
    parser.add_argument("--transport", type=str, default="stdio",
                      choices=["stdio", "http"],
                      help="Transport protocol (stdio or http)")
    args = parser.parse_args()
    
    # Create and start the server
    try:
        server = QBTMCPServer(config_path=args.config)
        server.setup()
        server.run(transport=args.transport)
    except Exception as e:
        logger.error("❌ Failed to start server: %s", str(e), exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
