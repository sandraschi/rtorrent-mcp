# pyright: reportUnusedFunction=false
"""
REST JSON endpoints for the web_sota SPA.

Registered on the FastMCP Starlette app via ``custom_route`` (same port as MCP HTTP).
This is not a second BitTorrent client - it uses the same ``RTorrentClient`` as MCP tools.
"""

from __future__ import annotations

import json
import logging
import os
import re
import shutil
import subprocess
import time
from collections import deque
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from rtorrent_mcp.config.settings import settings
from rtorrent_mcp.services.rtorrent_client import get_rtorrent_client

logger = logging.getLogger(__name__)

_MAGNET_RE = re.compile(r"^magnet:\?xt=urn:btih:[a-fA-F0-9]{32,}")


class ActivityLog:
    """In-memory activity ring buffer backing the webapp Logs page (/api/logs)."""

    def __init__(self, max_entries: int = 2000) -> None:
        self.max_entries = max_entries
        self._entries: deque[dict[str, Any]] = deque(maxlen=max_entries)

    def add(self, level: str, kind: str, detail: str, meta: dict[str, Any] | None = None) -> str:
        eid = f"{time.time():.6f}.{uuid4().hex[:6]}"
        self._entries.append(
            {
                "id": eid,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()),
                "level": level.upper(),
                "kind": kind,
                "detail": detail,
                "meta": meta or {},
            }
        )
        return eid

    def info(self, kind: str, detail: str, **meta: Any) -> str:
        return self.add("INFO", kind, detail, meta)

    def warn(self, kind: str, detail: str, **meta: Any) -> str:
        return self.add("WARNING", kind, detail, meta)

    def error(self, kind: str, detail: str, **meta: Any) -> str:
        return self.add("ERROR", kind, detail, meta)

    def query(
        self,
        limit: int = 50,
        offset: int = 0,
        level: str | None = None,
        kind: str | None = None,
        search: str | None = None,
        sort: str = "desc",
        after_id: str | None = None,
    ) -> dict[str, Any]:
        entries = list(self._entries)
        if after_id:
            try:
                at = float(after_id.split(".")[0])
                entries = [e for e in entries if float(e["id"].split(".")[0]) > at]
            except (ValueError, IndexError):
                pass
        if level:
            lo = {"DEBUG": 0, "INFO": 1, "WARNING": 2, "ERROR": 3}
            ml = lo.get(level.upper(), 1)
            entries = [e for e in entries if lo.get(e["level"], 1) >= ml]
        if kind:
            entries = [e for e in entries if e["kind"] == kind]
        if search:
            q = search.lower()
            entries = [e for e in entries if q in e["detail"].lower()]
        entries.sort(key=lambda e: e["id"], reverse=(sort == "desc"))
        total = len(entries)
        return {
            "entries": entries[offset : offset + limit],
            "total": total,
            "limit": limit,
            "offset": offset,
            "max_entries": self.max_entries,
            "sort": sort,
        }

    def stats(self) -> dict[str, Any]:
        levels: dict[str, int] = {}
        kinds: dict[str, int] = {}
        for e in self._entries:
            levels[e["level"]] = levels.get(e["level"], 0) + 1
            kinds[e["kind"]] = kinds.get(e["kind"], 0) + 1
        return {
            "total": len(self._entries),
            "max_entries": self.max_entries,
            "levels": levels,
            "kinds": kinds,
        }

    def clear(self) -> None:
        self._entries.clear()


_activity_log = ActivityLog()


def _auth_error(msg: str = "Missing or invalid API key") -> Response:
    return JSONResponse({"success": False, "error": msg, "error_code": "AUTH_REQUIRED"}, status_code=401)


def _qint(value: str | None, default: int) -> int:
    """Parse an int from a query-string value, falling back to ``default``."""
    if value is None:
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _sanitize_filename(name: str) -> str:
    """Strip path separators and control chars for a safe depot filename."""
    name = re.sub(r"[^\w.\-()\[\] ]", "_", name.strip())
    name = name.strip(" ._-")
    return name or "download.bin"


