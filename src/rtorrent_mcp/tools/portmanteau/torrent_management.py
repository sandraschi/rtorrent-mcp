"""
Torrent Management Portmanteau Tool

Consolidates all rTorrent and post-processing operations into a single tool.
"""

import asyncio
import logging
from typing import Any, Literal

from fastmcp import FastMCP

from ...services.post_processor import PostProcessor
from ...services.rtorrent_client import get_rtorrent_client

logger = logging.getLogger(__name__)

# Global post-processor instance
_post_processor: PostProcessor | None = None
_post_processor_lock = asyncio.Lock()
_poll_task: asyncio.Task | None = None
_post_processor_initialized = False


async def _get_post_processor(settings) -> PostProcessor:
    """Get or create post-processor instance"""
    global _post_processor, _post_processor_initialized
    async with _post_processor_lock:
        if _post_processor is None:
            config = {
                "ingestion_anime_path": settings.INGESTION_ANIME_PATH,
                "ingestion_tv_path": settings.INGESTION_TV_PATH,
                "ingestion_movies_path": settings.INGESTION_MOVIES_PATH,
                "poll_interval": settings.POST_PROCESSING_POLL_INTERVAL,
                "delete_torrent_after_complete": settings.DELETE_TORRENT_AFTER_COMPLETE,
                "normalize_filenames": settings.NORMALIZE_FILENAMES,
                # media service integration (Plex/Jellyfin — *arr not notified; it manages rTorrent itself)
                "plex_url": getattr(settings, "PLEX_URL", ""),
                "plex_token": getattr(settings, "PLEX_TOKEN", ""),
                "jellyfin_url": getattr(settings, "JELLYFIN_URL", ""),
                "jellyfin_api_key": getattr(settings, "JELLYFIN_API_KEY", ""),
            }
            _post_processor = PostProcessor(config)
        if not _post_processor_initialized:
            await _post_processor.initialize()
            _post_processor_initialized = True
    return _post_processor


TORRENT_ACTIONS = {
    "add": "Add a torrent via magnet link",
    "list": "List all torrents with status",
    "pause": "Pause a specific torrent",
    "resume": "Resume a specific torrent",
    "delete": "Delete a torrent (optionally with files)",
    "status": "Get rTorrent connection status",
    "info": "Get detailed info about a specific torrent",
    "notify_media": "Notify media services (*arr/Plex/Jellyfin) for a processed torrent",
    # Post-processing actions
    "check_completed": "Check for completed downloads ready for processing",
    "process": "Process a completed download (normalize, move)",
    "start_processing": "Start automatic post-processing loop",
    "stop_processing": "Stop automatic post-processing loop",
    "normalize": "Normalize a filename (preview)",
}


