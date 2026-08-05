"""
metadata_service.py - IMDb and TVDB metadata retrieval for RTorrent MCP
Provides metadata enrichment for movies and TV shows
"""

import logging
from typing import Any

import aiohttp

logger = logging.getLogger(__name__)

# IMDb alternatives (IMDb official API requires AWS subscription)
# Using cinemagoer (IMDbPY) or OMDb API as alternatives
OMDB_API_BASE = "https://www.omdbapi.com"

# TVDB API (v4 requires subscription)
TVDB_API_BASE = "https://api4.thetvdb.com"


async def get_imdb_metadata(
    title: str, year: int | None = None, imdb_id: str | None = None, api_key: str | None = None
) -> dict[str, Any]:
    """Get IMDb metadata for a movie or TV show

    Args:
        title: Movie/TV show title
        year: Release year (optional, helps disambiguate)
        imdb_id: IMDb ID (e.g., tt1234567) - if provided, used directly
        api_key: OMDb API key (optional, free at omdbapi.com)

    Returns:
        Dictionary with IMDb metadata (title, year, rating, plot, etc.)
    """
    try:
        if imdb_id:
            # Direct IMDb ID lookup (most reliable)
            params = {"i": imdb_id}
            params["apikey"] = api_key or ""
        else:
            # Title-based search
            params = {"t": title}
            if year:
                params["y"] = str(year)
            params["apikey"] = api_key or ""

        if not api_key:
            return {
                "error": "OMDb API key required since 2017. Set OMDB_API_KEY in .env or "
                "pass api_key. Free key: https://www.omdbapi.com/apikey.aspx"
            }

        url = OMDB_API_BASE

        async with aiohttp.ClientSession() as session, session.get(url, params=params) as response:
            if response.status != 200:
                logger.error(f"OMDb API returned {response.status}")
                return {"error": f"OMDb API returned {response.status}"}

            data = await response.json()

            if data.get("Response") == "False":
                error_msg = data.get("Error", "Unknown error")
                logger.warning(f"OMDb API error: {error_msg}")
                return {"error": error_msg}

            # Extract relevant metadata
            return {
                "title": data.get("Title", title),
                "year": data.get("Year", year),
                "rated": data.get("Rated", ""),
                "released": data.get("Released", ""),
                "runtime": data.get("Runtime", ""),
                "genre": data.get("Genre", ""),
                "director": data.get("Director", ""),
                "writer": data.get("Writer", ""),
                "actors": data.get("Actors", ""),
                "plot": data.get("Plot", ""),
                "language": data.get("Language", ""),
                "country": data.get("Country", ""),
                "awards": data.get("Awards", ""),
                "poster": data.get("Poster", ""),
                "imdb_rating": data.get("imdbRating", ""),
                "imdb_votes": data.get("imdbVotes", ""),
                "imdb_id": data.get("imdbID", imdb_id),
                "type": data.get("Type", ""),  # movie, series, episode
                "metascore": data.get("Metascore", ""),
            }

    except aiohttp.ClientError as e:
        logger.error(f"IMDb metadata network error: {e}")
        return {"error": f"Network error: {e!s}"}
    except Exception as e:
        logger.error(f"IMDb metadata retrieval failed: {e}")
        return {"error": f"Metadata retrieval failed: {e!s}"}


async def search_imdb(title: str, year: int | None = None, api_key: str | None = None) -> list[dict[str, Any]]:
    """Search IMDb for titles (returns multiple matches)

    Args:
        title: Movie/TV show title to search
        year: Release year (optional)
        api_key: OMDb API key (optional)

    Returns:
        List of matching titles with basic info
    """
    try:
        if not api_key:
            return [{"error": "OMDb API key required since 2017. Set OMDB_API_KEY in .env or pass api_key parameter."}]

        params = {"s": title, "apikey": api_key}
        if year:
            params["y"] = str(year)

        url = OMDB_API_BASE

        async with aiohttp.ClientSession() as session, session.get(url, params=params) as response:
            if response.status != 200:
                return [{"error": f"OMDb API returned {response.status}"}]

            data = await response.json()

            if data.get("Response") == "False":
                error_msg = data.get("Error", "Unknown error")
                return [{"error": error_msg}]

            search_results = data.get("Search", [])
            results = []

            for item in search_results:
                results.append(
                    {
                        "title": item.get("Title", ""),
                        "year": item.get("Year", ""),
                        "imdb_id": item.get("imdbID", ""),
                        "type": item.get("Type", ""),
                        "poster": item.get("Poster", ""),
                    }
                )

            return results

    except Exception as e:
        logger.error(f"IMDb search failed: {e}")
        return [{"error": f"Search failed: {e!s}"}]


