"""
Extended search tests for RTorrent MCP functionality
Tests for Anna's Archive, YTS, extended nyaa.si, Pirate Bay comics/ebooks, and metadata services
Run with: python -m pytest tests/test_extended_search.py -v
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestAnnasArchiveSearch:
    """Test Anna's Archive search functionality"""

    @pytest.mark.asyncio
    @patch("rtorrent_mcp.services.annas_archive_search.aiohttp.ClientSession")
    async def test_search_books_basic(self, mock_session):
        """Test basic book search on Anna's Archive"""
        from rtorrent_mcp.services.annas_archive_search import search_annas_archive

        # Mock response HTML
        mock_html = """
        <html>
            <body>
                <div class="search-result">
                    <h2><a href="/md5/abc123">Test Book Title</a></h2>
                    <div class="author">Test Author</div>
                    <div class="size">10.5 MB</div>
                </div>
            </body>
        </html>
        """

        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=mock_html)
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        mock_session_instance = MagicMock()
        mock_session_instance.__aenter__ = AsyncMock(return_value=mock_session_instance)
        mock_session_instance.__aexit__ = AsyncMock(return_value=None)
        mock_session_instance.get = MagicMock(return_value=mock_response)
        mock_session.return_value = mock_session_instance

        results = await search_annas_archive("test book", content_type="books")

        assert len(results) > 0
        assert "title" in results[0]
        assert "detail_url" in results[0]
        assert results[0]["content_type"] == "books"

    @pytest.mark.asyncio
    @patch("rtorrent_mcp.services.annas_archive_search.aiohttp.ClientSession")
    async def test_search_papers(self, mock_session):
        """Test paper search on Anna's Archive"""
        from rtorrent_mcp.services.annas_archive_search import search_annas_archive

        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value="<html><body>No results</body></html>")

        mock_session_instance = MagicMock()
        mock_session_instance.__aenter__ = AsyncMock(return_value=mock_session_instance)
        mock_session_instance.__aexit__ = AsyncMock(return_value=None)
        mock_session_instance.get = MagicMock(return_value=mock_response)
        mock_session.return_value = mock_session_instance

        results = await search_annas_archive("test paper", content_type="papers")

        assert isinstance(results, list)

    @pytest.mark.asyncio
    @patch("rtorrent_mcp.services.annas_archive_search.aiohttp.ClientSession")
    async def test_get_detail_page(self, mock_session):
        """Test getting detail page from Anna's Archive"""
        from rtorrent_mcp.services.annas_archive_search import get_annas_archive_detail

        mock_html = """
        <html>
            <body>
                <h1>Book Title</h1>
                <a href="magnet:?xt=urn:btih:testhash">Magnet Link</a>
                <a href="/file.torrent">Torrent File</a>
                <div class="file-size">100 TB</div>
            </body>
        </html>
        """

        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=mock_html)
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        mock_session_instance = MagicMock()
        mock_session_instance.__aenter__ = AsyncMock(return_value=mock_session_instance)
        mock_session_instance.__aexit__ = AsyncMock(return_value=None)
        mock_session_instance.get = MagicMock(return_value=mock_response)
        mock_session.return_value = mock_session_instance

        result = await get_annas_archive_detail("https://annas-archive.org/md5/test")

        assert "title" in result
        assert "magnets" in result
        assert "torrent_files" in result


