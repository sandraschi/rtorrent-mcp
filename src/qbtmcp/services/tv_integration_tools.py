"""
tv_integration_tools.py - Comprehensive TV show integration tools
Combines The Pirate Bay search, NLP processing, and torrent client integration
"""

import json
import logging

logger = logging.getLogger(__name__)

def register_tv_integration_tools(mcp):
    """Register comprehensive TV integration tools with FastMCP server"""

    @mcp.tool(
        name="tv_show_manager",
        description="""
        Comprehensive TV show management tool for The Pirate Bay integration.

        This tool handles the complete workflow from natural language query to torrent download:
        1. Parse natural language TV show requests
        2. Search The Pirate Bay for episodes
        3. Filter for new episodes and quality preferences
        4. Provide download recommendations

        Example usage:
        - "get new Only Murders in the Building episodes from piratebay"
        - "find latest Slow Horses episodes"
        - "download House of the Dragon from MeGusta"

        Args:
            query (str): Natural language TV show query
            downloaded_episodes (list): List of already downloaded episodes
            auto_download (bool): Whether to automatically initiate downloads

        Returns:
            dict: Complete TV show management results with recommendations
        """
    )
    async def tv_show_manager(query: str, downloaded_episodes: list[str] = None, auto_download: bool = False) -> dict:
        """Comprehensive TV show management"""
        if downloaded_episodes is None:
            downloaded_episodes = []

        # Import here to avoid circular imports
        from .piratebay_search import is_new_episode, search_piratebay_tv
        from .tv_nlp_tools import TVShowNLPProcessor

        processor = TVShowNLPProcessor()

        # Parse the query
        parsed_query = processor.parse_tv_query(query)
        search_params = processor.generate_search_parameters(parsed_query)

        # Perform search
        search_results = await search_piratebay_tv(
            search_params["query"],
            search_params["resolution"],
            search_params["group"]
        )

        # Filter for new episodes
        new_episodes = []
        downloaded_set = set(downloaded_episodes)

        for result in search_results:
            if "error" not in result:
                if parsed_query["new_only"] and is_new_episode(result["title"], downloaded_set):
                    new_episodes.append(result)
                elif not parsed_query["new_only"]:
                    new_episodes.append(result)

        # Generate recommendations
        recommendations = []
        download_actions = []

        if parsed_query["confidence"] < 0.5:
            recommendations.append("Consider being more specific about the show name")

        if not search_results or all("error" in result for result in search_results):
            recommendations.append("Try different search terms or check spelling")

        if new_episodes:
            # Sort by quality score
            new_episodes.sort(key=lambda x: x["quality_score"], reverse=True)

            # Generate download recommendations
            for episode in new_episodes[:3]:  # Top 3 recommendations
                download_actions.append({
                    "title": episode["title"],
                    "magnet": episode["magnet"],
                    "quality_score": episode["quality_score"],
                    "seeders": episode["seeders"],
                    "size": episode["size"],
                    "recommended": episode["quality_score"] > 100
                })

            recommendations.append(f"Found {len(new_episodes)} episodes. Top recommendations provided.")

        # Generate summary
        summary = {
            "show_name": parsed_query["show_name"],
            "total_results": len(search_results),
            "new_episodes_count": len(new_episodes),
            "high_quality_count": len([e for e in new_episodes if e["quality_score"] > 100]),
            "megusta_count": len([e for e in new_episodes if "MeGusta" in e["release_group"]]),
            "confidence": parsed_query["confidence"]
        }

        return {
            "parsed_query": parsed_query,
            "search_results": search_results,
            "new_episodes": new_episodes,
            "recommendations": recommendations,
            "download_actions": download_actions,
            "summary": summary
        }

    @mcp.tool(
        name="episode_tracker",
        description="""
        Track TV show episodes and manage download history.

        This tool helps track which episodes have been downloaded and provides
        intelligent recommendations for new episodes.

        Args:
            show_name (str): Name of the TV show
            action (str): Action to perform (list, add, remove, check)
            episode (str): Episode identifier (for add/remove actions)

        Returns:
            dict: Episode tracking information and recommendations
        """
    )
    async def episode_tracker(show_name: str, action: str = "list", episode: str = None) -> dict:
        """Track TV show episodes"""
        # This would integrate with a persistent storage system
        # For now, we'll simulate episode tracking

        # Simulate downloaded episodes (in real implementation, this would be persistent)
        downloaded_episodes = [
            "S01E01", "S01E02", "S01E03",  # Example downloaded episodes
        ]

        if action == "add" and episode:
            if episode not in downloaded_episodes:
                downloaded_episodes.append(episode)
                status = f"Added {episode} to downloaded episodes"
            else:
                status = f"{episode} already in downloaded episodes"
        elif action == "remove" and episode:
            if episode in downloaded_episodes:
                downloaded_episodes.remove(episode)
                status = f"Removed {episode} from downloaded episodes"
            else:
                status = f"{episode} not found in downloaded episodes"
        elif action == "check" and episode:
            status = f"{episode} {'found' if episode in downloaded_episodes else 'not found'} in downloaded episodes"
        else:
            status = f"Listed {len(downloaded_episodes)} downloaded episodes"

        # Generate recommendations for missing episodes
        recommendations = []
        if action == "list":
            recommendations.append("Use 'tv_show_manager' to find new episodes")
            recommendations.append("Use 'add' action to mark episodes as downloaded")

        return {
            "show_name": show_name,
            "downloaded_episodes": downloaded_episodes,
            "missing_episodes": [],  # Would be calculated based on show metadata
            "recommendations": recommendations,
            "status": status
        }

    @mcp.resource("tv://integration/overview")
    def tv_integration_overview() -> str:
        """TV integration overview and capabilities"""
        return json.dumps({
            "description": "Comprehensive TV show management with The Pirate Bay integration",
            "capabilities": [
                "Natural language query processing",
                "The Pirate Bay search with MeGusta prioritization",
                "Episode tracking and new episode detection",
                "Quality scoring and recommendations",
                "Automated download management"
            ],
            "supported_commands": [
                "get new [show] episodes from piratebay",
                "find latest [show] episodes",
                "download [show] from MeGusta",
                "track episodes for [show]"
            ],
            "quality_features": [
                "MeGusta release group prioritization",
                "HEVC x265 codec preference",
                "File size optimization",
                "Seeder count consideration"
            ],
            "integration_points": [
                "The Pirate Bay search API",
                "Natural language processing",
                "Episode tracking system",
                "Torrent client integration"
            ]
        })
