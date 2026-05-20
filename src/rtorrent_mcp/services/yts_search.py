"""
yts_search.py - YTS (yify) movie search functionality for RTorrent MCP
YTS is the gold standard for movie torrents
"""

import logging
from typing import Any
from urllib.parse import quote_plus

import aiohttp

logger = logging.getLogger(__name__)

# YTS API base URL (yts.mx/yts.am)
YTS_API_BASE = "https://yts.mx/api/v2"


async def search_yts_movies(
    query: str, quality: str = "1080p", sort_by: str = "seeds", limit: int = 20
) -> list[dict[str, Any]]:
    """Search YTS for movie releases

    Args:
        query: Movie name to search for
        quality: Preferred quality (720p, 1080p, 2160p, 3D)
        sort_by: Sort by seeds, peers, year, rating, downloads (default: seeds)
        limit: Maximum number of results (default: 20)

    Returns:
        List of movie release dictionaries with torrent details
    """
    try:
        # YTS API format: /api/v2/list_movies.json?query_term=moviename&quality=1080p&sort_by=seeds
        params = {"query_term": query, "quality": quality, "sort_by": sort_by, "limit": limit}

        url = f"{YTS_API_BASE}/list_movies.json"

        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

        async with aiohttp.ClientSession() as session, session.get(url, params=params, headers=headers) as response:
            if response.status != 200:
                logger.error(f"YTS API returned {response.status}")
                return [{"error": f"YTS API returned {response.status}"}]

            data = await response.json()

            if data.get("status") != "ok":
                error_msg = data.get("status_message", "Unknown error")
                logger.error(f"YTS API error: {error_msg}")
                return [{"error": f"YTS API error: {error_msg}"}]

            movies = data.get("data", {}).get("movies", [])
            if not movies:
                logger.info(f"No movies found for query: {query}")
                return []

            results = []

            for movie in movies:
                try:
                    movie_title = movie.get("title", "Unknown")
                    movie_year = movie.get("year", 0)
                    movie_rating = movie.get("rating", 0)
                    movie_runtime = movie.get("runtime", 0)

                    # Get torrents for the preferred quality
                    torrents = movie.get("torrents", [])
                    preferred_torrents = [t for t in torrents if t.get("quality", "").lower() == quality.lower()]

                    # If no preferred quality, use all available
                    if not preferred_torrents:
                        preferred_torrents = torrents

                    # Sort by seeds within quality
                    preferred_torrents.sort(key=lambda x: x.get("seeds", 0), reverse=True)

                    # Take the best torrent for this movie
                    if preferred_torrents:
                        best_torrent = preferred_torrents[0]

                        # YTS provides magnet links
                        magnet = best_torrent.get("url", "")
                        if not magnet.startswith("magnet:"):
                            # YTS sometimes provides hash, construct magnet
                            hash_str = best_torrent.get("hash", "")
                            if hash_str:
                                magnet = f"magnet:?xt=urn:btih:{hash_str}&dn={quote_plus(movie_title)}"

                        results.append(
                            {
                                "title": movie_title,
                                "year": movie_year,
                                "rating": movie_rating,
                                "runtime": movie_runtime,
                                "quality": best_torrent.get("quality", quality),
                                "size": best_torrent.get("size", "Unknown"),
                                "seeds": best_torrent.get("seeds", 0),
                                "peers": best_torrent.get("peers", 0),
                                "magnet": magnet,
                                "imdb_code": movie.get("imdb_code", ""),
                                "yts_id": movie.get("id", 0),
                            }
                        )

                except Exception as e:
                    logger.warning(f"Error parsing YTS movie: {e}")
                    continue

            # Sort by seeds (most active first)
            results.sort(key=lambda x: x["seeds"], reverse=True)
            return results[:10]  # Top 10 results

    except aiohttp.ClientError as e:
        logger.error(f"YTS search network error: {e}")
        return [{"error": f"Network error: {str(e)}"}]
    except Exception as e:
        logger.error(f"YTS search failed: {e}")
        return [{"error": f"Search failed: {str(e)}"}]
