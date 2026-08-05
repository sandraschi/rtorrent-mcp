"""
Integration tests for RTorrent MCP server.

Tests the legacy service-level tool registrations (services/core_tools,
services/rtorrent_client) against the FastMCP 3.4 API surface.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastmcp import FastMCP


@pytest.fixture
def mock_settings():
    """Mock settings for tests"""
    with patch("rtorrent_mcp.config.settings.settings") as mock_settings:
        mock_settings.APP_NAME = "RTorrent MCP"
        mock_settings.APP_VERSION = "3.0.0"
        mock_settings.ALLOWED_CATEGORIES = ["Anime"]
        mock_settings.ALLOWED_RESOLUTIONS = ["720p", "1080p"]
        yield mock_settings


@pytest.fixture
def mcp_server(mock_settings):
    """FastMCP server instance for integration tests"""
    server = FastMCP(name="RTorrent MCP", instructions="Test server")
    return server


class TestMCPIntegration:
    """Integration tests for MCP server"""

    def test_server_initialization(self, mcp_server):
        """Test server initialization"""
        assert mcp_server.name == "RTorrent MCP"

    @pytest.mark.asyncio
    async def test_tool_registration(self, mcp_server):
        """Test that tools are properly registered"""
        from rtorrent_mcp.services.core_tools import register_core_tools
        from rtorrent_mcp.services.rtorrent_client import register_rtorrent_tools

        register_core_tools(mcp_server)
        register_rtorrent_tools(mcp_server)

        # Check that tools are registered
        tools = await mcp_server.list_tools()
        tool_names = [tool.name for tool in tools]

        assert "help" in tool_names
        assert "get_system_status" in tool_names
        assert "analyze_repo" in tool_names
        assert "add_torrent_rt" in tool_names
        assert "list_rt_torrents" in tool_names

    @pytest.mark.asyncio
    async def test_help_tool_output(self, mcp_server):
        """Test help tool output format"""
        from rtorrent_mcp.services.core_tools import register_core_tools

        register_core_tools(mcp_server)

        help_tool = await mcp_server.get_tool("help")
        result = help_tool.fn()

        # The help tool returns a dict with tools/resources/configuration keys
        assert isinstance(result, dict)
        assert "tools" in result
        assert "resources" in result
        assert "configuration" in result

    @pytest.mark.asyncio
    async def test_rtorrent_tools_with_mock(self, mcp_server):
        """Test rTorrent tools with mocked client"""
        from rtorrent_mcp.services.rtorrent_client import register_rtorrent_tools

        register_rtorrent_tools(mcp_server)

        # Mock the client
        with patch("rtorrent_mcp.services.rtorrent_client.get_rtorrent_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.get_torrents = AsyncMock(return_value=[{"hash": "test", "name": "Test Torrent"}])
            mock_get_client.return_value = mock_client

            # Test list torrents
            list_tool = await mcp_server.get_tool("list_rt_torrents")
            result = await list_tool.fn()

            assert isinstance(result, dict)
            assert "torrents" in result
            assert len(result["torrents"]) == 1
            assert result["torrents"][0]["name"] == "Test Torrent"

    @pytest.mark.asyncio
    async def test_resource_registration(self, mcp_server):
        """Test resource registration"""
        from rtorrent_mcp.services.rtorrent_client import register_rtorrent_tools

        register_rtorrent_tools(mcp_server)

        resources = await mcp_server.list_resources()
        resource_uris = [str(resource.uri) for resource in resources]

        assert "rtorrent://config" in resource_uris

    @pytest.mark.asyncio
    async def test_error_handling(self, mcp_server):
        """Test error handling in tools"""
        from rtorrent_mcp.services.core_tools import register_core_tools

        register_core_tools(mcp_server)

        # get_system_status returns a structured error dict when psutil fails
        with patch("psutil.Process", side_effect=Exception("System error")):
            status_tool = await mcp_server.get_tool("get_system_status")
            result = status_tool.fn()

            assert isinstance(result, dict)
            assert result["server_status"] == "error"
            assert "errors" in result


@pytest.mark.asyncio
class TestAsyncIntegration:
    """Async integration tests"""

    async def test_async_tool_execution(self, mcp_server):
        """Test async tool execution"""
        from rtorrent_mcp.services.rtorrent_client import register_rtorrent_tools

        register_rtorrent_tools(mcp_server)

        # Mock the async client
        with patch("rtorrent_mcp.services.rtorrent_client.get_rtorrent_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.get_torrents = AsyncMock(return_value=[{"hash": "test", "name": "Test"}])
            mock_get_client.return_value = mock_client

            # Test async list torrents
            list_tool = await mcp_server.get_tool("list_rt_torrents")
            result = await list_tool.fn()

            assert isinstance(result, dict)
            assert "torrents" in result
            assert len(result["torrents"]) == 1
