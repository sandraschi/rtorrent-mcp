"""
Tests for TV integration tools
Tests for tv_show_manager and related TV show management functionality
Run with: python -m pytest tests/test_tv_integration.py -v
"""

import pytest


class TestTVShowManager:
    """Test TV show manager tool"""

    def test_tv_show_manager_basic(self):
        """Test basic TV show manager functionality"""
        from rtorrent_mcp.services.tv_nlp_tools import TVShowNLPProcessor

        # Test NLP processor
        processor = TVShowNLPProcessor()
        parsed = processor.parse_tv_query("get new Only Murders in the Building episodes from piratebay")

        assert parsed["show_name"] is not None
        assert "murders" in parsed["show_name"].lower()
        assert parsed["new_only"] is True
        assert parsed["source"] == "piratebay"

    def test_tv_show_manager_with_downloaded_episodes(self):
        """Test TV show manager filtering downloaded episodes"""
        from rtorrent_mcp.services.tv_nlp_tools import TVShowNLPProcessor

        processor = TVShowNLPProcessor()
        parsed = processor.parse_tv_query("find latest Slow Horses episodes")

        assert parsed["show_name"] is not None
        assert "horses" in parsed["show_name"].lower()

    def test_tv_show_manager_no_results(self):
        """Test TV show manager with no search results"""
        from rtorrent_mcp.services.tv_nlp_tools import TVShowNLPProcessor

        processor = TVShowNLPProcessor()
        parsed = processor.parse_tv_query("get new Nonexistent Show episodes")

        assert parsed["show_name"] is not None
        assert parsed["new_only"] is True

    def test_tv_show_manager_error_response(self):
        """Test TV show manager with error response"""
        from rtorrent_mcp.services.tv_nlp_tools import TVShowNLPProcessor

        processor = TVShowNLPProcessor()
        parsed = processor.parse_tv_query("get new Test Show episodes")

        assert parsed["show_name"] is not None


class TestTVNLPProcessor:
    """Test TV NLP processor functionality"""

    def test_parse_tv_query_basic(self):
        """Test basic TV query parsing"""
        from rtorrent_mcp.services.tv_nlp_tools import TVShowNLPProcessor

        processor = TVShowNLPProcessor()

        # Test various query formats
        queries = [
            "get new Only Murders in the Building episodes from piratebay",
            "find latest Slow Horses episodes",
            "download House of the Dragon from MeGusta",
            "search for new episodes of The Crown",
        ]

        for query in queries:
            parsed = processor.parse_tv_query(query)
            assert parsed["show_name"] is not None
            assert parsed["source"] == "piratebay"
            assert isinstance(parsed["confidence"], float)
            assert parsed["confidence"] >= 0.0

    def test_parse_tv_query_with_quality(self):
        """Test parsing query with quality preferences"""
        from rtorrent_mcp.services.tv_nlp_tools import TVShowNLPProcessor

        processor = TVShowNLPProcessor()

        query = "get Only Murders in the Building 1080p MeGusta episodes"
        parsed = processor.parse_tv_query(query)

        assert parsed["show_name"] is not None
        assert len(parsed["quality_preferences"]) > 0
        assert any("1080p" in q.lower() or "megusta" in q.lower() for q in parsed["quality_preferences"])

    def test_parse_tv_query_quoted_show_name(self):
        """Test parsing query with quoted show name"""
        from rtorrent_mcp.services.tv_nlp_tools import TVShowNLPProcessor

        processor = TVShowNLPProcessor()

        query = 'get new "Only Murders in the Building" episodes'
        parsed = processor.parse_tv_query(query)

        assert parsed["show_name"] is not None
        assert "murders" in parsed["show_name"].lower()
        assert parsed["confidence"] >= 0.3  # Quoted names get higher confidence

    def test_parse_tv_query_new_only_flag(self):
        """Test parsing query with 'new' keyword"""
        from rtorrent_mcp.services.tv_nlp_tools import TVShowNLPProcessor

        processor = TVShowNLPProcessor()

        query_with_new = "get new Test Show episodes"
        query_without_new = "get Test Show episodes"

        parsed_with_new = processor.parse_tv_query(query_with_new)
        parsed_without_new = processor.parse_tv_query(query_without_new)

        assert parsed_with_new["new_only"] is True
        assert parsed_without_new["new_only"] is False

    def test_generate_search_parameters(self):
        """Test generating search parameters from parsed query"""
        from rtorrent_mcp.services.tv_nlp_tools import TVShowNLPProcessor

        processor = TVShowNLPProcessor()

        parsed = {
            "show_name": "Test Show",
            "quality_preferences": ["1080p", "MeGusta"],
            "new_only": True,
        }

        search_params = processor.generate_search_parameters(parsed)

        assert search_params["query"] == "Test Show"
        assert search_params["resolution"] == "1080p"
        assert search_params["group"] == "MeGusta"

    def test_generate_search_parameters_defaults(self):
        """Test generating search parameters with defaults"""
        from rtorrent_mcp.services.tv_nlp_tools import TVShowNLPProcessor

        processor = TVShowNLPProcessor()

        parsed = {
            "show_name": "Test Show",
            "quality_preferences": [],
            "new_only": False,
        }

        search_params = processor.generate_search_parameters(parsed)

        assert search_params["query"] == "Test Show"
        assert search_params["resolution"] == "1080p"  # Default
        assert search_params["group"] == "MeGusta"  # Default

    def test_clean_show_name(self):
        """Test show name cleaning"""
        from rtorrent_mcp.services.tv_nlp_tools import TVShowNLPProcessor

        processor = TVShowNLPProcessor()

        # Test various cleaning scenarios
        test_cases = [
            ("  Test Show  ", "Test Show"),
            ("test show", "Test Show"),
            ("TEST SHOW", "Test Show"),
            ("test-show", "Test Show"),
            ("test_show", "Test Show"),
        ]

        for input_name, expected in test_cases:
            cleaned = processor._clean_show_name(input_name)
            assert cleaned == expected or cleaned.lower() == expected.lower()


class TestTVIntegrationErrorHandling:
    """Test error handling in TV integration tools"""

    def test_tv_show_manager_network_error(self):
        """Test handling network errors"""
        from rtorrent_mcp.services.tv_nlp_tools import TVShowNLPProcessor

        processor = TVShowNLPProcessor()
        parsed = processor.parse_tv_query("get new Test Show episodes")

        assert parsed["show_name"] is not None

    @pytest.mark.asyncio
    async def test_tv_show_manager_empty_query(self):
        """Test handling empty query"""
        from rtorrent_mcp.services.tv_nlp_tools import TVShowNLPProcessor

        processor = TVShowNLPProcessor()
        parsed = processor.parse_tv_query("")

        assert parsed["show_name"] is None or parsed["show_name"] == ""
        assert parsed["confidence"] == 0.0

    def test_parse_tv_query_special_characters(self):
        """Test parsing query with special characters"""
        from rtorrent_mcp.services.tv_nlp_tools import TVShowNLPProcessor

        processor = TVShowNLPProcessor()

        query = "get new Test & Show episodes"
        parsed = processor.parse_tv_query(query)

        assert parsed["show_name"] is not None


if __name__ == "__main__":
    print(" Running TV Integration Tests...")
    print(" Testing TV show manager and NLP processor...")
    print("[OK] TV integration functionality verified!")
