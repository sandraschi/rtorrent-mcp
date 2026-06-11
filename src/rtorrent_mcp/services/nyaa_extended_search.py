"""
nyaa_extended_search.py - Extended nyaa.si search for manga, Japanese TV, etc.
Expands nyaa.si search beyond anime to include manga (raw/translated) and Japanese television
"""

import logging
from typing import Any
from urllib.parse import quote_plus

import aiohttp
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# nyaa.si categories:
# 1_1: Anime - Audio
# 1_2: Anime - Video
# 1_3: Anime - Non-English
# 1_4: Anime - Raw
# 2_1: Live Action - Raw
# 2_2: Live Action - Non-English
# 2_3: Live Action - English-translated
# 2_4: Live Action - Movie
# 2_5: Live Action - TV Series
# 3_1: Manga - Raw
# 3_2: Manga - Translated
# 3_3: Manga - Non-English
# 3_4: Manga - English-translated

NYAA_CATEGORIES = {
    "anime": "1_2",
    "anime_raw": "1_4",
    "japanese_tv": "2_5",
    "japanese_tv_raw": "2_1",
    "manga_raw": "3_1",
    "manga_translated": "3_2",
    "manga_english": "3_4",
}


async def search_nyaa_extended(
    query: str, content_type: str = "manga", subcategory: str = "translated"
) -> list[dict[str, Any]]:
    """Search nyaa.si for manga, Japanese TV, or other content types

    Args:
        query: Content name to search for
        content_type: Type of content (manga, japanese_tv)
        subcategory: Subcategory (raw, translated, english for manga; raw for japanese_tv)

    Returns:
        List of release dictionaries with torrent details
    """
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                " (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            )
        }

        # Determine category code
        category_key = content_type
        if content_type == "manga":
            if subcategory == "raw":
                category_key = "manga_raw"
            elif subcategory == "translated":
                category_key = "manga_translated"
            elif subcategory == "english":
                category_key = "manga_english"
        elif content_type == "japanese_tv":
            category_key = "japanese_tv_raw" if subcategory == "raw" else "japanese_tv"

        category_code = NYAA_CATEGORIES.get(category_key, "3_2")  # Default to manga translated

        encoded_query = quote_plus(query)
        url = f"https://nyaa.si/?f=0&c={category_code}&q={encoded_query}&s=seeders&o=desc"

        async with aiohttp.ClientSession() as session, session.get(url, headers=headers) as response:
            if response.status != 200:
                return [{"error": f"nyaa.si returned {response.status}"}]

            html = await response.text()
            soup = BeautifulSoup(html, "html.parser")

            # nyaa.si table structure: table has class 'torrent-list'
            table = soup.select_one("table.torrent-list")
            if not table:
                table = soup.select_one("table")
            if not table:
                logger.warning("No table found on nyaa.si page")
                # Check for "no results" message
                no_results = soup.find(string=lambda text: text and "no results" in text.lower())
                if no_results:
                    logger.info(f"No results found for query: {query}")
                    return []
                return []

            rows = table.select("tr")
            if len(rows) <= 1:
                logger.info(f"No results found for query: {query}")
                return []

            results = []
            rows = rows[1:21]  # Skip header row, get top 20 results

            for row in rows:
                try:
                    cells = row.select("td")
                    if len(cells) < 7:
                        continue

                    # Extract torrent info
                    title_cell = cells[1] if len(cells) > 1 else None
                    if not title_cell:
                        continue

                    title_link = title_cell.select_one('a[href^="/view/"]')
                    title = title_link.text.strip() if title_link else title_cell.text.strip()

                    if not title:
                        continue

                    # Get magnet link
                    magnet_link = row.select_one('a[href^="magnet:"]')
                    magnet = magnet_link.get("href") if magnet_link else None

                    # Parse seeders/leechers
                    seeders = cells[5].text.strip() if len(cells) > 5 else "0"
                    leechers = cells[6].text.strip() if len(cells) > 6 else "0"

                    # Size parsing
                    size = cells[3].text.strip() if len(cells) > 3 else "Unknown"

                    results.append(
                        {
                            "title": title,
                            "magnet": magnet,
                            "seeders": int(seeders) if seeders.isdigit() else 0,
                            "leechers": int(leechers) if leechers.isdigit() else 0,
                            "size": size,
                            "content_type": content_type,
                            "subcategory": subcategory,
                        }
                    )

                except Exception as e:
                    logger.warning(f"Error parsing nyaa.si row: {e}")
                    continue

            # Sort by seeders (most active first)
            results.sort(key=lambda x: x["seeders"], reverse=True)
            return results[:10]  # Top 10 results

    except Exception as e:
        logger.error(f"nyaa.si extended search failed: {e}")
        return [{"error": f"Search failed: {e!s}"}]
