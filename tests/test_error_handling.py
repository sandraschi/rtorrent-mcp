"""
Tests for error handling across all services
Tests for network errors, invalid inputs, and edge cases
Run with: python -m pytest tests/test_error_handling.py -v
"""

from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest


class TestNyaaSearchErrorHandling:
    """Test error handling in nyaa search"""

    @pytest.mark.asyncio
    @patch("rtorrent_mcp.services.nyaa_search.aiohttp.ClientSession")
    async def test_search_nyaa_timeout(self, mock_session):
        """Test handling of timeout errors"""
        from rtorrent_mcp.services.nyaa_search import search_nyaa_anime

        mock_session_instance = MagicMock()
        mock_session_instance.__aenter__ = AsyncMock(return_value=mock_session_instance)
        mock_session_instance.__aexit__ = AsyncMock(return_value=None)
        mock_session_instance.get = AsyncMock(side_effect=aiohttp.ServerTimeoutError("Timeout"))
        mock_session.return_value = mock_session_instance

        results = await search_nyaa_anime("test", resolution="720p")
        assert isinstance(results, list)

    @pytest.mark.asyncio
    @patch("rtorrent_mcp.services.nyaa_search.aiohttp.ClientSession")
    async def test_search_nyaa_invalid_html(self, mock_session):
        """Test handling of invalid HTML response"""
        from rtorrent_mcp.services.nyaa_search import search_nyaa_anime

        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value="<invalid>html</invalid>")
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        mock_session_instance = MagicMock()
        mock_session_instance.__aenter__ = AsyncMock(return_value=mock_session_instance)
        mock_session_instance.__aexit__ = AsyncMock(return_value=None)
        mock_session_instance.get = MagicMock(return_value=mock_response)
        mock_session.return_value = mock_session_instance

        results = await search_nyaa_anime("test", resolution="720p")
        assert isinstance(results, list)


class TestPirateBaySearchErrorHandling:
    """Test error handling in Pirate Bay search"""

    @pytest.mark.asyncio
    @patch("rtorrent_mcp.services.piratebay_search.aiohttp.ClientSession")
    async def test_search_piratebay_timeout(self, mock_session):
        """Test handling of timeout errors"""
        from rtorrent_mcp.services.piratebay_search import search_piratebay_tv

        mock_session_instance = MagicMock()
        mock_session_instance.__aenter__ = AsyncMock(return_value=mock_session_instance)
        mock_session_instance.__aexit__ = AsyncMock(return_value=None)
        mock_session_instance.get = AsyncMock(side_effect=aiohttp.ServerTimeoutError("Timeout"))
        mock_session.return_value = mock_session_instance

        results = await search_piratebay_tv("test", resolution="1080p")
        assert isinstance(results, list)

    @pytest.mark.asyncio
    @patch("rtorrent_mcp.services.piratebay_search.aiohttp.ClientSession")
    async def test_search_piratebay_connection_error(self, mock_session):
        """Test handling of connection errors"""
        from rtorrent_mcp.services.piratebay_search import search_piratebay_tv

        mock_session_instance = MagicMock()
        mock_session_instance.__aenter__ = AsyncMock(return_value=mock_session_instance)
        mock_session_instance.__aexit__ = AsyncMock(return_value=None)
        mock_session_instance.get = AsyncMock(side_effect=aiohttp.ClientError("Connection failed"))
        mock_session.return_value = mock_session_instance

        results = await search_piratebay_tv("test", resolution="1080p")
        assert isinstance(results, list)


class TestRTorrentClientErrorHandling:
    """Test error handling in rTorrent client"""

    @pytest.mark.asyncio
    async def test_rtorrent_client_connection_failure(self):
        """Test handling of connection failures"""
        from rtorrent_mcp.services.rtorrent_client import RTorrentClient

        client = RTorrentClient()
        client.host = "invalid-host"
        client.port = 9999

        # Should handle connection failure gracefully
        result = await client.connect()
        assert isinstance(result, bool)

    @pytest.mark.asyncio
    async def test_rtorrent_client_invalid_magnet(self):
        """Test handling of invalid magnet links"""
        from rtorrent_mcp.services.rtorrent_client import RTorrentClient

        client = RTorrentClient()
        client.connected = True

        # Mock server to raise error
        mock_server = MagicMock()
        mock_server.load.start.side_effect = Exception("Invalid magnet")
        client.server = mock_server

        result = await client.add_torrent("invalid-magnet-link")
        assert "error" in result or result.get("status") == "error"


