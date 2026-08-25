"""
Unit tests for Gutenberg search functionality.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from rtorrent_mcp.services.gutenberg_search import search_gutenberg


@pytest.mark.asyncio
async def test_search_gutenberg_success():
    mock_data = {
        "results": [
            {
                "id": 1342,
                "title": "Pride and Prejudice",
                "authors": [{"name": "Austen, Jane", "birth_year": 1775, "death_year": 1817}],
                "languages": ["en"],
                "subjects": ["Courtship -- Fiction", "Domestic fiction"],
                "download_count": 50000,
                "formats": {
                    "application/epub+zip": "https://www.gutenberg.org/ebooks/1342.epub3.images",
                    "image/jpeg": "https://www.gutenberg.org/cache/epub/1342/pg1342.cover.medium.jpg",
                },
                "copyright": False,
            }
        ]
    }

    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value=mock_data)

    mock_get_ctx = MagicMock()
    mock_get_ctx.__aenter__ = AsyncMock(return_value=mock_response)
    mock_get_ctx.__aexit__ = AsyncMock(return_value=None)

    mock_session = MagicMock()
    mock_session.get.return_value = mock_get_ctx

    mock_session_ctx = MagicMock()
    mock_session_ctx.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session_ctx.__aexit__ = AsyncMock(return_value=None)

    with patch("aiohttp.ClientSession", return_value=mock_session_ctx):
        results = await search_gutenberg("Pride and Prejudice")
        assert len(results) == 1
        book = results[0]
        assert book["id"] == 1342
        assert book["title"] == "Pride and Prejudice"
        assert book["author"] == "Austen, Jane"
        assert book["download_url"] == "https://www.gutenberg.org/ebooks/1342.epub3.images"
        assert book["copyright"] is False
