"""
tv_nlp_tools.py - Natural Language Processing for TV show queries
Handles natural language commands like "get new Only Murders in the Building episodes from piratebay"
"""

import json
import logging
import re
from typing import Any

logger = logging.getLogger(__name__)


class TVShowNLPProcessor:
    """Natural Language Processor for TV show queries"""

    def __init__(self):
        self.action_patterns = [
            r"get\s+(?:new\s+)?(.+?)\s+episodes?\s+(?:from\s+)?(?:piratebay|the\s*pirate\s*bay)",
            r"find\s+(?:new\s+)?(.+?)\s+episodes?\s+(?:from\s+)?(?:piratebay|the\s*pirate\s*bay)",
            r"download\s+(?:new\s+)?(.+?)\s+episodes?\s+(?:from\s+)?(?:piratebay|the\s*pirate\s*bay)",
            r"search\s+for\s+(?:new\s+)?(.+?)\s+episodes?\s+(?:from\s+)?(?:piratebay|the\s*pirate\s*bay)",
            r"get\s+(?:new\s+)?(.+?)\s+from\s+(?:piratebay|the\s*pirate\s*bay)",
            r"find\s+(?:new\s+)?(.+?)\s+from\s+(?:piratebay|the\s*pirate\s*bay)",
            r"download\s+(?:new\s+)?(.+?)\s+from\s+(?:piratebay|the\s*pirate\s*bay)",
            r"find\s+(?:latest\s+)?(.+?)\s+episodes?",
            r"get\s+(?:latest\s+)?(.+?)\s+episodes?",
            r"download\s+(?:latest\s+)?(.+?)\s+episodes?",
        ]

        self.quality_patterns = [
            r"(?:megusta|me\s*gusta)",
            r"(?:1080p|720p|4k|2160p)",
            r"(?:hevc|x265|h\.?265)",
            r"(?:hdtv|webrip|bluray|dvdrip)",
        ]

        self.show_name_patterns = [
            r"(.+?)\s+(?:season|s\d+)",
            r"(.+?)\s+(?:episode|e\d+)",
            r"(.+?)\s+(?:episodes?)",
        ]

    def parse_tv_query(self, query: str) -> dict[str, Any]:
        """Parse natural language TV show query"""
        query_lower = query.lower().strip()

        result = {
            "show_name": None,
            "action": "search",
            "source": "piratebay",
            "new_only": False,
            "quality_preferences": [],
            "raw_query": query,
            "confidence": 0.0,
        }

        # Extract action and show name
        for pattern in self.action_patterns:
            match = re.search(pattern, query_lower, re.IGNORECASE)
            if match:
                result["confidence"] += 0.4
                result["show_name"] = self._clean_show_name(match.group(1))
                break

        # Check for "new" keyword
        if "new" in query_lower:
            result["new_only"] = True
            result["confidence"] += 0.2

        # Extract quality preferences
        quality_matches = []
        for pattern in self.quality_patterns:
            matches = re.findall(pattern, query_lower, re.IGNORECASE)
            quality_matches.extend(matches)

        if quality_matches:
            result["quality_preferences"] = quality_matches
            result["confidence"] += 0.2

        # Extract show name using additional patterns if not found
        if not result["show_name"]:
            for pattern in self.show_name_patterns:
                match = re.search(pattern, query_lower, re.IGNORECASE)
                if match:
                    result["show_name"] = self._clean_show_name(match.group(1))
                    result["confidence"] += 0.1
                    break

        # Fallback: try to extract show name from quoted text
        if not result["show_name"]:
            quoted_match = re.search(r'"([^"]+)"', query)
            if quoted_match:
                result["show_name"] = self._clean_show_name(quoted_match.group(1))
                result["confidence"] += 0.3

        return result

    def _clean_show_name(self, name: str) -> str:
        """Clean and normalize show name"""
        # Remove common words that might interfere with search
        stop_words = [
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
        ]

        # Split and clean
        words = name.strip().split()
        cleaned_words = []

        for word in words:
            word = word.strip(".,!?;:'\"()[]{}")
            if word.lower() not in stop_words or len(cleaned_words) == 0:
                cleaned_words.append(word)

        return " ".join(cleaned_words)

    def extract_episode_tracking_info(self, query: str) -> dict[str, Any]:
        """Extract episode tracking information from query"""
        query_lower = query.lower()

        tracking_info = {
            "track_episodes": False,
            "season_specific": None,
            "episode_specific": None,
            "latest_only": False,
        }

        # Check for season-specific requests
        season_match = re.search(r"season\s*(\d+)", query_lower)
        if season_match:
            tracking_info["season_specific"] = int(season_match.group(1))
            tracking_info["track_episodes"] = True

        # Check for episode-specific requests
        episode_match = re.search(r"episode\s*(\d+)", query_lower)
        if episode_match:
            tracking_info["episode_specific"] = int(episode_match.group(1))
            tracking_info["track_episodes"] = True

        # Check for "latest" keyword
        if "latest" in query_lower:
            tracking_info["latest_only"] = True
            tracking_info["track_episodes"] = True

        return tracking_info

    def generate_search_parameters(self, parsed_query: dict[str, Any]) -> dict[str, Any]:
        """Generate search parameters from parsed query"""
        params = {"query": parsed_query["show_name"], "resolution": "1080p", "group": "MeGusta"}

        # Adjust parameters based on quality preferences
        quality_prefs = parsed_query.get("quality_preferences", [])

        for pref in quality_prefs:
            pref_lower = pref.lower()
            if pref_lower in ["1080p", "720p", "4k", "2160p"]:
                params["resolution"] = pref_lower
            elif pref_lower in ["megusta", "me gusta"]:
                params["group"] = "MeGusta"
            elif pref_lower in ["rarbg", "eztv", "yify", "yts"]:
                params["group"] = pref_lower.upper()

        return params


