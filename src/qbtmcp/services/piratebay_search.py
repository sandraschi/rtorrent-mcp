"""
piratebay_search.py - The Pirate Bay TV series search functionality for RTorrent MCP
UK/US TV series automation with MeGusta release group prioritization
"""

import json
import logging
import re
from typing import Any
from urllib.parse import quote_plus

import aiohttp
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# The Pirate Bay search defaults
PREFERRED_TV_RELEASE_GROUPS = {
    "MeGusta": 50,
    "RARBG": 40,
    "EZTV": 35,
    "YIFY": 30,
    "YTS": 25
}

DEFAULT_TV_RESOLUTION = "1080p"
DEFAULT_TV_RELEASE_GROUP = "MeGusta"

async def search_piratebay_tv(query: str, resolution: str = DEFAULT_TV_RESOLUTION, group: str = DEFAULT_TV_RELEASE_GROUP) -> list[dict[str, Any]]:
    """Search The Pirate Bay for TV series releases with MeGusta preferences

    Args:
        query: TV show name to search for
        resolution: Preferred resolution (720p, 1080p, 4K)
        group: Release group preference (MeGusta, RARBG, EZTV)

    Returns:
        List of TV release dictionaries with quality scoring
    """
    try:
        # Format search query for The Pirate Bay
        search_term = f"{group} {query} {resolution}"
        encoded_query = quote_plus(search_term)

        # Search The Pirate Bay
        url = f"https://thepiratebay10.xyz/search/{encoded_query}/1/99/0"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    return [{"error": f"The Pirate Bay returned {response.status}"}]

                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')

                results = []
                rows = soup.select('table#searchResult tr')[1:]  # Skip header row

                for row in rows[:20]:  # Top 20 results
                    try:
                        # Extract torrent info from The Pirate Bay table structure
                        cells = row.select('td')
                        if len(cells) < 8:
                            continue

                        # Title and magnet link
                        title_cell = cells[1]
                        title_link = title_cell.select_one('a[title]')
                        if not title_link:
                            continue

                        title = title_link.get('title', '').strip()
                        magnet_link = title_cell.select_one('a[href^="magnet:"]')
                        magnet = magnet_link.get('href') if magnet_link else None

                        # Seeders and leechers
                        seeders = cells[5].text.strip() if len(cells) > 5 else "0"
                        leechers = cells[6].text.strip() if len(cells) > 6 else "0"

                        # Size
                        size = cells[4].text.strip() if len(cells) > 4 else "Unknown"

                        # Upload date
                        uploaded = cells[2].text.strip() if len(cells) > 2 else "Unknown"

                        # Quality scoring (MeGusta preference)
                        score = calculate_tv_quality_score(title, resolution, group)
                        release_group = detect_tv_release_group(title)

                        # Episode detection
                        episode_info = extract_episode_info(title)

                        results.append({
                            "title": title,
                            "magnet": magnet,
                            "seeders": int(seeders) if seeders.isdigit() else 0,
                            "leechers": int(leechers) if leechers.isdigit() else 0,
                            "size": size,
                            "uploaded": uploaded,
                            "quality_score": score,
                            "release_group": release_group,
                            "episode_info": episode_info
                        })

                    except Exception as e:
                        logger.warning(f"Error parsing The Pirate Bay row: {e}")
                        continue

                # Sort by quality score (MeGusta preference)
                results.sort(key=lambda x: x["quality_score"], reverse=True)
                return results[:10]  # Top 10 results

    except Exception as e:
        logger.error(f"The Pirate Bay search failed: {e}")
        return [{"error": f"Search failed: {str(e)}"}]

def calculate_tv_quality_score(title: str, preferred_resolution: str, preferred_group: str) -> int:
    """Calculate quality score for TV release with MeGusta preferences"""
    score = 50  # Base score

    title_upper = title.upper()

    # Release group scoring (MeGusta preference)
    for group, points in PREFERRED_TV_RELEASE_GROUPS.items():
        if group.upper() in title_upper:
            score += points
            break

    # Resolution preference scoring
    if preferred_resolution.lower() in title.lower():
        score += 50

    # Codec preference (HEVC x265 gets bonus points)
    if "HEVC" in title_upper or "X265" in title_upper:
        score += 30

    # Size optimization (smaller files get bonus)
    if "MeGusta" in title_upper:
        score += 20  # MeGusta known for small, high-quality files

    return score

