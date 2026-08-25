# pyright: reportUnusedFunction=false
"""
REST JSON endpoints for the web_sota SPA.

Registered on the FastMCP Starlette app via ``custom_route`` (same port as MCP HTTP).
This is not a second BitTorrent client - it uses the same ``RTorrentClient`` as MCP tools.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
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
    server._rtorrent_web_api_registered = True

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
        magnet = str(body.get("magnet") or body.get("magnet_link"))
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

    @server.custom_route("/api/capabilities", methods=["GET"])
    async def api_capabilities(request: Request) -> Response:
        """Capability surface: tools, resources, skills (dynamic discovery)."""
        if not _check_auth(request):
            return _auth_error()
        try:
            tools = await server.list_tools()
            tool_names = sorted(tool.name for tool in tools)
            resources = await server.list_resources()
            resource_uris = sorted(str(r.uri) for r in resources)
            return JSONResponse(
                {
                    "ok": True,
                    "server": "rtorrent-mcp",
                    "version": app_version,
                    "tools": tool_names,
                    "tool_count": len(tool_names),
                    "resources": resource_uris,
                    "skills": ["rtorrent-mcp"],
                    "sampling": bool(settings.sampling_base_url),
                }
            )
        except Exception:
            logger.exception("api capabilities")
            return JSONResponse({"ok": False, "error": "Failed to enumerate capabilities"}, status_code=500)

    @server.custom_route("/api/skills", methods=["GET"])
    async def api_skills(request: Request) -> Response:
        """List bundled skills (used by the webapp Skills page + chat preprompt)."""
        if not _check_auth(request):
            return _auth_error()
        skills_root = Path(__file__).resolve().parent.parent / "skills"
        skills = []
        if skills_root.is_dir():
            for skill_dir in sorted(skills_root.iterdir()):
                if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
                    skills.append({"name": skill_dir.name, "path": f"/api/skills/{skill_dir.name}"})
        return JSONResponse({"success": True, "skills": skills})

    @server.custom_route("/api/skills/{skill_name}", methods=["GET"])
    async def api_skill_content(request: Request) -> Response:
        """Return the raw SKILL.md content for a skill."""
        if not _check_auth(request):
            return _auth_error()
        skill_name = request.path_params.get("skill_name", "")
        skill_file = Path(__file__).resolve().parent.parent / "skills" / skill_name / "SKILL.md"
        if not skill_file.exists():
            return JSONResponse({"success": False, "error": f"Skill '{skill_name}' not found"}, status_code=404)
        return Response(content=skill_file.read_text(encoding="utf-8"), media_type="text/markdown")

    @server.custom_route("/api/llm/discover", methods=["GET"])
    async def api_llm_discover(request: Request) -> Response:
        """Probe local LLM providers (Ollama / LM Studio / vLLM)."""
        if not _check_auth(request):
            return _auth_error()
        import asyncio

        import httpx

        async def probe(name: str, port: int, path: str, key: str) -> dict:
            base = f"http://127.0.0.1:{port}"
            try:
                async with httpx.AsyncClient(timeout=2.0) as client:
                    r = await client.get(f"{base}{path}")
                    if r.status_code != 200:
                        return {"name": name, "port": port, "detected": False, "models": []}
                    data = r.json()
                    if key == "name":
                        models = [m.get("name") for m in data.get("models", []) if m.get("name")]
                    else:
                        models = [m.get("id") for m in data.get("data", []) if m.get("id")]
                    return {"name": name, "port": port, "detected": True, "models": models}
            except Exception:
                return {"name": name, "port": port, "detected": False, "models": []}

        results = await asyncio.gather(
            probe("ollama", 11434, "/api/tags", "name"),
            probe("lm_studio", 1234, "/v1/models", "id"),
            probe("vllm", 8000, "/v1/models", "id"),
        )
        providers = [r for r in results]
        default = next((r["name"] for r in providers if r["detected"]), None)
        return JSONResponse({"success": True, "providers": providers, "default": default})

    @server.custom_route("/api/ai/chat", methods=["POST"])
    async def api_ai_chat(request: Request) -> Response:
        """Chat completion via the configured OpenAI-compatible sampling endpoint."""
        if not _check_auth(request):
            return _auth_error()
        try:
            body: dict[str, Any] = await request.json()
        except Exception:
            return JSONResponse({"success": False, "error": "Invalid JSON body"}, status_code=400)
        message = str(body.get("message") or "").strip()
        if not message:
            return JSONResponse({"success": False, "error": "Missing message"}, status_code=400)

        system_prompt = str(body.get("system_prompt") or "")
        context = body.get("context") or {}
        history = context.get("history") or []
        messages: list[dict[str, Any]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        for entry in history[-20:]:
            role = entry.get("role")
            content = entry.get("content")
            if role in ("user", "assistant") and content:
                messages.append({"role": role, "content": str(content)})
        messages.append({"role": "user", "content": message})

        base_url = settings.sampling_base_url
        if not base_url:
            return JSONResponse(
                {"success": False, "error": "No LLM provider configured (RTORRENT_SAMPLING_BASE_URL)"},
                status_code=503,
            )
        url = f"{base_url}/chat/completions"
        headers = {"Content-Type": "application/json"}
        api_key = settings.sampling_api_key
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        payload = {"model": settings.sampling_model, "messages": messages, "temperature": 0.7}

        import httpx

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                r = await client.post(url, json=payload, headers=headers)
                if r.status_code != 200:
                    return JSONResponse(
                        {"success": False, "error": f"LLM provider returned HTTP {r.status_code}"},
                        status_code=502,
                    )
                data = r.json()
            reply = (data.get("choices") or [{}])[0].get("message", {}).get("content") or ""
            return JSONResponse({"success": True, "reply": reply})
        except Exception as e:
            logger.exception("chat completion")
            return JSONResponse(
                {"success": False, "error": f"LLM provider unreachable: {e!s}"},
                status_code=502,
            )

    @server.custom_route("/api/fleet/apps", methods=["GET"])
    async def api_fleet_apps(request: Request) -> Response:
        """Probe the fleet webapp reservoir for live peers (Apps Hub discovery)."""
        if not _check_auth(request):
            return _auth_error()
        import asyncio

        OWN = {10910, 10911}

        async def check_port(port: int) -> int | None:
            try:
                reader, _ = await asyncio.open_connection("127.0.0.1", port, timeout=0.4)
                reader.read(1) if reader else None
                return port
            except Exception:
                return None

        ports = [p for p in range(10700, 11161) if p not in OWN]
        live = [p for p in await asyncio.gather(*(check_port(p) for p in ports)) if p is not None]
        apps = [{"port": port, "url": f"http://127.0.0.1:{port}", "ok": True} for port in sorted(live)]
        return JSONResponse({"success": True, "apps": apps, "count": len(apps)})

    @server.custom_route("/api/v1/diagnostics", methods=["GET"])
    async def api_v1_diagnostics(request: Request) -> Response:
        """CUA-NSIS diagnostics: tools, system info, errors."""
        if not _check_auth(request):
            return _auth_error()
        try:
            import platform

            import psutil

            tools = await server.list_tools()
            return JSONResponse(
                {
                    "status": "ok",
                    "server": "rtorrent-mcp",
                    "version": app_version,
                    "tool_count": len(tools),
                    "tools": [{"name": t.name} for t in tools],
                    "system": {
                        "platform": platform.system(),
                        "python": platform.python_version(),
                        "cpu_percent": psutil.cpu_percent(interval=0.1),
                        "memory_percent": psutil.virtual_memory().percent,
                    },
                    "errors": [],
                }
            )
        except Exception:
            logger.exception("diagnostics")
            return JSONResponse({"status": "error", "errors": ["diagnostics failed"]}, status_code=500)

    @server.custom_route("/api/v1/system/info", methods=["GET"])
    async def api_v1_system_info(request: Request) -> Response:
        """Alias for CUA feature smoke (cua-nsis-config feature_smoke_path)."""
        return await api_v1_diagnostics(request)

    @server.custom_route("/api/search/nyaa", methods=["GET"])
    async def api_search_nyaa(request: Request) -> Response:
        """Search Nyaa.si anime releases."""
        if not _check_auth(request):
            return _auth_error()
        query = request.query_params.get("query", "").strip()
        if not query:
            return JSONResponse({"success": False, "error": "Query parameter is required"}, status_code=400)
        resolution = request.query_params.get("resolution", "1080p")
        group = request.query_params.get("group", "ASW")

        try:
            from rtorrent_mcp.services.nyaa_search import search_nyaa_anime

            results = await search_nyaa_anime(query, resolution=resolution, group=group)
            return JSONResponse({"success": True, "query": query, "count": len(results), "results": results})
        except Exception as e:
            logger.exception("nyaa search endpoint failed")
            return JSONResponse({"success": False, "error": str(e)}, status_code=500)

    @server.custom_route("/api/search/piratebay", methods=["GET"])
    async def api_search_piratebay(request: Request) -> Response:
        """Search The Pirate Bay TV & movie releases."""
        if not _check_auth(request):
            return _auth_error()
        query = request.query_params.get("query", "").strip()
        if not query:
            return JSONResponse({"success": False, "error": "Query parameter is required"}, status_code=400)
        resolution = request.query_params.get("resolution", "1080p")
        group = request.query_params.get("group", "MeGusta")

        try:
            from rtorrent_mcp.services.piratebay_search import search_piratebay_tv

            results = await search_piratebay_tv(query, resolution=resolution, group=group)
            return JSONResponse({"success": True, "query": query, "count": len(results), "results": results})
        except Exception as e:
            logger.exception("piratebay search endpoint failed")
            return JSONResponse({"success": False, "error": str(e)}, status_code=500)

    @server.custom_route("/api/normalize/filename", methods=["POST"])
    async def api_normalize_filename(request: Request) -> Response:
        """Normalize a filename or media path into Plex-compliant format."""
        if not _check_auth(request):
            return _auth_error()
        try:
            body: dict[str, Any] = await request.json()
        except Exception:
            return JSONResponse({"success": False, "error": "Invalid JSON body"}, status_code=400)
        filename = str(body.get("filename") or body.get("name") or "").strip()
        if not filename:
            return JSONResponse({"success": False, "error": "Missing filename parameter"}, status_code=400)
        category = str(body.get("category") or "anime")

        try:
            from rtorrent_mcp.services.filename_normalizer import FilenameNormalizer

            res = FilenameNormalizer.normalize(filename, category=category)
            return JSONResponse({"success": True, "normalized": res})
        except Exception as e:
            logger.exception("filename normalization failed")
            return JSONResponse({"success": False, "error": str(e)}, status_code=500)

    @server.custom_route("/api/plex/status", methods=["GET"])
    async def api_plex_status(request: Request) -> Response:
        """Check Plex server configuration and connection status."""
        if not _check_auth(request):
            return _auth_error()
        url = settings.PLEX_URL
        token = settings.PLEX_TOKEN
        configured = bool(url and token)
        return JSONResponse(
            {
                "success": True,
                "configured": configured,
                "plex_url": url or None,
                "link_mode": getattr(settings, "LINK_MODE", "hardlink"),
            }
        )

    @server.custom_route("/api/plex/scan", methods=["POST"])
    async def api_plex_scan(request: Request) -> Response:
        """Trigger Plex library refresh for sections or all libraries."""
        if not _check_auth(request):
            return _auth_error()
        try:
            body: dict[str, Any] = await request.json()
        except Exception:
            body = {}
        section_id = body.get("section_id")

        try:
            from rtorrent_mcp.services.media_integrator import MediaIntegrator

            cfg = {
                "plex_url": settings.PLEX_URL,
                "plex_token": settings.PLEX_TOKEN,
                "jellyfin_url": settings.JELLYFIN_URL,
                "jellyfin_api_key": settings.JELLYFIN_API_KEY,
            }
            mi = MediaIntegrator(cfg)
            res = await mi.scan_plex(section_id=str(section_id) if section_id else None)
            return JSONResponse({"success": True, "result": res})
        except Exception as e:
            logger.exception("plex scan endpoint failed")
            return JSONResponse({"success": False, "error": str(e)}, status_code=500)

    @server.custom_route("/api/plex/ingest", methods=["POST"])
    async def api_plex_ingest(request: Request) -> Response:
        """Trigger manual post-processing and Plex ingestion pass."""
        if not _check_auth(request):
            return _auth_error()
        try:
            from rtorrent_mcp.services.post_processor import PostProcessor

            cfg = {
                "ingestion_anime_path": getattr(settings, "INGESTION_ANIME_PATH", ""),
                "ingestion_tv_path": getattr(settings, "INGESTION_TV_PATH", ""),
                "ingestion_movies_path": getattr(settings, "INGESTION_MOVIES_PATH", ""),
                "normalize_filenames": True,
                "link_mode": getattr(settings, "LINK_MODE", "hardlink"),
                "plex_url": settings.PLEX_URL,
                "plex_token": settings.PLEX_TOKEN,
            }
            pp = PostProcessor(cfg)
            completed = await pp.check_completed_downloads()
            processed_results = []
            for torrent in completed:
                r = await pp.process_completed_torrent(torrent)
                processed_results.append(r)
            return JSONResponse(
                {
                    "success": True,
                    "completed_found": len(completed),
                    "processed": processed_results,
                }
            )
        except Exception as e:
            logger.exception("plex ingest endpoint failed")
            return JSONResponse({"success": False, "error": str(e)}, status_code=500)

