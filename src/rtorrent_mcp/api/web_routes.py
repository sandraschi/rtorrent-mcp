"""
REST JSON endpoints for the web_sota SPA.

Registered on the FastMCP Starlette app via ``custom_route`` (same port as MCP HTTP).
This is not a second BitTorrent client — it uses the same ``RTorrentClient`` as MCP tools.
"""

from __future__ import annotations

import logging
from typing import Any

from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from rtorrent_mcp.config.settings import settings
from rtorrent_mcp.services.rtorrent_client import RTorrentClient

logger = logging.getLogger(__name__)


def _client() -> RTorrentClient:
    return RTorrentClient(host=settings.RTORRENT_HOST, port=settings.RTORRENT_PORT)


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
    async def api_info(_request: Request) -> Response:
        return JSONResponse(
            {
                "app_name": settings.APP_NAME,
                "rtorrent_host": settings.RTORRENT_HOST,
                "rtorrent_port": settings.RTORRENT_PORT,
                "nyaa_base_url": settings.NYAA_BASE_URL,
            }
        )

    @server.custom_route("/api/rtorrent/status", methods=["GET"])
    async def rtorrent_status(_request: Request) -> Response:
        c = _client()
        try:
            ok = await c.connect()
            return JSONResponse(
                {
                    "connected": ok,
                    "host": settings.RTORRENT_HOST,
                    "port": settings.RTORRENT_PORT,
                    "rpc_path": "/RPC2",
                }
            )
        except Exception as e:
            logger.exception("rtorrent status")
            return JSONResponse(
                {
                    "connected": False,
                    "host": settings.RTORRENT_HOST,
                    "port": settings.RTORRENT_PORT,
                    "error": str(e),
                },
                status_code=200,
            )

    @server.custom_route("/api/rtorrent/torrents", methods=["GET"])
    async def rtorrent_torrents(_request: Request) -> Response:
        c = _client()
        try:
            if not await c.connect():
                return JSONResponse(
                    {
                        "success": False,
                        "error": "Could not connect to rTorrent XML-RPC",
                        "torrents": [],
                    },
                    status_code=503,
                )
            torrents = await c.get_torrents()
            return JSONResponse({"success": True, "count": len(torrents), "torrents": torrents})
        except Exception as e:
            logger.exception("rtorrent torrents list")
            return JSONResponse(
                {"success": False, "error": str(e), "torrents": []},
                status_code=503,
            )

    @server.custom_route("/api/rtorrent/magnet", methods=["POST"])
    async def rtorrent_magnet(request: Request) -> Response:
        try:
            body: dict[str, Any] = await request.json()
        except Exception:
            return JSONResponse({"success": False, "error": "Invalid JSON body"}, status_code=400)
        magnet = body.get("magnet") or body.get("magnet_link")
        if not magnet or not isinstance(magnet, str):
            return JSONResponse(
                {"success": False, "error": "Missing magnet or magnet_link string"},
                status_code=400,
            )
        category = str(body.get("category") or "anime")
        c = _client()
        try:
            result = await c.add_torrent(magnet, category=category)
            ok = result.get("status") == "success"
            return JSONResponse(result, status_code=200 if ok else 502)
        except Exception as e:
            logger.exception("add magnet")
            return JSONResponse({"success": False, "error": str(e)}, status_code=503)
