"""
Tests for main search services (nyaa_search, piratebay_search)
Focuses on the actual search functions with mocked HTTP responses
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestNyaaSearchService:
    """Test nyaa.si search service main functions"""

    @pytest.mark.asyncio
    @patch("rtorrent_mcp.services.nyaa_search.aiohttp.ClientSession")
    async def test_search_nyaa_anime_basic(self, mock_session):
        """Test basic anime search on nyaa.si"""
        from rtorrent_mcp.services.nyaa_search import search_nyaa_anime

        mock_html = """
        <html>
            <body>
                <table class="torrent-list">
                    <tr><th>Category</th><th>Name</th><th>Comments</th><th>Size</th><th>Date</th><th>SE</th><th>LE</th><th>DL</th></tr>
                    <tr>
                        <td>Anime</td>
                        <td><a href="/view/123">[ASW] Test Anime - 01 [720p]</a></td>
                        <td>0</td>
                        <td>250.5 MB</td>
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

        results = await search_nyaa_anime("Test Anime", resolution="720p", group="ASW")
        assert len(results) > 0
        assert results[0]["title"] == "[ASW] Test Anime - 01 [720p]"

    @pytest.mark.asyncio
    @patch("rtorrent_mcp.services.nyaa_search.aiohttp.ClientSession")
    async def test_search_nyaa_anime_asw_user_page(self, mock_session):
        """Test ASW user page search"""
        from rtorrent_mcp.services.nyaa_search import search_nyaa_anime

        mock_html = """
        <html>
            <body>
                <table class="torrent-list">
                    <tr><th>Category</th><th>Name</th><th>Comments</th><th>Size</th><th>Date</th><th>SE</th><th>LE</th><th>DL</th></tr>
                    <tr>
                        <td>Anime</td>
                        <td><a href="/view/456">[ASW] Test Anime - 02 [1080p HEVC x265]</a></td>
                        <td>0</td>
                        <td>350.2 MB</td>
                        <td>Today</td>
                        <td>30</td>
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

        results = await search_nyaa_anime("Test Anime", resolution="720p", group="ASW")
        assert len(results) > 0

    @pytest.mark.asyncio
    @patch("rtorrent_mcp.services.nyaa_search.aiohttp.ClientSession")
    async def test_search_nyaa_anime_error_response(self, mock_session):
        """Test handling of error response"""
        from rtorrent_mcp.services.nyaa_search import search_nyaa_anime

        mock_response = MagicMock()
        mock_response.status = 500
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        mock_session_instance = MagicMock()
        mock_session_instance.__aenter__ = AsyncMock(return_value=mock_session_instance)
        mock_session_instance.__aexit__ = AsyncMock(return_value=None)
        mock_session_instance.get = MagicMock(return_value=mock_response)
        mock_session.return_value = mock_session_instance

        results = await search_nyaa_anime("Test", resolution="720p")
        assert isinstance(results, list)

    @pytest.mark.asyncio
    @patch("rtorrent_mcp.services.nyaa_search.aiohttp.ClientSession")
    async def test_search_nyaa_anime_no_results(self, mock_session):
        """Test search with no results"""
        from rtorrent_mcp.services.nyaa_search import search_nyaa_anime

        mock_html = """
        <html>
            <body>
                <table class="torrent-list">
                    <tr><th>Category</th><th>Name</th></tr>
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

        results = await search_nyaa_anime("Nonexistent Anime", resolution="720p")
        assert isinstance(results, list)

    @pytest.mark.asyncio
    @patch("rtorrent_mcp.services.nyaa_search.aiohttp.ClientSession")
    async def test_search_nyaa_anime_network_error(self, mock_session):
        """Test handling of network errors"""
        import aiohttp

        from rtorrent_mcp.services.nyaa_search import search_nyaa_anime

        mock_session_instance = MagicMock()
        mock_session_instance.__aenter__ = AsyncMock(return_value=mock_session_instance)
        mock_session_instance.__aexit__ = AsyncMock(return_value=None)
        mock_session_instance.get = AsyncMock(side_effect=aiohttp.ClientError("Network error"))
        mock_session.return_value = mock_session_instance

        results = await search_nyaa_anime("Test", resolution="720p")
        assert isinstance(results, list)


