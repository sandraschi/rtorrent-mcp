#!/usr/bin/env python3
"""
RTorrent MCP Server

Main entry point for the RTorrent MCP FastMCP 2.12 server.
"""

import sys
from pathlib import Path

from rtorrent_mcp.server import main as server_main


def main():
    """Run the RTorrent MCP server."""
    # Simple argument handling - just pass the config path if provided
    config_path = ".env"  # Default config file
    if len(sys.argv) > 1 and not sys.argv[1].startswith("-"):
        config_path = sys.argv[1]
        if not Path(config_path).exists():
            print(f"Error: Config file not found: {config_path}", file=sys.stderr)
            sys.exit(1)

    # Run the server
    try:
        server_main(config_path)
    except KeyboardInterrupt:
        print("\nShutting down RTorrent MCP server...")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
