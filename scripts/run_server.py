#!/usr/bin/env python3
"""
Script to run the RTorrent MCP server
"""

import sys
import os
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from qbtmcp.server import main

if __name__ == "__main__":
    main()
