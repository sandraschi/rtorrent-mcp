# pyright: reportUnusedFunction=false
"""
Search Management Portmanteau Tool

Consolidates all search operations into a single tool with action-based interface.
Supports anime, manga, movies, TV shows, ebooks, comics, and metadata searches.
"""

import logging
from typing import Any, Literal

from fastmcp import FastMCP

from ...services.annas_archive_search import get_annas_archive_detail, search_annas_archive
from ...services.gutenberg_search import search_gutenberg
from ...services.metadata_service import get_imdb_metadata, get_tvdb_metadata, search_imdb
from ...services.nyaa_extended_search import search_nyaa_extended
from ...services.nyaa_search import search_nyaa_anime
from ...services.piratebay_extended_search import search_piratebay_category
from ...services.piratebay_search import is_new_episode, search_piratebay_tv
from ...services.tv_nlp_tools import TVShowNLPProcessor
from ...services.yts_search import search_yts_movies

logger = logging.getLogger(__name__)

SEARCH_ACTIONS = {
    "anime": "Search nyaa.si for anime releases with Austrian preferences",
    "manga": "Search nyaa.si for manga releases (raw/translated)",
    "japanese_tv": "Search nyaa.si for Japanese TV series",
    "movies": "Search YTS for movie releases (gold standard for movies)",
    "tv_shows": "Search Pirate Bay for Western TV shows (MeGusta prioritized)",
    "tv_smart": "Smart NLP-powered TV search (natural language queries)",
    "ebooks_annas": "Search Anna's Archive for ebooks (60M+ books!)",
    "ebooks_gutenberg": "Search Project Gutenberg for free public domain books (70,000+ classics!)",
    "ebooks_pb": "Search Pirate Bay for ebooks (weak, use Anna's instead)",
    "comics": "Search Pirate Bay for western comics",
    "annas_detail": "Get detailed torrent info from Anna's Archive page",
    "imdb": "Get IMDb metadata for movie/TV show",
    "imdb_search": "Search IMDb for multiple title matches",
    "tvdb": "Get TVDB metadata for TV show (requires subscription)",
}


