"""
NLP tools for RTorrent MCP Server

MCP tools for natural language processing and command interpretation
"""

import logging

from fastmcp import FastMCP

from ..services.natural_language import get_command_examples, process_sandra_command

logger = logging.getLogger(__name__)


def register_nlp_tools(mcp: FastMCP, settings) -> None:
    """
    Register natural language processing tools with FastMCP server.

    Args:
        mcp: FastMCP server instance
        settings: Application settings
    """

    @mcp.tool(
        name="sandra_anime_command",
        description="Process Sandra's natural language anime commands. "
        "Interprets natural language commands for anime torrent operations. "
        "Supports both English and German commands with Austrian context. "
        "Examples: 'get me this weeks asw anime, 720p', 'lade detective conan asw 720p'. "
        "Args: command (str): Natural language command to process. "
        "Returns: dict with parsed command results and anime suggestions.",
    )
    async def sandra_anime_command(command: str) -> dict:
        """Process Sandra's natural language anime commands"""
        try:
            return await process_sandra_command(command)
        except Exception as e:
            logger.error(f"Error processing command '{command}': {e}")
            return {
                "command": command,
                "status": "Error processing command",
                "error": str(e),
                "suggestions": [
                    "Try: 'get me this weeks asw anime, 720p'",
                    "Or: 'lade detective conan asw 720p'",
                ],
            }

    @mcp.tool(
        name="parse_anime_command",
        description="Parse anime command and extract components without searching. "
        "Analyzes a natural language command and extracts anime name, "
        "resolution, and release group preferences without performing search. "
        "Args: command (str): Command to parse. "
        "Returns: dict with parsed command components.",
    )
    def parse_anime_command(command: str) -> dict:
        """Parse anime command and extract components without searching"""
        try:
            return {
                "original_command": command,
                "anime_name": extract_anime_name(command),
                "resolution": extract_resolution(command),
                "release_group": extract_release_group(command),
                "language": "german"
                if any(word in command.lower() for word in ["lade", "herunterladen"])
                else "english",
            }
        except Exception as e:
            logger.error(f"Error parsing command '{command}': {e}")
            return {"original_command": command, "error": f"Failed to parse command: {str(e)}"}

    @mcp.tool(
        name="get_command_help",
        description="Get help for Sandra's anime command patterns. "
        "Provides examples and supported parameters for natural language commands. "
        "Returns: dict with command help information, examples, and supported parameters.",
    )
    def get_command_help() -> dict:
        """Get help for Sandra's anime command patterns"""
        try:
            return {
                "examples": get_command_examples(),
                "supported_anime": [
                    "Detective Conan",
                    "One Piece",
                    "Spy x Family",
                    "Attack on Titan",
                    "Demon Slayer",
                    "Jujutsu Kaisen",
                ],
                "supported_groups": ["ASW", "SubsPlease", "Erai-raws", "EMBER", "Judas"],
                "supported_resolutions": ["720p", "1080p", "4K"],
                "languages": ["English", "German (Austrian context)"],
                "german_commands": "lade [anime] [group] [resolution]",
            }
        except Exception as e:
            logger.error(f"Error generating command help: {e}")
            return {
                "error": f"Failed to generate help: {str(e)}",
                "examples": {},
                "supported_anime": [],
                "supported_groups": [],
                "supported_resolutions": [],
                "languages": [],
            }

    # Import helper functions from service
    from ..services.natural_language import (
        extract_anime_name,
        extract_release_group,
        extract_resolution,
    )

    # Resource for command examples
    @mcp.resource("nlp://examples")
    def command_examples() -> str:
        """Natural language command examples"""
        try:
            import json

            return json.dumps(
                {
                    "sandra_patterns": get_command_examples(),
                    "austrian_context": True,
                    "german_support": True,
                    "benny_approved": "Woof! (Good commands!)",
                }
            )
        except Exception as e:
            logger.error(f"Error generating command examples: {e}")
            return json.dumps({"error": f"Failed to load examples: {str(e)}"})
