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

# The Pirate Bay search defaults (use __init__ versions if available)
try:
    from . import (
        DEFAULT_TV_RELEASE_GROUP as _INIT_GROUP,
    )
    from . import (
        DEFAULT_TV_RESOLUTION as _INIT_RESOLUTION,
    )
    from . import (
        PREFERRED_TV_RELEASE_GROUPS as _INIT_GROUPS,
    )

    PREFERRED_TV_RELEASE_GROUPS = _INIT_GROUPS
    DEFAULT_TV_RESOLUTION = _INIT_RESOLUTION
    DEFAULT_TV_RELEASE_GROUP = _INIT_GROUP
except ImportError:
    PREFERRED_TV_RELEASE_GROUPS = {"MeGusta": 50, "RARBG": 40, "EZTV": 35, "YIFY": 30, "YTS": 25}
    DEFAULT_TV_RESOLUTION = "1080p"
    DEFAULT_TV_RELEASE_GROUP = "MeGusta"


def _get_piratebay_base_url() -> str:
    try:
        from rtorrent_mcp.config.settings import settings

        return settings.PIRATEBAY_BASE_URL
    except Exception:
        return "https://thepiratebay10.xyz"


async def search_piratebay_tv(
    query: str, resolution: str = DEFAULT_TV_RESOLUTION, group: str = DEFAULT_TV_RELEASE_GROUP
) -> list[dict[str, Any]]:
    """Search The Pirate Bay for TV series releases with MeGusta preferences

    Args:
        query: TV show name to search for
        resolution: Preferred resolution (720p, 1080p, 4K)
        group: Release group preference (MeGusta, RARBG, EZTV)

    Returns:
        List of TV release dictionaries with quality scoring
    """
    try:
        # Use User-Agent to avoid being blocked
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                " (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            )
        }

        # Optimized search: Pirate Bay format is "show name season/episode group"
        # Format from web: "south park s28e03 megusta" (group at end, no resolution in search)
        # Pirate Bay search works better when query format matches their standard: "show SxxExx group"
        # Format: "show name S28E03 megusta" (group at end, matches Pirate Bay format)
        search_term_with_group = f"{query} {group}" if group else None

        # Fallback search without group
        search_term = query

        async with aiohttp.ClientSession() as session:
            results = []

            # Try group-specific search first if group specified
            if search_term_with_group:
                encoded_query = quote_plus(search_term_with_group)
                url = f"{_get_piratebay_base_url()}/search/{encoded_query}/1/99/0"

                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, "html.parser")

                        # The Pirate Bay uses table#searchResult
                        table = soup.select_one("table#searchResult")
                        if table:
                            rows = table.select("tr")[1:51]  # Top 50 results

                            for row in rows:
                                try:
                                    cells = row.select("td")
                                    if len(cells) < 7:
                                        continue

                                    # Cell structure: 0=category, 1=title/magnet, 2=uploaded, 3=size, 4=SE, 5=LE, 6=UL
                                    # Title and magnet link are in cell 1
                                    title_cell = cells[1]

                                    # Try different title link selectors
                                    title_link = title_cell.select_one('a[href*="/torrent/"]') or title_cell.select_one(
                                        "a[title]"
                                    )
                                    if not title_link:
                                        continue

                                    # Get title - prefer title attribute, fallback to text
                                    title = title_link.get("title", "")
                                    if not title or title.startswith("Details for "):
                                        # If title starts with "Details for ", get actual title from link text
                                        title = title_link.text.strip()
                                    if not title:
                                        continue

                                    # Clean up "Details for " prefix if present
                                    if title.startswith("Details for "):
                                        title = title[12:].strip()

                                    # Magnet link is also in cell 1
                                    magnet_link = title_cell.select_one('a[href^="magnet:"]')
                                    magnet = magnet_link.get("href") if magnet_link else None

                                    # Seeders (SE) and leechers (LE) - check both possible positions
                                    seeders = "0"
                                    leechers = "0"
                                    if len(cells) > 5:
                                        seeders = cells[5].text.strip()
                                    if len(cells) > 6:
                                        leechers = cells[6].text.strip()

                                    # Size is in cell 3
                                    size = cells[3].text.strip() if len(cells) > 3 else "Unknown"

                                    # Upload date is in cell 2
                                    uploaded = cells[2].text.strip() if len(cells) > 2 else "Unknown"

                                    # Quality scoring (MeGusta preference)
                                    score = calculate_tv_quality_score(title, resolution, group)
                                    release_group = detect_tv_release_group(title)

                                    # Episode detection (supports S28E03 format)
                                    episode_info = extract_episode_info(title)

                                    results.append(
                                        {
                                            "title": title,
                                            "magnet": magnet,
                                            "seeders": int(seeders) if seeders.isdigit() else 0,
                                            "leechers": int(leechers) if leechers.isdigit() else 0,
                                            "size": size,
                                            "uploaded": uploaded,
                                            "quality_score": score,
                                            "release_group": release_group,
                                            "episode_info": episode_info,
                                        }
                                    )
                                except Exception as e:
                                    logger.warning(f"Error parsing The Pirate Bay row: {e}")
                                    continue

            # If group specified and we have results, filter to preferred group AND query match
            if group and results:
                # Extract query terms (excluding season/episode which is already handled)
                query_terms = query.lower().split()
                # Filter: must have preferred group AND match query terms
                preferred_results = []
                for r in results:
                    if r["release_group"].upper() == group.upper():
                        # Check if title matches query terms (at least some words)
                        title_lower = r["title"].lower()
                        # For TV shows, check if show name and episode info match
                        # Allow some flexibility (e.g., "south park" should match)
                        matches = sum(
                            1
                            for term in query_terms
                            if term in title_lower or term.replace(" ", "") in title_lower.replace(" ", "")
                        )
                        if matches >= max(1, len(query_terms) - 1):  # Allow one mismatch for formatting
                            preferred_results.append(r)

                if preferred_results:
                    # Sort by quality score and seeders
                    preferred_results.sort(key=lambda x: (x["quality_score"], x["seeders"]), reverse=True)
                    logger.info(f"Found {len(preferred_results)} {group} results matching query from Pirate Bay")
                    return preferred_results[:10]
                else:
                    # No preferred group found in group-specific search, try fallback
                    logger.warning(f"No {group} results matching query found, trying broader search")

            # If no group-specific results or no group specified, do broader search
            if not results:
                seen_titles = {r["title"].lower() for r in results}
                encoded_query = quote_plus(search_term)
                url = f"{_get_piratebay_base_url()}/search/{encoded_query}/1/99/0"

                async with session.get(url, headers=headers) as response:
                    if response.status != 200:
                        if not results:
                            return [{"error": f"The Pirate Bay returned {response.status}"}]
                        # Continue with existing results
                    else:
                        html = await response.text()
                        soup = BeautifulSoup(html, "html.parser")

                        table = soup.select_one("table#searchResult")
                        if table:
                            rows = table.select("tr")[1:51]  # Top 50 results

                            for row in rows:
                                try:
                                    cells = row.select("td")
                                    if len(cells) < 7:
                                        continue

                                    title_cell = cells[1]

                                    # Try different title link selectors
                                    title_link = title_cell.select_one('a[href*="/torrent/"]') or title_cell.select_one(
                                        "a[title]"
                                    )
                                    if not title_link:
                                        continue

                                    # Get title - prefer title attribute, fallback to text
                                    title = title_link.get("title", "")
                                    if not title or title.startswith("Details for "):
                                        # If title starts with "Details for ", get actual title from link text
                                        title = title_link.text.strip()
                                    if not title:
                                        continue

                                    # Clean up "Details for " prefix if present
                                    if title.startswith("Details for "):
                                        title = title[12:].strip()

                                    # Skip if already in results (avoid duplicates)
                                    if title.lower() in seen_titles:
                                        continue
                                    seen_titles.add(title.lower())

                                    magnet_link = title_cell.select_one('a[href^="magnet:"]')
                                    magnet = magnet_link.get("href") if magnet_link else None

                                    seeders = "0"
                                    leechers = "0"
                                    if len(cells) > 5:
                                        seeders = cells[5].text.strip()
                                    if len(cells) > 6:
                                        leechers = cells[6].text.strip()

                                    size = cells[3].text.strip() if len(cells) > 3 else "Unknown"
                                    uploaded = cells[2].text.strip() if len(cells) > 2 else "Unknown"

                                    score = calculate_tv_quality_score(title, resolution, group or "MeGusta")
                                    release_group = detect_tv_release_group(title)
                                    episode_info = extract_episode_info(title)

                                    results.append(
                                        {
                                            "title": title,
                                            "magnet": magnet,
                                            "seeders": int(seeders) if seeders.isdigit() else 0,
                                            "leechers": int(leechers) if leechers.isdigit() else 0,
                                            "size": size,
                                            "uploaded": uploaded,
                                            "quality_score": score,
                                            "release_group": release_group,
                                            "episode_info": episode_info,
                                        }
                                    )
                                except Exception as e:
                                    logger.warning(f"Error parsing The Pirate Bay row: {e}")
                                    continue

            # Sort by quality score (MeGusta preference built into scoring)
            results.sort(key=lambda x: (x["quality_score"], x["seeders"]), reverse=True)
            return results[:10]  # Top 10 results

    except Exception as e:
        logger.error(f"The Pirate Bay search failed: {e}")
        return [{"error": f"Search failed: {e!s}"}]


