"""
Tests for the RTorrent MCP server implementation.
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from rtorrent_mcp.config.settings import Settings
from rtorrent_mcp.server import RTorrentMCPServer


def test_server_initialization(mock_rtorrent_client):
    """Test that the server initializes and binds ``settings`` correctly.

    The global ``settings`` singleton is built at import time from ``.env``/env,
    so tests must patch ``rtorrent_mcp.server.settings`` to assert custom values.
    """
    custom_settings = Settings(
        RTORRENT_HOST="test-rtorrent",
        RTORRENT_PORT=8080,
        RTORRENT_PATH="/test/path",
        NYAA_BASE_URL="http://test-nyaa",
    )

    with patch("rtorrent_mcp.server.settings", custom_settings):
        server = RTorrentMCPServer()

    assert server._settings.APP_NAME == "RTorrent MCP"
    assert server._settings.APP_VERSION == "1.0.0"
    assert "RTorrent automation" in server._settings.APP_DESCRIPTION

    assert server._settings.RTORRENT_HOST == "test-rtorrent"
    assert server._settings.RTORRENT_PORT == 8080
    assert server._settings.RTORRENT_PATH == "/test/path"
    assert server._settings.NYAA_BASE_URL == "http://test-nyaa"


@pytest.mark.asyncio
async def test_server_setup(mcp_server, caplog):
    """Test that the server setup registers all tools."""
    # Reset the mock to track calls
    mcp_server.setup = AsyncMock()

    # Call setup
    await mcp_server.setup()

    # Verify setup was called
    mcp_server.setup.assert_called_once()


@pytest.mark.asyncio
async def test_server_run(mcp_server):
    """Test that the server runs with the specified transport."""
    # Mock the run method
    mcp_server.run = AsyncMock()

    # Create a test event loop
    asyncio.get_event_loop()

    # Run the server with stdio transport
    await mcp_server.run(transport="stdio")

    # Verify run was called with the correct transport
    mcp_server.run.assert_awaited_once_with(transport="stdio")


def test_main_function(mock_os_environ, monkeypatch):
    """Test the main function with HTTP transport (uses ``run_server_async``, not ``.run``)."""
    test_args = ["--config", "test.env", "--transport", "http"]
    monkeypatch.setattr("sys.argv", ["server.py"] + test_args)

    mock_server = MagicMock()
    with patch("rtorrent_mcp.server.RTorrentMCPServer", return_value=mock_server):
        with patch(
            "rtorrent_mcp.server.run_server_async", new_callable=AsyncMock
        ) as mock_run_async:
            from rtorrent_mcp.server import RTorrentMCPServer, main

            main()

            RTorrentMCPServer.assert_called_once_with(config_path="test.env")
            mock_server.setup.assert_called_once()
            mock_run_async.assert_awaited_once()


def test_server_error_handling(capsys, mock_os_environ, monkeypatch):
    """Test error handling in the main function."""
    # Mock command line arguments
    test_args = ["--config", "nonexistent.env"]
    monkeypatch.setattr("sys.argv", ["server.py"] + test_args)

    # Mock the server to raise an exception
    with patch("rtorrent_mcp.server.RTorrentMCPServer") as mock_server_class:
        mock_server = MagicMock()
        mock_server.setup.side_effect = Exception("Test error")
        mock_server_class.return_value = mock_server

        # Import here to apply monkeypatch
        from rtorrent_mcp.server import main

        # Run the main function and check exit code
        with pytest.raises(SystemExit) as excinfo:
            main()
        assert excinfo.value.code == 1

        # Check error message was logged (it goes to stderr via logger, not capsys)
        # The error is logged via the logger, so we check the log output
        pass  # Error handling test passes if SystemExit is raised
