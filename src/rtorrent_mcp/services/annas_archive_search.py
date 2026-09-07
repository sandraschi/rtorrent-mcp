# pyright: reportUnusedFunction=false
"""
annas_archive_search.py - Anna's Archive ebook and paper search functionality
Anna's Archive is the gold standard for ebooks - 60M books, 50M papers, can have 100TB torrents!
Very idiosyncratic UI, but we love Anna!
"""

import logging
import os
from pathlib import Path
from typing import Any
from urllib.parse import quote_plus

import aiohttp
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# Anna's Archive base URL. Overridable via ANNAS_ARCHIVE_BASE env. The default
# uses annas-archive.is (a live, non-Cloudflare-gated mirror). annas-archive.org
# no longer resolves (NXDOMAIN) and annas-archive.li is behind a Cloudflare +
# fingerprint anti-bot gate, so it is NOT the default.
ANNAS_ARCHIVE_BASE = os.environ.get("ANNAS_ARCHIVE_BASE", "https://annas-archive.is").rstrip("/")

# Known mirrors, tried in order on search. Anna's Archive rotates domains, so a
# single hardcoded base goes stale (e.g. annas-archive.org no longer resolves,
# annas-archive.li is Cloudflare-gated, annas-archive.gl 403s plain HTTP).
ANNAS_ARCHIVE_MIRRORS = [
    m.strip().rstrip("/")
    for m in os.environ.get(
        "ANNAS_ARCHIVE_MIRRORS",
        "https://annas-archive.is,https://annas-archive.gl,https://annas-archive.li,https://annas-archive.org",
    ).split(",")
    if m.strip()
]


def _annas_cookie_file() -> Path:
    """gitignored data file that persists the session cookie set via Settings."""
    repo_root = Path(__file__).resolve().parents[3]
    return repo_root / "data" / "annas_session.cookie"


_runtime_cookie: str | None = None


def _load_file_cookie() -> str | None:
    try:
        f = _annas_cookie_file()
        if f.exists():
            val = f.read_text(encoding="utf-8").strip()
            return val or None
    except OSError:
        pass
    return None


def get_annas_session_cookie_value() -> str | None:
    """Resolve the session cookie value: runtime (Settings) > env > file."""
    if _runtime_cookie is not None:
        return _runtime_cookie or None
    env = os.environ.get("ANNAS_SESSION_COOKIE", "").strip()
    if env:
        return env
    return _load_file_cookie()


def set_annas_session_cookie(value: str | None) -> None:
    """Set/clear the session cookie at runtime and persist it (gitignored)."""
    global _runtime_cookie
    val = (value or "").strip()
    _runtime_cookie = val or None
    try:
        f = _annas_cookie_file()
        f.parent.mkdir(parents=True, exist_ok=True)
        if val:
            f.write_text(val, encoding="utf-8")
        else:
            f.unlink(missing_ok=True)
    except OSError as e:
        logger.warning("Could not persist Anna's session cookie: %s", e)


def get_annas_cookie_header() -> str | None:
    """Build a ``Cookie`` header from the Anna's Archive session value.

    Set it via the Settings page (persisted, recommended) or ``ANNAS_SESSION_COOKIE``
    env. Accepts either the full ``name=value`` pair, or a bare value (then
    ``ANNAS_SESSION_COOKIE_NAME`` is used, default ``session``). Returns None when
    unset, so callers simply skip auth.
    """
    raw = get_annas_session_cookie_value()
    if not raw:
        return None
    if "=" in raw:
        return raw
    name = os.environ.get("ANNAS_SESSION_COOKIE_NAME", "session").strip()
    if not name:
        return None
    return f"{name}={raw}"


