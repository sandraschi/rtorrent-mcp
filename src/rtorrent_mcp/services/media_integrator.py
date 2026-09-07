"""
media_integrator.py - Notify Plex/Jellyfin after rTorrent downloads complete.

For direct downloads (e.g. anime from nyaa via rtorrent-mcp), there is no *arr
in the loop. After the PostProcessor moves files to ingestion folders, this
module tells Plex/Jellyfin to scan so content appears without waiting for a
filesystem-scheduled scan.

For *arr-managed content: configure rTorrent as a download client in Radarr/Sonarr
directly (Settings > Download Clients > rTorrent). The *arr handles magnet dispatch,
completion detection, import, and media-server notification itself.

Architecture:
    Direct (anime):  rTorrent → PostProcessor → MediaIntegrator → scan Plex/Jellyfin
    *arr (movies/TV): *arr → rTorrent → *arr (detects completion) → *arr import → *arr notifies Plex/Jellyfin

Each service is opt-in: only enabled when the corresponding URL is set.
"""

from __future__ import annotations

import logging
from typing import Any

import aiohttp

logger = logging.getLogger(__name__)


class MediaIntegrator:
    """Notify Plex/Jellyfin about completed downloads from direct rTorrent operations."""

    def __init__(self, config: dict[str, Any]) -> None:
        self.cfg = config

    async def scan_plex(self, section_id: str | None = None) -> dict[str, Any]:
        """Trigger a Plex library scan.

        If *section_id* is omitted, auto-discovers all sections and refreshes each.
        """
        url = self.cfg.get("plex_url", "").rstrip("/")
        token = self.cfg.get("plex_token", "")
        if not url or not token:
            return {"service": "plex", "status": "skipped", "reason": "not configured"}
        headers = {"X-Plex-Token": token, "Accept": "application/json"}
        try:
            if not section_id:
                async with (
                    aiohttp.ClientSession(headers=headers) as session,
                    session.get(f"{url}/library/sections") as resp,
                ):
                    if resp.status != 200:
                        return {"service": "plex", "status": "error", "error": f"list sections returned {resp.status}"}
                    sections = (await resp.json()).get("MediaContainer", {}).get("Directory", [])
                    results = []
                    for sec in sections:
                        sid = sec.get("key")
                        if sid:
                            results.append(await self._refresh_plex_section(url, token, sid))
                    return {"service": "plex", "status": "ok", "sections_refreshed": results}
            return await self._refresh_plex_section(url, token, section_id)
        except Exception as e:
            logger.exception("plex scan failed")
            return {"service": "plex", "status": "error", "error": str(e)}

    async def _refresh_plex_section(self, url: str, token: str, section_id: str | None) -> dict[str, Any]:
        headers = {"X-Plex-Token": token}
        async with (
            aiohttp.ClientSession(headers=headers) as session,
            session.post(f"{url}/library/sections/{section_id}/refresh") as resp,
        ):
            return {"section_id": section_id, "status": "ok" if resp.status < 400 else "error", "http": resp.status}

    async def scan_jellyfin(self, path: str = "") -> dict[str, Any]:
        """Trigger a Jellyfin library scan.

        If *path* is provided, notifies incremental update at that path
        (POST /Library/Media/Updated). Otherwise triggers a full refresh
        (POST /Library/Refresh).
        """
        url = self.cfg.get("jellyfin_url", "").rstrip("/")
        key = self.cfg.get("jellyfin_api_key", "")
        if not url or not key:
            return {"service": "jellyfin", "status": "skipped", "reason": "not configured"}
        headers = {"X-MediaBrowser-Token": key, "Content-Type": "application/json"}
        try:
            payload = {"Updates": [{"Path": str(path), "UpdateType": "Created"}]} if path else {}
            api_url = f"{url}/Library/Media/Updated" if path else f"{url}/Library/Refresh"
            async with aiohttp.ClientSession(headers=headers) as session, session.post(api_url, json=payload) as resp:
                return {"service": "jellyfin", "status": "ok" if resp.status < 400 else "error", "http": resp.status}
        except Exception as e:
            logger.exception("jellyfin scan failed")
            return {"service": "jellyfin", "status": "error", "error": str(e)}

    async def notify_all(self, category: str, file_paths: list[str]) -> list[dict[str, Any]]:
        """Notify all configured media services after a completed download.

        Fires Plex and Jellyfin scans. Does NOT notify *arr apps -
        *arr should be configured with rTorrent as a download client directly.
        """
        results: list[dict[str, Any]] = []
        parent = ""
        if file_paths:
            import os as _os

            try:
                parent = (
                    _os.path.dirname(_os.path.commonpath(file_paths))
                    if len(file_paths) > 1
                    else _os.path.dirname(file_paths[0])
                )
            except ValueError:
                parent = _os.path.dirname(file_paths[0])
        results.append(await self.scan_plex())
        results.append(await self.scan_jellyfin(parent))
        return results
