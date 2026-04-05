"""
Additional tests to improve coverage for services with low coverage
Focuses on error handling, edge cases, and code paths not covered by existing tests
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestAnnasArchiveCoverage:
    """Additional tests for Anna's Archive to improve coverage"""

    @pytest.mark.asyncio
    @patch("rtorrent_mcp.services.annas_archive_search.aiohttp.ClientSession")
    async def test_search_annas_archive_error_response(self, mock_session):
        """Test handling of non-200 HTTP response"""
        from rtorrent_mcp.services.annas_archive_search import search_annas_archive

        mock_response = MagicMock()
        mock_response.status = 500
        mock_response.text = AsyncMock(return_value="Server Error")

        mock_session_instance = MagicMock()
        mock_session_instance.__aenter__ = AsyncMock(return_value=mock_session_instance)
        mock_session_instance.__aexit__ = AsyncMock(return_value=None)
        mock_session_instance.get = AsyncMock(return_value=mock_response)
        mock_session.return_value = mock_session_instance

        results = await search_annas_archive("test", content_type="books")
        assert len(results) > 0
        assert "error" in results[0]

    @pytest.mark.asyncio
    @patch("rtorrent_mcp.services.annas_archive_search.aiohttp.ClientSession")
    async def test_search_annas_archive_with_result_containers(self, mock_session):
        """Test search with result containers found"""
        from rtorrent_mcp.services.annas_archive_search import search_annas_archive

        mock_html = """
        <html>
            <body>
                <div class="search-result">
                    <h2><a href="/md5/abc123">Test Book</a></h2>
                    <div class="author">Test Author</div>
                    <div class="size">10 MB</div>
                    <div class="format">PDF</div>
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

        results = await search_annas_archive("test", content_type="books", max_results=5)
        assert len(results) > 0
        assert results[0]["title"] == "Test Book"

    @pytest.mark.asyncio
    @patch("rtorrent_mcp.services.annas_archive_search.aiohttp.ClientSession")
    async def test_search_annas_archive_no_results_message(self, mock_session):
        """Test handling of 'no results' message"""
        from rtorrent_mcp.services.annas_archive_search import search_annas_archive

        mock_html = """
        <html>
            <body>
                <div>No results found for your query</div>
            </body>
        </html>
        """

        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=mock_html)

        mock_session_instance = MagicMock()
        mock_session_instance.__aenter__ = AsyncMock(return_value=mock_session_instance)
        mock_session_instance.__aexit__ = AsyncMock(return_value=None)
        mock_session_instance.get = AsyncMock(return_value=mock_response)
        mock_session.return_value = mock_session_instance

        results = await search_annas_archive("nonexistent", content_type="books")
        assert isinstance(results, list)

    @pytest.mark.asyncio
    @patch("rtorrent_mcp.services.annas_archive_search.aiohttp.ClientSession")
    async def test_get_annas_detail_with_magnets(self, mock_session):
        """Test getting detail page with magnet links"""
        from rtorrent_mcp.services.annas_archive_search import get_annas_archive_detail

        mock_html = """
        <html>
            <body>
                <h1>Test Book</h1>
                <a href="magnet:?xt=urn:btih:testhash1">Magnet 1</a>
                <a href="magnet:?xt=urn:btih:testhash2">Magnet 2</a>
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
        assert "magnets" in result
        assert len(result["magnets"]) > 0


