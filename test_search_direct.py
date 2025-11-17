#!/usr/bin/env python3
"""
Direct test of nyaa.si search functionality
"""

import asyncio
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from qbtmcp.services.nyaa_search import search_nyaa_anime


async def test_search():
    print("🎌 Testing nyaa.si search...")

    # Test simple search
    try:
        results = await search_nyaa_anime("gachiakuta", "720p", "ASW")
        print(f"✅ Search completed: {len(results)} results")

        if results and not results[0].get("error"):
            print(f"📺 First result: {results[0]['title'][:70]}...")
            print(f"🎯 Quality score: {results[0]['quality_score']}")
            print(f"🌱 Seeders: {results[0]['seeders']}")
            print(f"🔗 Has magnet: {'Yes' if results[0]['magnet'] else 'No'}")
        else:
            print(f"❌ Search failed or no results: {results}")

    except Exception as e:
        print(f"💥 Error during search: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_search())
