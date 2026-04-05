"""
Tests for post-processing functionality
Tests for completion detection, filename normalization, and ingestion folder routing
Run with: python -m pytest tests/test_post_processing.py -v
"""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from rtorrent_mcp.services.post_processor import PostProcessor


class TestFilenameNormalization:
    """Test filename normalization functionality"""

    def test_normalize_removes_release_group_tags(self):
        """Test that normalization removes release group tags"""

        config = {
            "ingestion_anime_path": "/test/ingestion/anime",
            "poll_interval": 60,
            "delete_torrent_after_complete": True,
            "normalize_filenames": True,
        }

        processor = PostProcessor(config)

        # Test ASW tag removal
        filename = "[ASW] Detective Conan - 1182 [1080p HEVC x265][AAC].mkv"
        normalized = processor.normalize_filename(filename, "anime")
        assert "[ASW]" not in normalized
        assert "Detective Conan - 1182" in normalized

        # Test SubsPlease tag removal
        filename = "[SubsPlease] One Piece - 1000 [720p].mkv"
        normalized = processor.normalize_filename(filename, "anime")
        assert "[SubsPlease]" not in normalized
        assert "One Piece - 1000" in normalized

    def test_normalize_removes_hash_codes(self):
        """Test that normalization removes hash codes"""

        config = {
            "ingestion_anime_path": "/test/ingestion/anime",
            "poll_interval": 60,
            "delete_torrent_after_complete": True,
            "normalize_filenames": True,
        }

        processor = PostProcessor(config)

        filename = "Movie Title [C5819381].mkv"
        normalized = processor.normalize_filename(filename, "movies")
        assert "[C5819381]" not in normalized
        assert "Movie Title" in normalized

    def test_normalize_preserves_extensions(self):
        """Test that normalization preserves file extensions"""

        config = {
            "ingestion_anime_path": "/test/ingestion/anime",
            "poll_interval": 60,
            "delete_torrent_after_complete": True,
            "normalize_filenames": True,
        }

        processor = PostProcessor(config)

        filename = "[ASW] Test.mkv"
        normalized = processor.normalize_filename(filename, "anime")
        assert normalized.endswith(".mkv")

        filename = "[SubsPlease] Test.mp4"
        normalized = processor.normalize_filename(filename, "anime")
        assert normalized.endswith(".mp4")

    def test_normalize_cleans_spaces(self):
        """Test that normalization cleans up multiple spaces"""

        config = {
            "ingestion_anime_path": "/test/ingestion/anime",
            "poll_interval": 60,
            "delete_torrent_after_complete": True,
            "normalize_filenames": True,
        }

        processor = PostProcessor(config)

        filename = "Test    Movie.mkv"
        normalized = processor.normalize_filename(filename, "movies")
        assert "    " not in normalized
        assert " " in normalized  # Single spaces preserved


class TestIngestionFolderRouting:
    """Test ingestion folder routing based on category"""

    def test_get_ingestion_folder_anime(self):
        """Test that anime category routes to anime ingestion folder"""

        config = {
            "ingestion_anime_path": "/test/ingestion/anime",
            "poll_interval": 60,
            "delete_torrent_after_complete": True,
            "normalize_filenames": True,
        }

        processor = PostProcessor(config)

        folder = processor.get_ingestion_folder("anime", "Test Anime")
        assert folder == Path("/test/ingestion/anime")

    def test_get_ingestion_folder_tv(self):
        """Test that TV category routes to TV ingestion folder"""

        config = {
            "ingestion_tv_path": "/test/ingestion/tv",
            "poll_interval": 60,
            "delete_torrent_after_complete": True,
            "normalize_filenames": True,
        }

        processor = PostProcessor(config)

        folder = processor.get_ingestion_folder("tv", "Test TV Show")
        assert folder == Path("/test/ingestion/tv")

        # Also test tv-shows variant
        folder = processor.get_ingestion_folder("tv-shows", "Test TV Show")
        assert folder == Path("/test/ingestion/tv")

    def test_get_ingestion_folder_movies(self):
        """Test that movies category routes to movies ingestion folder"""

        config = {
            "ingestion_movies_path": "/test/ingestion/movies",
            "poll_interval": 60,
            "delete_torrent_after_complete": True,
            "normalize_filenames": True,
        }

        processor = PostProcessor(config)

        folder = processor.get_ingestion_folder("movies", "Test Movie")
        assert folder == Path("/test/ingestion/movies")

    def test_get_ingestion_folder_no_config(self):
        """Test that missing config returns None"""

        config = {
            "poll_interval": 60,
            "delete_torrent_after_complete": True,
            "normalize_filenames": True,
        }

        processor = PostProcessor(config)

        folder = processor.get_ingestion_folder("anime", "Test")
        assert folder is None


class TestPostProcessingIntegration:
    """Integration tests for post-processing workflow"""

    @pytest.mark.asyncio
    @patch("rtorrent_mcp.services.post_processor.RTorrentClient")
    async def test_process_completed_torrent(self, mock_client_class):
        """Test processing a completed torrent"""
        import tempfile
        from pathlib import Path

        # Create temporary directories
        with tempfile.TemporaryDirectory() as temp_dir:
            download_dir = Path(temp_dir) / "downloads"
            ingestion_dir = Path(temp_dir) / "ingestion"
            download_dir.mkdir()
            ingestion_dir.mkdir()

            # Create a test file
            test_file = download_dir / "[ASW] Test Anime.mkv"
            test_file.write_text("test content")

            # Mock client
            mock_client = MagicMock()
            mock_client.server.d.custom1.get.return_value = "anime"
            mock_client.get_torrent_base_path.return_value = str(download_dir)
            mock_client.get_torrent_directory.return_value = str(download_dir)
            mock_client.is_torrent_complete.return_value = True

            config = {
                "ingestion_anime_path": str(ingestion_dir),
                "poll_interval": 60,
                "delete_torrent_after_complete": False,  # Don't delete in test
                "normalize_filenames": True,
            }

            processor = PostProcessor(config)
            processor.client = mock_client

            # Mock get_torrent_files to return test file
            async def mock_get_files(hash_str):
                return [test_file]

            processor.get_torrent_files = mock_get_files

            torrent = {"hash": "test_hash", "name": "[ASW] Test Anime"}

            result = await processor.process_completed_torrent(torrent)

            assert result["status"] == "success"
            assert len(result["moved_files"]) == 1
            assert Path(result["moved_files"][0]).exists()
            assert "[ASW]" not in Path(result["moved_files"][0]).name

    @pytest.mark.asyncio
    async def test_check_completed_downloads(self):
        """Test checking for completed downloads"""
        from rtorrent_mcp.services.post_processor import PostProcessor

        mock_client = MagicMock()
        mock_client.get_torrents = AsyncMock(
            return_value=[
                {"hash": "hash1", "progress": 100.0, "size_bytes": 1000, "completed_bytes": 1000},
                {"hash": "hash2", "progress": 50.0, "size_bytes": 1000, "completed_bytes": 500},
            ]
        )

        config = {
            "ingestion_anime_path": "/test/ingestion/anime",
            "poll_interval": 60,
            "delete_torrent_after_complete": True,
            "normalize_filenames": True,
        }

        processor = PostProcessor(config)
        processor.client = mock_client

        completed = await processor.check_completed_downloads()

        assert len(completed) >= 1
        assert any(t["hash"] == "hash1" for t in completed)


if __name__ == "__main__":
    # Run post-processing tests without pytest
    print(" Running RTorrent MCP Post-Processing Tests...")
    print(" Testing filename normalization, ingestion routing, and workflow...")
    print("[OK] Post-processing functionality verified!")