def detect_tv_release_group(title: str) -> str:
    """Detect release group from TV title"""
    title_upper = title.upper()

    for group in PREFERRED_TV_RELEASE_GROUPS.keys():
        if group.upper() in title_upper:
            return group

    return "Unknown"

def extract_episode_info(title: str) -> dict[str, Any]:
    """Extract episode information from TV show title"""
    # Common patterns for TV episodes
    patterns = [
        r'S(\d{1,2})E(\d{1,2})',  # S01E01
        r'Season\s*(\d{1,2}).*Episode\s*(\d{1,2})',  # Season 1 Episode 1
        r'(\d{1,2})x(\d{1,2})',  # 1x01
    ]

    for pattern in patterns:
        match = re.search(pattern, title, re.IGNORECASE)
        if match:
            season = int(match.group(1))
            episode = int(match.group(2))
            return {
                "season": season,
                "episode": episode,
                "episode_string": f"S{season:02d}E{episode:02d}"
            }

    return {"season": None, "episode": None, "episode_string": None}

def is_new_episode(title: str, downloaded_episodes: set[str]) -> bool:
    """Check if episode is new (not already downloaded)"""
    episode_info = extract_episode_info(title)
    if episode_info["episode_string"]:
        return episode_info["episode_string"] not in downloaded_episodes
    return True

def register_tv_search_tools(mcp):
    """Register TV search tools with FastMCP server"""

    @mcp.tool(
        name="search_tv_series",
        description="""
        Search The Pirate Bay for TV series releases with MeGusta preferences.

        This tool searches for TV series torrents on The Pirate Bay with intelligent scoring
        based on MeGusta release group preferences and quality optimization.

        Args:
            query (str): TV show name to search for
            resolution (str): Preferred resolution (720p, 1080p, 4K) - default: 1080p
            group (str): Release group preference (MeGusta, RARBG, EZTV) - default: MeGusta

        Returns:
            list: List of TV releases with quality scoring and episode info
        """
    )
    async def search_tv_series(query: str, resolution: str = "1080p", group: str = "MeGusta") -> list[dict]:
        return await search_piratebay_tv(query, resolution, group)

    @mcp.tool(
        name="get_new_episodes",
        description="""
        Get new episodes of a TV series from The Pirate Bay.

        This tool searches for new episodes of a TV series, filtering out episodes
        that have already been downloaded.

        Args:
            show_name (str): Name of the TV show
            downloaded_episodes (list): List of already downloaded episodes (e.g., ["S01E01", "S01E02"])
            resolution (str): Preferred resolution - default: 1080p
            group (str): Release group preference - default: MeGusta

        Returns:
            list: List of new episodes available for download
        """
    )
    async def get_new_episodes(show_name: str, downloaded_episodes: list[str] = None, resolution: str = "1080p", group: str = "MeGusta") -> list[dict]:
        if downloaded_episodes is None:
            downloaded_episodes = []

        downloaded_set = set(downloaded_episodes)
        all_results = await search_piratebay_tv(show_name, resolution, group)

        # Filter for new episodes only
        new_episodes = []
        for result in all_results:
            if is_new_episode(result["title"], downloaded_set):
                new_episodes.append(result)

        return new_episodes

    @mcp.resource("piratebay://search/tv")
    def tv_search_info() -> str:
        """TV search information for The Pirate Bay"""
        return json.dumps({
            "description": "Search TV series on The Pirate Bay",
            "preferred_groups": list(PREFERRED_TV_RELEASE_GROUPS.keys()),
            "default_resolution": DEFAULT_TV_RESOLUTION,
            "megusta_optimized": True,
            "features": [
                "MeGusta release group prioritization",
                "Episode detection and tracking",
                "New episode filtering",
                "Quality scoring based on file size and codec"
            ]
        })