def register_tv_nlp_tools(mcp):
    """Register TV NLP tools with FastMCP server"""

    processor = TVShowNLPProcessor()

    @mcp.tool(
        name="parse_tv_query",
        description="""
        Parse natural language TV show queries for The Pirate Bay search.

        This tool understands natural language commands like:
        - "get new Only Murders in the Building episodes from piratebay"
        - "find latest Slow Horses episodes"
        - "download new House of the Dragon from MeGusta"

        Args:
            query (str): Natural language query about TV shows

        Returns:
            dict: Parsed query with show name, preferences, and search parameters
        """,
    )
    async def parse_tv_query(query: str) -> dict:
        parsed = processor.parse_tv_query(query)
        parsed["search_parameters"] = processor.generate_search_parameters(parsed)
        return parsed

    @mcp.tool(
        name="smart_tv_search",
        description="""
        Smart TV show search using natural language processing.

        This tool combines natural language parsing with The Pirate Bay search
        to provide intelligent TV show discovery.

        Args:
            query (str): Natural language query about TV shows
            downloaded_episodes (list): List of already downloaded episodes

        Returns:
            dict: Search results with parsed query information
        """,
    )
    async def smart_tv_search(query: str, downloaded_episodes: list[str] = None) -> dict:
        if downloaded_episodes is None:
            downloaded_episodes = []

        # Parse the query
        parsed_query = processor.parse_tv_query(query)
        search_params = processor.generate_search_parameters(parsed_query)

        # Import here to avoid circular imports
        from .piratebay_search import is_new_episode, search_piratebay_tv

        # Perform search
        search_results = await search_piratebay_tv(
            search_params["query"], search_params["resolution"], search_params["group"]
        )

        # Filter for new episodes if requested
        new_episodes = []
        if parsed_query["new_only"]:
            downloaded_set = set(downloaded_episodes)
            for result in search_results:
                if "error" not in result and is_new_episode(result["title"], downloaded_set):
                    new_episodes.append(result)

        # Generate recommendations
        recommendations = []
        if parsed_query["confidence"] < 0.5:
            recommendations.append("Consider being more specific about the show name")

        if not search_results or all("error" in result for result in search_results):
            recommendations.append("Try different search terms or check spelling")

        return {
            "parsed_query": parsed_query,
            "search_results": search_results,
            "new_episodes": new_episodes,
            "recommendations": recommendations,
        }

    @mcp.resource("nlp://tv/patterns")
    def tv_nlp_patterns() -> str:
        """TV NLP patterns and examples"""
        return json.dumps(
            {
                "description": "Natural Language Processing for TV show queries",
                "supported_patterns": [
                    "get new [show] episodes from piratebay",
                    "find latest [show] episodes",
                    "download [show] from MeGusta",
                    "search for [show] episodes",
                ],
                "quality_keywords": ["megusta", "1080p", "720p", "4k", "hevc", "x265"],
                "examples": [
                    "get new Only Murders in the Building episodes from piratebay",
                    "find latest Slow Horses episodes",
                    "download House of the Dragon from MeGusta",
                ],
            }
        )