def register_search_management_tool(mcp: FastMCP, settings) -> None:
    """Register the search management portmanteau tool."""

    @mcp.tool()
    async def search_management(
        action: Literal[
            "anime",
            "manga",
            "japanese_tv",
            "movies",
            "tv_shows",
            "tv_smart",
            "ebooks_annas",
            "ebooks_gutenberg",
            "ebooks_pb",
            "comics",
            "annas_detail",
            "imdb",
            "imdb_search",
            "tvdb",
        ],
        query: str | None = None,
        resolution: str = "720p",
        group: str = "ASW",
        subcategory: str = "translated",
        quality: str = "1080p",
        sort_by: str = "seeds",
        content_type: str = "books",
        max_results: int = 20,
        limit: int = 20,
        book_url: str | None = None,
        title: str | None = None,
        year: int | None = None,
        imdb_id: str | None = None,
        tvdb_id: int | None = None,
        api_key: str | None = None,
        pin: str | None = None,
        downloaded_episodes: list[str] | None = None,
        new_only: bool = True,
    ) -> dict[str, Any]:
        """
        Comprehensive search management portmanteau tool for torrents and metadata.

        PORTMANTEAU PATTERN RATIONALE:
        Instead of creating 11+ separate tools (one per search type), this tool consolidates related
        search operations into a single interface. Prevents tool explosion (11 tools → 1 tool) while maintaining
        full functionality and improving discoverability. Follows FastMCP 2.12+ best practices.

        SEARCH SOURCES:
        - nyaa.si: Anime, manga, Japanese TV (THE gold standard for anime)
        - YTS: Movies (gold standard for movie torrents)
        - Anna's Archive: Ebooks (60M+ books, 50M+ papers - THE gold standard!)
        - Pirate Bay: Comics, ebooks (fallback)
        - OMDb/TVDB: Metadata enrichment

        Args:
            action (Literal, required): The search operation to perform. Must be one of:
                - "anime": Search nyaa.si (requires: query, optional: resolution, group)
                - "manga": Search nyaa.si (requires: query, optional: subcategory)
                - "japanese_tv": Search nyaa.si (requires: query, optional: subcategory)
                - "movies": Search YTS (requires: query, optional: quality, sort_by, limit)
                - "ebooks_annas": Search Anna's Archive (requires: query, optional: content_type, max_results)
                - "ebooks_pb": Search Pirate Bay (requires: query, optional: max_results)
                - "comics": Search Pirate Bay (requires: query, optional: max_results)
                - "annas_detail": Get Anna's detail page (requires: book_url)
                - "imdb": Get IMDb metadata (requires: title, optional: year, imdb_id)
                - "imdb_search": Search IMDb (requires: title, optional: year)
                - "tvdb": Get TVDB metadata (requires: title, optional: year, tvdb_id)

            query (str | None): Search query for torrent searches.
                Required for: anime, manga, japanese_tv, movies, ebooks_annas, ebooks_pb, comics
                Example: "One Piece", "Detective Conan", "Python Programming"

            resolution (str): Video resolution preference. Used by: anime.
                Default: "720p". Valid: "480p", "720p", "1080p", "2160p"

            group (str): Release group preference. Used by: anime.
                Default: "ASW" (Austrian preference). Valid: "ASW", "SubsPlease", "Erai-raws", etc.

            subcategory (str): Content subcategory. Used by: manga, japanese_tv.
                Default: "translated". Valid: "raw", "translated", "english"

            quality (str): Movie quality. Used by: movies.
                Default: "1080p". Valid: "720p", "1080p", "2160p", "3D"

            sort_by (str): Sort order. Used by: movies.
                Default: "seeds". Valid: "seeds", "peers", "year", "rating", "downloads"

            content_type (str): Content type. Used by: ebooks_annas.
                Default: "books". Valid: "books", "papers"

            max_results (int): Maximum results. Used by: ebooks_annas, ebooks_pb, comics.
                Default: 20

            limit (int): Result limit. Used by: movies. Default: 20

            book_url (str | None): Anna's Archive book URL for detail retrieval.
                Required for: annas_detail

            title (str | None): Title for metadata lookup.
                Required for: imdb, imdb_search, tvdb

            year (int | None): Release year for disambiguation.
                Optional for: imdb, imdb_search, tvdb

            imdb_id (str | None): IMDb ID for direct lookup (e.g., "tt1234567").
                Optional for: imdb

            tvdb_id (int | None): TVDB ID for direct lookup.
                Optional for: tvdb

            api_key (str | None): API key for metadata services.
                Optional for: imdb, imdb_search, tvdb (uses env vars if not provided)

            pin (str | None): TVDB PIN. Optional for: tvdb

        Returns:
            dict[str, Any]: Dictionary containing:
                - success (bool): Boolean indicating if operation succeeded
                - action (str): The action that was performed
                - data (dict|list): Search results or metadata
                - count (int): Number of results (for search actions)
                - error (str | None): Error message if success is False

        Examples:
            # Search anime with Austrian preferences
            result = await search_management(action="anime", query="Detective Conan", resolution="720p", group="ASW")

            # Search manga
            result = await search_management(action="manga", query="One Piece", subcategory="translated")

            # Search movies on YTS
            result = await search_management(action="movies", query="The Matrix", quality="1080p")

            # Search ebooks on Anna's Archive (THE gold standard!)
            result = await search_management(action="ebooks_annas", query="Python Programming", content_type="books")

            # Get IMDb metadata
            result = await search_management(action="imdb", title="The Matrix", year=1999)
        """
        try:
            if action not in SEARCH_ACTIONS:
                return {
                    "success": False,
                    "action": action,
                    "error": f"Invalid action '{action}'. Available: {list(SEARCH_ACTIONS.keys())}",
                }

            logger.info(f"Executing search action: {action}")

            # Anime search
            if action == "anime":
                if not query:
                    return {
                        "success": False,
                        "action": action,
                        "error": "query is required for 'anime' action",
                    }
                results = await search_nyaa_anime(query, resolution, group)
                return {"success": True, "action": action, "data": results, "count": len(results)}

            # Manga search
            if action == "manga":
                if not query:
                    return {
                        "success": False,
                        "action": action,
                        "error": "query is required for 'manga' action",
                    }
                results = await search_nyaa_extended(query, content_type="manga", subcategory=subcategory)
                return {"success": True, "action": action, "data": results, "count": len(results)}

            # Japanese TV search
            if action == "japanese_tv":
                if not query:
                    return {
                        "success": False,
                        "action": action,
                        "error": "query is required for 'japanese_tv' action",
                    }
                results = await search_nyaa_extended(query, content_type="japanese_tv", subcategory=subcategory)
                return {"success": True, "action": action, "data": results, "count": len(results)}

            # Movies search (YTS - gold standard)
            if action == "movies":
                if not query:
                    return {
                        "success": False,
                        "action": action,
                        "error": "query is required for 'movies' action",
                    }
                results = await search_yts_movies(query, quality, sort_by, limit)
                return {"success": True, "action": action, "data": results, "count": len(results)}

            # Ebooks search - Anna's Archive (THE gold standard!)
            if action == "ebooks_annas":
                if not query:
                    return {
                        "success": False,
                        "action": action,
                        "error": "query is required for 'ebooks_annas' action",
                    }
                results = await search_annas_archive(query, content_type, max_results)
                return {"success": True, "action": action, "data": results, "count": len(results)}

            # Ebooks search - Project Gutenberg (70,000+ public domain classics!)
            if action == "ebooks_gutenberg":
                if not query:
                    return {
                        "success": False,
                        "action": action,
                        "error": "query is required for 'ebooks_gutenberg' action",
                    }
                results = await search_gutenberg(query, max_results=max_results)
                return {"success": True, "action": action, "data": results, "count": len(results)}

            # Ebooks search - Pirate Bay (weak)
            if action == "ebooks_pb":
                if not query:
                    return {
                        "success": False,
                        "action": action,
                        "error": "query is required for 'ebooks_pb' action",
                    }
                results = await search_piratebay_category(query, category="ebooks", max_results=max_results)
                return {"success": True, "action": action, "data": results, "count": len(results)}

            # Comics search
            if action == "comics":
                if not query:
                    return {
                        "success": False,
                        "action": action,
                        "error": "query is required for 'comics' action",
                    }
                results = await search_piratebay_category(query, category="comics", max_results=max_results)
                return {"success": True, "action": action, "data": results, "count": len(results)}

            # TV Shows search (Pirate Bay with MeGusta priority)
            if action == "tv_shows":
                if not query:
                    return {
                        "success": False,
                        "action": action,
                        "error": "query is required for 'tv_shows' action",
                    }
                tv_group = group if group != "ASW" else "MeGusta"
                results = await search_piratebay_tv(query, resolution, tv_group)
                # Filter for new episodes if requested
                if new_only and downloaded_episodes:
                    downloaded_set = set(downloaded_episodes)
                    results = [r for r in results if "error" not in r and is_new_episode(r["title"], downloaded_set)]
                return {"success": True, "action": action, "data": results, "count": len(results)}

            # Smart TV search with NLP
            if action == "tv_smart":
                if not query:
                    return {
                        "success": False,
                        "action": action,
                        "error": "query is required for 'tv_smart' action",
                    }
                processor = TVShowNLPProcessor()
                parsed_query = processor.parse_tv_query(query)
                search_params = processor.generate_search_parameters(parsed_query)
                results = await search_piratebay_tv(
                    search_params["query"], search_params["resolution"], search_params["group"]
                )
                # Filter for new episodes
                new_episodes = []
                if parsed_query["new_only"] and downloaded_episodes:
                    downloaded_set = set(downloaded_episodes or [])
                    new_episodes = [
                        r for r in results if "error" not in r and is_new_episode(r["title"], downloaded_set)
                    ]
                elif not parsed_query["new_only"]:
                    new_episodes = [r for r in results if "error" not in r]
                return {
                    "success": True,
                    "action": action,
                    "data": {
                        "parsed_query": parsed_query,
                        "search_results": results,
                        "new_episodes": new_episodes,
                        "recommendations": [],
                    },
                    "count": len(results),
                }

            # Anna's Archive detail
            if action == "annas_detail":
                if not book_url:
                    return {
                        "success": False,
                        "action": action,
                        "error": "book_url is required for 'annas_detail' action",
                    }
                result = await get_annas_archive_detail(book_url)
                return {"success": True, "action": action, "data": result}

            # IMDb metadata
            if action == "imdb":
                if not title:
                    return {
                        "success": False,
                        "action": action,
                        "error": "title is required for 'imdb' action",
                    }
                omdb_key = api_key or getattr(settings, "OMDB_API_KEY", None)
                result = await get_imdb_metadata(title, year, imdb_id, omdb_key)
                return {"success": True, "action": action, "data": result}

            # IMDb search
            if action == "imdb_search":
                if not title:
                    return {
                        "success": False,
                        "action": action,
                        "error": "title is required for 'imdb_search' action",
                    }
                omdb_key = api_key or getattr(settings, "OMDB_API_KEY", None)
                results = await search_imdb(title, year, omdb_key)
                return {"success": True, "action": action, "data": results, "count": len(results)}

            # TVDB metadata
            if action == "tvdb":
                if not title:
                    return {
                        "success": False,
                        "action": action,
                        "error": "title is required for 'tvdb' action",
                    }
                tvdb_key = api_key or getattr(settings, "TVDB_API_KEY", None)
                tvdb_pin = pin or getattr(settings, "TVDB_PIN", None)
                result = await get_tvdb_metadata(title, year, tvdb_id, tvdb_key, tvdb_pin)
                return {"success": True, "action": action, "data": result}

            return {
                "success": False,
                "action": action,
                "error": f"Action '{action}' not implemented",
            }

        except Exception as e:
            logger.error(f"Error in search action '{action}': {e}", exc_info=True)
            return {"success": False, "action": action, "error": f"Search failed: {e!s}"}