def register_torrent_management_tool(mcp: FastMCP, settings) -> None:
    """Register the torrent management portmanteau tool."""

    @mcp.tool()
    async def torrent_management(
        action: Literal[
            "add",
            "list",
            "pause",
            "resume",
            "delete",
            "status",
            "info",
            "notify_media",
            "check_completed",
            "process",
            "start_processing",
            "stop_processing",
            "normalize",
        ],
        magnet_link: str | None = None,
        torrent_hash: str | None = None,
        category: str = "anime",
        delete_files: bool = False,
        filename: str | None = None,
    ) -> dict[str, Any]:
        """
        Comprehensive torrent management portmanteau tool for rTorrent and post-processing.

        PORTMANTEAU PATTERN RATIONALE:
        Instead of creating 12 separate tools, this tool consolidates all torrent and post-processing
        operations into a single interface. Prevents tool explosion while maintaining full functionality.

        Args:
            action (Literal, required): The operation to perform. Must be one of:
                TORRENT OPERATIONS:
                - "add": Add torrent via magnet link (requires: magnet_link, optional: category)
                - "list": List all torrents with status (no params required)
                - "pause": Pause a torrent (requires: torrent_hash)
                - "resume": Resume a torrent (requires: torrent_hash)
                - "delete": Delete a torrent (requires: torrent_hash, optional: delete_files)
                - "status": Get rTorrent connection status (no params required)
                - "info": Get detailed torrent info (requires: torrent_hash)

                POST-PROCESSING OPERATIONS:
                - "check_completed": Check for completed downloads ready for processing
                - "process": Process completed download (requires: torrent_hash)
                - "start_processing": Start automatic post-processing loop
                - "stop_processing": Stop automatic post-processing loop
                - "normalize": Preview filename normalization (requires: filename, optional: category)

            magnet_link (str | None): Magnet URI. Required for: add

            torrent_hash (str | None): Torrent hash. Required for: pause, resume, delete, info, process

            category (str): Category for categorization. Used by: add, normalize. Default: "anime"

            delete_files (bool): Delete files when deleting torrent. Default: False

            filename (str | None): Filename for normalization preview. Required for: normalize

        Returns:
            dict[str, Any]: Dictionary with success, action, data, and optional error

        Examples:
            # Add torrent
            result = await torrent_management(action="add", magnet_link="magnet:?...", category="anime")

            # List torrents
            result = await torrent_management(action="list")

            # Check completed downloads
            result = await torrent_management(action="check_completed")

            # Process completed download
            result = await torrent_management(action="process", torrent_hash="abc123...")

            # Start auto-processing
            result = await torrent_management(action="start_processing")

            # Preview filename normalization
            result = await torrent_management(action="normalize", filename="Show.S01E01.720p.mkv")
        """
        try:
            if action not in TORRENT_ACTIONS:
                return {
                    "success": False,
                    "action": action,
                    "error": f"Invalid action '{action}'. Available: {list(TORRENT_ACTIONS.keys())}",
                }

            logger.info(f"Executing torrent management action: {action}")
            client = await get_rtorrent_client()

            if action == "add":
                if not magnet_link:
                    return {
                        "success": False,
                        "action": action,
                        "error": "magnet_link is required for 'add' action",
                    }
                logger.info(f"Adding torrent with category '{category}': {magnet_link[:50]}...")
                result = await client.add_torrent(magnet_link, category)
                return {
                    "success": result.get("status") == "success",
                    "message": result.get("message", ""),
                    "next_steps": result.get("next_steps", []),
                    "action": action,
                    "data": result,
                }

            if action == "list":
                torrents = await client.get_torrents()
                return {
                    "success": True,
                    "message": f"Found {len(torrents)} torrents",
                    "next_steps": [],
                    "action": action,
                    "data": {"torrents": torrents, "count": len(torrents)},
                }

            if action == "pause":
                if not torrent_hash:
                    return {
                        "success": False,
                        "message": "torrent_hash is required for 'pause' action",
                        "next_steps": [],
                        "action": action,
                        "error": "torrent_hash is required for 'pause' action",
                    }
                result = await client.pause_torrent(torrent_hash)
                return {
                    "success": result.get("status") == "success",
                    "message": result.get("message", ""),
                    "next_steps": result.get("next_steps", []),
                    "action": action,
                    "data": result,
                }

            if action == "resume":
                if not torrent_hash:
                    return {
                        "success": False,
                        "message": "torrent_hash is required for 'resume' action",
                        "next_steps": [],
                        "action": action,
                        "error": "torrent_hash is required for 'resume' action",
                    }
                result = await client.resume_torrent(torrent_hash)
                return {
                    "success": result.get("status") == "success",
                    "message": result.get("message", ""),
                    "next_steps": result.get("next_steps", []),
                    "action": action,
                    "data": result,
                }

            if action == "delete":
                if not torrent_hash:
                    return {
                        "success": False,
                        "message": "torrent_hash is required for 'delete' action",
                        "next_steps": [],
                        "action": action,
                        "error": "torrent_hash is required for 'delete' action",
                    }
                result = await client.delete_torrent(torrent_hash, delete_files)
                return {
                    "success": result.get("status") == "success",
                    "message": result.get("message", ""),
                    "next_steps": result.get("next_steps", []),
                    "action": action,
                    "data": result,
                }

            if action == "status":
                if not client.connected:
                    await client.connect()
                return {
                    "success": True,
                    "action": action,
                    "data": {
                        "connected": client.connected,
                        "host": client.host,
                        "port": client.port,
                        "message": "Connected to rTorrent" if client.connected else "Not connected",
                    },
                }

            if action == "info":
                if not torrent_hash:
                    return {
                        "success": False,
                        "action": action,
                        "error": "torrent_hash is required for 'info' action",
                    }
                torrents = await client.get_torrents()
                torrent = next((t for t in torrents if t.get("hash") == torrent_hash), None)
                if torrent:
                    return {"success": True, "action": action, "data": torrent}
                return {
                    "success": False,
                    "action": action,
                    "error": f"Torrent with hash '{torrent_hash}' not found",
                }

            if action == "notify_media":
                processor = await _get_post_processor(settings)
                if not hasattr(processor, "_media_integrator") or processor._media_integrator is None:
                    return {
                        "success": False,
                        "action": action,
                        "error": "No media services configured. Set PLEX_URL or JELLYFIN_URL in .env",
                    }
                # Get torrent path if hash provided
                path = ""
                if torrent_hash:
                    try:
                        path = await client.get_torrent_base_path(torrent_hash)
                    except Exception:
                        pass
                category = category or "anime"
                result = await processor._media_integrator.notify_all(category, [path] if path else [])
                return {
                    "success": True,
                    "message": "Media library notified",
                    "next_steps": [],
                    "action": action,
                    "data": result,
                }

            # POST-PROCESSING ACTIONS
            if action == "check_completed":
                processor = await _get_post_processor(settings)
                completed = await processor.check_completed_downloads()
                return {
                    "success": True,
                    "action": action,
                    "data": {"completed": completed, "count": len(completed)},
                }

            if action == "process":
                if not torrent_hash:
                    return {
                        "success": False,
                        "action": action,
                        "error": "torrent_hash is required for 'process' action",
                    }
                processor = await _get_post_processor(settings)
                torrents = await client.get_torrents()
                torrent = next((t for t in torrents if t.get("hash") == torrent_hash), None)
                if not torrent:
                    return {
                        "success": False,
                        "action": action,
                        "error": f"Torrent {torrent_hash} not found",
                    }
                result = await processor.process_completed_torrent(torrent)
                return {
                    "success": result.get("status") == "success",
                    "message": result.get("message", ""),
                    "next_steps": result.get("next_steps", []),
                    "action": action,
                    "data": result,
                }

            if action == "start_processing":
                if not settings.POST_PROCESSING_ENABLED:
                    return {
                        "success": False,
                        "action": action,
                        "error": "Post-processing disabled. Set POST_PROCESSING_ENABLED=true",
                    }
                global _poll_task
                if _poll_task is not None and not _poll_task.done():
                    return {
                        "success": True,
                        "action": action,
                        "data": {"status": "already_running", "message": "Polling loop is already active"},
                    }
                processor = await _get_post_processor(settings)
                _poll_task = asyncio.create_task(processor.run_polling_loop())
                return {
                    "success": True,
                    "action": action,
                    "data": {
                        "status": "started",
                        "poll_interval": settings.POST_PROCESSING_POLL_INTERVAL,
                        "delete_after_complete": settings.DELETE_TORRENT_AFTER_COMPLETE,
                    },
                }

            if action == "stop_processing":
                processor = await _get_post_processor(settings)
                processor.stop()
                if _poll_task is not None and not _poll_task.done():
                    _poll_task.cancel()
                _poll_task = None
                return {"success": True, "action": action, "data": {"status": "stopped"}}

            if action == "normalize":
                if not filename:
                    return {
                        "success": False,
                        "action": action,
                        "error": "filename is required for 'normalize' action",
                    }
                processor = _get_post_processor(settings)
                normalized = processor.normalize_filename(filename, category)
                return {
                    "success": True,
                    "action": action,
                    "data": {"original": filename, "normalized": normalized, "category": category},
                }

            return {
                "success": False,
                "action": action,
                "error": f"Action '{action}' not implemented",
            }

        except ConnectionError as e:
            logger.error(f"rTorrent connection error: {e}", exc_info=True)
            return {
                "success": False,
                "message": "Failed to connect to rTorrent. Is it running?",
                "next_steps": ["Check rTorrent is running", "Verify RTORRENT_HOST/RTORRENT_PORT"],
                "action": action,
                "error": "Failed to connect to rTorrent. Is it running?",
                "error_type": "connection_error",
            }
        except TimeoutError as e:
            logger.error(f"Timeout error: {e}", exc_info=True)
            return {
                "success": False,
                "message": "Operation timed out. rTorrent may be unresponsive.",
                "next_steps": ["Check rTorrent health", "Increase timeout if needed"],
                "action": action,
                "error": "Operation timed out. rTorrent may be unresponsive.",
                "error_type": "timeout_error",
            }
        except Exception as e:
            logger.error(f"Error in torrent management action '{action}': {e}", exc_info=True)
            return {
                "success": False,
                "message": f"Failed to execute: {e!s}",
                "next_steps": ["Check logs for details"],
                "action": action,
                "error": f"Failed to execute: {e!s}",
            }