def _filename_from_content_disposition(cd: str) -> str | None:
    """Best-effort filename extraction from a Content-Disposition header."""
    m = re.search(r'filename\*?="?([^";]+)', cd)
    return m.group(1).strip().strip('"') if m else None


# --- Obscura (headless) integration for JS-gated / anti-bot downloads ---
# Cross-connect to the Obscura Rust engine (same one obscura-mcp wraps) so
# Anna's Archive slow-mirror unlock pages can be rendered past the JS countdown
# and the actual file downloaded (binary-safe via --dump original).


def _obscura_bin() -> str | None:
    for c in (
        os.environ.get("RTORRENT_OBSCURA_BIN"),
        r"D:\Dev\repos\external\obscura\target\release\obscura.exe",
        r"D:\Dev\repos\external\obscura\target\debug\obscura.exe",
        shutil.which("obscura"),
    ):
        if c and os.path.exists(c):
            return c
    return None


def _obscura_available() -> bool:
    if os.environ.get("RTORRENT_OBSCURA_FALLBACK", "").lower() in ("0", "false", "no", "off"):
        return False
    return _obscura_bin() is not None


def _obscura_render(url: str, timeout: int = 45) -> str:
    """Render a page past its JS unlock using the Obscura engine."""
    binary = _obscura_bin()
    if not binary:
        raise FileNotFoundError("Obscura binary not found")
    cmd = [
        binary,
        "fetch",
        url,
        "--dump",
        "html",
        "--wait-until",
        "networkidle0",
        "--stealth",
        "--timeout",
        str(timeout),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 15)
    return result.stdout or ""


_FILE_EXT_RE = re.compile(r"\.(epub|pdf|mobi|azw3|txt|fb2|djv|cbr|cbz|zip)$", re.I)


def _extract_file_url(html: str, base: str) -> str | None:
    """Return the first direct file link in rendered HTML, else None."""
    seen: set[str] = set()
    for match in re.finditer(r'href=["\']([^"\']+)["\']', html):
        href = match.group(1).strip()
        if not href or href.startswith(("javascript:", "#", "mailto:")):
            continue
        if href in seen:
            continue
        seen.add(href)
        if _FILE_EXT_RE.search(href) or "/slow_download/" in href or "/dl/" in href:
            return href if href.startswith("http") else f"{base}{href}"
    return None


def _looks_like_html(path: Path, sample: int = 512) -> bool:
    try:
        with open(path, "rb") as fh:
            head = fh.read(sample).lower()
    except OSError:
        return True
    stripped = head.lstrip()
    return stripped.startswith(b"<!doctype") or stripped.startswith(b"<html") or b"<?xml" in head[:256]


