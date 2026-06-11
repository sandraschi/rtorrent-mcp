"""
Search tools for RTorrent MCP Server

MCP tools for anime, manga, Japanese TV, movies, and metadata search
"""

import logging

from fastmcp import FastMCP

from ..services.annas_archive_search import get_annas_archive_detail, search_annas_archive
from ..services.metadata_service import get_imdb_metadata, get_tvdb_metadata, search_imdb
from ..services.nyaa_extended_search import search_nyaa_extended
from ..services.nyaa_search import search_nyaa_anime
from ..services.piratebay_extended_search import search_piratebay_category
from ..services.yts_search import search_yts_movies

logger = logging.getLogger(__name__)


def register_search_tools(mcp: FastMCP, settings) -> None:
    """
    Register search tools with FastMCP server.

    Args:
        mcp: FastMCP server instance
        settings: Application settings
    """

    @mcp.tool(
        name="search_anime",
        description="Search nyaa.si for anime releases with Austrian preferences. "
        "This tool searches for anime torrents on nyaa.si with intelligent scoring "
        "based on Austrian legal requirements and preferred release groups. "
        "Args: query (str): Anime name to search for, "
        "resolution (str): Preferred resolution (default: '720p'), "
        "group (str): Release group preference (default: 'ASW'). "
        "Returns: array of anime releases with quality scoring and torrent details.",
    )
    async def search_anime(query: str, resolution: str = "720p", group: str = "ASW") -> list[dict]:
        """Search nyaa.si for anime releases with Austrian preferences"""
        try:
            return await search_nyaa_anime(query, resolution, group)
        except Exception as e:
            logger.error(f"Error searching anime '{query}': {e}")
            return [{"error": f"Search failed: {e!s}"}]

    @mcp.tool(
        name="search_manga",
        description="Search nyaa.si for manga releases (raw or translated). "
        "Args: query (str): Manga name to search for, "
        "subcategory (str): 'raw', 'translated', or 'english' (default: 'translated'). "
        "Returns: array of manga releases with torrent details.",
    )
    async def search_manga(query: str, subcategory: str = "translated") -> list[dict]:
        """Search nyaa.si for manga releases"""
        try:
            return await search_nyaa_extended(query, content_type="manga", subcategory=subcategory)
        except Exception as e:
            logger.error(f"Error searching manga '{query}': {e}")
            return [{"error": f"Search failed: {e!s}"}]

    @mcp.tool(
        name="search_japanese_tv",
        description="Search nyaa.si for Japanese television series (raw or translated). "
        "Args: query (str): TV series name to search for, "
        "subcategory (str): 'raw' or 'translated' (default: 'translated'). "
        "Returns: array of Japanese TV releases with torrent details.",
    )
    async def search_japanese_tv(query: str, subcategory: str = "translated") -> list[dict]:
        """Search nyaa.si for Japanese TV series"""
        try:
            return await search_nyaa_extended(query, content_type="japanese_tv", subcategory=subcategory)
        except Exception as e:
            logger.error(f"Error searching Japanese TV '{query}': {e}")
            return [{"error": f"Search failed: {e!s}"}]

    @mcp.tool(
        name="search_movies",
        description="Search YTS (yify) for movie releases - YTS is the gold standard for movies. "
        "Args: query (str): Movie name to search for, "
        "quality (str): Preferred quality '720p', '1080p', '2160p', '3D' (default: '1080p'), "
        "sort_by (str): Sort by 'seeds', 'peers', 'year', 'rating', 'downloads' (default: 'seeds'), "
        "limit (int): Maximum results (default: 20). "
        "Returns: array of movie releases with torrent details and IMDb codes.",
    )
    async def search_movies(query: str, quality: str = "1080p", sort_by: str = "seeds", limit: int = 20) -> list[dict]:
        """Search YTS for movie releases"""
        try:
            return await search_yts_movies(query, quality, sort_by, limit)
        except Exception as e:
            logger.error(f"Error searching movies '{query}': {e}")
            return [{"error": f"Search failed: {e!s}"}]

    @mcp.tool(
        name="get_imdb_metadata",
        description="Get IMDb metadata for a movie or TV show using OMDb API. "
        "Args: title (str): Movie/TV show title, "
        "year (int, optional): Release year for disambiguation, "
        "imdb_id (str, optional): IMDb ID (e.g., tt1234567) for direct lookup, "
        "api_key (str, optional): OMDb API key (free at omdbapi.com). "
        "Returns: dictionary with IMDb metadata (title, year, rating, plot, etc.).",
    )
    async def get_imdb_metadata_tool(
        title: str, year: int | None = None, imdb_id: str | None = None, api_key: str | None = None
    ) -> dict:
        """Get IMDb metadata for a movie or TV show"""
        try:
            omdb_key = api_key or getattr(settings, "OMDB_API_KEY", None)
            return await get_imdb_metadata(title, year, imdb_id, omdb_key)
        except Exception as e:
            logger.error(f"Error getting IMDb metadata for '{title}': {e}")
            return {"error": f"Metadata retrieval failed: {e!s}"}

    @mcp.tool(
        name="search_imdb",
        description="Search IMDb for titles (returns multiple matches). "
        "Args: title (str): Movie/TV show title to search, "
        "year (int, optional): Release year for disambiguation, "
        "api_key (str, optional): OMDb API key (free at omdbapi.com). "
        "Returns: list of matching titles with basic info and IMDb IDs.",
    )
    async def search_imdb_tool(title: str, year: int | None = None, api_key: str | None = None) -> list[dict]:
        """Search IMDb for titles"""
        try:
            omdb_key = api_key or getattr(settings, "OMDB_API_KEY", None)
            return await search_imdb(title, year, omdb_key)
        except Exception as e:
            logger.error(f"Error searching IMDb for '{title}': {e}")
            return [{"error": f"Search failed: {e!s}"}]

    @mcp.tool(
        name="get_tvdb_metadata",
        description="Get TVDB metadata for a TV show (requires TVDB API subscription). "
        "Args: title (str): TV show title, "
        "year (int, optional): Release year, "
        "tvdb_id (int, optional): TVDB ID if known, "
        "api_key (str, optional): TVDB API key, "
        "pin (str, optional): TVDB PIN. "
        "Returns: dictionary with TVDB metadata (series info, episodes, etc.).",
    )
    async def get_tvdb_metadata_tool(
        title: str,
        year: int | None = None,
        tvdb_id: int | None = None,
        api_key: str | None = None,
        pin: str | None = None,
    ) -> dict:
        """Get TVDB metadata for a TV show"""
        try:
            tvdb_key = api_key or getattr(settings, "TVDB_API_KEY", None)
            tvdb_pin = pin or getattr(settings, "TVDB_PIN", None)
            return await get_tvdb_metadata(title, year, tvdb_id, tvdb_key, tvdb_pin)
        except Exception as e:
            logger.error(f"Error getting TVDB metadata for '{title}': {e}")
            return {"error": f"Metadata retrieval failed: {e!s}"}

    @mcp.tool(
        name="search_ebooks_annas",
        description="Search Anna's Archive for ebooks - 60M+ books, 50M papers, huge torrents. "
        "Args: query (str): title/author/ISBN, "
        "content_type (str): 'books' or 'papers' (default: 'books'), "
        "max_results (int): Maximum results (default: 20). "
        "Returns: array of book/paper releases with detail URLs (visit detail_url for full torrent info).",
    )
    async def search_ebooks_annas(query: str, content_type: str = "books", max_results: int = 20) -> list[dict]:
        """Search Anna's Archive for ebooks - the gold standard!"""
        try:
            return await search_annas_archive(query, content_type, max_results)
        except Exception as e:
            logger.error(f"Error searching Anna's Archive for '{query}': {e}")
            return [{"error": f"Search failed: {e!s}"}]

    @mcp.tool(
        name="get_annas_detail",
        description="Get detailed torrent information from Anna's Archive detail page. "
        "This returns full magnet links and torrent files (can be 100TB+!). "
        "Args: book_url (str): Full URL to Anna's Archive book/paper detail page. "
        "Returns: dictionary with detailed torrent info including magnet links.",
    )
    async def get_annas_detail_tool(book_url: str) -> dict:
        """Get detailed torrent info from Anna's Archive"""
        try:
            return await get_annas_archive_detail(book_url)
        except Exception as e:
            logger.error(f"Error getting Anna's Archive detail from '{book_url}': {e}")
            return {"error": f"Detail fetch failed: {e!s}"}

    @mcp.tool(
        name="search_comics",
        description="Search The Pirate Bay for comics (western comics). "
        "Args: query (str): Comic book title to search for, "
        "max_results (int): Maximum results (default: 20). "
        "Returns: array of comic releases with torrent details.",
    )
    async def search_comics(query: str, max_results: int = 20) -> list[dict]:
        """Search Pirate Bay for comics"""
        try:
            return await search_piratebay_category(query, category="comics", max_results=max_results)
        except Exception as e:
            logger.error(f"Error searching comics for '{query}': {e}")
            return [{"error": f"Search failed: {e!s}"}]

    @mcp.tool(
        name="search_ebooks_pb",
        description="Search The Pirate Bay for ebooks (weak selection, but available). "
        "For better results, use search_ebooks_annas (Anna's Archive is the gold standard!). "
        "Args: query (str): Ebook title to search for, "
        "max_results (int): Maximum results (default: 20). "
        "Returns: array of ebook releases with torrent details.",
    )
    async def search_ebooks_pb(query: str, max_results: int = 20) -> list[dict]:
        """Search Pirate Bay for ebooks (weak selection)"""
        try:
            return await search_piratebay_category(query, category="ebooks", max_results=max_results)
        except Exception as e:
            logger.error(f"Error searching ebooks on Pirate Bay for '{query}': {e}")
            return [{"error": f"Search failed: {e!s}"}]