async def get_tvdb_metadata(
    title: str,
    year: int | None = None,
    tvdb_id: int | None = None,
    api_key: str | None = None,
    pin: str | None = None,
) -> dict[str, Any]:
    """Get TVDB metadata for a TV show

    Args:
        title: TV show title
        year: Release year (optional)
        tvdb_id: TVDB ID (if known)
        api_key: TVDB API key (required for v4)
        pin: TVDB PIN (required for v4 authentication)

    Returns:
        Dictionary with TVDB metadata (series info, episodes, etc.)

    Note:
        TVDB v4 requires subscription and authentication.
        This is a placeholder implementation - full auth flow needed.
    """
    try:
        if not api_key or not pin:
            logger.warning("TVDB API key and PIN required for v4 API")
            return {
                "error": "TVDB v4 requires API key and PIN subscription",
                "note": "TVDB v4 API requires paid subscription. See https://thetvdb.com/api-information",
            }

        # TVDB v4 authentication flow:
        # 1. POST /login with {"apikey": "...", "pin": "..."}
        # 2. Get token from response
        # 3. Use token in Authorization header for subsequent requests

        # Placeholder implementation
        auth_url = f"{TVDB_API_BASE}/v4/login"

        auth_data = {"apikey": api_key, "pin": pin}

        async with aiohttp.ClientSession() as session, session.post(auth_url, json=auth_data) as auth_response:
            if auth_response.status != 200:
                return {"error": f"TVDB authentication failed: {auth_response.status}"}

            auth_result = await auth_response.json()
            token = auth_result.get("data", {}).get("token")

            if not token:
                return {"error": "Failed to get TVDB authentication token"}

            # Use token to search/get metadata
            headers = {"Authorization": f"Bearer {token}"}

            if tvdb_id:
                metadata_url = f"{TVDB_API_BASE}/v4/series/{tvdb_id}/extended"
            else:
                search_url = f"{TVDB_API_BASE}/v4/search"
                search_params = {"query": title}
                if year:
                    search_params["year"] = str(year)

                async with session.get(search_url, params=search_params, headers=headers) as search_response:
                    if search_response.status != 200:
                        return {"error": f"TVDB search failed: {search_response.status}"}

                    search_data = await search_response.json()
                    results = search_data.get("data", [])

                    if not results:
                        return {"error": f"No TVDB results for: {title}"}

                    tvdb_id = results[0].get("tvdb_id")
                    if not tvdb_id:
                        return {"error": "TVDB search returned no ID"}

                    metadata_url = f"{TVDB_API_BASE}/v4/series/{tvdb_id}/extended"

            async with session.get(metadata_url, headers=headers) as metadata_response:
                if metadata_response.status != 200:
                    return {"error": f"TVDB metadata request failed: {metadata_response.status}"}

                data = await metadata_response.json()
                series_data = data.get("data", {})

                return {
                    "title": series_data.get("name", title),
                    "tvdb_id": series_data.get("tvdb_id", tvdb_id),
                    "year": series_data.get("year", year),
                    "network": series_data.get("network", {}),
                    "status": series_data.get("status", {}),
                    "genres": series_data.get("genres", []),
                    "seasons": series_data.get("seasons", []),
                    "episodes": series_data.get("episodes", []),
                }

    except Exception as e:
        logger.error(f"TVDB metadata retrieval failed: {e}")
        return {"error": f"Metadata retrieval failed: {e!s}"}