def calculate_tv_quality_score(title: str, preferred_resolution: str, preferred_group: str) -> int:
    """Calculate quality score for TV release with MeGusta preferences

    MeGusta is known for excellent small TV episode rips with high quality.
    Prioritize MeGusta releases when available.
    """
    score = 50  # Base score

    title_upper = title.upper()

    # Release group scoring (MeGusta preference - highest priority)
    for group, points in PREFERRED_TV_RELEASE_GROUPS.items():
        if group.upper() in title_upper:
            score += points
            # Extra boost for MeGusta (known for small, high-quality files)
            if group.upper() == "MEGUSTA":
                score += 30
            break

    # Resolution preference scoring
    if preferred_resolution.lower() in title.lower():
        score += 50

    # Codec preference (HEVC x265 gets bonus points - MeGusta uses this)
    if "HEVC" in title_upper or "X265" in title_upper:
        score += 30

    # Size optimization - MeGusta known for small files with great quality
    if "MEGUSTA" in title_upper:
        score += 25  # Extra bonus for MeGusta's efficient encoding

    return score


def detect_tv_release_group(title: str) -> str:
    """Detect release group from TV title"""
    title_upper = title.upper()

    for group in PREFERRED_TV_RELEASE_GROUPS:
        if group.upper() in title_upper:
            return group

    return "Unknown"


