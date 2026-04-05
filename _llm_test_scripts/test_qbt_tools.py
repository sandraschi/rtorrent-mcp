"""
Test script for main qBTMCP tools

This script tests the core functionality of the qBTMCP server tools.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from rtorrent_mcp.server import RTorrentMCPServer


async def test_system_tools():
    """Test system tools"""
    print("\n" + "=" * 60)
    print("TESTING SYSTEM TOOLS")
    print("=" * 60)

    server = RTorrentMCPServer(config_path=".env")
    server.setup()

    # Test help tool
    print("\n1. Testing help tool (basic level)...")
    try:
        help_tool = await server.get_tool("help")
        result = await help_tool.run({"level": "basic"})
        content = result.content[0].text if result.content else "{}"
        parsed = json.loads(content)
        print("[OK] Help tool works")
        print(f"   Tools found: {len(parsed.get('tools', []))}")
    except Exception as e:
        print(f"[FAIL] Help tool failed: {e}")

    # Test get_system_status
    print("\n2. Testing get_system_status tool...")
    try:
        status_tool = await server.get_tool("get_system_status")
        result = await status_tool.run({})
        content = result.content[0].text if result.content else "{}"
        parsed = json.loads(content)
        print("[OK] System status tool works")
        print(f"   Server status: {parsed.get('server_status')}")
        metrics = parsed.get("system_metrics", {})
        py_version = metrics.get("python_version", "N/A")
        if isinstance(py_version, str):
            print(f"   Python version: {py_version[:50]}")
    except Exception as e:
        print(f"[FAIL] System status tool failed: {e}")

    # Test validate_rtorrent_setup
    print("\n3. Testing validate_rtorrent_setup tool...")
    try:
        validate_tool = await server.get_tool("validate_rtorrent_setup")
        result = await validate_tool.run({})
        content = result.content[0].text if result.content else "{}"
        parsed = json.loads(content)
        print("[OK] Validation tool works")
        print(f"   Installation status: {parsed.get('installation_status')}")
        checks = parsed.get("checks", {})
        print(f"   Checks passed: {sum(1 for v in checks.values() if v)}/{len(checks)}")
    except Exception as e:
        print(f"[FAIL] Validation tool failed: {e}")

    # Test analyze_repo
    print("\n4. Testing analyze_repo tool...")
    try:
        analyze_tool = await server.get_tool("analyze_repo")
        result = await analyze_tool.run({})
        content = result.content[0].text if result.content else "{}"
        parsed = json.loads(content)
        print("[OK] Repository analysis tool works")
        project_info = parsed.get("project_info", {})
        print(f"   Project: {project_info.get('name')} v{project_info.get('version')}")
        code_quality = parsed.get("code_quality", {})
        print(f"   Python files: {code_quality.get('python_files')}")
        print(f"   Test files: {code_quality.get('test_files')}")
    except Exception as e:
        print(f"[FAIL] Repository analysis tool failed: {e}")


async def test_torrent_tools():
    """Test torrent tools"""
    print("\n" + "=" * 60)
    print("TESTING TORRENT TOOLS")
    print("=" * 60)

    server = RTorrentMCPServer(config_path=".env")
    server.setup()

    # Test get_status (from torrent_tools)
    print("\n1. Testing get_status (rTorrent connection)...")
    try:
        status_tool = await server.get_tool("get_status")
        result = await status_tool.run({})
        content = result.content[0].text if result.content else "{}"
        parsed = json.loads(content)
        print("[OK] Status tool works")
        print(f"   Status: {parsed.get('status', 'unknown')}")
        if "host" in parsed:
            print(f"   Host: {parsed.get('host')}:{parsed.get('port', 'N/A')}")
    except Exception as e:
        print(f"[FAIL] Status tool failed: {e}")
        print("   (This is expected if rTorrent is not running)")

    # Test list_torrents
    print("\n2. Testing list_torrents tool...")
    try:
        list_tool = await server.get_tool("list_torrents")
        result = await list_tool.run({})
        content = result.content[0].text if result.content else "[]"
        parsed = json.loads(content)
        print("[OK] List torrents tool works")
        if isinstance(parsed, list):
            print(f"   Torrents found: {len(parsed)}")
            if parsed and len(parsed) > 0:
                first = parsed[0]
                if isinstance(first, dict):
                    print(f"   First torrent: {first.get('name', 'N/A')[:50]}")
        else:
            print(f"   Result type: {type(parsed)}")
    except Exception as e:
        print(f"[FAIL] List torrents tool failed: {e}")
        print("   (This is expected if rTorrent is not running)")


async def test_search_tools():
    """Test search tools"""
    print("\n" + "=" * 60)
    print("TESTING SEARCH TOOLS")
    print("=" * 60)

    server = RTorrentMCPServer(config_path=".env")
    server.setup()

    # Test search_anime
    print("\n1. Testing search_anime tool...")
    try:
        search_tool = await server.get_tool("search_anime")
        result = await search_tool.run({"query": "test", "resolution": "720p", "group": "ASW"})
        content = result.content[0].text if result.content else "[]"
        parsed = json.loads(content)
        print("[OK] Search anime tool works")
        if isinstance(parsed, list):
            print(f"   Results found: {len(parsed)}")
            if parsed and len(parsed) > 0:
                first_result = parsed[0]
                if isinstance(first_result, dict):
                    if "error" not in first_result:
                        print(f"   First result: {first_result.get('title', 'N/A')[:50]}")
                    else:
                        print(f"   Error in result: {first_result.get('error')}")
        else:
            print(f"   Result type: {type(parsed)}")
    except Exception as e:
        print(f"[FAIL] Search anime tool failed: {e}")


async def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("qBTMCP TOOLS TEST SUITE")
    print("=" * 60)
    print("Testing qBTMCP server tools...")

    # Test system tools (synchronous)
    await test_system_tools()

    # Test torrent tools (async)
    await test_torrent_tools()

    # Test search tools (async)
    await test_search_tools()

    print("\n" + "=" * 60)
    print("TEST SUITE COMPLETE")
    print("=" * 60)
    print("\nNote: Some tools may fail if rTorrent is not running or")
    print("      network connectivity is unavailable. This is expected.")


if __name__ == "__main__":
    asyncio.run(main())
