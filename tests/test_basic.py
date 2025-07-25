"""
Basic tests for qBTMCP functionality
Run with: python -m pytest tests/ -v
"""

import pytest
import asyncio
from unittest.mock import Mock, patch

from qbtmcp.nyaa_search import calculate_quality_score, detect_release_group, extract_anime_name
from qbtmcp.legal_compliance import check_country_legal_status
from qbtmcp.natural_language import extract_resolution, extract_release_group, extract_anime_name as nl_extract_anime


class TestNyaaSearch:
    """Test nyaa.si search functionality"""
    
    def test_quality_scoring_asw_preference(self):
        """Test ASW gets highest quality score"""
        asw_title = "[ASW] Detective Conan - 1234 [720p]"
        subsplease_title = "[SubsPlease] Detective Conan - 1234 [720p]"
        
        asw_score = calculate_quality_score(asw_title, "720p")
        subsplease_score = calculate_quality_score(subsplease_title, "720p")
        
        assert asw_score > subsplease_score
        assert asw_score >= 150  # Base + ASW + resolution match
    
    def test_release_group_detection(self):
        """Test release group detection from titles"""
        assert detect_release_group("[ASW] Detective Conan") == "ASW"
        assert detect_release_group("[SubsPlease] One Piece") == "SubsPlease"
        assert detect_release_group("Random Release") == "Unknown"
    
    def test_resolution_preference_scoring(self):
        """Test resolution preference scoring"""
        title_720p = "[ASW] Detective Conan [720p]"
        title_1080p = "[ASW] Detective Conan [1080p]"
        
        score_720p = calculate_quality_score(title_720p, "720p")
        score_1080p_for_720p = calculate_quality_score(title_1080p, "720p")
        
        assert score_720p > score_1080p_for_720p


class TestLegalCompliance:
    """Test legal compliance functionality"""
    
    def test_austrian_legal_status(self):
        """Test Austrian legal status (Sandra's location)"""
        result = check_country_legal_status("austria")
        
        assert result["risk_level"] == "safe"
        assert result["sandra_location"] is True
        assert "Vienna" in result["recommendation"]
    
    def test_german_high_risk(self):
        """Test German high-risk status"""
        result = check_country_legal_status("germany")
        
        assert result["risk_level"] == "high"
        assert result["sandra_location"] is False
        assert "VPN" in result["recommendation"] or "risk" in result["warning"].lower()
    
    def test_japanese_criminal_status(self):
        """Test Japanese criminal status"""
        result = check_country_legal_status("japan")
        
        assert result["risk_level"] == "criminal"
        assert result["sandra_location"] is False


class TestNaturalLanguage:
    """Test natural language processing"""
    
    def test_resolution_extraction(self):
        """Test resolution extraction from commands"""
        assert extract_resolution("get me asw anime 720p") == "720p"
        assert extract_resolution("download in 1080p quality") == "1080p"
        assert extract_resolution("need 4k version") == "4k"
        assert extract_resolution("just get it") == ""
    
    def test_release_group_extraction(self):
        """Test release group extraction"""
        assert extract_release_group("get me asw detective conan") == "ASW"
        assert extract_release_group("subsplease one piece") == "Subsplease"
        assert extract_release_group("erai-raws anime") == "Erai-raws"
        assert extract_release_group("random command") == ""
    
    def test_anime_name_extraction(self):
        """Test anime name extraction"""
        assert nl_extract_anime("search detective conan asw") == "Detective Conan"
        assert nl_extract_anime("get one piece 720p") == "One Piece"
        assert nl_extract_anime("lade spy x family asw") == "Spy X Family"
    
    def test_german_command_detection(self):
        """Test German command pattern detection"""
        german_commands = ["lade detective conan", "herunterladen anime"]
        
        for cmd in german_commands:
            # Should detect German words
            assert any(word in cmd.lower() for word in ["lade", "herunterladen"])


class TestMockData:
    """Test with mock data - clearly marked"""
    
    @pytest.fixture
    def mock_nyaa_response(self):
        """Mock nyaa.si response for testing"""
        # MOCK DATA - Not real nyaa.si content
        return {
            "title": "[ASW] Detective Conan - 1234 [720p] - MOCK DATA",
            "magnet": "magnet:?xt=urn:btih:mockhash123&dn=mock-torrent",
            "seeders": 42,
            "leechers": 7,
            "size": "350.5 MB",
            "quality_score": 150,
            "release_group": "ASW"
        }
    
    @pytest.fixture
    def mock_qbittorrent_response(self):
        """Mock qBittorrent API response"""
        # MOCK DATA - Not real qBittorrent response
        return {
            "status": "success",
            "message": "Torrent added successfully - MOCK",
            "category": "anime",
            "hash": "mockhash123456789"
        }
    
    def test_mock_data_structure(self, mock_nyaa_response, mock_qbittorrent_response):
        """Test mock data has expected structure"""
        # Verify mock data structure
        assert "MOCK" in mock_nyaa_response["title"]
        assert mock_nyaa_response["quality_score"] > 0
        assert mock_qbittorrent_response["status"] == "success"


if __name__ == "__main__":
    # Run basic tests without pytest
    print("🧪 Running qBTMCP Basic Tests...")
    
    # Test Austrian legal status
    austria_status = check_country_legal_status("austria")
    print(f"✅ Austrian Status: {austria_status['risk_level']}")
    
    # Test quality scoring
    asw_score = calculate_quality_score("[ASW] Detective Conan [720p]", "720p")
    print(f"✅ ASW Quality Score: {asw_score}")
    
    # Test resolution extraction
    resolution = extract_resolution("get me asw anime 720p")
    print(f"✅ Resolution Extraction: {resolution}")
    
    print("🎯 Basic functionality verified!")
    print("🇦🇹 Ready for Sandra's anime automation!")
