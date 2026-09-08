"""
Unit tests for Anna's Archive search: the fast aiohttp path, the honest
empty-result path (regression test for BUG-032 -- the empty-state message
box used to get scraped as a fake "book"), and the Obscura headless-browser
fallback for anti-bot-gated mirrors (e.g. ``.gl``'s DDoS-Guard).
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from rtorrent_mcp.services.annas_archive_search import (
    _looks_bot_gated,
    _parse_annas_html,
    search_annas_archive,
)

# Minimal fixtures using Anna's Archive's real primary selector
# (div.bg-white.rounded-lg) with synthetic, non-real content -- structurally
# representative, not scraped from the live site.

REAL_RESULT_HTML = """
<html><body>
<div class="bg-white rounded-lg">
  <h2><a href="/md5/deadbeef1234">Test Book Title</a></h2>
  <div class="author">Test Author</div>
  <div class="size">3.2 MB</div>
  <div class="format">epub</div>
</div>
</body></html>
"""

# What the real "no records" empty state gets scraped as if the title
# fallback isn't guarded (BUG-032): a div matching the broad selector, no
# real title link inside it, just the site's own empty-state copy.
EMPTY_STATE_HTML = """
<html><body>
<div class="bg-white rounded-lg is-relative">
  <p>No records found</p>
  <p>Try broadening the search, changing language or file type filters, or browsing a different category.</p>
</div>
</body></html>
"""

DDOS_GUARD_HTML = """
<html><head><title>DDoS-Guard</title></head><body>
<p>Checking your browser before accessing the site.</p>
</body></html>
"""


def _mock_session(status: int, text: str):
    mock_response = MagicMock()
    mock_response.status = status
    mock_response.text = AsyncMock(return_value=text)

    mock_get_ctx = MagicMock()
    mock_get_ctx.__aenter__ = AsyncMock(return_value=mock_response)
    mock_get_ctx.__aexit__ = AsyncMock(return_value=None)

    mock_session = MagicMock()
    mock_session.get.return_value = mock_get_ctx

    mock_session_ctx = MagicMock()
    mock_session_ctx.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session_ctx.__aexit__ = AsyncMock(return_value=None)
    return mock_session_ctx


# --- Pure parsing tests (no I/O, no mocking needed) ---


def test_parse_real_result():
    results = _parse_annas_html(
        REAL_RESULT_HTML, "https://annas-archive.is", "https://annas-archive.is/search?q=x", "books", 20
    )
    assert len(results) == 1
    assert results[0]["title"] == "Test Book Title"
    assert results[0]["author"] == "Test Author"
    assert results[0]["detail_url"] == "https://annas-archive.is/md5/deadbeef1234"


def test_parse_empty_state_is_not_a_fake_result():
    """Regression test for BUG-032: the site's own 'No records found' box
    matches the broad container selector but has no real title link inside
    it, and must be skipped rather than scraped as a fabricated title."""
    results = _parse_annas_html(
        EMPTY_STATE_HTML, "https://annas-archive.is", "https://annas-archive.is/search?q=x", "books", 20
    )
    assert results == []


def test_looks_bot_gated_detects_status_codes():
    assert _looks_bot_gated(403, "") is True
    assert _looks_bot_gated(503, "") is True
    assert _looks_bot_gated(200, "") is False


def test_looks_bot_gated_detects_challenge_markers():
    assert _looks_bot_gated(200, DDOS_GUARD_HTML) is True
    assert _looks_bot_gated(200, REAL_RESULT_HTML) is False


# --- End-to-end search_annas_archive tests (mocked network + Obscura) ---


@pytest.mark.asyncio
async def test_search_annas_archive_fast_path_success():
    with patch("aiohttp.ClientSession", return_value=_mock_session(200, REAL_RESULT_HTML)):
        results = await search_annas_archive("Test Book Title")
        assert len(results) == 1
        assert results[0]["title"] == "Test Book Title"


@pytest.mark.asyncio
async def test_search_annas_archive_genuine_no_results():
    """A real 200 with the site's own empty-state box must return an honest
    empty list, not the fabricated placeholder BUG-032 produced."""
    with patch("aiohttp.ClientSession", return_value=_mock_session(200, EMPTY_STATE_HTML)):
        results = await search_annas_archive("some nonsense query")
        assert results == []


@pytest.mark.asyncio
async def test_search_annas_archive_bot_gated_falls_back_to_obscura():
    """A 403/DDoS-Guard response should trigger the Obscura fallback, and a
    successful render should be parsed exactly like a plain 200 response."""
    with (
        patch("aiohttp.ClientSession", return_value=_mock_session(403, DDOS_GUARD_HTML)),
        patch("rtorrent_mcp.services.annas_archive_search.obscura_available", return_value=True),
        patch(
            "rtorrent_mcp.services.annas_archive_search.obscura_render",
            return_value=REAL_RESULT_HTML,
        ) as mock_render,
    ):
        results = await search_annas_archive("Test Book Title")
        assert len(results) == 1
        assert results[0]["title"] == "Test Book Title"
        mock_render.assert_called_once()


@pytest.mark.asyncio
async def test_search_annas_archive_bot_gated_no_obscura_available():
    """When bot-gated and Obscura isn't installed, fail cleanly with an
    error rather than crashing or fabricating a result."""
    with (
        patch("aiohttp.ClientSession", return_value=_mock_session(403, DDOS_GUARD_HTML)),
        patch("rtorrent_mcp.services.annas_archive_search.obscura_available", return_value=False),
    ):
        results = await search_annas_archive("Test Book Title")
        # All mirrors fail the same way in this test -> aggregate error result
        assert results == [] or (len(results) == 1 and "error" in results[0])
