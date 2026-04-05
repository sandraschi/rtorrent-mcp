#!/usr/bin/env python3
"""
Development testing script for rtorrent-mcp (run from repo root: uv run python dev_test.py).
"""

import asyncio
import logging

from rtorrent_mcp.services.legal_compliance import (
    check_country_legal_status,
    get_austrian_legal_framework,
)
from rtorrent_mcp.services.natural_language import process_sandra_command
from rtorrent_mcp.services.nyaa_search import search_nyaa_anime
from rtorrent_mcp.services.rtorrent_client import RTorrentClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_anime_search():
    """Test anime search functionality"""
    print("\n[Anime search] Testing...")

    results = await search_nyaa_anime("Detective Conan", "720p", "ASW")

    if results and not results[0].get("error"):
        print(f"[OK] Found {len(results)} results")
        print(f"Top result: {results[0]['title'][:50]}...")
        print(f"Quality score: {results[0]['quality_score']}")
        print(f"Seeders: {results[0]['seeders']}")
    else:
        print("[FAIL] Search failed or no results")


async def test_natural_language():
    """Test natural language processing"""
    print("\n Testing Natural Language...")
    result = await process_sandra_command("Find Detective Conan 1080p ASW")
    print(f"Result: {result}")


def test_legal_compliance():
    """Test legal compliance"""
    print("\n[Legal] Testing compliance...")
    countries = ["austria", "germany", "usa"]
    for country in countries:
        status = check_country_legal_status(country)
        print(f"{country.title()}: {status['risk_level']} - {status['warning']}")

    austria_info = get_austrian_legal_framework()
    print(f"\n(AT) Sandra in {austria_info['sandra_location']}: {austria_info['legal_status']}")


async def test_rtorrent_connection():
    """Test rTorrent XML-RPC (if RTORRENT_* reachable)"""
    print("\n[rTorrent] Testing XML-RPC...")

    client = RTorrentClient()
    try:
        connected = await client.connect()
        if connected:
            print("[OK] Connected to rTorrent")
            torrents = await client.get_torrents()
            print(f" Found {len(torrents)} torrents")
        else:
            print(
                "[FAIL] Failed to connect to rTorrent (check RTORRENT_HOST / RTORRENT_PORT, Docker)"
            )
    except Exception as e:
        print(f"[FAIL] rTorrent connection error: {e}")


async def main():
    """Run all development tests"""
    print("[rtorrent-mcp] development testing")
    print("[AT] Austrian Anime Automation for Sandra")
    print("=" * 50)

    await test_anime_search()
    await test_natural_language()
    test_legal_compliance()
    await test_rtorrent_connection()

    print("\n" + "=" * 50)
    print("[OK] Development testing complete!")


if __name__ == "__main__":
    asyncio.run(main())