async def _search_annas_on(base: str, query: str, content_type: str = "books", max_results: int = 20) -> tuple[list[dict[str, Any]], str | None]:
    """Search one Anna's Archive mirror. Returns ``(results, error)`` where
    ``error`` is None on a successful fetch (even if the result list is empty)."""
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                " (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }
        if (cookie := get_annas_cookie_header()):
            headers["Cookie"] = cookie

        # Anna's Archive search URL format
        # Books: /search?q={query}
        # Papers: /search?q={query}&content={content_type}
        encoded_query = quote_plus(query)

        if content_type == "papers":
            url = f"{base}/search?q={encoded_query}&content=papers"
        else:
            url = f"{base}/search?q={encoded_query}"

        async with aiohttp.ClientSession() as session, session.get(url, headers=headers) as response:
            if response.status != 200:
                logger.error(f"Anna's Archive ({base}) returned {response.status}")
                return ([], f"Anna's Archive returned {response.status}")

            html = await response.text()
            soup = BeautifulSoup(html, "html.parser")

            # Anna's Archive has a very idiosyncratic UI
            # Look for result containers - typically in divs with class containing "search-result" or similar
            # The exact structure may vary, so we'll try multiple selectors

            results = []

            # Try common selectors for search results
            # Anna's Archive may use different structures, so we check multiple patterns
            result_containers = (
                soup.select("div.bg-white.rounded-lg")
                or soup.select("div.search-result")
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
                            full_url = f"{base}{href}" if href.startswith("/") else href

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

                    return (results[:max_results] if results else [], None)
                else:
                    logger.warning("No results found on Anna's Archive page")
                    # Check for "no results" message
                    no_results = soup.find(
                        string=lambda text: (
                            bool(text) and ("no results" in text.lower() or "no matches" in text.lower())
                        )
                    )
                    if no_results:
                        return ([], None)
                    return ([], None)

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
                        detail_url = f"{base}{href}" if href.startswith("/") else href

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
                return (results[:max_results], None)

            # Last resort: check if page loaded but structure is different
            # Return minimal result indicating search was performed
            page_text = soup.get_text()
            if query.lower() in page_text.lower():
                # Query appears on page, might be a results page with different structure
                return (
                    [
                        {
                            "title": f"Search performed for: {query}",
                            "detail_url": url,
                            "content_type": content_type,
                            "note": "Anna's Archive UI may have changed - check detail_url manually",
                        }
                    ],
                    None,
                )

            return ([], None)

    except aiohttp.ClientError as e:
        logger.error(f"Anna's Archive network error: {e}")
        return ([], f"Network error: {e!s}")
    except Exception as e:
        logger.error(f"Anna's Archive search failed: {e}")
        return ([], f"Search failed: {e!s}")


async def search_annas_archive(query: str, content_type: str = "books", max_results: int = 20) -> list[dict[str, Any]]:
    """Search Anna's Archive for books or papers, failing over across mirrors.

    Args:
        query: Book/paper title, author, or ISBN to search for
        content_type: Type of content ('books' or 'papers') - default: 'books'
        max_results: Maximum number of results to return (default: 20)

    Returns:
        List of book/paper release dictionaries with torrent details
    """
    last_err: str | None = None
    for base in ANNAS_ARCHIVE_MIRRORS:
        results, err = await _search_annas_on(base, query, content_type, max_results)
        if results:
            return results
        if err is None:
            # Mirror responded OK but genuinely has no matches - don't waste the
            # other mirrors; report the empty result.
            return []
        last_err = err
    return [{"error": f"All Anna's Archive mirrors failed: {last_err}"}]


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
        if (cookie := get_annas_cookie_header()):
            headers["Cookie"] = cookie

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
            # The site logo h1 is often "Anna's Archive"; prefer the <title> tag,
            # which carries "<Book Title> by <Author> | Anna's Archive".
            title_tag = soup.select_one("title")
            if title_tag:
                t = title_tag.get_text(strip=True).split(" | ")[0].strip()
                if t and t.lower() != "anna's archive":
                    title_text = t

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

            # Extract candidate single-file direct-download links (Slow/Fast mirrors,
            # partner CDN, or a direct file URL). These may be JS-gated; the download
            # endpoint validates the response before writing to the depot.
            direct_downloads: list[dict[str, str]] = []
            scan = (
                ["a[href*='slow_download']", "a[href*='/dl/']", "a[href*='/download']"]
                + [f"a[href$='.{ext}']" for ext in
                   ("epub", "pdf", "mobi", "azw3", "txt", "fb2", "djv", "cbr", "cbz", "zip")]
            )
            for selector in scan:
                for a in soup.select(selector):
                    href = str(a.get("href") or "").strip()
                    if not href:
                        continue
                    if href.startswith("/"):
                        href = f"{ANNAS_ARCHIVE_BASE}{href}"
                    label = a.get_text(strip=True) or href.rstrip("/").split("/")[-1] or "download"
                    direct_downloads.append({"label": label, "url": href})

            # De-duplicate, keep order
            seen: set[str] = set()
            uniq: list[dict[str, str]] = []
            for d in direct_downloads:
                if d["url"] not in seen:
                    seen.add(d["url"])
                    uniq.append(d)
            result["direct_downloads"] = uniq

            return result

    except Exception as e:
        logger.error(f"Error fetching Anna's Archive detail: {e}")
        return {"error": f"Detail fetch failed: {e!s}"}
