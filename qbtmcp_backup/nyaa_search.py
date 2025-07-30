"""
nyaa_search.py - nyaa.si anime search functionality for qBTMCP
Austrian anime automation with ASW release group prioritization
"""

import logging
from typing import List, Dict, Any
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import quote_plus

from . import PREFERRED_RELEASE_GROUPS, DEFAULT_RESOLUTION, DEFAULT_RELEASE_GROUP

logger = logging.getLogger(__name__)

async def search_nyaa_anime(query: str, resolution: str = DEFAULT_RESOLUTION, group: str = DEFAULT_RELEASE_GROUP) -> List[Dict[str, Any]]:
    """Search nyaa.si for anime releases with Austrian preferences
    
    Args:
        query: Anime name to search for
        resolution: Preferred resolution (720p, 1080p, 4K)
        group: Release group preference (ASW, SubsPlease, Erai-raws)
    
    Returns:
        List of anime release dictionaries with quality scoring
    """
    try:
        # Format search query for nyaa.si
        search_term = f"{group} {query} {resolution}"
        encoded_query = quote_plus(search_term)
        
        # Search nyaa.si (ASW anime focus)
        url = f"https://nyaa.si/?f=0&c=1_2&q={encoded_query}&s=seeders&o=desc"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    return [{"error": f"nyaa.si returned {response.status}"}]
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                results = []
                rows = soup.select('tbody tr')[:10]  # Top 10 results
                
                for row in rows:
                    try:
                        # Extract torrent info
                        title_cell = row.select_one('td:nth-child(2) a[title]')
                        if not title_cell:
                            continue
                            
                        title = title_cell.get('title', '').strip()
                        magnet_link = row.select_one('a[href^="magnet:"]')
                        magnet = magnet_link.get('href') if magnet_link else None
                        
                        # Parse seeders/leechers
                        seeders = row.select_one('td:nth-child(6)').text.strip() if row.select_one('td:nth-child(6)') else "0"
                        leechers = row.select_one('td:nth-child(7)').text.strip() if row.select_one('td:nth-child(7)') else "0"
                        
                        # Size parsing
                        size_cell = row.select_one('td:nth-child(4)')
                        size = size_cell.text.strip() if size_cell else "Unknown"
                        
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
                return results[:5]  # Top 5 results
                
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
    
    @mcp.tool()
    async def search_anime(query: str, resolution: str = "720p", group: str = "ASW") -> List[dict]:
        """Search nyaa.si for anime releases with Austrian preferences
        
        Args:
            query: Anime name to search for
            resolution: Preferred resolution (720p, 1080p, 4K)
            group: Release group preference (ASW, SubsPlease, Erai-raws)
        """
        return await search_nyaa_anime(query, resolution, group)
    
    @mcp.resource("anime://search/recent")
    def recent_anime_releases() -> str:
        """Recent anime releases information"""
        import json
        return json.dumps({
            "description": "Search recent anime releases on nyaa.si",
            "preferred_groups": list(PREFERRED_RELEASE_GROUPS.keys()),
            "default_resolution": DEFAULT_RESOLUTION,
            "austrian_optimized": True
        })