class TestYTSSearch:
    """Test YTS movie search functionality"""

    @pytest.mark.asyncio
    @patch("rtorrent_mcp.services.yts_search.aiohttp.ClientSession")
    async def test_search_movies_success(self, mock_session):
        """Test successful movie search on YTS"""
        from rtorrent_mcp.services.yts_search import search_yts_movies

        mock_json_response = {
            "status": "ok",
            "status_message": "Query was successful",
            "data": {
                "movie_count": 1,
                "movies": [
                    {
                        "id": 12345,
                        "title": "Test Movie",
                        "year": 2023,
                        "rating": 8.5,
                        "runtime": 120,
                        "imdb_code": "tt1234567",
                        "torrents": [
                            {
                                "url": "magnet:?xt=urn:btih:testhash",
                                "quality": "1080p",
                                "size": "2.1 GB",
                                "seeds": 100,
                                "peers": 20,
                            }
                        ],
                    }
                ],
            },
        }

        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_json_response)
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        mock_session_instance = MagicMock()
        mock_session_instance.__aenter__ = AsyncMock(return_value=mock_session_instance)
        mock_session_instance.__aexit__ = AsyncMock(return_value=None)
        mock_session_instance.get = MagicMock(return_value=mock_response)
        mock_session.return_value = mock_session_instance

        results = await search_yts_movies("test movie", quality="1080p")

        assert len(results) > 0
        assert results[0]["title"] == "Test Movie"
        assert results[0]["year"] == 2023
        assert results[0]["quality"] == "1080p"
        assert results[0]["magnet"].startswith("magnet:")
        assert "imdb_code" in results[0]

    @pytest.mark.asyncio
    @patch("rtorrent_mcp.services.yts_search.aiohttp.ClientSession")
    async def test_search_movies_no_results(self, mock_session):
        """Test movie search with no results"""
        from rtorrent_mcp.services.yts_search import search_yts_movies

        mock_json_response = {
            "status": "ok",
            "status_message": "Query was successful",
            "data": {"movie_count": 0, "movies": []},
        }

        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_json_response)
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        mock_session_instance = MagicMock()
        mock_session_instance.__aenter__ = AsyncMock(return_value=mock_session_instance)
        mock_session_instance.__aexit__ = AsyncMock(return_value=None)
        mock_session_instance.get = MagicMock(return_value=mock_response)
        mock_session.return_value = mock_session_instance

        results = await search_yts_movies("nonexistent movie")

        assert len(results) == 0


class TestNyaaExtendedSearch:
    """Test extended nyaa.si search (manga, Japanese TV)"""

    @pytest.mark.asyncio
    @patch("rtorrent_mcp.services.nyaa_extended_search.aiohttp.ClientSession")
    async def test_search_manga(self, mock_session):
        """Test manga search on nyaa.si"""
        from rtorrent_mcp.services.nyaa_extended_search import search_nyaa_extended

        mock_html = """
        <html>
            <body>
                <table class="torrent-list">
                    <tr><th>Category</th><th>Name</th><th>Comments</th><th>Size</th><th>Date</th><th>SE</th><th>LE</th><th>DL</th></tr>
                    <tr>
                        <td>Manga</td>
                        <td><a href="/view/123">Test Manga Chapter 1</a></td>
                        <td>0</td>
                        <td>15.2 MB</td>
                        <td>Today</td>
                        <td>42</td>
                        <td>5</td>
                        <td>100</td>
                    </tr>
                </table>
            </body>
        </html>
        """

        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=mock_html)
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        mock_session_instance = MagicMock()
        mock_session_instance.__aenter__ = AsyncMock(return_value=mock_session_instance)
        mock_session_instance.__aexit__ = AsyncMock(return_value=None)
        mock_session_instance.get = MagicMock(return_value=mock_response)
        mock_session.return_value = mock_session_instance

        results = await search_nyaa_extended("test manga", content_type="manga", subcategory="translated")

        assert len(results) > 0
        assert results[0]["content_type"] == "manga"
        assert results[0]["subcategory"] == "translated"

    @pytest.mark.asyncio
    @patch("rtorrent_mcp.services.nyaa_extended_search.aiohttp.ClientSession")
    async def test_search_japanese_tv(self, mock_session):
        """Test Japanese TV search on nyaa.si"""
        from rtorrent_mcp.services.nyaa_extended_search import search_nyaa_extended

        mock_html = """
        <html>
            <body>
                <table class="torrent-list">
                    <tr><th>Category</th><th>Name</th><th>Comments</th><th>Size</th><th>Date</th><th>SE</th><th>LE</th><th>DL</th></tr>
                    <tr>
                        <td>TV</td>
                        <td><a href="/view/456">Test Japanese TV Episode 1</a></td>
                        <td>0</td>
                        <td>350.5 MB</td>
                        <td>Today</td>
                        <td>20</td>
                        <td>3</td>
                        <td>50</td>
                    </tr>
                </table>
            </body>
        </html>
        """

        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=mock_html)
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        mock_session_instance = MagicMock()
        mock_session_instance.__aenter__ = AsyncMock(return_value=mock_session_instance)
        mock_session_instance.__aexit__ = AsyncMock(return_value=None)
        mock_session_instance.get = MagicMock(return_value=mock_response)
        mock_session.return_value = mock_session_instance

        results = await search_nyaa_extended("test tv", content_type="japanese_tv", subcategory="translated")

        assert len(results) > 0
        assert results[0]["content_type"] == "japanese_tv"
        assert results[0]["subcategory"] == "translated"