def extract_episode_info(title: str) -> dict[str, Any]:
    """Extract episode information from TV show title

    Supports standard formats:
    - S28E03 (season 28, episode 03) - standard format
    - S01E01 (season 1, episode 1)
    - Season 1 Episode 1
    - 1x01
    """
    # Common patterns for TV episodes (S28E03 is the standard format)
    patterns = [
        r"S(\d{1,2})E(\d{1,2})",  # S28E03, S01E01 - standard format
        r"Season\s*(\d{1,2}).*Episode\s*(\d{1,2})",  # Season 28 Episode 03
        r"(\d{1,2})x(\d{1,2})",  # 28x03, 1x01
        r"S(\d{1,2})\s*-\s*E(\d{1,2})",  # S28-E03
    ]

    for pattern in patterns:
        match = re.search(pattern, title, re.IGNORECASE)
        if match:
            season = int(match.group(1))
            episode = int(match.group(2))
            return {
                "season": season,
                "episode": episode,
                "episode_string": f"S{season:02d}E{episode:02d}",
                "format": "SxxExx",  # Standard format indicator
            }

    return {"season": None, "episode": None, "episode_string": None, "format": None}


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
        """,
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
        """,
    )
    async def get_new_episodes(
        show_name: str,
        downloaded_episodes: list[str] | None = None,
        resolution: str = "1080p",
        group: str = "MeGusta",
    ) -> list[dict]:
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
        return json.dumps(
            {
                "description": "Search TV series on The Pirate Bay",
                "preferred_groups": list(PREFERRED_TV_RELEASE_GROUPS.keys()),
                "default_resolution": DEFAULT_TV_RESOLUTION,
                "megusta_optimized": True,
                "features": [
                    "MeGusta release group prioritization",
                    "Episode detection and tracking",
                    "New episode filtering",
                    "Quality scoring based on file size and codec",
                ],
            }
        )
