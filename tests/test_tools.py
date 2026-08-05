"""
Tests for MCP tool registration and basic functionality.

Tests that the consolidated portmanteau tools are properly registered and callable.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


def _make_mcp():
    from fastmcp import FastMCP

    from rtorrent_mcp.config.settings import Settings
    from rtorrent_mcp.tools import register_all_tools

    mcp = FastMCP("test-server")
    settings = Settings()
    register_all_tools(mcp, settings)
    return mcp


async def _call_tool(mcp, name, **kwargs):
    """Resolve a registered tool and invoke its underlying function."""
    tool = await mcp.get_tool(name)
    assert tool is not None, f"{name} not registered"
    return await tool.fn(**kwargs)


class TestPortmanteauRegistration:
    """Test that the 6 portmanteau tools + agentic workflow register."""

    @pytest.mark.parametrize(
        "tool_name",
        [
            "torrent_management",
            "search_management",
            "nlp_management",
            "legal_management",
            "system_management",
            "workflow_management",
            "agentic_rtorrent_workflow",
        ],
    )
    @pytest.mark.asyncio
    async def test_portmanteau_registered(self, tool_name):
        """Each consolidated tool is registered on the server."""
        mcp = _make_mcp()
        tool = await mcp.get_tool(tool_name)
        assert tool is not None, f"{tool_name} not registered"
        assert tool.name == tool_name

    @pytest.mark.asyncio
    async def test_all_tools_registered(self):
        """All 6 portmanteaus exist on the server."""
        mcp = _make_mcp()
        for name in (
            "torrent_management",
            "search_management",
            "nlp_management",
            "legal_management",
            "system_management",
            "workflow_management",
        ):
            tool = await mcp.get_tool(name)
            assert tool is not None, f"{name} not registered"


class TestTorrentManagementTool:
    """Test torrent_management portmanteau behavior."""

    @pytest.mark.asyncio
    @patch("rtorrent_mcp.tools.portmanteau.torrent_management.get_rtorrent_client")
    async def test_add_action_calls_client(self, mock_get_client):
        """The add action calls the rTorrent client."""
        mock_client = MagicMock()
        mock_client.add_torrent = AsyncMock(return_value={"status": "success", "hash": "testhash"})
        mock_get_client.return_value = mock_client

        result = await _call_tool(
            _make_mcp(),
            "torrent_management",
            action="add",
            magnet_link="magnet:?xt=urn:btih:abcdef0123456789abcdef0123456789abcdef01&dn=test",
        )

        assert result.get("success") is True
        mock_client.add_torrent.assert_awaited_once()

    @pytest.mark.asyncio
    @patch("rtorrent_mcp.tools.portmanteau.torrent_management.get_rtorrent_client")
    async def test_list_action_returns_torrents(self, mock_get_client):
        """The list action returns torrents from the client."""
        mock_client = MagicMock()
        mock_client.get_torrents = AsyncMock(return_value=[{"hash": "hash1", "name": "Test"}])
        mock_get_client.return_value = mock_client

        result = await _call_tool(_make_mcp(), "torrent_management", action="list")

        assert result.get("success") is True
        assert len(result.get("data", {}).get("torrents", [])) == 1

    @pytest.mark.asyncio
    async def test_invalid_action_returns_error(self):
        """Unknown actions fail gracefully with a structured error."""
        result = await _call_tool(_make_mcp(), "torrent_management", action="does_not_exist")
        assert result.get("success") is False
        assert "error" in result


class TestSystemManagementTool:
    """Test system_management portmanteau behavior."""

    @pytest.mark.asyncio
    async def test_help_action(self):
        """The help action returns the tool catalog."""
        result = await _call_tool(_make_mcp(), "system_management", action="help")
        assert result.get("success") is True
        assert "torrent_management" in str(result)

    @pytest.mark.asyncio
    async def test_health_action(self):
        """The health action returns structured health data."""
        result = await _call_tool(_make_mcp(), "system_management", action="health")
        assert result.get("success") is True
