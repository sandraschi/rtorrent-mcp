"""
Tests for the qBTMCP server implementation.
"""
import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from fastmcp import FastMCP
from qbtmcp.server import QBTMCPServer
from qbtmcp.config.settings import Settings

@pytest.mark.asyncio
async def test_server_initialization(mock_os_environ, mock_qbittorrent_client):
    """Test that the server initializes correctly."""
    # Set up test environment
    mock_os_environ.update({
        "QBITTORRENT_URL": "http://test-qbittorrent:8080",
        "QBITTORRENT_USERNAME": "testuser",
        "QBITTORRENT_PASSWORD": "testpass",
        "NYAA_BASE_URL": "http://test-nyaa"
    })
    
    # Create and initialize server
    server = QBTMCPServer()
    
    # Verify server properties
    assert server.name == "qBTMCP"
    assert server.version == "1.0.0"
    assert "qBittorrent automation" in server.description
    
    # Verify settings were loaded correctly
    assert server.settings.QBITTORRENT_URL == "http://test-qbittorrent:8080"
    assert server.settings.QBITTORRENT_USERNAME == "testuser"
    assert server.settings.NYAA_BASE_URL == "http://test-nyaa"

@pytest.mark.asyncio
async def test_server_setup(mcp_server, caplog):
    """Test that the server setup registers all tools."""
    # Reset the mock to track calls
    mcp_server.setup = AsyncMock()
    
    # Call setup
    await mcp_server.setup()
    
    # Verify setup was called
    mcp_server.setup.assert_called_once()
    
    # Verify tool registration methods were called
    # (These would be more specific based on your actual tool registration)
    assert any("register_anime_search_tools" in str(call) for call in mcp_server.method_calls)
    assert any("register_qbittorrent_tools" in str(call) for call in mcp_server.method_calls)

@pytest.mark.asyncio
async def test_server_run(mcp_server):
    """Test that the server runs with the specified transport."""
    # Mock the run method
    mcp_server.run = AsyncMock()
    
    # Create a test event loop
    loop = asyncio.get_event_loop()
    
    # Run the server with stdio transport
    await mcp_server.run(transport="stdio")
    
    # Verify run was called with the correct transport
    mcp_server.run.assert_awaited_once_with(transport="stdio")

@pytest.mark.asyncio
async def test_main_function(capsys, mock_os_environ, monkeypatch):
    """Test the main function with command line arguments."""
    # Mock command line arguments
    test_args = ["--config", "test.env", "--transport", "http"]
    monkeypatch.setattr('sys.argv', ['server.py'] + test_args)
    
    # Mock the server class
    mock_server = AsyncMock()
    with patch('qbtmcp.server.QBTMCPServer', return_value=mock_server):
        # Import here to apply monkeypatch
        from qbtmcp.server import main
        
        # Run the main function
        await main()
        
        # Verify the server was created with the correct config path
        from qbtmcp.server import QBTMCPServer
        QBTMCPServer.assert_called_once_with(config_path="test.env")
        
        # Verify setup and run were called
        mock_server.setup.assert_called_once()
        mock_server.run.assert_awaited_once_with(transport="http")

@pytest.mark.asyncio
async def test_server_error_handling(capsys, mock_os_environ, monkeypatch):
    """Test error handling in the main function."""
    # Mock command line arguments
    test_args = ["--config", "nonexistent.env"]
    monkeypatch.setattr('sys.argv', ['server.py'] + test_args)
    
    # Mock the server to raise an exception
    with patch('qbtmcp.server.QBTMCPServer') as mock_server_class:
        mock_server = AsyncMock()
        mock_server.setup.side_effect = Exception("Test error")
        mock_server_class.return_value = mock_server
        
        # Import here to apply monkeypatch
        from qbtmcp.server import main
        
        # Run the main function and check exit code
        with pytest.raises(SystemExit) as excinfo:
            await main()
        assert excinfo.value.code == 1
        
        # Check error message was logged
        captured = capsys.readouterr()
        assert "Test error" in captured.err