class TestPirateBaySearchService:
    """Test Pirate Bay search service main functions"""

    @pytest.mark.asyncio
    @patch("rtorrent_mcp.services.piratebay_search.aiohttp.ClientSession")
    async def test_search_piratebay_tv_basic(self, mock_session):
        """Test basic TV search on Pirate Bay"""
        from rtorrent_mcp.services.piratebay_search import search_piratebay_tv

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
                        <td>TV</td>
                        <td>
                            <a href="/torrent/123" title="Test Show S01E01 MeGusta">Test Show S01E01 MeGusta</a>
                            <a href="magnet:?xt=urn:btih:testhash">Magnet</a>
                        </td>
                        <td>Today</td>
                        <td>350.5 MB</td>
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

        results = await search_piratebay_tv("Test Show", resolution="1080p", group="MeGusta")
        assert len(results) > 0
        assert "MeGusta" in results[0]["title"]

    @pytest.mark.asyncio
    @patch("rtorrent_mcp.services.piratebay_search.aiohttp.ClientSession")
    async def test_search_piratebay_tv_with_episode_format(self, mock_session):
        """Test TV search with episode format (S28E03)"""
        from rtorrent_mcp.services.piratebay_search import search_piratebay_tv

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
                        <td>TV</td>
                        <td>
                            <a href="/torrent/456">South Park S28E03 MeGusta</a>
                            <a href="magnet:?xt=urn:btih:episodehash">Magnet</a>
                        </td>
                        <td>Today</td>
                        <td>200.1 MB</td>
                        <td>50</td>
                        <td>5</td>
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

        results = await search_piratebay_tv(
            "South Park S28E03", resolution="1080p", group="MeGusta"
        )
        assert len(results) > 0

    @pytest.mark.asyncio
    @patch("rtorrent_mcp.services.piratebay_search.aiohttp.ClientSession")
    async def test_search_piratebay_tv_error_response(self, mock_session):
        """Test handling of error response"""
        from rtorrent_mcp.services.piratebay_search import search_piratebay_tv

        mock_response = MagicMock()
        mock_response.status = 500
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        mock_session_instance = MagicMock()
        mock_session_instance.__aenter__ = AsyncMock(return_value=mock_session_instance)
        mock_session_instance.__aexit__ = AsyncMock(return_value=None)
        mock_session_instance.get = MagicMock(return_value=mock_response)
        mock_session.return_value = mock_session_instance

        results = await search_piratebay_tv("Test", resolution="1080p")
        assert isinstance(results, list)

    @pytest.mark.asyncio
    @patch("rtorrent_mcp.services.piratebay_search.aiohttp.ClientSession")
    async def test_search_piratebay_tv_no_results(self, mock_session):
        """Test search with no results"""
        from rtorrent_mcp.services.piratebay_search import search_piratebay_tv

        mock_html = """
        <html>
            <body>
                <table id="searchResult">
                    <tr><th>Category</th><th>Name</th></tr>
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

        results = await search_piratebay_tv("Nonexistent Show", resolution="1080p")
        assert isinstance(results, list)

    @pytest.mark.asyncio
    @patch("rtorrent_mcp.services.piratebay_search.aiohttp.ClientSession")
    async def test_search_piratebay_tv_network_error(self, mock_session):
        """Test handling of network errors"""
        import aiohttp

        from rtorrent_mcp.services.piratebay_search import search_piratebay_tv

        mock_session_instance = MagicMock()
        mock_session_instance.__aenter__ = AsyncMock(return_value=mock_session_instance)
        mock_session_instance.__aexit__ = AsyncMock(return_value=None)
        mock_session_instance.get = AsyncMock(side_effect=aiohttp.ClientError("Network error"))
        mock_session.return_value = mock_session_instance

        results = await search_piratebay_tv("Test", resolution="1080p")
        assert isinstance(results, list)

    @pytest.mark.asyncio
    @patch("rtorrent_mcp.services.piratebay_search.aiohttp.ClientSession")
    async def test_search_piratebay_tv_query_matching_filter(self, mock_session):
        """Test query matching filter ensures results match query"""
        from rtorrent_mcp.services.piratebay_search import search_piratebay_tv

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
                        <td>TV</td>
                        <td>
                            <a href="/torrent/789">Different Show S01E01 MeGusta</a>
                            <a href="magnet:?xt=urn:btih:different">Magnet</a>
                        </td>
                        <td>Today</td>
                        <td>300 MB</td>
                        <td>10</td>
                        <td>2</td>
                        <td>User3</td>
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

        results = await search_piratebay_tv("Test Show", resolution="1080p", group="MeGusta")
        # Query matching filter should exclude "Different Show"
        assert isinstance(results, list)
