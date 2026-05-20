"""
piratebay_extended_search.py - Extended Pirate Bay search for comics and ebooks
Pirate Bay is good for TV series, comics (western), and ebooks (weak selection)
"""

import logging
from typing import Any
from urllib.parse import quote_plus

import aiohttp
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# The Pirate Bay category codes:
# 601: Comics
# 602: Ebooks
# 99: TV Shows (already implemented)
PIRATEBAY_CATEGORIES = {"comics": "601", "ebooks": "602", "tv": "99"}


def _get_piratebay_base_url() -> str:
    try:
        from rtorrent_mcp.config.settings import settings

        return settings.PIRATEBAY_BASE_URL
    except Exception:
        return "https://thepiratebay10.xyz"


async def search_piratebay_category(
    query: str, category: str = "comics", max_results: int = 20
) -> list[dict[str, Any]]:
    """Search The Pirate Bay for comics or ebooks

    Args:
        query: Comic book/ebook title to search for
        category: Category to search ('comics' or 'ebooks') - default: 'comics'
        max_results: Maximum number of results to return (default: 20)

    Returns:
        List of release dictionaries with torrent details
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        # Get category code
        category_code = PIRATEBAY_CATEGORIES.get(category.lower(), "601")

        # Pirate Bay search URL format: /search/{query}/{page}/{category}/{sort}
        encoded_query = quote_plus(query)
        url = f"{_get_piratebay_base_url()}/search/{encoded_query}/1/{category_code}/0"

        async with aiohttp.ClientSession() as session, session.get(url, headers=headers) as response:
            if response.status != 200:
                logger.error(f"Pirate Bay returned {response.status}")
                return [{"error": f"Pirate Bay returned {response.status}"}]

            html = await response.text()
            soup = BeautifulSoup(html, "html.parser")

            # The Pirate Bay uses table#searchResult
            table = soup.select_one("table#searchResult")
            if not table:
                logger.warning("No results table found on Pirate Bay page")
                # Check for "no results" message
                no_results = soup.find(string=lambda text: text and "no results" in text.lower())
                if no_results:
                    return []
                return []

            rows = table.select("tr")[1 : max_results + 1]  # Skip header row
            results = []

            for row in rows:
                try:
                    cells = row.select("td")
                    if len(cells) < 7:
                        continue

                    # Cell structure: 0=category, 1=title/magnet, 2=uploaded, 3=size, 4=SE, 5=LE, 6=UL
                    title_cell = cells[1]

                    # Get title
                    title_link = title_cell.select_one('a[href*="/torrent/"]') or title_cell.select_one("a[title]")
                    if not title_link:
                        continue

                    title = title_link.get("title", "")
                    if not title or title.startswith("Details for "):
                        title = title_link.text.strip()
                    if not title:
                        continue

                    # Clean up "Details for " prefix
                    if title.startswith("Details for "):
                        title = title[12:].strip()

                    # Get magnet link
                    magnet_link = title_cell.select_one('a[href^="magnet:"]')
                    magnet = magnet_link.get("href") if magnet_link else None

                    # Get seeders/leechers
                    seeders = cells[5].text.strip() if len(cells) > 5 else "0"
                    leechers = cells[6].text.strip() if len(cells) > 6 else "0"

                    # Size
                    size = cells[3].text.strip() if len(cells) > 3 else "Unknown"

                    # Upload date
                    uploaded = cells[2].text.strip() if len(cells) > 2 else "Unknown"

                    results.append(
                        {
                            "title": title,
                            "magnet": magnet,
                            "seeders": int(seeders) if seeders.isdigit() else 0,
                            "leechers": int(leechers) if leechers.isdigit() else 0,
                            "size": size,
                            "uploaded": uploaded,
                            "category": category,
                        }
                    )

                except Exception as e:
                    logger.warning(f"Error parsing Pirate Bay row: {e}")
                    continue

            # Sort by seeders (most active first)
            results.sort(key=lambda x: x["seeders"], reverse=True)
            return results[:max_results]

    except aiohttp.ClientError as e:
        logger.error(f"Pirate Bay network error: {e}")
        return [{"error": f"Network error: {str(e)}"}]
    except Exception as e:
        logger.error(f"Pirate Bay search failed: {e}")
        return [{"error": f"Search failed: {str(e)}"}]
