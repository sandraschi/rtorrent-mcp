"""
Test configuration and fixtures for RTorrent MCP Server tests.
"""
import asyncio
import os
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from fastmcp import FastMCP
from qbtmcp.server import RTorrentMCPServer
from qbtmcp.config.settings import Settings

# Add the src directory to the Python path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def test_settings():
    """Fixture providing test settings."""
    return Settings(
        RTORRENT_HOST="localhost",
        RTORRENT_PORT=5000,
        NYAA_BASE_URL="http://test-nyaa",
        DEBUG=True,
        LOG_LEVEL="DEBUG"
    )

@pytest.fixture
def mock_rtorrent_client():
    """Fixture providing a mocked rTorrent client."""
    with patch('qbtmcp.services.qbittorrent_client.RTorrentClient') as mock_client:
        mock_instance = AsyncMock()
        mock_client.return_value = mock_instance
        mock_instance.connect.return_value = True
        yield mock_instance

@pytest.fixture
async def mcp_server(test_settings):
    """Fixture providing a configured MCP server for testing."""
    # Patch settings to use test settings
    with patch('qbtmcp.config.settings.settings', test_settings):
        server = RTorrentMCPServer()
        # Don't actually start the server
        server.setup = AsyncMock()
        server.run_stdio = AsyncMock()
        yield server

@pytest.fixture
def mock_httpx_client():
    """Fixture providing a mocked HTTPX client."""
    with patch('httpx.AsyncClient') as mock_client:
        mock_instance = AsyncMock()
        mock_client.return_value.__aenter__.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def mock_os_environ():
    """Fixture to mock os.environ for testing environment variables."""
    with patch.dict(os.environ, clear=True):
        yield os.environ
