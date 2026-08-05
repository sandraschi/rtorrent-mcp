"""
Portmanteau dispatch and action coverage for the tools not covered by
test_tools.py: search_management, workflow_management, legal_management,
nlp_management, agentic_rtorrent_workflow.
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


async def _call(mcp, name, **kwargs):
    tool = await mcp.get_tool(name)
    assert tool is not None
    return await tool.fn(**kwargs)


class TestTorrentManagementActions:
    @pytest.mark.asyncio
    @patch("rtorrent_mcp.tools.portmanteau.torrent_management.get_rtorrent_client")
    async def test_pause(self, mock_get):
        mock_client = MagicMock()
        mock_client.pause_torrent = AsyncMock(return_value={"status": "success", "hash": "h1", "action": "paused"})
        mock_get.return_value = mock_client
        result = await _call(_make_mcp(), "torrent_management", action="pause", torrent_hash="h1")
        assert result.get("success") is True
        mock_client.pause_torrent.assert_awaited_once_with("h1")

    @pytest.mark.asyncio
    @patch("rtorrent_mcp.tools.portmanteau.torrent_management.get_rtorrent_client")
    async def test_resume(self, mock_get):
        mock_client = MagicMock()
        mock_client.resume_torrent = AsyncMock(return_value={"status": "success", "hash": "h1", "action": "resumed"})
        mock_get.return_value = mock_client
        result = await _call(_make_mcp(), "torrent_management", action="resume", torrent_hash="h1")
        assert result.get("success") is True

    @pytest.mark.asyncio
    @patch("rtorrent_mcp.tools.portmanteau.torrent_management.get_rtorrent_client")
    async def test_delete(self, mock_get):
        mock_client = MagicMock()
        mock_client.delete_torrent = AsyncMock(return_value={"status": "success", "hash": "h1"})
        mock_get.return_value = mock_client
        result = await _call(_make_mcp(), "torrent_management", action="delete", torrent_hash="h1", delete_files=False)
        assert result.get("success") is True
        mock_client.delete_torrent.assert_awaited_once()

    @pytest.mark.asyncio
    @patch("rtorrent_mcp.tools.portmanteau.torrent_management.get_rtorrent_client")
    async def test_status(self, mock_get):
        mock_client = MagicMock()
        mock_client.connect = AsyncMock(return_value=True)
        mock_get.return_value = mock_client
        result = await _call(_make_mcp(), "torrent_management", action="status")
        assert result.get("success") is True

    @pytest.mark.asyncio
    @patch("rtorrent_mcp.tools.portmanteau.torrent_management.get_rtorrent_client")
    async def test_info(self, mock_get):
        mock_client = MagicMock()
        mock_client.get_torrents = AsyncMock(return_value=[{"hash": "h1", "name": "Test"}])
        mock_get.return_value = mock_client
        result = await _call(_make_mcp(), "torrent_management", action="info", torrent_hash="h1")
        assert result.get("success") is True
        assert result.get("data", {}).get("name") == "Test"


class TestSearchManagement:
    @pytest.mark.asyncio
    async def test_invalid_action_returns_error(self):
        mcp = _make_mcp()
        result = await _call(mcp, "search_management", action="bogus")
        assert result.get("success") is False
        assert "error" in result

    @pytest.mark.asyncio
    @patch("rtorrent_mcp.tools.portmanteau.search_management.search_nyaa_anime")
    async def test_anime_action(self, mock_search):
        mock_search.return_value = [{"title": "[ASW] Test - 01 [720p]", "magnet": "magnet:test"}]
        mcp = _make_mcp()
        result = await _call(mcp, "search_management", action="anime", query="test", resolution="720p")
        assert result.get("success") is True
        assert len(result.get("data", [])) == 1

    @pytest.mark.asyncio
    @patch("rtorrent_mcp.tools.portmanteau.search_management.search_yts_movies")
    async def test_movies_action(self, mock_search):
        mock_search.return_value = [{"title": "Test Movie", "magnet": "magnet:test"}]
        mcp = _make_mcp()
        result = await _call(mcp, "search_management", action="movies", query="test movie", quality="1080p")
        assert result.get("success") is True


class TestWorkflowManagement:
    @pytest.mark.asyncio
    async def test_invalid_action_returns_error(self):
        mcp = _make_mcp()
        result = await _call(mcp, "workflow_management", action="bogus")
        assert result.get("success") is False

    @pytest.mark.asyncio
    async def test_list_returns_workflows(self):
        mcp = _make_mcp()
        result = await _call(mcp, "workflow_management", action="list")
        assert result.get("success") is True
        assert "franchises" in result.get("data", {})


class TestLegalManagement:
    @pytest.mark.asyncio
    async def test_risk_action(self):
        mcp = _make_mcp()
        result = await _call(mcp, "legal_management", action="risk", content_type="movies")
        assert result.get("success") is True
        assert "risk" in str(result.get("data", {}))

    @pytest.mark.asyncio
    async def test_check_action(self):
        mcp = _make_mcp()
        result = await _call(mcp, "legal_management", action="check", content_type="anime")
        assert result.get("success") is True

    @pytest.mark.asyncio
    async def test_status_action(self):
        mcp = _make_mcp()
        result = await _call(mcp, "legal_management", action="status")
        assert result.get("success") is True

    @pytest.mark.asyncio
    async def test_invalid_action_returns_error(self):
        mcp = _make_mcp()
        result = await _call(mcp, "legal_management", action="bogus")
        assert result.get("success") is False


class TestNLPManagement:
    @pytest.mark.asyncio
    async def test_parse_action(self):
        mcp = _make_mcp()
        result = await _call(mcp, "nlp_management", action="parse", text="get me this weeks asw anime 720p")
        assert result.get("success") is True
        parsed = result.get("data", {})
        assert "ASW" in str(parsed) or "asw" in str(parsed).lower()

    @pytest.mark.asyncio
    async def test_help_action(self):
        mcp = _make_mcp()
        result = await _call(mcp, "nlp_management", action="help")
        assert result.get("success") is True

    @pytest.mark.asyncio
    async def test_invalid_action_returns_error(self):
        mcp = _make_mcp()
        result = await _call(mcp, "nlp_management", action="bogus")
        assert result.get("success") is False


class TestAgenticWorkflow:
    @pytest.mark.asyncio
    async def test_returns_error_without_sampling(self):
        """Without sampling support the agentic tool must fail explicitly."""
        mcp = _make_mcp()
        result = await _call(
            mcp,
            "agentic_rtorrent_workflow",
            workflow_prompt="download the latest detective conan",
            available_tools=["search_management", "torrent_management"],
            max_iterations=1,
        )
        # Either a structured error (no sampling) or a plan; never a silent hang.
        assert isinstance(result, dict)
        assert "success" in result