def _obscura_download(url: str, dest: Path, timeout: int = 180) -> bool:
    """Download ``url`` to ``dest`` binary-safely via Obscura. Returns True on success."""
    binary = _obscura_bin()
    if not binary:
        return False
    cmd = [binary, "fetch", url, "--dump", "original", "--stealth", "--timeout", str(timeout), "-o", str(dest)]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 20)
    if result.returncode != 0:
        return False
    if not dest.exists() or dest.stat().st_size == 0:
        return False
    return not _looks_like_html(dest)


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

    @server.custom_route("/api/logs", methods=["GET"])
    async def api_logs(request: Request) -> Response:
        """Query the activity log ring buffer (webapp Logs page)."""
        qp = request.query_params
        return JSONResponse(
            _activity_log.query(
                limit=_qint(qp.get("limit"), 50),
                offset=_qint(qp.get("offset"), 0),
                level=qp.get("level"),
                kind=qp.get("kind"),
                search=qp.get("search"),
                sort=qp.get("sort", "desc"),
                after_id=qp.get("after_id"),
            )
        )

    @server.custom_route("/api/logs/stats", methods=["GET"])
    async def api_logs_stats(_request: Request) -> Response:
        """Return per-level/per-kind log totals."""
        return JSONResponse(_activity_log.stats())

    @server.custom_route("/api/logs/export", methods=["GET"])
    async def api_logs_export(request: Request) -> Response:
        """Export logs as JSON or CSV attachment."""
        qp = request.query_params
        fmt = qp.get("format", "json")
        result = _activity_log.query(
            limit=_activity_log.max_entries,
            level=qp.get("level"),
            kind=qp.get("kind"),
            search=qp.get("search"),
        )
        if fmt == "csv":
            import csv
            import io

            buf = io.StringIO()
            w = csv.writer(buf)
            w.writerow(["id", "timestamp", "level", "kind", "detail", "meta"])
            for e in result["entries"]:
                w.writerow([e["id"], e["timestamp"], e["level"], e["kind"], e["detail"], json.dumps(e["meta"])])
            return Response(
                content=buf.getvalue(),
                media_type="text/csv",
                headers={"Content-Disposition": 'attachment; filename="logs.csv"'},
            )
        return Response(
            content=json.dumps(result["entries"], indent=2),
            media_type="application/json",
            headers={"Content-Disposition": 'attachment; filename="logs.json"'},
        )

    @server.custom_route("/api/logs", methods=["DELETE"])
    async def api_logs_clear(_request: Request) -> Response:
        """Clear the activity log ring buffer."""
        _activity_log.clear()
        return JSONResponse({"success": True, "message": "Logs cleared."})

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
            _activity_log.info("torrent", f"add [{category}] {'OK' if ok else 'FAILED'}: {magnet[:40]}...")
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
            _activity_log.info("search", f"nyaa '{query}' -> {len(results)} results")
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
            _activity_log.info("search", f"piratebay '{query}' -> {len(results)} results")
            return JSONResponse({"success": True, "query": query, "count": len(results), "results": results})
        except Exception as e:
            logger.exception("piratebay search endpoint failed")
            return JSONResponse({"success": False, "error": str(e)}, status_code=500)

    @server.custom_route("/api/search/gutenberg", methods=["GET"])
    async def api_search_gutenberg(request: Request) -> Response:
        """Search Project Gutenberg public domain e-books."""
        if not _check_auth(request):
            return _auth_error()
        query = request.query_params.get("query", "").strip()
        if not query:
            return JSONResponse({"success": False, "error": "Query parameter is required"}, status_code=400)
        topic = request.query_params.get("topic")

        try:
            from rtorrent_mcp.services.gutenberg_search import search_gutenberg

            results = await search_gutenberg(query, topic=topic)
            _activity_log.info("search", f"gutenberg '{query}' -> {len(results)} results")
            return JSONResponse({"success": True, "query": query, "count": len(results), "results": results})
        except Exception as e:
            logger.exception("gutenberg search endpoint failed")
            return JSONResponse({"success": False, "error": str(e)}, status_code=500)

    @server.custom_route("/api/search/annas", methods=["GET"])
    async def api_search_annas(request: Request) -> Response:
        """Search Anna's Archive for ebooks or papers."""
        if not _check_auth(request):
            return _auth_error()
        query = request.query_params.get("query", "").strip()
        if not query:
            return JSONResponse({"success": False, "error": "Query parameter is required"}, status_code=400)
        content_type = request.query_params.get("content_type", "books")
        max_results = _qint(request.query_params.get("max_results"), 20)

        try:
            from rtorrent_mcp.services.annas_archive_search import search_annas_archive

            results = await search_annas_archive(query, content_type=content_type, max_results=max_results)
            _activity_log.info("search", f"annas '{query}' -> {len(results)} results")
            return JSONResponse({"success": True, "query": query, "count": len(results), "results": results})
        except Exception as e:
            logger.exception("annas search endpoint failed")
            return JSONResponse({"success": False, "error": str(e)}, status_code=500)

    @server.custom_route("/api/search/annas/detail", methods=["GET"])
    async def api_search_annas_detail(request: Request) -> Response:
        """Fetch a single Anna's Archive book detail page (magnet links)."""
        if not _check_auth(request):
            return _auth_error()
        book_url = request.query_params.get("book_url", "").strip()
        if not book_url:
            return JSONResponse({"success": False, "error": "book_url parameter is required"}, status_code=400)

        try:
            from rtorrent_mcp.services.annas_archive_search import get_annas_archive_detail

            result = await get_annas_archive_detail(book_url)
            _activity_log.info("search", f"annas detail {book_url[:60]}")
            return JSONResponse({"success": True, "result": result})
        except Exception as e:
            logger.exception("annas detail endpoint failed")
            return JSONResponse({"success": False, "error": str(e)}, status_code=500)

    @server.custom_route("/api/annas/config", methods=["GET"])
    async def api_annas_config(_request: Request) -> Response:
        """Anna's Archive config + whether a session cookie is configured."""
        from rtorrent_mcp.services.annas_archive_search import (
            ANNAS_ARCHIVE_BASE,
            ANNAS_ARCHIVE_MIRRORS,
            get_annas_session_cookie_value,
        )

        return JSONResponse(
            {
                "success": True,
                "base": ANNAS_ARCHIVE_BASE,
                "mirrors": ANNAS_ARCHIVE_MIRRORS,
                "authenticated": get_annas_session_cookie_value() is not None,
            }
        )

    @server.custom_route("/api/annas/config", methods=["POST"])
    async def api_annas_config_set(request: Request) -> Response:
        """Set/clear the Anna's Archive session cookie (persisted, gitignored)."""
        if not _check_auth(request):
            return _auth_error()
        try:
            body: dict[str, Any] = await request.json()
        except Exception:
            return JSONResponse({"success": False, "error": "Invalid JSON body"}, status_code=400)
        from rtorrent_mcp.services.annas_archive_search import (
            get_annas_session_cookie_value,
            set_annas_session_cookie,
        )

        value = str(body.get("session_cookie") or "").strip()
        set_annas_session_cookie(value or None)
        return JSONResponse({"success": True, "authenticated": get_annas_session_cookie_value() is not None})

    @server.custom_route("/api/annas/download", methods=["POST"])
    async def api_annas_download(request: Request) -> Response:
        """Download a single Anna's Archive file directly to the depot (no rTorrent)."""
        if not _check_auth(request):
            return _auth_error()
        try:
            body: dict[str, Any] = await request.json()
        except Exception:
            return JSONResponse({"success": False, "error": "Invalid JSON body"}, status_code=400)
        url = str(body.get("url") or "").strip()
        if not url:
            return JSONResponse({"success": False, "error": "url is required"}, status_code=400)
        if not url.startswith("https://") or "annas-archive." not in url:
            return JSONResponse(
                {"success": False, "error": "Only annas-archive.org mirror URLs are allowed"}, status_code=400
            )

        name_hint = str(body.get("filename") or "").strip()
        repo_root = Path(__file__).resolve().parents[3]
        depot = Path(os.environ.get("RTORRENT_DEPOT_PATH") or str(repo_root / "downloads"))
        depot.mkdir(parents=True, exist_ok=True)
        max_bytes = int(os.environ.get("RTORRENT_DEPOT_MAX_BYTES", str(2 * 1024**3)))  # 2GB default

        import aiohttp

        from rtorrent_mcp.services.annas_archive_search import get_annas_cookie_header

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            )
        }
        if cookie := get_annas_cookie_header():
            headers["Cookie"] = cookie

        def _dedupe_target(depot: Path, fname: str) -> Path:
            target = depot / fname
            if target.exists():
                from uuid import uuid4

                target = depot / f"{target.stem}.{uuid4().hex[:6]}{target.suffix}"
            return target

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, allow_redirects=True) as resp:
                    if resp.status != 200:
                        return JSONResponse(
                            {"success": False, "error": f"Download returned HTTP {resp.status}"}, status_code=502
                        )
                    ctype = (resp.headers.get("Content-Type") or "").lower()
                    if "text/html" in ctype or "application/xhtml" in ctype:
                        # JS-gated slow mirror: hand off to the Obscura engine.
                        if not _obscura_available():
                            return JSONResponse(
                                {
                                    "success": False,
                                    "error": (
                                        "Mirror returned an HTML page (JS unlock / queue required). "
                                        "Obscura not available to solve it - set RTORRENT_OBSCURA_BIN "
                                        "or build the engine, or open the downloader link manually."
                                    ),
                                },
                                status_code=502,
                            )
                        render = ""
                        try:
                            render = _obscura_render(url)
                        except Exception as e:
                            logger.exception("obscura render failed")
                            return JSONResponse(
                                {"success": False, "error": f"Obscura render failed: {e!s}"}, status_code=502
                            )
                        direct = _extract_file_url(render, url)
                        if not direct:
                            return JSONResponse(
                                {
                                    "success": False,
                                    "error": (
                                        "Obscura rendered the unlock page but found no direct file link. "
                                        "The mirror may need a per-file click; open the downloader link manually."
                                    ),
                                },
                                status_code=502,
                            )
                        fname = _sanitize_filename(
                            _filename_from_content_disposition(resp.headers.get("Content-Disposition", ""))
                            or name_hint
                            or direct.rstrip("/").split("/")[-1]
                            or "download.bin"
                        )
                        target = _dedupe_target(depot, fname)
                        if not _obscura_download(direct, target):
                            target.unlink(missing_ok=True)
                            return JSONResponse(
                                {"success": False, "error": "Obscura resolved a link but the file download failed."},
                                status_code=502,
                            )
                        size = target.stat().st_size
                        if size > max_bytes:
                            target.unlink(missing_ok=True)
                            return JSONResponse(
                                {"success": False, "error": f"Refusing file larger than {max_bytes // (1024**3)}GB."},
                                status_code=413,
                            )
                        _activity_log.info("depot", f"downloaded {target.name} via obscura ({size} bytes)")
                        return JSONResponse(
                            {"success": True, "filename": target.name, "path": str(target), "size_bytes": size}
                        )

                    fname = (
                        _filename_from_content_disposition(resp.headers.get("Content-Disposition", ""))
                        or name_hint
                        or url.rstrip("/").split("/")[-1]
                        or "download.bin"
                    )
                    fname = _sanitize_filename(fname)
                    target = _dedupe_target(depot, fname)

                    size = 0
                    with open(target, "wb") as fh:
                        async for chunk in resp.content.iter_chunked(256 * 1024):
                            size += len(chunk)
                            if size > max_bytes:
                                fh.close()
                                target.unlink(missing_ok=True)
                                return JSONResponse(
                                    {
                                        "success": False,
                                        "error": (
                                            f"Refusing file larger than {max_bytes // (1024**3)}GB "
                                            "(bulk dataset guard). Pick a single-book mirror."
                                        ),
                                    },
                                    status_code=413,
                                )
                            fh.write(chunk)

            _activity_log.info("depot", f"downloaded {fname} ({size} bytes)")
            return JSONResponse({"success": True, "filename": fname, "path": str(target), "size_bytes": size})
        except Exception as e:
            logger.exception("annas download failed")
            return JSONResponse({"success": False, "error": str(e)}, status_code=502)

    @server.custom_route("/api/depot", methods=["GET"])
    async def api_depot(request: Request) -> Response:
        """List the download depot directory (output of completed media)."""
        if not _check_auth(request):
            return _auth_error()
        repo_root = Path(__file__).resolve().parents[3]
        base = os.environ.get("RTORRENT_DEPOT_PATH") or str(repo_root / "downloads")
        depot = Path(base)
        if not depot.is_dir():
            return JSONResponse(
                {"success": False, "error": f"Depot path not found: {base}", "depot_path": base},
                status_code=404,
            )
        entries: list[dict[str, Any]] = []
        for it in sorted(depot.iterdir(), key=lambda x: x.name.lower()):
            try:
                st = it.stat()
                entries.append(
                    {
                        "name": it.name,
                        "path": str(it),
                        "type": "dir" if it.is_dir() else "file",
                        "size_bytes": st.st_size if it.is_file() else None,
                        "modified": datetime.fromtimestamp(st.st_mtime).isoformat(),
                    }
                )
            except (OSError, PermissionError):
                continue
        return JSONResponse({"success": True, "depot_path": base, "count": len(entries), "entries": entries})

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

    _activity_log.info("server", "HTTP REST API registered")
