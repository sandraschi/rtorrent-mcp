"""
nyaa_search.py - nyaa.si anime search functionality for RTorrent MCP
Austrian anime automation with ASW release group prioritization
"""

import json
import logging
from typing import Any
from urllib.parse import quote_plus

import aiohttp
from bs4 import BeautifulSoup

from . import DEFAULT_RELEASE_GROUP, DEFAULT_RESOLUTION, PREFERRED_RELEASE_GROUPS

logger = logging.getLogger(__name__)


def _get_asw_username() -> str:
    try:
        from rtorrent_mcp.config.settings import settings

        return settings.NYAA_ASW_USERNAME
    except Exception:
        return "AkihitoSubsWeeklies"


async def search_nyaa_anime(
    query: str, resolution: str = DEFAULT_RESOLUTION, group: str = DEFAULT_RELEASE_GROUP
) -> list[dict[str, Any]]:
    """Search nyaa.si for anime releases with Austrian preferences

    Args:
        query: Anime name to search for
        resolution: Preferred resolution (720p, 1080p, 4K)
        group: Release group preference (ASW, SubsPlease, Erai-raws)

    Returns:
        List of anime release dictionaries with quality scoring
    """
    try:
        # Use User-Agent to avoid being blocked
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                " (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            )
        }

        # Optimized search: When ASW is requested, also search ASW user page directly
        # ASW releases are from user "AkihitoSubsWeeklies" on nyaa.si
        search_term = f"{query} {resolution}"
        asw_user_url = None

        # If ASW is requested, prepare direct user page search
        # ASW often releases in 1080p, so try both requested resolution and without resolution filter
        if group and group.upper() == "ASW":
            # Try with requested resolution first
            asw_query = quote_plus(f"{query} {resolution}")
            asw_user_url = f"https://nyaa.si/user/{_get_asw_username()}?f=0&c=1_2&q={asw_query}&s=seeders&o=desc"
            # Also prepare fallback without resolution (ASW often uses 1080p)
            asw_query_no_res = quote_plus(query)
            asw_user_url_fallback = (
                f"https://nyaa.si/user/{_get_asw_username()}?f=0&c=1_2&q={asw_query_no_res}&s=seeders&o=desc"
            )
        else:
            asw_user_url_fallback = None

        async with aiohttp.ClientSession() as session:
            # First, try ASW user page if ASW is requested
            asw_results = []
            if asw_user_url:
                try:
                    async with session.get(asw_user_url, headers=headers) as asw_response:
                        if asw_response.status == 200:
                            asw_html = await asw_response.text()
                            asw_soup = BeautifulSoup(asw_html, "html.parser")
                            asw_table = asw_soup.select_one("table.torrent-list") or asw_soup.select_one("table")

                            if asw_table:
                                asw_rows = asw_table.select("tr")[1:21]  # Top 20 from ASW user
                                for row in asw_rows:
                                    try:
                                        cells = row.select("td")
                                        if len(cells) < 7:
                                            continue
                                        title_cell = cells[1]
                                        title_link = title_cell.select_one('a[href^="/view/"]')
                                        title = title_link.text.strip() if title_link else title_cell.text.strip()
                                        if not title:
                                            continue

                                        magnet_link = row.select_one('a[href^="magnet:"]')
                                        magnet = magnet_link.get("href") if magnet_link else None
                                        seeders = cells[5].text.strip() if len(cells) > 5 else "0"
                                        leechers = cells[6].text.strip() if len(cells) > 6 else "0"
                                        size = cells[3].text.strip() if len(cells) > 3 else "Unknown"

                                        score = calculate_quality_score(title, resolution)
                                        release_group = detect_release_group(title)

                                        asw_results.append(
                                            {
                                                "title": title,
                                                "magnet": magnet,
                                                "seeders": int(seeders) if seeders.isdigit() else 0,
                                                "leechers": int(leechers) if leechers.isdigit() else 0,
                                                "size": size,
                                                "quality_score": score,
                                                "release_group": release_group,
                                            }
                                        )
                                    except Exception as e:
                                        logger.warning(f"Error parsing ASW user page row: {e}")
                                        continue
                except Exception as e:
                    logger.warning(f"Error searching ASW user page: {e}")

            # If no ASW results found and fallback URL exists, try without resolution filter
            if not asw_results and asw_user_url_fallback:
                try:
                    async with session.get(asw_user_url_fallback, headers=headers) as asw_response:
                        if asw_response.status == 200:
                            asw_html = await asw_response.text()
                            asw_soup = BeautifulSoup(asw_html, "html.parser")
                            asw_table = asw_soup.select_one("table.torrent-list") or asw_soup.select_one("table")

                            if asw_table:
                                asw_rows = asw_table.select("tr")[1:21]  # Top 20 from ASW user
                                for row in asw_rows:
                                    try:
                                        cells = row.select("td")
                                        if len(cells) < 7:
                                            continue
                                        title_cell = cells[1]
                                        title_link = title_cell.select_one('a[href^="/view/"]')
                                        title = title_link.text.strip() if title_link else title_cell.text.strip()
                                        if not title:
                                            continue

                                        # Only include if it matches the query (anime name)
                                        if query.lower() not in title.lower():
                                            continue

                                        magnet_link = row.select_one('a[href^="magnet:"]')
                                        magnet = magnet_link.get("href") if magnet_link else None
                                        seeders = cells[5].text.strip() if len(cells) > 5 else "0"
                                        leechers = cells[6].text.strip() if len(cells) > 6 else "0"
                                        size = cells[3].text.strip() if len(cells) > 3 else "Unknown"

                                        score = calculate_quality_score(title, resolution)
                                        release_group = detect_release_group(title)

                                        asw_results.append(
                                            {
                                                "title": title,
                                                "magnet": magnet,
                                                "seeders": int(seeders) if seeders.isdigit() else 0,
                                                "leechers": int(leechers) if leechers.isdigit() else 0,
                                                "size": size,
                                                "quality_score": score,
                                                "release_group": release_group,
                                            }
                                        )
                                    except Exception as e:
                                        logger.warning(f"Error parsing ASW user page fallback row: {e}")
                                        continue
                except Exception as e:
                    logger.warning(f"Error searching ASW user page fallback: {e}")

            # Also do general search
            encoded_query = quote_plus(search_term)
            url = f"https://nyaa.si/?f=0&c=1_2&q={encoded_query}&s=seeders&o=desc"

            async with session.get(url, headers=headers) as response:
                if response.status != 200:
                    return [{"error": f"nyaa.si returned {response.status}"}]

                html = await response.text()
                soup = BeautifulSoup(html, "html.parser")

                # nyaa.si table structure: table has class 'torrent-list'
                table = soup.select_one("table.torrent-list")
                if not table:
                    # Fallback to any table
                    table = soup.select_one("table")
                if not table:
                    logger.warning("No table found on nyaa.si page")
                    return []

                rows = table.select("tr")
                if len(rows) <= 1:
                    # Only header row, no results
                    logger.info(f"No results found for query: {query}")
                    return []

                # Process more results to find ASW releases (search top 50 to ensure we find ASW)
                rows = rows[1:51]  # Skip header row, get top 50 results
                results = []

                for row in rows:
                    try:
                        cells = row.select("td")
                        if len(cells) < 7:
                            continue

                        # Extract torrent info
                        # Cell: 0=icon, 1=title, 2=comments, 3=size, 4=date, 5=seeders, 6=leechers, 7=downloads
                        title_cell = cells[1] if len(cells) > 1 else None
                        if not title_cell:
                            continue

                        # Get title from link or text
                        title_link = title_cell.select_one('a[href^="/view/"]')
                        title = title_link.text.strip() if title_link else title_cell.text.strip()

                        if not title:
                            continue

                        # Get magnet link
                        magnet_link = row.select_one('a[href^="magnet:"]')
                        magnet = magnet_link.get("href") if magnet_link else None

                        # Parse seeders/leechers (cells 5 and 6)
                        seeders = cells[5].text.strip() if len(cells) > 5 else "0"
                        leechers = cells[6].text.strip() if len(cells) > 6 else "0"

                        # Size parsing (cell 3)
                        size = cells[3].text.strip() if len(cells) > 3 else "Unknown"

                        # Quality scoring (Austrian ASW preference)
                        score = calculate_quality_score(title, resolution)
                        release_group = detect_release_group(title)

                        results.append(
                            {
                                "title": title,
                                "magnet": magnet,
                                "seeders": int(seeders) if seeders.isdigit() else 0,
                                "leechers": int(leechers) if leechers.isdigit() else 0,
                                "size": size,
                                "quality_score": score,
                                "release_group": release_group,
                            }
                        )

                    except Exception as e:
                        logger.warning(f"Error parsing nyaa.si row: {e}")
                        continue

                # Combine ASW user page results with general search results
                if asw_results:
                    # Add ASW results to main results (they're already from ASW user, so guaranteed ASW)
                    results.extend(asw_results)
                    # Remove duplicates based on title + size (defends against same-named different encodes)
                    seen = set()
                    unique_results = []
                    for r in results:
                        key = (r["title"].lower(), r.get("size", ""))
                        if key not in seen:
                            seen.add(key)
                            unique_results.append(r)
                    results = unique_results

                # If group is specified, prioritize that group's results
                if group and results:
                    # Separate results by group (case-insensitive match)
                    preferred_results = [r for r in results if r["release_group"].upper() == group.upper()]
                    other_results = [r for r in results if r["release_group"].upper() != group.upper()]

                    # If we found preferred group results, return ONLY those (no fallback)
                    if preferred_results:
                        # Sort preferred results by quality score (highest first)
                        preferred_results.sort(key=lambda x: (x["quality_score"], x["seeders"]), reverse=True)
                        logger.info(
                            f"Found {len(preferred_results)} {group} results (prio over {len(other_results)} others)"
                        )
                        # Return top preferred results only
                        return preferred_results[:5]
                    else:
                        # No preferred group found, log warning but return best available
                        logger.warning(f"No {group} results found in search, returning best available results")

                # Sort by quality score (ASW preference built into scoring)
                results.sort(key=lambda x: x["quality_score"], reverse=True)
                return results[:5]  # Top 5 results

            # No results from any search term
            logger.info(f"No results found for query: {query}")
            return []

    except Exception as e:
        logger.error(f"nyaa.si search failed: {e}")
        return [{"error": f"Search failed: {e!s}"}]


