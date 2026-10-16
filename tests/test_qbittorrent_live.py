"""Live tests vs a real qBittorrent (env-gated, never in CI).

Set QBITTORRENT_TEST_URL (+ optional QBITTORRENT_TEST_USER/PASS) to run.
Read-only except enforce_no_seed, which caps seeding time to 1 minute —
run only against your own client.
"""

import os

import pytest

from rtorrent_mcp.services.qbittorrent_client import QBittorrentClient

TEST_URL = os.environ.get("QBITTORRENT_TEST_URL", "")
TEST_USER = os.environ.get("QBITTORRENT_TEST_USER", "")
TEST_PASS = os.environ.get("QBITTORRENT_TEST_PASS", "")

pytestmark = pytest.mark.skipif(not TEST_URL, reason="QBITTORRENT_TEST_URL not set")


@pytest.mark.asyncio
async def test_live_connect_and_list():
    c = QBittorrentClient(base_url=TEST_URL, username=TEST_USER or None, password=TEST_PASS or None)
    assert await c.connect() is True
    version = await c.app_version()
    assert version.startswith("v")
    torrents = await c.get_torrents()
    assert isinstance(torrents, list)
    for t in torrents:
        assert {"hash", "name", "progress"} <= set(t)