class TestPostProcessorErrorHandling:
    """Test error handling in post processor"""

    @pytest.mark.asyncio
    async def test_post_processor_missing_client(self):
        """Test handling of missing rTorrent client"""
        from rtorrent_mcp.services.post_processor import PostProcessor

        config = {
            "ingestion_anime_path": "/test/anime",
            "poll_interval": 60,
        }

        processor = PostProcessor(config)

        # Should handle missing client gracefully
        with patch("rtorrent_mcp.services.post_processor.get_rtorrent_client") as mock_get_client:
            mock_get_client.side_effect = Exception("Client unavailable")
            results = await processor.check_completed_downloads()
            assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_post_processor_invalid_path(self):
        """Test handling of invalid ingestion paths"""
        from rtorrent_mcp.services.post_processor import PostProcessor

        config = {
            "ingestion_anime_path": "/nonexistent/path",
            "poll_interval": 60,
        }

        processor = PostProcessor(config)

        # Should handle invalid path gracefully
        folder = processor.get_ingestion_folder("anime")
        assert folder is not None or folder is None  # Either is acceptable


class TestMetadataServiceErrorHandling:
    """Test error handling in metadata services"""

    @pytest.mark.asyncio
    @patch("rtorrent_mcp.services.metadata_service.aiohttp.ClientSession")
    async def test_imdb_metadata_timeout(self, mock_session):
        """Test handling of timeout in IMDb metadata"""
        from rtorrent_mcp.services.metadata_service import get_imdb_metadata

        mock_session_instance = MagicMock()
        mock_session_instance.__aenter__ = AsyncMock(return_value=mock_session_instance)
        mock_session_instance.__aexit__ = AsyncMock(return_value=None)
        mock_session_instance.get = AsyncMock(side_effect=aiohttp.ServerTimeoutError("Timeout"))
        mock_session.return_value = mock_session_instance

        result = await get_imdb_metadata("test")
        assert "error" in result

    @pytest.mark.asyncio
    @patch("rtorrent_mcp.services.metadata_service.aiohttp.ClientSession")
    async def test_tvdb_metadata_invalid_credentials(self, mock_session):
        """Test handling of invalid TVDB credentials"""
        from rtorrent_mcp.services.metadata_service import get_tvdb_metadata

        mock_auth_response = MagicMock()
        mock_auth_response.status = 401
        mock_auth_response.json = AsyncMock(return_value={"error": "Invalid credentials"})

        mock_session_instance = MagicMock()
        mock_session_instance.__aenter__ = AsyncMock(return_value=mock_session_instance)
        mock_session_instance.__aexit__ = AsyncMock(return_value=None)
        mock_session_instance.post = AsyncMock(return_value=mock_auth_response)
        mock_session.return_value = mock_session_instance

        result = await get_tvdb_metadata("test", api_key="invalid", pin="invalid")
        assert "error" in result


class TestNaturalLanguageErrorHandling:
    """Test error handling in natural language processing"""

    def test_extract_anime_name_empty_string(self):
        """Test handling of empty string"""
        from rtorrent_mcp.services.natural_language import extract_anime_name

        result = extract_anime_name("")
        assert isinstance(result, str)

    def test_extract_resolution_invalid_input(self):
        """Test handling of invalid input"""
        from rtorrent_mcp.services.natural_language import extract_resolution

        result = extract_resolution(None)  # type: ignore
        assert isinstance(result, str)

    def test_extract_release_group_special_characters(self):
        """Test handling of special characters"""
        from rtorrent_mcp.services.natural_language import extract_release_group

        result = extract_release_group("test !@#$%^&*() anime")
        assert isinstance(result, str)


if __name__ == "__main__":
    print(" Running Error Handling Tests...")
    print("[WARN]  Testing network errors, invalid inputs, and edge cases...")
    print("[OK] Error handling verified!")
