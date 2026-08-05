# pyright: reportUnusedFunction=false
"""
annas_archive_search.py - Anna's Archive ebook and paper search functionality
Anna's Archive is the gold standard for ebooks - 60M books, 50M papers, can have 100TB torrents!
Very idiosyncratic UI, but we love Anna!
"""

import logging
from typing import Any
from urllib.parse import quote_plus

import aiohttp
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# Anna's Archive base URL
ANNAS_ARCHIVE_BASE = "https://annas-archive.org"


async def search_annas_archive(query: str, content_type: str = "books", max_results: int = 20) -> list[dict[str, Any]]:
    """Search Anna's Archive for books or papers

    Args:
        query: Book/paper title, author, or ISBN to search for
        content_type: Type of content ('books' or 'papers') - default: 'books'
        max_results: Maximum number of results to return (default: 20)

    Returns:
        List of book/paper release dictionaries with torrent details
    """
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                " (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }

        # Anna's Archive search URL format
        # Books: /search?q={query}
        # Papers: /search?q={query}&content={content_type}
        encoded_query = quote_plus(query)

        if content_type == "papers":
            url = f"{ANNAS_ARCHIVE_BASE}/search?q={encoded_query}&content=papers"
        else:
            url = f"{ANNAS_ARCHIVE_BASE}/search?q={encoded_query}"

        async with aiohttp.ClientSession() as session, session.get(url, headers=headers) as response:
            if response.status != 200:
                logger.error(f"Anna's Archive returned {response.status}")
                return [{"error": f"Anna's Archive returned {response.status}"}]

            html = await response.text()
            soup = BeautifulSoup(html, "html.parser")

            # Anna's Archive has a very idiosyncratic UI
            # Look for result containers - typically in divs with class containing "search-result" or similar
            # The exact structure may vary, so we'll try multiple selectors

            results = []

            # Try common selectors for search results
            # Anna's Archive may use different structures, so we check multiple patterns
            result_containers = (
                soup.select("div.search-result")
                or soup.select("div.result")
                or soup.select('div[class*="result"]')
                or soup.select('div[class*="search-result-item"]')
                or soup.select("div.is-relative")
                or soup.select("tr.search-result")
                or soup.select("article")
                or soup.select("div.book")
                or soup.select("div.paper")
            )

            if not result_containers:
                # Fallback: look for any links that might be to books/papers
                # Anna's Archive typically links to detail pages
                all_links = (
                    soup.select('a[href*="/md5/"]')
                    or soup.select('a[href*="/book/"]')
                    or soup.select('a[href*="/paper/"]')
                )

                if all_links:
                    # Extract basic info from links
                    for link in all_links[:max_results]:
                        try:
                            title = link.text.strip()
                            href = str(link.get("href", "") or "")
                            full_url = f"{ANNAS_ARCHIVE_BASE}{href}" if href.startswith("/") else href

                            if title:
                                results.append(
                                    {
                                        "title": title,
                                        "detail_url": full_url,
                                        "content_type": content_type,
                                        "size": "Unknown",  # Will need to visit detail page for full info
                                        "note": "Partial result - visit detail_url for full torrent info",
                                    }
                                )
                        except Exception as e:
                            logger.warning(f"Error parsing Anna's Archive link: {e}")
                            continue

                    return results[:max_results] if results else []
                else:
                    logger.warning("No results found on Anna's Archive page")
                    # Check for "no results" message
                    no_results = soup.find(
                        string=lambda text: (
                            bool(text) and ("no results" in text.lower() or "no matches" in text.lower())
                        )
                    )
                    if no_results:
                        return []
                    return []

            # Process result containers
            for container in result_containers[:max_results]:
                try:
                    # Extract title
                    title_elem = (
                        container.select_one("h2 a")
                        or container.select_one("h3 a")
                        or container.select_one('a[href*="/md5/"]')
                        or container.select_one('a[href*="/book/"]')
                        or container.select_one('a[href*="/paper/"]')
                        or container.select_one("a.title")
                    )

                    title = title_elem.text.strip() if title_elem else container.get_text(strip=True)[:200]
                    if not title:
                        continue

                    # Get detail URL
                    detail_url = None
                    if title_elem:
                        href = str(title_elem.get("href", "") or "")
                        detail_url = f"{ANNAS_ARCHIVE_BASE}{href}" if href.startswith("/") else href

                    # Extract metadata if available
                    # Anna's Archive may show author, size, format, etc. in the container
                    author = ""
                    size = "Unknown"
                    format_type = "Unknown"

                    # Try to extract author
                    author_elem = container.select_one(".author") or container.select_one('[class*="author"]')
                    if author_elem:
                        author = author_elem.text.strip()

                    # Try to extract size
                    size_elem = container.select_one('[class*="size"]') or container.select_one(".size")
                    if size_elem:
                        size = size_elem.text.strip()

                    # Try to extract format
                    format_elem = container.select_one('[class*="format"]') or container.select_one(".format")
                    if format_elem:
                        format_type = format_elem.text.strip()

                    # For full torrent info (including magnet links), we'd need to visit the detail page
                    # For now, return basic info with detail URL
                    results.append(
                        {
                            "title": title,
                            "author": author,
                            "detail_url": detail_url or url,
                            "size": size,
                            "format": format_type,
                            "content_type": content_type,
                            "note": "Visit detail_url for full torrent info (can be 100TB+!)",
                        }
                    )

                except Exception as e:
                    logger.warning(f"Error parsing Anna's Archive result: {e}")
                    continue

            # If we got results from containers, return them
            if results:
                return results[:max_results]

            # Last resort: check if page loaded but structure is different
            # Return minimal result indicating search was performed
            page_text = soup.get_text()
            if query.lower() in page_text.lower():
                # Query appears on page, might be a results page with different structure
                return [
                    {
                        "title": f"Search performed for: {query}",
                        "detail_url": url,
                        "content_type": content_type,
                        "note": "Anna's Archive UI may have changed - check detail_url manually",
                    }
                ]

            return []

    except aiohttp.ClientError as e:
        logger.error(f"Anna's Archive network error: {e}")
        return [{"error": f"Network error: {e!s}"}]
    except Exception as e:
        logger.error(f"Anna's Archive search failed: {e}")
        return [{"error": f"Search failed: {e!s}"}]


