"""
post_processor.py - Post-processing service for completed downloads
Handles completion detection, torrent removal, filename normalization, and Plex integration
"""

import asyncio
import logging
import re
import shutil
from pathlib import Path
from typing import Any

from .rtorrent_client import RTorrentClient, get_rtorrent_client

logger = logging.getLogger(__name__)


class PostProcessor:
    """Post-process completed torrents: normalize filenames and move to ingestion folders"""

    def __init__(self, config: dict[str, Any]):
        """Initialize post-processor with configuration

        Args:
            config: Configuration dict with:
                - ingestion_anime_path: Path to temporary ingestion folder for anime
                - ingestion_tv_path: Path to temporary ingestion folder for TV shows
                - ingestion_movies_path: Path to temporary ingestion folder for movies
                - poll_interval: Seconds between polling for completed downloads
                - delete_torrent_after_complete: Whether to remove torrent after processing
                - normalize_filenames: Whether to normalize filenames before moving
        """
        self.config = config
        self.processed_hashes: set[str] = set()
        self.client: RTorrentClient | None = None
        self.running = False

    async def initialize(self):
        """Initialize rTorrent client"""
        self.client = await get_rtorrent_client()

    async def check_completed_downloads(self) -> list[dict[str, Any]]:
        """Check for completed downloads by polling rTorrent

        Returns:
            List of completed torrent dictionaries
        """
        if not self.client:
            await self.initialize()

        torrents = await self.client.get_torrents()
        completed = []

        for torrent in torrents:
            hash_str = torrent.get("hash")
            if not hash_str or hash_str in self.processed_hashes:
                continue

            # Check if 100% complete
            size_bytes = torrent.get("size_bytes", 0)
            completed_bytes = torrent.get("completed_bytes", 0)
            progress = torrent.get("progress", 0)

            # Consider complete if progress >= 99.9% (handles rounding)
            if progress >= 99.9 and size_bytes > 0 and completed_bytes >= size_bytes:
                completed.append(torrent)

        return completed

    def normalize_filename(self, filename: str, category: str = "anime") -> str:
        """Normalize filename by removing release group tags and cleaning format

        Args:
            filename: Original filename
            category: Torrent category (anime/TV/movies)

        Returns:
            Normalized filename
        """
        # Remove common release group tags
        patterns_to_remove = [
            r"\[ASW\]",
            r"\[SubsPlease\]",
            r"\[Erai-raws\]",
            r"\[MeGusta\]",
            r"\[RARBG\]",
            r"\[EZTV\]",
            r"-\s*ASW",
            r"-\s*SubsPlease",
            r"-\s*MeGusta",
            r"-\s*RARBG",
            r"-\s*EZTV",
        ]

        normalized = filename
        for pattern in patterns_to_remove:
            normalized = re.sub(pattern, "", normalized, flags=re.IGNORECASE)

        # Clean up multiple spaces and dots
        normalized = re.sub(r"\s+", " ", normalized)
        normalized = re.sub(r"\.+", ".", normalized)
        normalized = re.sub(r"\s*-\s*", " - ", normalized)

        # Remove hash codes like [C5819381]
        normalized = re.sub(r"\[[A-F0-9]{8,}\]", "", normalized)

        # Clean up leading/trailing spaces and dots
        normalized = normalized.strip(" .-")

        # Ensure file extension is preserved
        if not normalized.endswith((".mkv", ".mp4", ".avi", ".mkv", ".m4v")):
            # If we removed too much, try to preserve original extension
            original_ext = Path(filename).suffix
            if original_ext and not normalized.endswith(original_ext):
                normalized += original_ext

        return normalized

    def get_ingestion_folder(self, category: str, torrent_name: str) -> Path | None:
        """Determine appropriate ingestion folder based on category

        Args:
            category: Torrent category (anime/TV/movies)
            torrent_name: Name of the torrent

        Returns:
            Path to ingestion folder, or None if not configured
        """
        category_lower = category.lower()

        if (
            category_lower == "anime"
            and "ingestion_anime_path" in self.config
            and self.config["ingestion_anime_path"]
        ):
            return Path(self.config["ingestion_anime_path"])
        elif (
            category_lower in ("tv", "tv-shows")
            and "ingestion_tv_path" in self.config
            and self.config["ingestion_tv_path"]
        ):
            return Path(self.config["ingestion_tv_path"])
        elif (
            category_lower == "movies"
            and "ingestion_movies_path" in self.config
            and self.config["ingestion_movies_path"]
        ):
            return Path(self.config["ingestion_movies_path"])

        return None

    async def get_torrent_files(self, torrent_hash: str) -> list[Path]:
        """Get list of files in a torrent

        Args:
            torrent_hash: Torrent hash identifier

        Returns:
            List of file paths
        """
        if not self.client:
            await self.initialize()

        try:
            loop = asyncio.get_event_loop()
            # Get torrent base path (directory or file path)
            base_path = await loop.run_in_executor(
                None, self.client.server.d.get_base_path, torrent_hash
            )
            await loop.run_in_executor(None, self.client.server.d.get_name, torrent_hash)

            if not base_path:
                return []

            # Handle Docker paths: base_path might be in container format
            # e.g., /downloads/... needs to map to Windows path if needed
            base = Path(base_path)

            # Check if path exists (might be container path)
            if not base.exists():
                logger.warning(f"Torrent path doesn't exist: {base_path} (might be container path)")
                # Try to find files anyway (might need Docker path mapping)
                # For now, return empty - user can configure path mapping if needed
                return []

            # Check if it's a single file or directory
            if base.is_file():
                return [base]
            elif base.is_dir():
                # Get all video files in directory
                video_extensions = {
                    ".mkv",
                    ".mp4",
                    ".avi",
                    ".m4v",
                    ".mov",
                    ".mpg",
                    ".mpeg",
                    ".flv",
                    ".webm",
                }
                files = []
                for ext in video_extensions:
                    try:
                        found_files = list(base.rglob(f"*{ext}"))
                        files.extend(found_files)
                    except Exception as e:
                        logger.warning(f"Error searching for {ext} files: {e}")
                return sorted(files)
            else:
                logger.warning(f"Torrent path is not a file or directory: {base_path}")
                return []

        except Exception as e:
            logger.error(f"Error getting torrent files for {torrent_hash}: {e}")
            return []

    async def process_completed_torrent(self, torrent: dict[str, Any]) -> dict[str, Any]:
        """Process a completed torrent: normalize and move to ingestion folder

        Args:
            torrent: Torrent dictionary from get_torrents()

        Returns:
            Processing result dictionary
        """
        torrent_hash = torrent.get("hash")
        torrent_name = torrent.get("name", "Unknown")

        if not torrent_hash:
            return {"status": "error", "message": "No torrent hash"}

        # Get category from torrent custom field
        try:
            if self.client:
                loop = asyncio.get_event_loop()
                category = (
                    await loop.run_in_executor(None, self.client.server.d.custom1.get, torrent_hash)
                    or "anime"
                )
            else:
                category = "anime"
        except Exception:
            category = "anime"

        # Get files
        files = await self.get_torrent_files(torrent_hash)
        if not files:
            return {"status": "error", "message": f"No files found for torrent {torrent_name}"}

        # Get ingestion folder
        ingestion_folder = self.get_ingestion_folder(category, torrent_name)
        if not ingestion_folder:
            logger.warning(
                f"No ingestion folder configured for category '{category}', skipping move"
            )
            # Still mark as processed if configured to delete
            if self.config.get("delete_torrent_after_complete", False):
                await self._delete_torrent(torrent_hash)
            return {
                "status": "skipped",
                "message": f"No ingestion folder for category '{category}'",
            }

        # Ensure ingestion folder exists
        ingestion_folder.mkdir(parents=True, exist_ok=True)

        moved_files = []
        errors = []

        # Process each file
        for file_path in files:
            try:
                # Normalize filename if enabled
                if self.config.get("normalize_filenames", True):
                    normalized_name = self.normalize_filename(file_path.name, category)
                else:
                    normalized_name = file_path.name

                dest_path = ingestion_folder / normalized_name

                # Handle duplicate files
                if dest_path.exists():
                    # Add timestamp or number suffix
                    stem = dest_path.stem
                    suffix = dest_path.suffix
                    counter = 1
                    while dest_path.exists():
                        dest_path = ingestion_folder / f"{stem}_{counter}{suffix}"
                        counter += 1

                # Move file
                shutil.move(str(file_path), str(dest_path))
                moved_files.append(str(dest_path))
                logger.info(f"Moved {file_path.name} → {dest_path}")

            except Exception as e:
                error_msg = f"Error moving {file_path}: {e}"
                logger.error(error_msg)
                errors.append(error_msg)

        # Delete torrent if configured (no sharing)
        if self.config.get("delete_torrent_after_complete", False):
            delete_result = await self._delete_torrent(torrent_hash)
            if delete_result.get("status") != "success":
                errors.append(f"Failed to delete torrent: {delete_result.get('message')}")

        # Mark as processed
        self.processed_hashes.add(torrent_hash)

        result = {
            "status": "success" if not errors else "partial",
            "torrent_hash": torrent_hash,
            "torrent_name": torrent_name,
            "category": category,
            "moved_files": moved_files,
            "ingestion_folder": str(ingestion_folder) if ingestion_folder else None,
        }

        if errors:
            result["errors"] = errors

        return result

    async def _delete_torrent(self, torrent_hash: str) -> dict[str, Any]:
        """Delete torrent from rTorrent (no sharing)

        Args:
            torrent_hash: Torrent hash identifier

        Returns:
            Deletion result
        """
        if not self.client:
            await self.initialize()

        try:
            # Close and remove torrent (delete_files=False - files already moved)
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self.client.server.d.close, torrent_hash)
            await loop.run_in_executor(None, self.client.server.d.erase, torrent_hash)

            return {"status": "success", "hash": torrent_hash}
        except Exception as e:
            return {"status": "error", "hash": torrent_hash, "message": str(e)}

    async def run_polling_loop(self):
        """Run continuous polling loop for completed downloads"""
        self.running = True
        poll_interval = self.config.get("poll_interval", 60)  # Default 60 seconds

        logger.info(f"Starting post-processing polling loop (interval: {poll_interval}s)")

        while self.running:
            try:
                completed = await self.check_completed_downloads()

                for torrent in completed:
                    logger.info(f"Processing completed torrent: {torrent.get('name')}")
                    result = await self.process_completed_torrent(torrent)

                    if result.get("status") == "success":
                        logger.info(
                            f"Successfully processed {torrent.get('name')}: {len(result.get('moved_files', []))} files moved"
                        )
                    elif result.get("status") == "partial":
                        logger.warning(
                            f"Partially processed {torrent.get('name')}: {result.get('errors')}"
                        )
                    else:
                        logger.error(
                            f"Failed to process {torrent.get('name')}: {result.get('message')}"
                        )

                await asyncio.sleep(poll_interval)

            except Exception as e:
                logger.error(f"Error in polling loop: {e}")
                await asyncio.sleep(poll_interval)

    def stop(self):
        """Stop the polling loop"""
        self.running = False
        logger.info("Post-processing polling loop stopped")
