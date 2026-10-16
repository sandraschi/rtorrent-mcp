"""Torrent backend protocol + factory (dual-backend seam).

Tools (`torrent_management`, `post_processor`, `media_integrator`) program
against `TorrentBackend`, never against rTorrent XML-RPC or the qBittorrent
WebUI API directly. See docs/DUAL_BACKEND_SPEC.md.
"""

import os
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class TorrentBackend(Protocol):
    """Minimal surface every torrent backend must implement."""

    backend_name: str

    async def connect(self) -> bool:
        """Establish the backend session. True when usable."""
        ...

    async def get_torrents(self) -> list[dict[str, Any]]:
        """All torrents as {hash, name, state, size_bytes, completed_bytes, progress}."""
        ...

    async def add_torrent(self, magnet_link: str, category: str = "anime") -> dict[str, Any]:
        """Add from magnet; returns {status, hash?, message, ...}."""
        ...

    async def pause_torrent(self, torrent_hash: str) -> dict[str, Any]:
        """Stop/pause a torrent (also the no-seed primitive)."""
        ...

    async def resume_torrent(self, torrent_hash: str) -> dict[str, Any]:
        """Resume a paused torrent."""
        ...

    async def delete_torrent(self, torrent_hash: str, delete_files: bool = False) -> dict[str, Any]:
        """Remove (and optionally erase data for) a torrent."""
        ...

    async def get_torrent_base_path(self, torrent_hash: str) -> str:
        """Base path (directory or file) for local file processing."""
        ...

    async def get_torrent_directory(self, torrent_hash: str) -> str:
        """Containing directory for local file processing."""
        ...

    async def is_torrent_complete(self, torrent_hash: str) -> bool:
        """True at >= 99.9% (handles rounding on both backends)."""
        ...

    async def enforce_no_seed(self) -> dict[str, Any]:
        """Backend-specific no-seed enforcement (global caps). Re-run on
        every (re)connect so restarts can't silently re-enable seeding."""
        ...

    def describe(self) -> dict[str, Any]:
        """Connection info for status callers (no secrets)."""
        ...

    async def get_torrent_category(self, torrent_hash: str) -> str:
        """Routing category for post-processing (custom1 / qBit category)."""
        ...

    async def erase_torrent(self, torrent_hash: str) -> dict[str, Any]:
        """Remove the torrent entry AND its original data (post-processing
        cleanup after files were moved/linked elsewhere)."""
        ...


def get_torrent_backend(settings: Any) -> TorrentBackend:
    """Factory: TORRENT_BACKEND=rtorrent (default) or qbittorrent.

    Raises ValueError naming the valid set on anything else (fail fast).
    """
    from .qbittorrent_client import QBittorrentClient
    from .rtorrent_client import RTorrentClient

    which = str(getattr(settings, "TORRENT_BACKEND", "rtorrent") or "rtorrent").lower()
    if which == "rtorrent":
        return RTorrentClient(
            host=getattr(settings, "RTORRENT_HOST", "localhost"),
            port=int(getattr(settings, "RTORRENT_PORT", 12224)),
        )
    if which == "qbittorrent":
        return QBittorrentClient(
            base_url=getattr(settings, "QBITTORRENT_URL", "http://localhost:18080"),
            api_key=getattr(settings, "QBITTORRENT_API_KEY", "") or None,
            username=getattr(settings, "QBITTORRENT_USERNAME", "") or None,
            password=getattr(settings, "QBITTORRENT_PASSWORD", "") or None,
        )
    raise ValueError(f"Unknown TORRENT_BACKEND={which!r}; valid: rtorrent, qbittorrent")


_backend_singleton: TorrentBackend | None = None


async def get_torrent_client() -> TorrentBackend:
    """Env-based backend singleton (tool path; mirrors get_rtorrent_client).

    Reads TORRENT_BACKEND / RTORRENT_* / QBITTORRENT_* from the environment
    so tool calls need no settings object. Default: rtorrent (unchanged).
    """
    global _backend_singleton
    if _backend_singleton is not None:
        return _backend_singleton
    from .qbittorrent_client import QBittorrentClient
    from .rtorrent_client import RTorrentClient

    which = (os.environ.get("TORRENT_BACKEND") or "rtorrent").lower()
    if which == "rtorrent":
        _backend_singleton = RTorrentClient(
            host=os.environ.get("RTORRENT_HOST", "localhost"),
            port=int(os.environ.get("RTORRENT_PORT", "12224")),
        )
    elif which == "qbittorrent":
        _backend_singleton = QBittorrentClient(
            base_url=os.environ.get("QBITTORRENT_URL", "http://localhost:18080"),
            api_key=os.environ.get("QBITTORRENT_API_KEY") or None,
            username=os.environ.get("QBITTORRENT_USERNAME") or None,
            password=os.environ.get("QBITTORRENT_PASSWORD") or None,
        )
    else:
        raise ValueError(f"Unknown TORRENT_BACKEND={which!r}; valid: rtorrent, qbittorrent")
    return _backend_singleton


def reset_torrent_client() -> None:
    """Drop the singleton (tests + backend switches)."""
    global _backend_singleton
    _backend_singleton = None
