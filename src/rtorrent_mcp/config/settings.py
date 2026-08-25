"""
Configuration settings for RTorrent MCP Server
"""

import json
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# ``src/rtorrent_mcp/config/settings.py`` → repo root (so ``.env`` loads even if cwd is ``web_sota/``)
_REPO_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    """Application settings"""

    # Application settings
    APP_NAME: str = "RTorrent MCP"
    APP_VERSION: str = "3.0.0"
    APP_DESCRIPTION: str = "RTorrent automation with nyaa.si anime search and Austrian legal compliance"

    # Server settings
    HOST: str = "127.0.0.1"
    PORT: int = 10910
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # rTorrent settings
    RTORRENT_HOST: str = "localhost"
    RTORRENT_PORT: int = 12224  # XMLRPC through nginx (maps to container port 8000)
    RTORRENT_PATH: str = "/var/lib/rtorrent/session"

    # Nyaa.si settings
    NYAA_BASE_URL: str = "https://nyaa.si"
    NYAA_ASW_USERNAME: str = "AkihitoSubsWeeklies"

    # The Pirate Bay settings (domain changes frequently)
    PIRATEBAY_BASE_URL: str = "https://thepiratebay10.xyz"

    # Legal compliance settings (Austria-specific)
    ALLOWED_CATEGORIES_STR: str = "Anime"
    ALLOWED_RESOLUTIONS_STR: str = "720p,1080p"
    MAX_TORRENT_SIZE_GB: int = 10  # Maximum allowed torrent size in GB

    # Post-processing settings
    POST_PROCESSING_ENABLED: bool = False
    POST_PROCESSING_POLL_INTERVAL: int = 60  # Seconds between checks for completed downloads
    DELETE_TORRENT_AFTER_COMPLETE: bool = True  # Remove torrent after completion (no sharing)
    NORMALIZE_FILENAMES: bool = True  # Normalize filenames (remove release group tags)

    # Temporary ingestion folders (staging area before Plex organizes)
    INGESTION_ANIME_PATH: str = ""  # Temporary ingestion folder for anime (e.g., "D:/Ingestion/Anime")
    INGESTION_TV_PATH: str = ""  # Temporary ingestion folder for TV shows (e.g., "D:/Ingestion/TV")
    INGESTION_MOVIES_PATH: str = ""  # Temporary ingestion folder for movies (e.g., "D:/Ingestion/Movies")

    # Metadata API keys (optional)
    OMDB_API_KEY: str = ""  # OMDb API key for IMDb metadata (free at omdbapi.com)
    TVDB_API_KEY: str = ""  # TVDB API key (requires subscription)
    TVDB_PIN: str = ""  # TVDB PIN (required for v4 API)

    # API authentication (optional - if set, all /api/* endpoints require this key)
    API_KEY: str = ""

    # Media service integration (Plex/Jellyfin - for direct downloads without *arr)
    # For *arr-managed content: configure rTorrent as download client in Radarr/Sonarr directly
    PLEX_URL: str = ""
    PLEX_TOKEN: str = ""
    JELLYFIN_URL: str = ""
    JELLYFIN_API_KEY: str = ""

    # FastMCP 3.1 sampling (OpenAI-compatible; default Ollama on localhost)
    RTORRENT_SAMPLING_BASE_URL: str = "http://127.0.0.1:11434/v1"
    RTORRENT_SAMPLING_API_KEY: str | None = None
    RTORRENT_SAMPLING_MODEL: str = "llama3.2"

    @property
    def sampling_base_url(self) -> str:
        return self.RTORRENT_SAMPLING_BASE_URL.rstrip("/")

    @property
    def sampling_api_key(self) -> str | None:
        key = self.RTORRENT_SAMPLING_API_KEY
        if key is not None and str(key).strip() == "":
            return None
        return key

    @property
    def sampling_model(self) -> str:
        return self.RTORRENT_SAMPLING_MODEL

    @property
    def ALLOWED_CATEGORIES(self) -> list[str]:
        """Parse ALLOWED_CATEGORIES_STR as list"""
        if self.ALLOWED_CATEGORIES_STR.startswith("["):
            try:
                return json.loads(self.ALLOWED_CATEGORIES_STR)
            except (json.JSONDecodeError, TypeError):
                pass
        return [cat.strip() for cat in self.ALLOWED_CATEGORIES_STR.split(",") if cat.strip()]

    @property
    def ALLOWED_RESOLUTIONS(self) -> list[str]:
        """Parse ALLOWED_RESOLUTIONS_STR as list"""
        if self.ALLOWED_RESOLUTIONS_STR.startswith("["):
            try:
                return json.loads(self.ALLOWED_RESOLUTIONS_STR)
            except (json.JSONDecodeError, TypeError):
                pass
        return [res.strip() for res in self.ALLOWED_RESOLUTIONS_STR.split(",") if res.strip()]

    # Model configuration
    model_config = SettingsConfigDict(
        env_file=(str(_REPO_ROOT / ".env"), ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


def get_settings(env_file: str | None = None) -> Settings:
    """Create Settings from env, optionally overriding the env_file path.

    When env_file is provided, the .env file at that path is loaded first,
    then pydantic-settings reads os.environ + the default env_file fallback.
    """
    import os as _os

    from dotenv import load_dotenv as _load_dotenv

    if env_file:
        _os.environ["ENV_FILE"] = env_file
        _load_dotenv(env_file, override=True)
    return Settings()


settings = get_settings()
