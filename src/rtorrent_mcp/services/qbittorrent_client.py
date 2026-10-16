"""qBittorrent WebUI API client (dual-backend P0).

Speaks Web API v2 (verified live against v5.1.4 / WebAPI 2.11.4).
Auth: API key when configured (needs qBittorrent >= v5.2.0), else
username/password cookie session with lazy login + re-auth on 403.

No-seed posture: `enforce_no_seed()` caps global seeding time; per-torrent
share limits are set on every add. In-download piece uploads are protocol,
not policy (see docs).
"""

import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class QBittorrentClient:
    """Async qBittorrent WebUI client implementing the TorrentBackend seam."""

    backend_name = "qbittorrent"

    def __init__(
        self,
        base_url: str = "http://localhost:18080",
        api_key: str | None = None,
        username: str | None = None,
        password: str | None = None,
        timeout: float = 20.0,
    ) -> None:
        self.base_url = (base_url or "").rstrip("/")
        self.api_key = api_key
        self.username = username
        self.password = password
        self.timeout = timeout
        self.connected = False
        self._client: httpx.AsyncClient | None = None

    async def _session(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(base_url=self.base_url, cookies=httpx.Cookies(), timeout=self.timeout)
        return self._client

    async def connect(self) -> bool:
        """Login (API key header or user/pass cookie). True when usable."""
        try:
            client = await self._session()
            if self.api_key:
                # Stateless key auth (qBittorrent >= v5.2.0); validated lazily.
                client.headers["Authorization"] = f"Bearer {self.api_key}"
                r = await client.get("/api/v2/app/version")
                self.connected = r.status_code == 200
            elif self.username:
                r = await client.post(
                    "/api/v2/auth/login",
                    data={"username": self.username, "password": self.password or ""},
                )
                self.connected = r.status_code == 200 and r.text.strip().lower().startswith("ok")
                if not self.connected:
                    logger.error("qBittorrent login failed (HTTP %s)", r.status_code)
            else:
                logger.error("qBittorrent needs QBITTORRENT_API_KEY or USERNAME/PASSWORD")
                self.connected = False
            if self.connected:
                logger.info("Connected to qBittorrent at %s", self.base_url)
            return self.connected
        except Exception as e:
            logger.error("qBittorrent connection error: %s", e)
            self.connected = False
            return False

    async def _req(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        """Authed request with one re-login retry on 403 (expired cookie)."""
        client = await self._session()
        if not self.connected and not self.api_key:
            await self.connect()
        r = await client.request(method, path, **kwargs)
        if r.status_code == 403 and not self.api_key:
            logger.info("qBittorrent session expired, re-logging in")
            if await self.connect():
                r = await client.request(method, path, **kwargs)
        r.raise_for_status()
        return r

    @staticmethod
    def _norm(t: dict[str, Any]) -> dict[str, Any]:
        size = int(t.get("size") or 0)
        progress = float(t.get("progress") or 0.0)
        completed = int(progress * size)
        return {
            "hash": str(t.get("hash") or ""),
            "name": str(t.get("name") or ""),
            "state": str(t.get("state") or ""),
            "size_bytes": size,
            "completed_bytes": completed,
            "progress": progress * 100.0,
            "save_path": str(t.get("save_path") or t.get("content_path") or ""),
            "category": str(t.get("category") or ""),
        }

    async def get_torrents(self) -> list[dict[str, Any]]:
        try:
            r = await self._req("GET", "/api/v2/torrents/info")
            return [self._norm(t) for t in r.json()]
        except Exception as e:
            logger.error("Error getting torrents: %s", e)
            return []

    async def add_torrent(self, magnet_link: str, category: str = "anime") -> dict[str, Any]:
        """Add via magnet/URL, then cap its seeding time (no-seed posture)."""
        try:
            before = {t["hash"] for t in await self.get_torrents()}
            r = await self._req(
                "POST",
                "/api/v2/torrents/add",
                data={"urls": magnet_link, "category": category},
            )
            if r.status_code != 200 or not r.text.strip().lower().startswith("ok"):
                return {"status": "error", "message": f"Add rejected: {r.text[:200]}"}
            new_hash: str | None = None
            for _ in range(5):
                after = {t["hash"] for t in await self.get_torrents()}
                fresh = after - before
                if fresh:
                    new_hash = sorted(fresh)[0]
                    break
                import asyncio

                await asyncio.sleep(1)
            if not new_hash:
                return {"status": "error", "message": "Torrent added but hash not found"}
            await self._req(
                "POST",
                "/api/v2/torrents/setShareLimits",
                data={"hashes": new_hash, "seedingTimeLimit": 1},
            )
            return {
                "status": "success",
                "hash": new_hash,
                "message": "Torrent added successfully",
                "category": category,
                "magnet": magnet_link[:50] + "...",
            }
        except Exception as e:
            logger.error("Error adding torrent: %s", e)
            return {"status": "error", "message": f"Error adding torrent: {e!s}"}

    async def pause_torrent(self, torrent_hash: str) -> dict[str, Any]:
        try:
            await self._req("POST", "/api/v2/torrents/stop", data={"hashes": torrent_hash})
            return {"status": "success", "hash": torrent_hash, "action": "paused"}
        except Exception as e:
            return {"status": "error", "hash": torrent_hash, "message": str(e)}

    async def resume_torrent(self, torrent_hash: str) -> dict[str, Any]:
        try:
            await self._req("POST", "/api/v2/torrents/start", data={"hashes": torrent_hash})
            return {"status": "success", "hash": torrent_hash, "action": "resumed"}
        except Exception as e:
            return {"status": "error", "hash": torrent_hash, "message": str(e)}

    async def delete_torrent(self, torrent_hash: str, delete_files: bool = False) -> dict[str, Any]:
        try:
            await self._req(
                "POST",
                "/api/v2/torrents/delete",
                data={"hashes": torrent_hash, "deleteFiles": str(delete_files).lower()},
            )
            return {
                "status": "success",
                "hash": torrent_hash,
                "action": "deleted",
                "files_deleted": delete_files,
            }
        except Exception as e:
            return {"status": "error", "hash": torrent_hash, "message": str(e)}

    async def _properties(self, torrent_hash: str) -> dict[str, Any]:
        r = await self._req("GET", "/api/v2/torrents/properties", params={"hash": torrent_hash})
        data = r.json()
        return data if isinstance(data, dict) else {}

    async def get_torrent_base_path(self, torrent_hash: str) -> str:
        try:
            props = await self._properties(torrent_hash)
            return str(props.get("save_path") or "")
        except Exception as e:
            logger.error("Error getting base path for %s: %s", torrent_hash, e)
            return ""

    async def get_torrent_directory(self, torrent_hash: str) -> str:
        try:
            props = await self._properties(torrent_hash)
            return str(props.get("save_path") or "")
        except Exception as e:
            logger.error("Error getting directory for %s: %s", torrent_hash, e)
            return ""

    async def is_torrent_complete(self, torrent_hash: str) -> bool:
        try:
            props = await self._properties(torrent_hash)
            total = float(props.get("total_size") or 0)
            done = float(props.get("total_downloaded") or 0)
            if total <= 0:
                return False
            return (done / total) >= 0.999
        except Exception as e:
            logger.error("Error checking completion for %s: %s", torrent_hash, e)
            return False

    async def enforce_no_seed(self) -> dict[str, Any]:
        """Cap global seeding time to 1 minute (verified pref keys on v5.1.4).

        Ratio keys are deliberately untouched: max_ratio_act semantics are
        unverified on this version and a wrong value could disable limits.
        Re-run on every (re)connect.
        """
        try:
            await self._req(
                "POST",
                "/api/v2/app/setPreferences",
                data={"json": '{"max_seeding_time_enabled": true, "max_seeding_time": 1}'},
            )
            return {"status": "success", "applied": {"max_seeding_time": 1}}
        except Exception as e:
            logger.error("Error enforcing no-seed: %s", e)
            return {"status": "error", "message": str(e)}

    async def app_version(self) -> str:
        """WebUI app version (capability probe, e.g. 'v5.1.4')."""
        r = await self._req("GET", "/api/v2/app/version")
        return r.text.strip()
