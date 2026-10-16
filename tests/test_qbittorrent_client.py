"""Unit tests for QBittorrentClient (MockTransport) + backend factory."""

import httpx
import pytest

from rtorrent_mcp.services.qbittorrent_client import QBittorrentClient
from rtorrent_mcp.services.torrent_backend import get_torrent_backend

TORRENTS = [
    {
        "hash": "abc123",
        "name": "Some Show S01E01",
        "state": "downloading",
        "size": 400000000,
        "progress": 0.5,
        "save_path": "D:/dl",
        "category": "anime",
    },
    {
        "hash": "def456",
        "name": "Done Movie",
        "state": "uploading",
        "size": 1000000000,
        "progress": 1.0,
        "save_path": "D:/dl",
        "category": "",
    },
]


def make_client(handler):
    calls: list = []

    def wrapped(request: httpx.Request) -> httpx.Response:
        calls.append((request.method, request.url.path))
        return handler(request)

    client = QBittorrentClient(base_url="http://test:18080", username="admin", password="x")
    client._client = httpx.AsyncClient(
        base_url="http://test:18080", cookies=httpx.Cookies(), transport=httpx.MockTransport(wrapped)
    )
    return client, calls


def ok_json(payload, status=200):
    return httpx.Response(status, json=payload)


@pytest.mark.asyncio
async def test_login_and_version():
    def handler(request):
        if request.url.path == "/api/v2/auth/login":
            return httpx.Response(200, text="Ok.", headers={"set-cookie": "SID=1"})
        if request.url.path == "/api/v2/app/version":
            return httpx.Response(200, text="v5.1.4")
        return httpx.Response(404)

    client, _ = make_client(handler)
    assert await client.connect() is True
    assert await client.app_version() == "v5.1.4"


@pytest.mark.asyncio
async def test_login_failure():
    def handler(request):
        return httpx.Response(200, text="Fails.")

    client, _ = make_client(handler)
    assert await client.connect() is False


@pytest.mark.asyncio
async def test_get_torrents_normalized():
    def handler(request):
        if request.url.path.endswith("/login"):
            return httpx.Response(200, text="Ok.")
        return ok_json(TORRENTS)

    client, _ = make_client(handler)
    torrents = await client.get_torrents()
    assert len(torrents) == 2
    first = torrents[0]
    assert first["hash"] == "abc123"
    assert first["size_bytes"] == 400000000
    assert first["completed_bytes"] == 200000000
    assert first["progress"] == 50.0


@pytest.mark.asyncio
async def test_reauth_on_403():
    logins: list = []
    infos: list = []

    def handler(request):
        if request.url.path.endswith("/login"):
            logins.append(1)
            return httpx.Response(200, text="Ok.")
        if request.url.path.endswith("/info") and not infos:
            infos.append(1)
            return httpx.Response(403)
        return ok_json(TORRENTS)

    client, _ = make_client(handler)
    client.connected = True  # simulate live-but-expired session
    torrents = await client.get_torrents()
    assert len(torrents) == 2
    assert len(logins) == 1  # exactly one re-login


@pytest.mark.asyncio
async def test_add_torrent_finds_hash_and_caps_seeding():
    seen: list = []
    state = {"listed": False}

    def handler(request):
        if request.url.path.endswith("/login"):
            return httpx.Response(200, text="Ok.")
        if request.url.path.endswith("/torrents/add"):
            return httpx.Response(200, text="Ok.")
        if request.url.path.endswith("/torrents/setShareLimits"):
            seen.append(request.url.path)
            return httpx.Response(200, text="Ok.")
        items = list(TORRENTS)
        if state["listed"]:
            items = [
                *items,
                {
                    "hash": "new999",
                    "name": "New",
                    "state": "downloading",
                    "size": 10,
                    "progress": 0.0,
                    "save_path": "",
                    "category": "",
                },
            ]
        state["listed"] = True
        return ok_json(items)

    client, _ = make_client(handler)
    result = await client.add_torrent("magnet:?xt=urn:btih:new999", category="anime")
    assert result["status"] == "success"
    assert result["hash"] == "new999"
    assert seen, "setShareLimits must be called on every add"


