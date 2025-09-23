"""
Integration tests for RTorrent MCP server
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from fastmcp import FastMCP


@pytest.fixture
def mock_settings():
    """Mock settings for tests"""
    with patch('src.qbtmcp.config.settings.settings') as mock_settings:
        mock_settings.APP_NAME = "RTorrent MCP"
        mock_settings.APP_VERSION = "1.0.0"
        mock_settings.ALLOWED_CATEGORIES = ["Anime"]
        mock_settings.ALLOWED_RESOLUTIONS = ["720p", "1080p"]
        yield mock_settings


@pytest.fixture
def mcp_server(mock_settings):
    """FastMCP server instance for integration tests"""
    server = FastMCP(
        name="RTorrent MCP",
        version="1.0.0",
        description="Test server"
    )
    return server


class TestMCPIntegration:
    """Integration tests for MCP server"""

    def test_server_initialization(self, mcp_server):
        """Test server initialization"""
        assert mcp_server.name == "RTorrent MCP"
        assert mcp_server.version == "1.0.0"

    def test_tool_registration(self, mcp_server):
        """Test that tools are properly registered"""
        from src.qbtmcp.services.core_tools import register_core_tools
        from src.qbtmcp.services.rtorrent_client import register_rtorrent_tools

        register_core_tools(mcp_server)
        register_rtorrent_tools(mcp_server)

        # Check that tools are registered
        tools = mcp_server.get_tools()
        tool_names = [tool.name for tool in tools]

        assert "help" in tool_names
        assert "get_system_status" in tool_names
        assert "analyze_repo" in tool_names
        assert "add_torrent_rt" in tool_names
        assert "list_rt_torrents" in tool_names

    def test_help_tool_output(self, mcp_server):
        """Test help tool output format"""
        from src.qbtmcp.services.core_tools import register_core_tools

        register_core_tools(mcp_server)

        # Mock the help function
        help_tool = mcp_server.get_tool("help")
        result = help_tool.func()

        assert isinstance(result, dict)
        assert "tools" in result
        assert "resources" in result
        assert "configuration" in result
        assert "troubleshooting" in result

    def test_rtorrent_tools_with_mock(self, mcp_server):
        """Test rTorrent tools with mocked client"""
        from src.qbtmcp.services.rtorrent_client import register_rtorrent_tools

        register_rtorrent_tools(mcp_server)

        # Mock the client
        with patch('src.qbtmcp.services.rtorrent_client.get_rtorrent_client') as mock_get_client:
            mock_client = MagicMock()
            mock_client.get_torrents.return_value = [{"hash": "test", "name": "Test Torrent"}]
            mock_get_client.return_value = mock_client

            # Test list torrents
            list_tool = mcp_server.get_tool("list_rt_torrents")
            result = list_tool.func()

            assert isinstance(result, list)
            assert len(result) == 1
            assert result[0]["name"] == "Test Torrent"

    def test_resource_registration(self, mcp_server):
        """Test resource registration"""
        from src.qbtmcp.services.rtorrent_client import register_rtorrent_tools

        register_rtorrent_tools(mcp_server)

        resources = mcp_server.get_resources()
        resource_uris = [resource.uri for resource in resources]

        assert "rtorrent://config" in resource_uris

    def test_error_handling(self, mcp_server):
        """Test error handling in tools"""
        from src.qbtmcp.services.core_tools import register_core_tools

        register_core_tools(mcp_server)

        # Test help tool error handling
        help_tool = mcp_server.get_tool("help")

        # Simulate an error
        with patch('src.qbtmcp.services.core_tools.logger') as mock_logger:
            # Force an error in help function
            with patch('src.qbtmcp.services.core_tools.json.dumps', side_effect=Exception("Test error")):
                result = help_tool.func()

                assert "error" in result
                assert "Test error" in result["error"]
                mock_logger.error.assert_called()


@pytest.mark.asyncio
class TestAsyncIntegration:
    """Async integration tests"""

    async def test_async_tool_execution(self, mcp_server):
        """Test async tool execution"""
        from src.qbtmcp.services.rtorrent_client import register_rtorrent_tools

        register_rtorrent_tools(mcp_server)

        # Mock the async client
        with patch('src.qbtmcp.services.rtorrent_client.get_rtorrent_client') as mock_get_client:
            mock_client = MagicMock()
            mock_client.get_torrents = AsyncMock(return_value=[{"hash": "test", "name": "Test"}])
            mock_get_client.return_value = mock_client

            # Test async list torrents
            list_tool = mcp_server.get_tool("list_rt_torrents")
            result = await list_tool.func()

            assert isinstance(result, list)
            assert len(result) == 1
