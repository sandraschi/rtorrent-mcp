"""
Configuration settings for qBTMCP (qBittorrent MCP Server)
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    """Application settings"""
    # Application settings
    APP_NAME: str = "qBTMCP"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "qBittorrent automation with nyaa.si anime search and Austrian legal compliance"
    
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    # qBittorrent settings
    QBITTORRENT_URL: str = "http://localhost:8080"
    QBITTORRENT_USERNAME: str = "admin"
    QBITTORRENT_PASSWORD: str = "adminadmin"
    
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
