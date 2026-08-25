"""
REST bridge tests (web_routes.py) via the FastMCP Starlette app.

Covers the /api/* surface the webapp and CUA smoke test depend on:
health, capabilities, skills, llm/discover, ai/chat, rtorrent/*,
fleet/apps, v1/diagnostics, and API-key auth.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from starlette.testclient import TestClient


@pytest.fixture()
def client():
    """TestClient over the fully-wired server app."""
    from rtorrent_mcp.server import RTorrentMCPServer

    srv = RTorrentMCPServer()
    srv.setup()
    app = srv.http_app(path="/mcp", middleware=srv._cors_middleware)
    return TestClient(app)


class TestHealthAndInfo:
    def test_health(self, client):
        r = client.get("/api/health")
        assert r.status_code == 200
        body = r.json()
        assert body["ok"] is True
        assert body["service"] == "rtorrent-mcp"
        assert body["version"]

    def test_info(self, client):
        r = client.get("/api/info")
        assert r.status_code == 200
        body = r.json()
        assert body["app_name"]
        assert body["app_version"] == "3.0.0"


class TestCapabilities:
    def test_capabilities_lists_tools_and_resources(self, client):
        r = client.get("/api/capabilities")
        assert r.status_code == 200
        body = r.json()
        assert body["ok"] is True
        assert "torrent_management" in body["tools"]
        assert "search_management" in body["tools"]
        assert body["tool_count"] >= 6
        assert "skill://rtorrent-mcp/SKILL.md" in body["resources"]
        assert "rtorrent-mcp" in body["skills"]


class TestSkills:
    def test_skills_list(self, client):
        r = client.get("/api/skills")
        assert r.status_code == 200
        body = r.json()
        assert body["success"] is True
        assert any(s["name"] == "rtorrent-mcp" for s in body["skills"])

    def test_skill_content(self, client):
        r = client.get("/api/skills/rtorrent-mcp")
        assert r.status_code == 200
        assert "# rTorrent MCP" in r.text

    def test_skill_not_found(self, client):
        r = client.get("/api/skills/nonexistent")
        assert r.status_code == 404


class TestLLMDiscover:
    def test_discovers_providers(self, client, monkeypatch):
        import httpx

        class FakeResponse:
            status_code = 200

            def json(self):
                return {"models": [{"name": "llama3.2"}, {"name": "qwen3"}]}

        class FakeClient:
            def __init__(self, *a, **k):
                pass

            async def __aenter__(self):
                return self

            async def __aexit__(self, *a):
                return False

            async def get(self, *a, **k):
                return FakeResponse()

        monkeypatch.setattr(httpx, "AsyncClient", FakeClient)
        r = client.get("/api/llm/discover")
        assert r.status_code == 200
        body = r.json()
        assert body["success"] is True
        assert body["default"] == "ollama"
        detected = [p for p in body["providers"] if p["detected"]]
        assert len(detected) == 3

    def test_no_provider_when_down(self, client, monkeypatch):
        import httpx

        class FakeClient:
            def __init__(self, *a, **k):
                pass

            async def __aenter__(self):
                return self

            async def __aexit__(self, *a):
                return False

            async def get(self, *a, **k):
                raise httpx.ConnectError("down")

        monkeypatch.setattr(httpx, "AsyncClient", FakeClient)
        r = client.get("/api/llm/discover")
        body = r.json()
        assert body["default"] is None
        assert all(p["detected"] is False for p in body["providers"])


class TestAIChat:
    def test_chat_success(self, client, monkeypatch):
        import httpx

        class FakeResponse:
            status_code = 200

            def json(self):
                return {"choices": [{"message": {"content": "Here is the answer."}}]}

        class FakeClient:
            def __init__(self, *a, **k):
                pass

            async def __aenter__(self):
                return self

            async def __aexit__(self, *a):
                return False

            async def post(self, *a, **k):
                return FakeResponse()

        monkeypatch.setattr(httpx, "AsyncClient", FakeClient)
        r = client.post(
            "/api/ai/chat", json={"message": "hello", "system_prompt": "be brief", "context": {"history": []}}
        )
        assert r.status_code == 200
        assert r.json()["reply"] == "Here is the answer."

    def test_chat_missing_message(self, client):
        r = client.post("/api/ai/chat", json={})
        assert r.status_code == 400

    def test_chat_provider_down(self, client, monkeypatch):
        import httpx

        class FakeClient:
            def __init__(self, *a, **k):
                pass

            async def __aenter__(self):
                return self

            async def __aexit__(self, *a):
                return False

            async def post(self, *a, **k):
                raise httpx.ConnectError("refused")

        monkeypatch.setattr(httpx, "AsyncClient", FakeClient)
        r = client.post("/api/ai/chat", json={"message": "hi"})
        assert r.status_code == 502


class TestRTorrentRoutes:
    @pytest.mark.asyncio
    @patch("rtorrent_mcp.api.web_routes.get_rtorrent_client")
    async def test_status_connected(self, mock_get, client):
        mock_client = MagicMock()
        mock_client.connect = AsyncMock(return_value=True)
        mock_get.return_value = mock_client
        r = client.get("/api/rtorrent/status")
        assert r.status_code == 200
        assert r.json()["connected"] is True

    @pytest.mark.asyncio
    @patch("rtorrent_mcp.api.web_routes.get_rtorrent_client")
    async def test_status_unreachable(self, mock_get, client):
        mock_client = MagicMock()
        mock_client.connect = AsyncMock(side_effect=Exception("down"))
        mock_get.return_value = mock_client
        r = client.get("/api/rtorrent/status")
        assert r.status_code == 503
        assert r.json()["connected"] is False

    @pytest.mark.asyncio
    @patch("rtorrent_mcp.api.web_routes.get_rtorrent_client")
    async def test_torrents_list(self, mock_get, client):
        mock_client = MagicMock()
        mock_client.connect = AsyncMock(return_value=True)
        mock_client.get_torrents = AsyncMock(return_value=[{"hash": "h1", "name": "Test"}])
        mock_get.return_value = mock_client
        r = client.get("/api/rtorrent/torrents")
        assert r.status_code == 200
        body = r.json()
        assert body["success"] is True
        assert len(body["torrents"]) == 1

    @pytest.mark.asyncio
    @patch("rtorrent_mcp.api.web_routes.get_rtorrent_client")
    async def test_torrents_unreachable(self, mock_get, client):
        mock_client = MagicMock()
        mock_client.connect = AsyncMock(return_value=False)
        mock_get.return_value = mock_client
        r = client.get("/api/rtorrent/torrents")
        assert r.status_code == 503

    @pytest.mark.asyncio
    @patch("rtorrent_mcp.api.web_routes.get_rtorrent_client")
    async def test_magnet_success(self, mock_get, client):
        mock_client = MagicMock()
        mock_client.add_torrent = AsyncMock(return_value={"status": "success", "hash": "h1"})
        mock_get.return_value = mock_client
        r = client.post(
            "/api/rtorrent/magnet",
            json={"magnet": "magnet:?xt=urn:btih:0123456789abcdef0123456789abcdef01234567&dn=x", "category": "anime"},
        )
        assert r.status_code == 200
        assert r.json()["hash"] == "h1"

    def test_magnet_invalid(self, client):
        r = client.post("/api/rtorrent/magnet", json={"magnet": "not-a-magnet"})
        assert r.status_code == 400

    def test_magnet_missing_body(self, client):
        r = client.post("/api/rtorrent/magnet", json={})
        assert r.status_code == 400


class TestFleetApps:
    def test_no_live_apps(self, client, monkeypatch):
        async def fake_connect(host, port, timeout=None):
            raise OSError("refused")

        monkeypatch.setattr("asyncio.open_connection", fake_connect)
        r = client.get("/api/fleet/apps")
        assert r.status_code == 200
        body = r.json()
        assert body["success"] is True
        assert body["count"] == 0

    def test_live_apps_found(self, client, monkeypatch):
        class FakeReader:
            def read(self, n):
                return b""

        async def fake_connect(host, port, timeout=None):
            if port == 10700:
                return FakeReader(), None
            raise OSError("refused")

        monkeypatch.setattr("asyncio.open_connection", fake_connect)
        r = client.get("/api/fleet/apps")
        body = r.json()
        assert body["count"] >= 1
        assert any(a["port"] == 10700 for a in body["apps"])


class TestDiagnostics:
    def test_diagnostics(self, client):
        r = client.get("/api/v1/diagnostics")
        assert r.status_code == 200
        body = r.json()
        assert body["status"] == "ok"
        assert body["tool_count"] >= 6
        assert "torrent_management" in [t["name"] for t in body["tools"]]
        assert body["system"]["platform"]

    def test_system_info_alias(self, client):
        r = client.get("/api/v1/system/info")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"


class TestAuth:
    def test_api_key_required(self, client, monkeypatch):
        from rtorrent_mcp.config.settings import settings

        monkeypatch.setattr(settings, "API_KEY", "sekret")
        r = client.get("/api/info")
        assert r.status_code == 401

    def test_api_key_accepted(self, client, monkeypatch):
        from rtorrent_mcp.config.settings import settings

        monkeypatch.setattr(settings, "API_KEY", "sekret")
        r = client.get("/api/info", headers={"Authorization": "Bearer sekret"})
        assert r.status_code == 200


class TestSearchAndNormalizeRoutes:
    def test_normalize_filename_endpoint(self, client):
        r = client.post(
            "/api/normalize/filename",
            json={"filename": "[SubsPlease] Boku no Hero Academia - 139 (1080p).mkv", "category": "anime"},
        )
        assert r.status_code == 200
        body = r.json()
        assert body["success"] is True
        assert body["normalized"]["title"] == "Boku no Hero Academia"

    def test_normalize_filename_missing(self, client):
        r = client.post("/api/normalize/filename", json={})
        assert r.status_code == 400

    @pytest.mark.asyncio
    @patch("rtorrent_mcp.services.nyaa_search.search_nyaa_anime")
    async def test_search_nyaa_endpoint(self, mock_search, client):
        mock_search.return_value = [{"title": "Hero", "magnet": "magnet:?xt=urn:btih:123"}]
        r = client.get("/api/search/nyaa?query=Hero")
        assert r.status_code == 200
        body = r.json()
        assert body["success"] is True
        assert body["count"] == 1

    def test_search_nyaa_missing_query(self, client):
        r = client.get("/api/search/nyaa")
        assert r.status_code == 400

    @pytest.mark.asyncio
    @patch("rtorrent_mcp.services.piratebay_search.search_piratebay_tv")
    async def test_search_piratebay_endpoint(self, mock_search, client):
        mock_search.return_value = [{"title": "South Park", "magnet": "magnet:?xt=urn:btih:456"}]
        r = client.get("/api/search/piratebay?query=South+Park")
        assert r.status_code == 200
        body = r.json()
        assert body["success"] is True
        assert body["count"] == 1


class TestPlexRoutes:
    def test_plex_status(self, client):
        r = client.get("/api/plex/status")
        assert r.status_code == 200
        body = r.json()
        assert body["success"] is True
        assert "configured" in body

    @pytest.mark.asyncio
    @patch("rtorrent_mcp.services.media_integrator.MediaIntegrator.scan_plex")
    async def test_plex_scan(self, mock_scan, client):
        mock_scan.return_value = {"service": "plex", "status": "ok"}
        r = client.post("/api/plex/scan", json={"section_id": "1"})
        assert r.status_code == 200
        assert r.json()["success"] is True

    @pytest.mark.asyncio
    @patch("rtorrent_mcp.services.post_processor.PostProcessor.check_completed_downloads")
    async def test_plex_ingest(self, mock_check, client):
        mock_check.return_value = []
        r = client.post("/api/plex/ingest")
        assert r.status_code == 200
        assert r.json()["success"] is True
        assert r.json()["completed_found"] == 0

