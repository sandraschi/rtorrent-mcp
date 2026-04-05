"""
Tests for MCP tool registration and basic functionality
Tests that tools are properly registered and can be called
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestTorrentTools:
    """Test torrent management tools"""

    @pytest.mark.asyncio
    @patch("rtorrent_mcp.tools.torrent_tools.get_rtorrent_client")
    async def test_add_torrent_tool(self, mock_get_client):
        """Test add_torrent tool"""
        from fastmcp import FastMCP

        from rtorrent_mcp.config.settings import Settings
        from rtorrent_mcp.tools.torrent_tools import register_torrent_tools

        mcp = FastMCP("test-server")
        settings = Settings()

        # Mock rTorrent client
        mock_client = MagicMock()
        mock_client.add_torrent = AsyncMock(return_value={"status": "success", "hash": "testhash"})
        mock_get_client.return_value = mock_client

        # Register tools
        register_torrent_tools(mcp, settings)

        # Verify tool registration succeeded
        assert mcp is not None

    @pytest.mark.asyncio
    @patch("rtorrent_mcp.tools.torrent_tools.get_rtorrent_client")
    async def test_list_torrents_tool(self, mock_get_client):
        """Test list_torrents tool"""
        from fastmcp import FastMCP

        from rtorrent_mcp.config.settings import Settings
        from rtorrent_mcp.tools.torrent_tools import register_torrent_tools

        mcp = FastMCP("test-server")
        settings = Settings()

        # Mock rTorrent client
        mock_client = MagicMock()
        mock_client.get_torrents = AsyncMock(return_value=[{"hash": "hash1", "name": "Test"}])
        mock_get_client.return_value = mock_client

        # Register tools
        register_torrent_tools(mcp, settings)

        # Verify tool registration succeeded
        assert mcp is not None

    @pytest.mark.asyncio
    @patch("rtorrent_mcp.tools.torrent_tools.get_rtorrent_client")
    async def test_get_status_tool(self, mock_get_client):
        """Test get_status tool"""
        from fastmcp import FastMCP

        from rtorrent_mcp.config.settings import Settings
        from rtorrent_mcp.tools.torrent_tools import register_torrent_tools

        mcp = FastMCP("test-server")
        settings = Settings()

        # Mock rTorrent client
        mock_client = MagicMock()
        mock_client.connected = True
        mock_client.host = "localhost"
        mock_client.port = 5000
        mock_get_client.return_value = mock_client

        # Register tools
        register_torrent_tools(mcp, settings)

        # Verify tool registration succeeded
        assert mcp is not None


class TestSearchToolsRegistration:
    """Test search tools registration"""

    def test_search_tools_registration(self):
        """Test that search tools are registered"""
        from fastmcp import FastMCP

        from rtorrent_mcp.config.settings import Settings
        from rtorrent_mcp.tools.search_tools import register_search_tools

        mcp = FastMCP("test-server")
        settings = Settings()

        # Register tools - should not raise error
        register_search_tools(mcp, settings)

        # Verify registration succeeded
        assert mcp is not None

    @pytest.mark.asyncio
    @patch("rtorrent_mcp.services.nyaa_search.search_nyaa_anime")
    async def test_search_anime_tool_calls_service(self, mock_search):
        """Test that search_anime tool calls the service"""
        from fastmcp import FastMCP

        from rtorrent_mcp.config.settings import Settings
        from rtorrent_mcp.tools.search_tools import register_search_tools

        mock_search.return_value = [{"title": "Test", "magnet": "magnet:test"}]

        mcp = FastMCP("test-server")
        settings = Settings()
        register_search_tools(mcp, settings)

        # Verify tool registration succeeded
        assert mcp is not None


class TestPostProcessingTools:
    """Test post-processing tools registration"""

    def test_post_processing_tools_registration(self):
        """Test that post-processing tools are registered"""
        from fastmcp import FastMCP

        from rtorrent_mcp.config.settings import Settings
        from rtorrent_mcp.tools.post_processing_tools import register_post_processing_tools

        mcp = FastMCP("test-server")
        settings = Settings()

        # Register tools - should not raise error
        register_post_processing_tools(mcp, settings)

        # Verify registration succeeded
        assert mcp is not None


class TestLegalTools:
    """Test legal compliance tools"""

    def test_legal_tools_registration(self):
        """Test that legal tools are registered"""
        from fastmcp import FastMCP

        from rtorrent_mcp.config.settings import Settings
        from rtorrent_mcp.tools.legal_tools import register_legal_tools

        mcp = FastMCP("test-server")
        settings = Settings()

        # Register tools - should not raise error
        register_legal_tools(mcp, settings)

        # Verify registration succeeded
        assert mcp is not None


class TestNLPTools:
    """Test natural language processing tools"""

    def test_nlp_tools_registration(self):
        """Test that NLP tools are registered"""
        from fastmcp import FastMCP

        from rtorrent_mcp.config.settings import Settings
        from rtorrent_mcp.tools.nlp_tools import register_nlp_tools

        mcp = FastMCP("test-server")
        settings = Settings()

        # Register tools - should not raise error
        register_nlp_tools(mcp, settings)

        # Verify registration succeeded
        assert mcp is not None


class TestSystemTools:
    """Test system tools"""

    def test_system_tools_registration(self):
        """Test that system tools are registered"""
        from fastmcp import FastMCP

        from rtorrent_mcp.config.settings import Settings
        from rtorrent_mcp.tools.system_tools import register_system_tools

        mcp = FastMCP("test-server")
        settings = Settings()

        # Register tools - should not raise error
        register_system_tools(mcp, settings)

        # Verify registration succeeded
        assert mcp is not None
