"""
REST JSON endpoints for the web_sota SPA.

Registered on the FastMCP Starlette app via ``custom_route`` (same port as MCP HTTP).
This is not a second BitTorrent client — it uses the same ``RTorrentClient`` as MCP tools.
"""

from __future__ import annotations

import logging
import re
from typing import Any

from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from rtorrent_mcp.config.settings import settings
from rtorrent_mcp.services.rtorrent_client import get_rtorrent_client

logger = logging.getLogger(__name__)

_MAGNET_RE = re.compile(r"^magnet:\?xt=urn:btih:[a-fA-F0-9]{32,}")


def _auth_error(msg: str = "Missing or invalid API key") -> Response:
    return JSONResponse({"success": False, "error": msg, "error_code": "AUTH_REQUIRED"}, status_code=401)


def _check_auth(request: Request) -> bool:
    expected = settings.API_KEY
    if not expected:
        return True
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header[7:] == expected
    return request.headers.get("X-API-Key", "") == expected


def register_web_api(server: Any, *, app_version: str) -> None:
    """Attach /api/* routes to the FastMCP server (idempotent)."""
    if getattr(server, "_rtorrent_web_api_registered", False):
        return
    server._rtorrent_web_api_registered = True  # noqa: SLF001

    @server.custom_route("/api/health", methods=["GET"])
    async def api_health(_request: Request) -> Response:
        return JSONResponse(
            {
                "ok": True,
                "service": "rtorrent-mcp",
                "version": app_version,
                "fastmcp": "3.1",
            }
        )

    @server.custom_route("/api/info", methods=["GET"])
    async def api_info(request: Request) -> Response:
        if not _check_auth(request):
            return _auth_error()
        return JSONResponse(
            {
                "app_name": settings.APP_NAME,
                "app_version": settings.APP_VERSION,
            }
        )

    @server.custom_route("/api/rtorrent/status", methods=["GET"])
    async def rtorrent_status(request: Request) -> Response:
        if not _check_auth(request):
            return _auth_error()
        try:
            c = await get_rtorrent_client()
            ok = await c.connect()
            return JSONResponse(
                {
                    "connected": ok,
                    "host": settings.RTORRENT_HOST,
                    "port": settings.RTORRENT_PORT,
                    "rpc_path": "/RPC2",
                }
            )
        except Exception:
            logger.exception("rtorrent status check")
            return JSONResponse(
                {
                    "connected": False,
                    "host": settings.RTORRENT_HOST,
                    "port": settings.RTORRENT_PORT,
                    "error": "Failed to connect to rTorrent",
                    "error_code": "RTORRENT_UNREACHABLE",
                },
                status_code=503,
            )

    @server.custom_route("/api/rtorrent/torrents", methods=["GET"])
    async def rtorrent_torrents(request: Request) -> Response:
        if not _check_auth(request):
            return _auth_error()
        try:
            c = await get_rtorrent_client()
            if not await c.connect():
                return JSONResponse(
                    {
                        "success": False,
                        "error": "Could not connect to rTorrent XML-RPC",
                        "error_code": "RTORRENT_UNREACHABLE",
                        "torrents": [],
                    },
                    status_code=503,
                )
            torrents = await c.get_torrents()
            return JSONResponse({"success": True, "count": len(torrents), "torrents": torrents})
        except Exception:
            logger.exception("rtorrent torrents list")
            return JSONResponse(
                {"success": False, "error": "Failed to list torrents", "error_code": "RTORRENT_ERROR", "torrents": []},
                status_code=503,
            )

    @server.custom_route("/api/rtorrent/magnet", methods=["POST"])
    async def rtorrent_magnet(request: Request) -> Response:
        if not _check_auth(request):
            return _auth_error()
        try:
            body: dict[str, Any] = await request.json()
        except Exception:
            return JSONResponse(
                {"success": False, "error": "Invalid JSON body", "error_code": "INVALID_JSON"},
                status_code=400,
            )
        magnet = body.get("magnet") or body.get("magnet_link")
        if not magnet or not isinstance(magnet, str):
            return JSONResponse(
                {"success": False, "error": "Missing magnet or magnet_link string", "error_code": "MISSING_MAGNET"},
                status_code=400,
            )
        if not _MAGNET_RE.match(magnet.strip()):
            return JSONResponse(
                {"success": False, "error": "Invalid magnet link format", "error_code": "INVALID_MAGNET"},
                status_code=400,
            )
        category = str(body.get("category") or "anime")
        try:
            c = await get_rtorrent_client()
            result = await c.add_torrent(magnet, category=category)
            ok = result.get("status") == "success"
            return JSONResponse(result, status_code=200 if ok else 502)
        except Exception:
            logger.exception("add magnet")
            return JSONResponse(
                {"success": False, "error": "Failed to add torrent", "error_code": "RTORRENT_ERROR"},
                status_code=503,
            )
