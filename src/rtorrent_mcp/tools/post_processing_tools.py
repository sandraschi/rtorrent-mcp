"""
Post-processing tools for RTorrent MCP Server

MCP tools for managing post-processing: completion detection, file normalization, and Plex integration
"""

import asyncio
import logging

from fastmcp import FastMCP

from ..config.settings import settings
from ..services.post_processor import PostProcessor

logger = logging.getLogger(__name__)

# Global post-processor instance
_post_processor: PostProcessor | None = None


def get_post_processor() -> PostProcessor:
    """Get or create post-processor instance"""
    global _post_processor
    if _post_processor is None:
        config = {
            "ingestion_anime_path": settings.INGESTION_ANIME_PATH,
            "ingestion_tv_path": settings.INGESTION_TV_PATH,
            "ingestion_movies_path": settings.INGESTION_MOVIES_PATH,
            "poll_interval": settings.POST_PROCESSING_POLL_INTERVAL,
            "delete_torrent_after_complete": settings.DELETE_TORRENT_AFTER_COMPLETE,
            "normalize_filenames": settings.NORMALIZE_FILENAMES,
        }
        _post_processor = PostProcessor(config)
    return _post_processor


def register_post_processing_tools(mcp: FastMCP, settings) -> None:
    """Register post-processing tools with FastMCP server"""

    @mcp.tool(
        name="check_completed_downloads",
        description="Check for completed downloads in rTorrent. "
        "Returns list of torrents that are 100% complete and ready for post-processing. "
        "Returns: list of completed torrent dictionaries.",
    )
    async def check_completed_downloads() -> list[dict]:
        """Check for completed downloads"""
        try:
            processor = get_post_processor()
            await processor.initialize()
            completed = await processor.check_completed_downloads()
            return completed
        except Exception as e:
            logger.error(f"Error checking completed downloads: {e}")
            return [{"error": f"Failed to check completed downloads: {str(e)}"}]

    @mcp.tool(
        name="process_completed_download",
        description="Process a completed download: normalize filename and move to ingestion folder. "
        "Args: torrent_hash (str): The hash identifier of the torrent to process. "
        "Returns: dict with processing result and moved files.",
    )
    async def process_completed_download(torrent_hash: str) -> dict:
        """Process a completed download"""
        try:
            processor = get_post_processor()
            await processor.initialize()

            # Get torrent info
            from ..services.rtorrent_client import get_rtorrent_client

            client = await get_rtorrent_client()
            torrents = await client.get_torrents()

            torrent = next((t for t in torrents if t.get("hash") == torrent_hash), None)
            if not torrent:
                return {"status": "error", "message": f"Torrent {torrent_hash} not found"}

            result = await processor.process_completed_torrent(torrent)
            return result
        except Exception as e:
            logger.error(f"Error processing completed download {torrent_hash}: {e}")
            return {"status": "error", "message": f"Failed to process download: {str(e)}"}

    @mcp.tool(
        name="start_post_processing",
        description="Start the post-processing polling loop. "
        "This will continuously check for completed downloads and process them automatically. "
        "Returns: dict with status message.",
    )
    async def start_post_processing() -> dict:
        """Start post-processing polling loop"""
        try:
            if not settings.POST_PROCESSING_ENABLED:
                return {
                    "status": "disabled",
                    "message": "Post-processing is disabled in settings. Set POST_PROCESSING_ENABLED=true to enable.",
                }

            processor = get_post_processor()
            await processor.initialize()

            # Start polling loop in background
            asyncio.create_task(processor.run_polling_loop())

            return {
                "status": "started",
                "message": "Post-processing polling loop started",
                "poll_interval": settings.POST_PROCESSING_POLL_INTERVAL,
                "delete_after_complete": settings.DELETE_TORRENT_AFTER_COMPLETE,
                "normalize_filenames": settings.NORMALIZE_FILENAMES,
            }
        except Exception as e:
            logger.error(f"Error starting post-processing: {e}")
            return {"status": "error", "message": f"Failed to start post-processing: {str(e)}"}

    @mcp.tool(
        name="stop_post_processing",
        description="Stop the post-processing polling loop. Returns: dict with status message.",
    )
    async def stop_post_processing() -> dict:
        """Stop post-processing polling loop"""
        try:
            processor = get_post_processor()
            processor.stop()
            return {"status": "stopped", "message": "Post-processing polling loop stopped"}
        except Exception as e:
            logger.error(f"Error stopping post-processing: {e}")
            return {"status": "error", "message": f"Failed to stop post-processing: {str(e)}"}

    @mcp.tool(
        name="normalize_filename",
        description="Normalize a filename by removing release group tags and cleaning format. "
        "Args: filename (str): The filename to normalize, "
        "category (str): The category (anime/TV/movies) for context. "
        "Returns: dict with normalized filename.",
    )
    async def normalize_filename(filename: str, category: str = "anime") -> dict:
        """Normalize a filename"""
        try:
            processor = get_post_processor()
            normalized = processor.normalize_filename(filename, category)
            return {"original": filename, "normalized": normalized, "category": category}
        except Exception as e:
            logger.error(f"Error normalizing filename: {e}")
            return {"status": "error", "message": f"Failed to normalize filename: {str(e)}"}