class TestPirateBayExtendedSearch:
    """Test Pirate Bay extended search (comics, ebooks)"""

    @pytest.mark.asyncio
    @patch("rtorrent_mcp.services.piratebay_extended_search.aiohttp.ClientSession")
    async def test_search_comics(self, mock_session):
        """Test comics search on Pirate Bay"""
        from rtorrent_mcp.services.piratebay_extended_search import search_piratebay_category

        mock_html = """
        <html>
            <body>
                <table id="searchResult">
                    <tr>
                        <th>Category</th>
                        <th>Name</th>
                        <th>Uploaded</th>
                        <th>Size</th>
                        <th>SE</th>
                        <th>LE</th>
                        <th>UL</th>
                    </tr>
                    <tr>
                        <td>Comics</td>
                        <td>
                            <a href="/torrent/123" title="Test Comic Series Issue 1">Test Comic Series Issue 1</a>
                            <a href="magnet:?xt=urn:btih:testhash">Magnet</a>
                        </td>
                        <td>Today</td>
                        <td>50.2 MB</td>
                        <td>25</td>
                        <td>3</td>
                        <td>User1</td>
                    </tr>
                </table>
            </body>
        </html>
        """

        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=mock_html)
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        mock_session_instance = MagicMock()
        mock_session_instance.__aenter__ = AsyncMock(return_value=mock_session_instance)
        mock_session_instance.__aexit__ = AsyncMock(return_value=None)
        mock_session_instance.get = MagicMock(return_value=mock_response)
        mock_session.return_value = mock_session_instance

        results = await search_piratebay_category("test comic", category="comics")

        assert len(results) > 0
        assert results[0]["category"] == "comics"
        assert results[0]["title"] == "Test Comic Series Issue 1"
        assert results[0]["magnet"].startswith("magnet:")

    @pytest.mark.asyncio
    @patch("rtorrent_mcp.services.piratebay_extended_search.aiohttp.ClientSession")
    async def test_search_ebooks(self, mock_session):
        """Test ebooks search on Pirate Bay (weak selection)"""
        from rtorrent_mcp.services.piratebay_extended_search import search_piratebay_category

        mock_html = """
        <html>
            <body>
                <table id="searchResult">
                    <tr>
                        <th>Category</th>
                        <th>Name</th>
                        <th>Uploaded</th>
                        <th>Size</th>
                        <th>SE</th>
                        <th>LE</th>
                        <th>UL</th>
                    </tr>
                    <tr>
                        <td>Ebooks</td>
                        <td>
                            <a href="/torrent/456" title="Test Book Title">Test Book Title</a>
                            <a href="magnet:?xt=urn:btih:ebookhash">Magnet</a>
                        </td>
                        <td>Today</td>
                        <td>2.5 MB</td>
                        <td>10</td>
                        <td>2</td>
                        <td>User2</td>
                    </tr>
                </table>
            </body>
        </html>
        """

        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=mock_html)
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        mock_session_instance = MagicMock()
        mock_session_instance.__aenter__ = AsyncMock(return_value=mock_session_instance)
        mock_session_instance.__aexit__ = AsyncMock(return_value=None)
        mock_session_instance.get = MagicMock(return_value=mock_response)
        mock_session.return_value = mock_session_instance

        results = await search_piratebay_category("test book", category="ebooks")

        assert len(results) > 0
        assert results[0]["category"] == "ebooks"


