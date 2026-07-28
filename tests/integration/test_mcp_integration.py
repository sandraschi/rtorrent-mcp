"""
Integration tests for RTorrent MCP server
"""

import json
from unittest.mock import MagicMock, patch

import pytest
from fastmcp import FastMCP


@pytest.fixture
def mock_settings():
    """Mock settings for tests"""
    with patch("rtorrent_mcp.config.settings.settings") as mock_settings:
        mock_settings.APP_NAME = "RTorrent MCP"
        mock_settings.APP_VERSION = "1.0.0"
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
        tools = await mcp_server.get_tools()
        tool_names = [tool.name for tool in tools]

        assert "help" in tool_names
        assert "get_system_status" in tool_names
        assert "analyze_repo" in tool_names
        assert "add_torrent" in tool_names
        assert "list_torrents" in tool_names

    @pytest.mark.asyncio
    async def test_help_tool_output(self, mcp_server):
        """Test help tool output format"""
        from rtorrent_mcp.services.core_tools import register_core_tools

        register_core_tools(mcp_server)

        # Mock the help function
        help_tool = await mcp_server.get_tool("help")
        result = await help_tool.run({})

        # ToolResult has a content attribute with TextContent
        assert hasattr(result, "content")
        content = result.content
        # Content is a list of TextContent objects
        assert isinstance(content, list)
        assert len(content) > 0
        text_content = content[0].text
        assert isinstance(text_content, str)
        # Parse the JSON content
        parsed_content = json.loads(text_content)
        assert "tools" in parsed_content
        assert "resources" in parsed_content
        assert "configuration" in parsed_content

    @pytest.mark.asyncio
    async def test_rtorrent_tools_with_mock(self, mcp_server):
        """Test rTorrent tools with mocked client"""
        from rtorrent_mcp.services.rtorrent_client import register_rtorrent_tools

        register_rtorrent_tools(mcp_server)

        # Mock the client
        with patch("rtorrent_mcp.services.rtorrent_client.get_rtorrent_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.get_torrents.return_value = [{"hash": "test", "name": "Test Torrent"}]
            mock_get_client.return_value = mock_client

            # Test list torrents
            list_tool = await mcp_server.get_tool("list_torrents")
            result = await list_tool.run({})

            # ToolResult has a content attribute
            assert hasattr(result, "content")
            content = result.content
            assert isinstance(content, dict)
            assert "torrents" in content
            assert len(content["torrents"]) == 1
            assert content["torrents"][0]["name"] == "Test Torrent"

    @pytest.mark.asyncio
    async def test_resource_registration(self, mcp_server):
        """Test resource registration"""
        from rtorrent_mcp.services.rtorrent_client import register_rtorrent_tools

        register_rtorrent_tools(mcp_server)

        resources = await mcp_server.get_resources()
        resource_uris = [resource.uri for resource in resources]

        assert "rtorrent://config" in resource_uris

    @pytest.mark.asyncio
    async def test_error_handling(self, mcp_server):
        """Test error handling in tools"""
        from rtorrent_mcp.services.core_tools import register_core_tools

        register_core_tools(mcp_server)

        # Test help tool error handling
        help_tool = await mcp_server.get_tool("help")

        # Simulate an error
        with patch("rtorrent_mcp.services.core_tools.logger") as mock_logger:
            # Force an error in help function
            with patch("rtorrent_mcp.services.core_tools.json.dumps", side_effect=Exception("Test error")):
                result = await help_tool.run({})

                # ToolResult has a content attribute with TextContent
                assert hasattr(result, "content")
                content = result.content
                # Content is a list of TextContent objects
                assert isinstance(content, list)
                assert len(content) > 0
                # The help tool should return help content, not error content
                # since the error is caught and handled gracefully
                text_content = content[0].text
                assert isinstance(text_content, str)
                mock_logger.error.assert_called()


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
            mock_client.get_torrents = MagicMock(return_value=[{"hash": "test", "name": "Test"}])
            mock_get_client.return_value = mock_client

            # Test async list torrents
            list_tool = await mcp_server.get_tool("list_torrents")
            result = await list_tool.run({})

            # ToolResult has a content attribute
            assert hasattr(result, "content")
            content = result.content
            assert isinstance(content, dict)
            assert "torrents" in content
            assert len(content["torrents"]) == 1
