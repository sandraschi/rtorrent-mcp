#!/usr/bin/env python3
"""
qBTMCP - qBittorrent MCP Server

Main entry point for the qBTMCP FastMCP 2.10 server.
"""

import asyncio
import sys
from pathlib import Path
from typing import Optional

from qbtmcp.server import main as server_main


def main():
    """Run the qBTMCP server."""
    # Handle command line arguments
    config_path = None
    if len(sys.argv) > 1:
        config_path = sys.argv[1]
        if not Path(config_path).exists():
            print(f"Error: Config file not found: {config_path}", file=sys.stderr)
            sys.exit(1)
    
    # Run the server
    try:
        asyncio.run(server_main(config_path))
    except KeyboardInterrupt:
        print("\nShutting down qBTMCP server...")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