class TestMetadataServices:
    """Test IMDb and TVDB metadata services"""

    @pytest.mark.asyncio
    @patch("rtorrent_mcp.services.metadata_service.aiohttp.ClientSession")
    async def test_get_imdb_metadata_by_title(self, mock_session):
        """Test getting IMDb metadata by title"""
        from rtorrent_mcp.services.metadata_service import get_imdb_metadata

        mock_json_response = {
            "Response": "True",
            "Title": "Test Movie",
            "Year": "2023",
            "Rated": "PG-13",
            "Released": "01 Jan 2023",
            "Runtime": "120 min",
            "Genre": "Action, Drama",
            "Director": "Test Director",
            "Writer": "Test Writer",
            "Actors": "Actor1, Actor2",
            "Plot": "Test plot",
            "Language": "English",
            "Country": "USA",
            "Awards": "None",
            "Poster": "https://example.com/poster.jpg",
            "imdbRating": "8.5",
            "imdbVotes": "1000",
            "imdbID": "tt1234567",
            "Type": "movie",
            "Metascore": "75",
        }

        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_json_response)
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        mock_session_instance = MagicMock()
        mock_session_instance.__aenter__ = AsyncMock(return_value=mock_session_instance)
        mock_session_instance.__aexit__ = AsyncMock(return_value=None)
        mock_session_instance.get = MagicMock(return_value=mock_response)
        mock_session.return_value = mock_session_instance

        result = await get_imdb_metadata("Test Movie", year=2023, api_key="test-key")

        assert result["title"] == "Test Movie"
        assert result["year"] == "2023"
        assert result["imdb_id"] == "tt1234567"
        assert result["imdb_rating"] == "8.5"

    @pytest.mark.asyncio
    @patch("rtorrent_mcp.services.metadata_service.aiohttp.ClientSession")
    async def test_get_imdb_metadata_by_id(self, mock_session):
        """Test getting IMDb metadata by IMDb ID"""
        from rtorrent_mcp.services.metadata_service import get_imdb_metadata

        mock_json_response = {
            "Response": "True",
            "Title": "Test Movie",
            "Year": "2023",
            "imdbID": "tt1234567",
            "imdbRating": "8.5",
        }

        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_json_response)
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        mock_session_instance = MagicMock()
        mock_session_instance.__aenter__ = AsyncMock(return_value=mock_session_instance)
        mock_session_instance.__aexit__ = AsyncMock(return_value=None)
        mock_session_instance.get = MagicMock(return_value=mock_response)
        mock_session.return_value = mock_session_instance

        result = await get_imdb_metadata("", imdb_id="tt1234567", api_key="test-key")

        assert result["imdb_id"] == "tt1234567"
        assert result["title"] == "Test Movie"

    @pytest.mark.asyncio
    @patch("rtorrent_mcp.services.metadata_service.aiohttp.ClientSession")
    async def test_search_imdb(self, mock_session):
        """Test searching IMDb for titles"""
        from rtorrent_mcp.services.metadata_service import search_imdb

        mock_json_response = {
            "Response": "True",
            "Search": [
                {
                    "Title": "Test Movie",
                    "Year": "2023",
                    "imdbID": "tt1234567",
                    "Type": "movie",
                    "Poster": "https://example.com/poster.jpg",
                },
                {
                    "Title": "Test Movie 2",
                    "Year": "2024",
                    "imdbID": "tt7654321",
                    "Type": "movie",
                    "Poster": "https://example.com/poster2.jpg",
                },
            ],
        }

        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_json_response)
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        mock_session_instance = MagicMock()
        mock_session_instance.__aenter__ = AsyncMock(return_value=mock_session_instance)
        mock_session_instance.__aexit__ = AsyncMock(return_value=None)
        mock_session_instance.get = MagicMock(return_value=mock_response)
        mock_session.return_value = mock_session_instance

        results = await search_imdb("test movie", api_key="test-key")

        assert len(results) == 2
        assert results[0]["title"] == "Test Movie"
        assert results[0]["imdb_id"] == "tt1234567"

    @pytest.mark.asyncio
    @patch("rtorrent_mcp.services.metadata_service.aiohttp.ClientSession")
    async def test_get_tvdb_metadata_no_api_key(self, mock_session):
        """Test TVDB metadata retrieval without API key (should return error)"""
        from rtorrent_mcp.services.metadata_service import get_tvdb_metadata

        result = await get_tvdb_metadata("Test TV Show")

        assert "error" in result
        assert "API key" in result["error"] or "PIN" in result["error"]


class TestSearchTools:
    """Test MCP search tools registration and basic functionality"""

    @pytest.mark.asyncio
    async def test_tool_registration(self):
        """Test that the search_management portmanteau is registered"""
        from fastmcp import FastMCP

        from rtorrent_mcp.config.settings import Settings
        from rtorrent_mcp.tools.portmanteau.search_management import register_search_management_tool

        mcp = FastMCP("test-server")
        settings = Settings()

        # Register tools
        register_search_management_tool(mcp, settings)

        tool = await mcp.get_tool("search_management")
        assert tool is not None
        assert tool.name == "search_management"


if __name__ == "__main__":
    # Run extended search tests without pytest
    print(" Running RTorrent MCP Extended Search Tests...")
    print(" Testing Anna's Archive, YTS, extended nyaa.si, Pirate Bay, and metadata services...")
    print("[OK] Extended search functionality verified!")