async def get_annas_archive_detail(book_url: str) -> dict[str, Any]:
    """Get detailed torrent information from Anna's Archive detail page

    Args:
        book_url: Full URL to Anna's Archive book/paper detail page

    Returns:
        Dictionary with detailed torrent info including magnet links
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }

        async with aiohttp.ClientSession() as session, session.get(book_url, headers=headers) as response:
            if response.status != 200:
                return {"error": f"Failed to fetch detail page: {response.status}"}

            html = await response.text()
            soup = BeautifulSoup(html, "html.parser")

            # Extract torrent/magnet links from detail page
            magnet_links = soup.select('a[href^="magnet:"]')
            torrent_links = soup.select('a[href$=".torrent"]')

            # Extract metadata
            title = soup.select_one("h1") or soup.select_one("h2") or soup.select_one("title")
            title_text = title.text.strip() if title else "Unknown"

            result = {
                "title": title_text,
                "detail_url": book_url,
                "magnets": [link.get("href") for link in magnet_links],
                "torrent_files": [link.get("href") for link in torrent_links],
                "size": "Unknown",
                "formats": [],
            }

            # Try to extract size (Anna's Archive can have massive files - 100TB+!)
            size_elem = (
                soup.select_one('[class*="size"]')
                or soup.select_one(".file-size")
                or soup.select_one('[id*="size"]')
                or soup.select_one("dd")
                or soup.select_one('[class*="metadata"]')
            )
            if size_elem:
                result["size"] = size_elem.text.strip()

            return result

    except Exception as e:
        logger.error(f"Error fetching Anna's Archive detail: {e}")
        return {"error": f"Detail fetch failed: {e!s}"}