def calculate_quality_score(title: str, preferred_resolution: str) -> int:
    """Calculate quality score for anime release with Austrian preferences"""
    score = 50  # Base score

    title_upper = title.upper()

    # Release group scoring (Austrian ASW preference)
    for group, points in PREFERRED_RELEASE_GROUPS.items():
        if group.upper() in title_upper:
            score += points
            break

    # Resolution preference scoring
    if preferred_resolution.lower() in title.lower():
        score += 50

    return score


def detect_release_group(title: str) -> str:
    """Detect release group from anime title"""
    title_upper = title.upper()

    for group in PREFERRED_RELEASE_GROUPS:
        if group.upper() in title_upper:
            return group

    return "Unknown"


def register_anime_search_tools(mcp):
    """Register anime search tools with FastMCP server"""

    @mcp.tool(
        name="search_anime",
        description="""
        Search nyaa.si for anime releases with Austrian preferences.

        This tool searches for anime torrents on nyaa.si with intelligent scoring
        based on Austrian legal requirements and preferred release groups.

        Args:
            query (str): Anime name to search for
            resolution (str): Preferred resolution (720p, 1080p, 4K) - default: 720p
            group (str): Release group preference (ASW, SubsPlease, Erai-raws) - default: ASW

        Returns:
            list: List of anime releases with quality scoring
        """,
        inputSchema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Anime name"},
                "resolution": {
                    "type": "string",
                    "description": "Preferred resolution",
                    "default": "720p",
                },
                "group": {"type": "string", "description": "Release group", "default": "ASW"},
            },
            "required": ["query"],
        },
        outputSchema={
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "magnet": {"type": "string"},
                    "seeders": {"type": "number"},
                    "leechers": {"type": "number"},
                    "size": {"type": "string"},
                    "quality_score": {"type": "number"},
                    "release_group": {"type": "string"},
                },
            },
        },
    )
    async def search_anime(query: str, resolution: str = "720p", group: str = "ASW") -> list[dict]:
        return await search_nyaa_anime(query, resolution, group)

    @mcp.resource("anime://search/recent")
    def recent_anime_releases() -> str:
        """Recent anime releases information"""
        return json.dumps(
            {
                "description": "Search recent anime releases on nyaa.si",
                "preferred_groups": list(PREFERRED_RELEASE_GROUPS.keys()),
                "default_resolution": DEFAULT_RESOLUTION,
                "austrian_optimized": True,
            }
        )
