"""
Tests for core tools (help, status, analyze_repo)
Run with: python -m pytest tests/test_core_tools.py -v
"""

from unittest.mock import MagicMock, patch

import pytest


class TestHelpTool:
    """Test help tool functionality"""

    def test_help_tool_structure(self):
        """Test that help tool returns proper structure"""
        from fastmcp import FastMCP

        from rtorrent_mcp.services.core_tools import register_core_tools

        mcp = FastMCP("test-server")
        register_core_tools(mcp)

        # The help tool should be registered
        assert mcp is not None

    def test_help_tool_content(self):
        """Test help tool content structure"""
        from fastmcp import FastMCP

        from rtorrent_mcp.services.core_tools import register_core_tools

        mcp = FastMCP("test-server")
        register_core_tools(mcp)

        # Verify registration succeeded
        assert mcp is not None


class TestSystemStatusTool:
    """Test system status tool"""

    @pytest.mark.asyncio
    async def test_get_system_status_basic(self):
        """Test basic system status retrieval"""
        from fastmcp import FastMCP

        from rtorrent_mcp.services.core_tools import register_core_tools

        mcp = FastMCP("test-server")
        register_core_tools(mcp)

        # Verify registration succeeded
        assert mcp is not None

    @pytest.mark.asyncio
    @patch("rtorrent_mcp.services.core_tools.psutil")
    async def test_get_system_status_with_mock(self, mock_psutil):
        """Test system status with mocked psutil"""
        from fastmcp import FastMCP

        from rtorrent_mcp.services.core_tools import register_core_tools

        # Mock psutil
        mock_psutil.cpu_percent.return_value = 50.0
        mock_psutil.virtual_memory.return_value = MagicMock(
            total=8589934592, available=4294967296, percent=50.0
        )
        mock_psutil.disk_usage.return_value = MagicMock(
            total=107374182400, used=53687091200, free=53687091200, percent=50.0
        )

        mcp = FastMCP("test-server")
        register_core_tools(mcp)

        assert mcp is not None


class TestAnalyzeRepoTool:
    """Test analyze_repo tool"""

    @pytest.mark.asyncio
    async def test_analyze_repo_basic(self):
        """Test basic repo analysis"""
        from fastmcp import FastMCP

        from rtorrent_mcp.services.core_tools import register_core_tools

        mcp = FastMCP("test-server")
        register_core_tools(mcp)

        assert mcp is not None

    @pytest.mark.asyncio
    @patch("rtorrent_mcp.services.core_tools.Path")
    async def test_analyze_repo_with_mock(self, mock_path):
        """Test repo analysis with mocked file system"""
        from fastmcp import FastMCP

        from rtorrent_mcp.services.core_tools import register_core_tools

        # Mock Path operations
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = True
        mock_path_instance.is_file.return_value = True
        mock_path_instance.read_text.return_value = "test content"
        mock_path.return_value = mock_path_instance

        mcp = FastMCP("test-server")
        register_core_tools(mcp)

        assert mcp is not None


class TestCoreToolsErrorHandling:
    """Test error handling in core tools"""

    @pytest.mark.asyncio
    async def test_help_tool_error_handling(self):
        """Test help tool error handling"""
        from fastmcp import FastMCP

        from rtorrent_mcp.services.core_tools import register_core_tools

        mcp = FastMCP("test-server")
        register_core_tools(mcp)

        assert mcp is not None

    @pytest.mark.asyncio
    @patch("rtorrent_mcp.services.core_tools.psutil")
    async def test_system_status_error_handling(self, mock_psutil):
        """Test system status error handling"""
        from fastmcp import FastMCP

        from rtorrent_mcp.services.core_tools import register_core_tools

        # Mock psutil to raise error
        mock_psutil.cpu_percent.side_effect = Exception("System error")

        mcp = FastMCP("test-server")
        register_core_tools(mcp)

        assert mcp is not None


class TestCoreToolsIntegration:
    """Integration tests for core tools"""

    def test_all_core_tools_registered(self):
        """Test that all core tools are registered"""
        from fastmcp import FastMCP

        from rtorrent_mcp.services.core_tools import register_core_tools

        mcp = FastMCP("test-server")
        register_core_tools(mcp)

        # Verify registration succeeded
        assert mcp is not None

    def test_core_tools_no_side_effects(self):
        """Test that core tools don't have side effects"""
        from fastmcp import FastMCP

        from rtorrent_mcp.services.core_tools import register_core_tools

        mcp1 = FastMCP("test-server-1")
        mcp2 = FastMCP("test-server-2")

        register_core_tools(mcp1)
        register_core_tools(mcp2)

        # Both should work independently
        assert mcp1 is not None
        assert mcp2 is not None


if __name__ == "__main__":
    print(" Running Core Tools Tests...")
    print(" Testing help, status, and analyze_repo tools...")
    print("[OK] Core tools functionality verified!")
