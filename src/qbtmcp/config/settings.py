"""
Configuration settings for RTorrent MCP Server
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    """Application settings"""
    # Application settings
    APP_NAME: str = "RTorrent MCP"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "RTorrent automation with nyaa.si anime search and Austrian legal compliance"

    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # rTorrent settings
    RTORRENT_HOST: str = "localhost"
    RTORRENT_PORT: int = 5000
    RTORRENT_PATH: str = "/var/lib/rtorrent/session"

    # Nyaa.si settings
    NYAA_BASE_URL: str = "https://nyaa.si"

    # Legal compliance settings (Austria-specific)
    ALLOWED_CATEGORIES: list[str] = ["Anime"]
    ALLOWED_RESOLUTIONS: list[str] = ["720p", "1080p"]
    MAX_TORRENT_SIZE_GB: int = 10  # Maximum allowed torrent size in GB

    # Model configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

# Create settings instance
settings = Settings()