@pytest.mark.asyncio
async def test_pause_resume_delete():
    def handler(request):
        if request.url.path.endswith("/login"):
            return httpx.Response(200, text="Ok.")
        return httpx.Response(200, text="Ok.")

    client, calls = make_client(handler)
    assert (await client.pause_torrent("abc123"))["action"] == "paused"
    assert (await client.resume_torrent("abc123"))["action"] == "resumed"
    out = await client.delete_torrent("abc123", delete_files=True)
    assert out["action"] == "deleted" and out["files_deleted"] is True
    paths = [p for _, p in calls]
    assert "/api/v2/torrents/stop" in paths
    assert "/api/v2/torrents/start" in paths
    assert "/api/v2/torrents/delete" in paths


@pytest.mark.asyncio
async def test_is_complete_and_paths():
    def handler(request):
        if request.url.path.endswith("/login"):
            return httpx.Response(200, text="Ok.")
        return ok_json({"save_path": "D:/dl", "total_size": 100, "total_downloaded": 100})

    client, _ = make_client(handler)
    assert await client.is_torrent_complete("abc123") is True
    assert await client.get_torrent_base_path("abc123") == "D:/dl"


@pytest.mark.asyncio
async def test_enforce_no_seed_posts_prefs():
    posted: list = []

    def handler(request):
        if request.url.path.endswith("/login"):
            return httpx.Response(200, text="Ok.")
        if request.url.path.endswith("/app/setPreferences"):
            posted.append(request.read().decode())
            return httpx.Response(200, text="Ok.")
        return httpx.Response(404)

    client, _ = make_client(handler)
    out = await client.enforce_no_seed()
    assert out["status"] == "success"
    assert "max_seeding_time" in posted[0]


@pytest.mark.asyncio
async def test_describe_category_erase():
    def handler(request):
        if request.url.path.endswith("/login"):
            return httpx.Response(200, text="Ok.")
        if request.url.path.endswith("/torrents/delete"):
            return httpx.Response(200, text="Ok.")
        return ok_json(TORRENTS)

    client, _ = make_client(handler)
    info = client.describe()
    assert info["backend"] == "qbittorrent" and "base_url" in info
    assert await client.get_torrent_category("abc123") == "anime"
    assert await client.get_torrent_category("nope") == ""
    out = await client.erase_torrent("abc123")
    assert out["status"] == "success"


class FakeSettings:
    def __init__(self, **kw):
        defaults = {
            "TORRENT_BACKEND": "rtorrent",
            "RTORRENT_HOST": "localhost",
            "RTORRENT_PORT": 12224,
            "QBITTORRENT_URL": "http://localhost:18080",
            "QBITTORRENT_API_KEY": "",
            "QBITTORRENT_USERNAME": "",
            "QBITTORRENT_PASSWORD": "",
        }
        self._kw = {**defaults, **kw}

    def __getattr__(self, name):
        return self._kw.get(name)


def test_factory_defaults_rtorrent():
    from rtorrent_mcp.services.rtorrent_client import RTorrentClient

    backend = get_torrent_backend(FakeSettings())
    assert isinstance(backend, RTorrentClient)
    assert backend.backend_name == "rtorrent"


def test_factory_qbittorrent():
    backend = get_torrent_backend(FakeSettings(TORRENT_BACKEND="qbittorrent"))
    assert isinstance(backend, QBittorrentClient)
    assert backend.backend_name == "qbittorrent"


def test_factory_invalid_raises():
    with pytest.raises(ValueError, match="qbittorrent"):
        get_torrent_backend(FakeSettings(TORRENT_BACKEND="utorrent"))


@pytest.mark.asyncio
async def test_env_singleton_factory(monkeypatch):
    from rtorrent_mcp.services import torrent_backend as tb

    tb.reset_torrent_client()
    monkeypatch.setenv("TORRENT_BACKEND", "qbittorrent")
    backend = await tb.get_torrent_client()
    assert backend.backend_name == "qbittorrent"
    tb.reset_torrent_client()
    monkeypatch.delenv("TORRENT_BACKEND")
    backend = await tb.get_torrent_client()
    assert backend.backend_name == "rtorrent"
    tb.reset_torrent_client()
    monkeypatch.setenv("TORRENT_BACKEND", "bogus")
    with pytest.raises(ValueError, match="rtorrent, qbittorrent"):
        await tb.get_torrent_client()
    tb.reset_torrent_client()