class TestYTSCoverage:
    """Additional tests for YTS to improve coverage"""

    @pytest.mark.asyncio
    @patch("rtorrent_mcp.services.yts_search.aiohttp.ClientSession")
    async def test_yts_error_response(self, mock_session):
        """Test handling of non-200 HTTP response"""
        from rtorrent_mcp.services.yts_search import search_yts_movies

        mock_response = MagicMock()
        mock_response.status = 500

        mock_session_instance = MagicMock()
        mock_session_instance.__aenter__ = AsyncMock(return_value=mock_session_instance)
        mock_session_instance.__aexit__ = AsyncMock(return_value=None)
        mock_session_instance.get = AsyncMock(return_value=mock_response)
        mock_session.return_value = mock_session_instance

        results = await search_yts_movies("test")
        assert len(results) > 0
        assert "error" in results[0]

    @pytest.mark.asyncio
    @patch("rtorrent_mcp.services.yts_search.aiohttp.ClientSession")
    async def test_yts_api_error_status(self, mock_session):
        """Test handling of API error status"""
        from rtorrent_mcp.services.yts_search import search_yts_movies

        mock_json_response = {
            "status": "error",
            "status_message": "Invalid query",
        }

        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_json_response)

        mock_session_instance = MagicMock()
        mock_session_instance.__aenter__ = AsyncMock(return_value=mock_session_instance)
        mock_session_instance.__aexit__ = AsyncMock(return_value=None)
        mock_session_instance.get = AsyncMock(return_value=mock_response)
        mock_session.return_value = mock_session_instance

        results = await search_yts_movies("test")
        assert len(results) > 0
        assert "error" in results[0]

    @pytest.mark.asyncio
    @patch("rtorrent_mcp.services.yts_search.aiohttp.ClientSession")
    async def test_yts_no_preferred_quality(self, mock_session):
        """Test when preferred quality not available, uses all torrents"""
        from rtorrent_mcp.services.yts_search import search_yts_movies

        mock_json_response = {
            "status": "ok",
            "data": {
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
                                "quality": "720p",  # Different from requested 1080p
                                "size": "1.5 GB",
                                "seeds": 50,
                                "peers": 10,
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

        results = await search_yts_movies("test", quality="1080p")
        assert len(results) > 0
        assert results[0]["quality"] == "720p"  # Falls back to available quality

    @pytest.mark.asyncio
    @patch("rtorrent_mcp.services.yts_search.aiohttp.ClientSession")
    async def test_yts_construct_magnet_from_hash(self, mock_session):
        """Test constructing magnet link from hash when URL not provided"""
        from rtorrent_mcp.services.yts_search import search_yts_movies

        mock_json_response = {
            "status": "ok",
            "data": {
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
                                "hash": "testhash123456",
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

        results = await search_yts_movies("test")
        assert len(results) > 0
        assert results[0]["magnet"].startswith("magnet:")

    @pytest.mark.asyncio
    @patch("rtorrent_mcp.services.yts_search.aiohttp.ClientSession")
    async def test_yts_network_error(self, mock_session):
        """Test handling of network errors"""
        import aiohttp

        from rtorrent_mcp.services.yts_search import search_yts_movies

        mock_session_instance = MagicMock()
        mock_session_instance.__aenter__ = AsyncMock(return_value=mock_session_instance)
        mock_session_instance.__aexit__ = AsyncMock(return_value=None)
        mock_session_instance.get = AsyncMock(side_effect=aiohttp.ClientError("Network error"))
        mock_session.return_value = mock_session_instance

        results = await search_yts_movies("test")
        assert len(results) > 0
        assert "error" in results[0]


class TestMetadataServiceCoverage:
    """Additional tests for metadata service to improve coverage"""

    @pytest.mark.asyncio
    @patch("rtorrent_mcp.services.metadata_service.aiohttp.ClientSession")
    async def test_get_imdb_metadata_error_response(self, mock_session):
        """Test handling of non-200 HTTP response"""
        from rtorrent_mcp.services.metadata_service import get_imdb_metadata

        mock_response = MagicMock()
        mock_response.status = 500

        mock_session_instance = MagicMock()
        mock_session_instance.__aenter__ = AsyncMock(return_value=mock_session_instance)
        mock_session_instance.__aexit__ = AsyncMock(return_value=None)
        mock_session_instance.get = AsyncMock(return_value=mock_response)
        mock_session.return_value = mock_session_instance

        result = await get_imdb_metadata("test")
        assert "error" in result

    @pytest.mark.asyncio
    @patch("rtorrent_mcp.services.metadata_service.aiohttp.ClientSession")
    async def test_get_imdb_metadata_false_response(self, mock_session):
        """Test handling of False response from OMDb"""
        from rtorrent_mcp.services.metadata_service import get_imdb_metadata

        mock_json_response = {
            "Response": "False",
            "Error": "Movie not found!",
        }

        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_json_response)

        mock_session_instance = MagicMock()
        mock_session_instance.__aenter__ = AsyncMock(return_value=mock_session_instance)
        mock_session_instance.__aexit__ = AsyncMock(return_value=None)
        mock_session_instance.get = AsyncMock(return_value=mock_response)
        mock_session.return_value = mock_session_instance

        result = await get_imdb_metadata("nonexistent")
        assert "error" in result

    @pytest.mark.asyncio
    @patch("rtorrent_mcp.services.metadata_service.aiohttp.ClientSession")
    async def test_get_imdb_metadata_with_api_key(self, mock_session):
        """Test getting metadata with API key"""
        from rtorrent_mcp.services.metadata_service import get_imdb_metadata

        mock_json_response = {
            "Response": "True",
            "Title": "Test Movie",
            "Year": "2023",
            "imdbID": "tt1234567",
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

        result = await get_imdb_metadata("test", api_key="test_key")
        assert result["title"] == "Test Movie"

    @pytest.mark.asyncio
    @patch("rtorrent_mcp.services.metadata_service.aiohttp.ClientSession")
    async def test_search_imdb_error_response(self, mock_session):
        """Test search IMDb with error response"""
        from rtorrent_mcp.services.metadata_service import search_imdb

        mock_response = MagicMock()
        mock_response.status = 500

        mock_session_instance = MagicMock()
        mock_session_instance.__aenter__ = AsyncMock(return_value=mock_session_instance)
        mock_session_instance.__aexit__ = AsyncMock(return_value=None)
        mock_session_instance.get = AsyncMock(return_value=mock_response)
        mock_session.return_value = mock_session_instance

        results = await search_imdb("test")
        assert len(results) > 0
        assert "error" in results[0]

    @pytest.mark.asyncio
    @patch("rtorrent_mcp.services.metadata_service.aiohttp.ClientSession")
    async def test_search_imdb_false_response(self, mock_session):
        """Test search IMDb with False response"""
        from rtorrent_mcp.services.metadata_service import search_imdb

        mock_json_response = {
            "Response": "False",
            "Error": "Too many results.",
        }

        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_json_response)

        mock_session_instance = MagicMock()
        mock_session_instance.__aenter__ = AsyncMock(return_value=mock_session_instance)
        mock_session_instance.__aexit__ = AsyncMock(return_value=None)
        mock_session_instance.get = AsyncMock(return_value=mock_response)
        mock_session.return_value = mock_session_instance

        results = await search_imdb("test")
        assert len(results) > 0
        assert "error" in results[0]

    @pytest.mark.asyncio
    @patch("rtorrent_mcp.services.metadata_service.aiohttp.ClientSession")
    async def test_get_tvdb_metadata_auth_failure(self, mock_session):
        """Test TVDB metadata with authentication failure"""
        from rtorrent_mcp.services.metadata_service import get_tvdb_metadata

        mock_auth_response = MagicMock()
        mock_auth_response.status = 401
        mock_auth_response.json = AsyncMock(return_value={"error": "Invalid credentials"})

        mock_session_instance = MagicMock()
        mock_session_instance.__aenter__ = AsyncMock(return_value=mock_session_instance)
        mock_session_instance.__aexit__ = AsyncMock(return_value=None)
        mock_session_instance.post = AsyncMock(return_value=mock_auth_response)
        mock_session.return_value = mock_session_instance

        result = await get_tvdb_metadata("test", api_key="invalid", pin="invalid")
        assert "error" in result

    @pytest.mark.asyncio
    @patch("rtorrent_mcp.services.metadata_service.aiohttp.ClientSession")
    async def test_get_tvdb_metadata_no_token(self, mock_session):
        """Test TVDB metadata when token not returned"""
        from rtorrent_mcp.services.metadata_service import get_tvdb_metadata

        mock_auth_response = MagicMock()
        mock_auth_response.status = 200
        mock_auth_response.json = AsyncMock(return_value={"data": {}})  # No token

        mock_session_instance = MagicMock()
        mock_session_instance.__aenter__ = AsyncMock(return_value=mock_session_instance)
        mock_session_instance.__aexit__ = AsyncMock(return_value=None)
        mock_session_instance.post = AsyncMock(return_value=mock_auth_response)
        mock_session.return_value = mock_session_instance

        result = await get_tvdb_metadata("test", api_key="test", pin="test")
        assert "error" in result

    @pytest.mark.asyncio
    @patch("rtorrent_mcp.services.metadata_service.aiohttp.ClientSession")
    async def test_get_tvdb_metadata_network_error(self, mock_session):
        """Test TVDB metadata with network error"""
        import aiohttp

        from rtorrent_mcp.services.metadata_service import get_tvdb_metadata

        mock_session_instance = MagicMock()
        mock_session_instance.__aenter__ = AsyncMock(return_value=mock_session_instance)
        mock_session_instance.__aexit__ = AsyncMock(return_value=None)
        mock_session_instance.post = AsyncMock(side_effect=aiohttp.ClientError("Network error"))
        mock_session.return_value = mock_session_instance

        result = await get_tvdb_metadata("test", api_key="test", pin="test")
        assert "error" in result


class TestPostProcessorCoverage:
    """Additional tests for post-processor to improve coverage"""

    @pytest.mark.asyncio
    async def test_check_completed_downloads_no_client(self):
        """Test checking completed downloads without initialized client"""
        from rtorrent_mcp.services.post_processor import PostProcessor

        config = {
            "ingestion_anime_path": "/test/anime",
            "poll_interval": 60,
            "delete_torrent_after_complete": True,
            "normalize_filenames": True,
        }

        processor = PostProcessor(config)
        # Client not initialized, should initialize automatically
        with patch("rtorrent_mcp.services.post_processor.get_rtorrent_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.get_torrents = AsyncMock(return_value=[])
            mock_get_client.return_value = mock_client

            results = await processor.check_completed_downloads()
            assert isinstance(results, list)

    def test_normalize_filename_edge_cases(self):
        """Test filename normalization with edge cases"""
        from rtorrent_mcp.services.post_processor import PostProcessor

        config = {
            "ingestion_anime_path": "/test/anime",
            "poll_interval": 60,
            "delete_torrent_after_complete": True,
            "normalize_filenames": True,
        }

        processor = PostProcessor(config)

        # Test with no extension initially
        filename = "[ASW] Test File"
        normalized = processor.normalize_filename(filename, "anime")
        assert "[ASW]" not in normalized

        # Test with multiple dots
        filename = "Test..File....mkv"
        normalized = processor.normalize_filename(filename, "anime")
        assert normalized.count(".") <= 2  # Extension dot + one dot max

        # Test with leading/trailing dashes
        filename = "-Test-File-.mkv"
        normalized = processor.normalize_filename(filename, "anime")
        assert not normalized.startswith("-")
        assert not normalized.endswith("-")

    def test_get_ingestion_folder_edge_cases(self):
        """Test ingestion folder routing with edge cases"""
        from rtorrent_mcp.services.post_processor import PostProcessor

        # Test with missing config
        config = {
            "poll_interval": 60,
        }
        processor = PostProcessor(config)
        result = processor.get_ingestion_folder("anime", "test")
        assert result is None

        # Test with unknown category
        config = {
            "ingestion_anime_path": "/test/anime",
            "poll_interval": 60,
        }
        processor = PostProcessor(config)
        result = processor.get_ingestion_folder("unknown", "test")
        assert result is None
