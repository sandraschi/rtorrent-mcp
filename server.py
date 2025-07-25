#!/usr/bin/env python3
"""
qBTMCP - qBittorrent MCP Server
FastMCP 2.1 compliant server for anime torrenting automation with Austrian legal compliance
"""

import logging
from fastmcp import FastMCP

from qbtmcp.nyaa_search import register_anime_search_tools
from qbtmcp.qbittorrent_client import register_qbittorrent_tools
from qbtmcp.legal_compliance import register_legal_tools
from qbtmcp.natural_language import register_nlp_tools

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create MCP server with FastMCP 2.1
mcp = FastMCP(
    name="qbtmcp",
    version="1.0.0",
    description="qBittorrent automation with nyaa.si anime search and Austrian legal compliance"
)

def main():
    """Initialize and start the qBTMCP server"""
    
    # Register all tool modules
    register_anime_search_tools(mcp)
    register_qbittorrent_tools(mcp)
    register_legal_tools(mcp)
    register_nlp_tools(mcp)
    
    logger.info("🎌 Starting qBTMCP - Austrian Anime Automation")
    logger.info("🇦🇹 Legal Status: Safe for Sandra in Vienna")
    logger.info("🎯 Focus: ASW releases, 720p anime automation")
    logger.info("📱 Inspector: http://localhost:8000/inspector")
    
    # Run with stdio transport for Claude Desktop
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
