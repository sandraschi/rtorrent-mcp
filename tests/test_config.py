"""
Tests for the qBTMCP configuration settings.
"""
import os
import pytest
from pathlib import Path
from unittest.mock import patch, mock_open

from qbtmcp.config.settings import Settings, settings

def test_default_settings():
    """Test that default settings are correctly set."""
    # Create a new settings instance without environment overrides
    test_settings = Settings()
    
    # Check default values
    assert test_settings.APP_NAME == "qBTMCP"
    assert test_settings.APP_VERSION == "1.0.0"
    assert "qBittorrent automation" in test_settings.APP_DESCRIPTION
    assert test_settings.HOST == "0.0.0.0"
    assert test_settings.PORT == 8000
    assert test_settings.DEBUG is False
    assert test_settings.LOG_LEVEL == "INFO"
    assert test_settings.QBITTORRENT_URL == "http://localhost:8080"
    assert test_settings.QBITTORRENT_USERNAME == "admin"
    assert test_settings.QBITTORRENT_PASSWORD == "adminadmin"
    assert test_settings.NYAA_BASE_URL == "https://nyaa.si"
    assert "Anime" in test_settings.ALLOWED_CATEGORIES
    assert "720p" in test_settings.ALLOWED_RESOLUTIONS
    assert test_settings.MAX_TORRENT_SIZE_GB == 10

def test_environment_variable_override():
    """Test that environment variables override default settings."""
    # Set up environment variables
    env_vars = {
        "QBITTORRENT_URL": "http://custom-qbittorrent:1234",
        "QBITTORRENT_USERNAME": "customuser",
        "QBITTORRENT_PASSWORD": "custompass",
        "NYAA_BASE_URL": "http://custom-nyaa",
        "DEBUG": "true",
        "LOG_LEVEL": "DEBUG",
        "ALLOWED_CATEGORIES": "Anime,Music",
        "ALLOWED_RESOLUTIONS": "1080p,4K",
        "MAX_TORRENT_SIZE_GB": "20"
    }
    
    with patch.dict(os.environ, env_vars, clear=True):
        test_settings = Settings()
        
        # Check that environment variables override defaults
        assert test_settings.QBITTORRENT_URL == "http://custom-qbittorrent:1234"
        assert test_settings.QBITTORRENT_USERNAME == "customuser"
        assert test_settings.QBITTORRENT_PASSWORD == "custompass"
        assert test_settings.NYAA_BASE_URL == "http://custom-nyaa"
        assert test_settings.DEBUG is True
        assert test_settings.LOG_LEVEL == "DEBUG"
        assert "Anime" in test_settings.ALLOWED_CATEGORIES
        assert "Music" in test_settings.ALLOWED_CATEGORIES
        assert "1080p" in test_settings.ALLOWED_RESOLUTIONS
        assert "4K" in test_settings.ALLOWED_RESOLUTIONS
        assert test_settings.MAX_TORRENT_SIZE_GB == 20

def test_env_file_loading(tmp_path):
    """Test that settings can be loaded from a .env file."""
    # Create a temporary .env file
    env_content = """
    QBITTORRENT_URL=http://from-env-file:8080
    QBITTORRENT_USERNAME=envuser
    QBITTORRENT_PASSWORD=envpass
    DEBUG=true
    """
    
    env_file = tmp_path / ".env"
    env_file.write_text(env_content)
    
    # Test loading settings from the .env file
    test_settings = Settings(_env_file=str(env_file))
    
    # Check that values from .env file are used
    assert test_settings.QBITTORRENT_URL == "http://from-env-file:8080"
    assert test_settings.QBITTORRENT_USERNAME == "envuser"
    assert test_settings.QBITTORRENT_PASSWORD == "envpass"
    assert test_settings.DEBUG is True
    
    # Check that other settings still use defaults
    assert test_settings.NYAA_BASE_URL == "https://nyaa.si"
    assert test_settings.PORT == 8000

def test_settings_singleton():
    """Test that the settings instance is a singleton."""
    # Import the settings instance
    from qbtmcp.config.settings import settings as settings1
    from qbtmcp.config.settings import settings as settings2
    
    # Verify they are the same object
    assert settings1 is settings2
    
    # Verify changing one affects the other
    original_debug = settings1.DEBUG
    settings1.DEBUG = not original_debug
    assert settings2.DEBUG == (not original_debug)
    
    # Clean up
    settings1.DEBUG = original_debug

def test_invalid_settings_validation():
    """Test that invalid settings raise validation errors."""
    # Test with invalid port
    with pytest.raises(ValueError):
        Settings(PORT=100000)  # Port out of range
    
    # Test with invalid URL
    with pytest.raises(ValueError):
        Settings(QBITTORRENT_URL="not-a-url")
    
    # Test with invalid log level
    with pytest.raises(ValueError):
        Settings(LOG_LEVEL="INVALID_LEVEL")
