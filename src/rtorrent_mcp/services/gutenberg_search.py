# pyright: reportUnusedFunction=false
"""
gutenberg_search.py - Project Gutenberg public domain e-book search functionality via Gutendex API
Project Gutenberg hosts 70,000+ free public domain books (ideal for pre-1900 classics).
"""

import logging
from typing import Any
from urllib.parse import quote_plus

import aiohttp

logger = logging.getLogger(__name__)

GUTENDEX_BASE_URL = "https://gutendex.com/books"


async def search_gutenberg(query: str, topic: str | None = None, max_results: int = 20) -> list[dict[str, Any]]:
    """Search Project Gutenberg via Gutendex API

    Args:
        query: Book title, author, or keyword search
        topic: Optional topic/subject filter
        max_results: Maximum results to return (default: 20)

    Returns:
        List of book dictionaries with Gutenberg IDs, authors, languages, formats, and direct EPUB links
    """
    try:
        headers = {
            "User-Agent": "rtorrent-mcp/3.1.0 (https://github.com/sandraschi/rtorrent-mcp)",
            "Accept": "application/json",
        }

        url = f"{GUTENDEX_BASE_URL}?search={quote_plus(query)}"
        if topic:
            url += f"&topic={quote_plus(topic)}"

        async with aiohttp.ClientSession() as session, session.get(url, headers=headers) as response:
            if response.status != 200:
                logger.error(f"Gutendex API returned status {response.status}")
                return [{"error": f"Gutendex API error {response.status}"}]

            data = await response.json()
            results = []

            for item in data.get("results", [])[:max_results]:
                book_id = item.get("id")
                title = item.get("title", "Unknown Title")
                
                # Format authors string
                authors = [a.get("name", "") for a in item.get("authors", []) if a.get("name")]
                authors_str = ", ".join(authors) if authors else "Public Domain Author"
                
                # Formats mapping
                formats = item.get("formats", {})
                epub_url = (
                    formats.get("application/epub+zip")
                    or formats.get("application/x-mobipocket-ebook")
                    or formats.get("text/html")
                    or f"https://www.gutenberg.org/ebooks/{book_id}.epub3.images"
                )
                cover_url = (
                    formats.get("image/jpeg")
                    or f"https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.cover.medium.jpg"
                )

                results.append(
                    {
                        "id": book_id,
                        "title": title,
                        "author": authors_str,
                        "authors": authors,
                        "languages": item.get("languages", ["en"]),
                        "subjects": item.get("subjects", [])[:5],
                        "download_count": item.get("download_count", 0),
                        "download_url": epub_url,
                        "cover_url": cover_url,
                        "formats": formats,
                        "gutenberg_url": f"https://www.gutenberg.org/ebooks/{book_id}",
                        "copyright": item.get("copyright", False),
                    }
                )

            return results

    except aiohttp.ClientError as e:
        logger.error(f"Gutenberg search network error: {e}")
        return [{"error": f"Network error: {e!s}"}]
    except Exception as e:
        logger.error(f"Gutenberg search failed: {e}")
        return [{"error": f"Gutenberg search failed: {e!s}"}]
