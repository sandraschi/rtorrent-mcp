#!/usr/bin/env python3
"""
Development testing script for qBTMCP
Quick local testing without MCP client setup
"""

import asyncio
import logging
from qbtmcp.nyaa_search import search_nyaa_anime
from qbtmcp.natural_language import process_sandra_command
from qbtmcp.legal_compliance import check_country_legal_status, get_austrian_legal_framework
from qbtmcp.qbittorrent_client import QBittorrentClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_anime_search():
    """Test anime search functionality"""
    print("\n🎌 Testing Anime Search...")
    
    # Test ASW Detective Conan search
    results = await search_nyaa_anime("Detective Conan", "720p", "ASW")
    
    if results and not results[0].get("error"):
        print(f"✅ Found {len(results)} results")
        print(f"Top result: {results[0]['title'][:50]}...")
        print(f"Quality score: {results[0]['quality_score']}")
        print(f"Seeders: {results[0]['seeders']}")
    else:
        print(f"❌ Search failed: {results}")

async def test_natural_language():
    """Test natural language processing"""
    print("\n🗣️ Testing Natural Language Commands...")
    
    commands = [
        "get me this weeks asw anime, 720p",
        "asw detective conan latest episode", 
        "lade detective conan asw 720p"  # German
    ]
    
    for cmd in commands:
        print(f"\nCommand: '{cmd}'")
        result = await process_sandra_command(cmd)
        if result.get("command_understood"):
            print(f"✅ Understood: {result.get('action', 'unknown action')}")
        else:
            print(f"❌ Not understood")

def test_legal_compliance():
    """Test legal compliance checking"""
    print("\n⚖️ Testing Legal Compliance...")
    
    countries = ["austria", "germany", "japan"]
    
    for country in countries:
        status = check_country_legal_status(country)
        print(f"{country.title()}: {status['risk_level']} - {status['warning']}")
    
    # Austrian framework
    austria_info = get_austrian_legal_framework()
    print(f"\n🇦🇹 Sandra in {austria_info['sandra_location']}: {austria_info['legal_status']}")

async def test_qbittorrent_connection():
    """Test qBittorrent connection (if available)"""
    print("\n🔧 Testing qBittorrent Connection...")
    
    client = QBittorrentClient()
    try:
        connected = await client.connect()
        if connected:
            print("✅ Connected to qBittorrent")
            
            # Test getting torrents
            torrents = await client.get_torrents()
            print(f"📊 Found {len(torrents)} torrents")
            
        else:
            print("❌ Failed to connect to qBittorrent")
            print("💡 Make sure qBittorrent is running with Web UI enabled")
            print("   Tools → Options → Web UI → Enable Remote Control")
    
    except Exception as e:
        print(f"❌ qBittorrent connection error: {e}")
        print("💡 Is qBittorrent running on localhost:8080?")
    
    finally:
        await client.close()

async def main():
    """Run all development tests"""
    print("🚀 qBTMCP Development Testing")
    print("🇦🇹 Austrian Anime Automation for Sandra")
    print("=" * 50)
    
    # Test all components
    await test_anime_search()
    await test_natural_language()
    test_legal_compliance()
    await test_qbittorrent_connection()
    
    print("\n" + "=" * 50)
    print("🎯 Development testing complete!")
    print("🎌 Ready for Vienna anime automation!")

if __name__ == "__main__":
    asyncio.run(main())
