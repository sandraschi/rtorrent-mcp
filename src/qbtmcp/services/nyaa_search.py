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

async def search_nyaa_anime(query: str, resolution: str = DEFAULT_RESOLUTION, group: str = DEFAULT_RELEASE_GROUP) -> list[dict[str, Any]]:
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
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        # Try group-specific search first, fallback to broader search if no results
        search_terms = []
        if group:
            search_terms.append(f"{group} {query} {resolution}")
        search_terms.append(f"{query} {resolution}")  # Fallback: search without group

        async with aiohttp.ClientSession() as session:
            for search_term in search_terms:
                encoded_query = quote_plus(search_term)
                url = f"https://nyaa.si/?f=0&c=1_2&q={encoded_query}&s=seeders&o=desc"

                async with session.get(url, headers=headers) as response:
                    if response.status != 200:
                        continue

                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')

                    # nyaa.si table structure: table has class 'torrent-list'
                    table = soup.select_one('table.torrent-list')
                    if not table:
                        # Fallback to any table
                        table = soup.select_one('table')
                    if not table:
                        # No results for this search term, try next
                        continue
                    
                    rows = table.select('tr')
                    if len(rows) <= 1:
                        # Only header row, no results, try next search term
                        continue
                    
                    # Found results! Process them
                    rows = rows[1:11]  # Skip header row, get top 10 results
                    results = []

                    for row in rows:
                        try:
                            cells = row.select('td')
                            if len(cells) < 7:
                                continue
                            
                            # Extract torrent info
                            # Cell structure: 0=icon, 1=title, 2=comments, 3=size, 4=date, 5=seeders, 6=leechers, 7=downloads
                            title_cell = cells[1] if len(cells) > 1 else None
                            if not title_cell:
                                continue
                            
                            # Get title from link or text
                            title_link = title_cell.select_one('a[href^="/view/"]')
                            if title_link:
                                title = title_link.text.strip()
                            else:
                                title = title_cell.text.strip()
                            
                            if not title:
                                continue
                            
                            # Get magnet link
                            magnet_link = row.select_one('a[href^="magnet:"]')
                            magnet = magnet_link.get('href') if magnet_link else None

                            # Parse seeders/leechers (cells 5 and 6)
                            seeders = cells[5].text.strip() if len(cells) > 5 else "0"
                            leechers = cells[6].text.strip() if len(cells) > 6 else "0"

                            # Size parsing (cell 3)
                            size = cells[3].text.strip() if len(cells) > 3 else "Unknown"

                            # Quality scoring (Austrian ASW preference)
                            score = calculate_quality_score(title, resolution)
                            release_group = detect_release_group(title)

                            results.append({
                                "title": title,
                                "magnet": magnet,
                                "seeders": int(seeders) if seeders.isdigit() else 0,
                                "leechers": int(leechers) if leechers.isdigit() else 0,
                                "size": size,
                                "quality_score": score,
                                "release_group": release_group
                            })

                        except Exception as e:
                            logger.warning(f"Error parsing nyaa.si row: {e}")
                            continue

                    # Sort by quality score (ASW preference)
                    results.sort(key=lambda x: x["quality_score"], reverse=True)
                    
                    # If we have results, return them (don't try fallback search)
                    if results:
                        return results[:5]  # Top 5 results
            
            # No results from any search term
            logger.info(f"No results found for query: {query}")
            return []

    except Exception as e:
        logger.error(f"nyaa.si search failed: {e}")
        return [{"error": f"Search failed: {str(e)}"}]

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

    for group in PREFERRED_RELEASE_GROUPS.keys():
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
                "resolution": {"type": "string", "description": "Preferred resolution", "default": "720p"},
                "group": {"type": "string", "description": "Release group", "default": "ASW"}
            },
            "required": ["query"]
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
                    "release_group": {"type": "string"}
                }
            }
        }
    )
    async def search_anime(query: str, resolution: str = "720p", group: str = "ASW") -> list[dict]:
        return await search_nyaa_anime(query, resolution, group)

    @mcp.resource("anime://search/recent")
    def recent_anime_releases() -> str:
        """Recent anime releases information"""
        return json.dumps({
            "description": "Search recent anime releases on nyaa.si",
            "preferred_groups": list(PREFERRED_RELEASE_GROUPS.keys()),
            "default_resolution": DEFAULT_RESOLUTION,
            "austrian_optimized": True
        })
