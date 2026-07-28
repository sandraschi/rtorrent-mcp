"""
Tests for media integrator — Plex/Jellyfin scan notification after post-processing.
"""

import asyncio

from rtorrent_mcp.services.media_integrator import MediaIntegrator


class TestMediaIntegrator:
    """MediaIntegrator notifies Plex/Jellyfin after direct rTorrent downloads."""

    def test_init_empty_config(self):
        inst = MediaIntegrator({})
        assert inst.cfg == {}

    def test_plex_skipped_when_not_configured(self):
        inst = MediaIntegrator({})
        r = asyncio.run(inst.scan_plex())
        assert r["service"] == "plex"
        assert r["status"] == "skipped"

    def test_jellyfin_skipped_when_not_configured(self):
        inst = MediaIntegrator({"jellyfin_url": "", "jellyfin_api_key": ""})
        r = asyncio.run(inst.scan_jellyfin("/test/path"))
        assert r["service"] == "jellyfin"
        assert r["status"] == "skipped"

    def test_jellyfin_skipped_when_no_url(self):
        inst = MediaIntegrator({"jellyfin_url": "", "jellyfin_api_key": "abc"})
        r = asyncio.run(inst.scan_jellyfin())
        assert r["status"] == "skipped"

    def test_notify_all_skips_when_nothing_configured(self):
        inst = MediaIntegrator({})
        r = asyncio.run(inst.notify_all("anime", []))
        assert len(r) == 2
        assert all(x["status"] == "skipped" for x in r)

    def test_notify_all_calls_both_when_plex_configured(self):
        inst = MediaIntegrator({"plex_url": "http://plex:32400", "plex_token": "abc"})
        r = asyncio.run(inst.notify_all("anime", ["/ingestion/anime/Show - 01.mkv"]))
        services = {x["service"] for x in r}
        assert "plex" in services
        assert "jellyfin" in services
        # Plex should attempt the call (not skipped)
        plex_result = next(x for x in r if x["service"] == "plex")
        assert plex_result["status"] != "skipped"
