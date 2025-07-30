"""
natural_language.py - Natural language processing for Sandra's anime commands
Austrian context with German language support
"""

import logging
from typing import Dict, Any
import re

from .nyaa_search import search_nyaa_anime
from . import DEFAULT_RESOLUTION, DEFAULT_RELEASE_GROUP

logger = logging.getLogger(__name__)

async def process_sandra_command(command: str) -> Dict[str, Any]:
    """Process Sandra's natural language anime commands
    
    Args:
        command: Natural language command like 'get me this weeks asw anime, 720p'
    
    Returns:
        Dictionary with command understanding and results
    """
    command_lower = command.lower()
    
    # Parse common Sandra patterns
    if "asw" in command_lower and "720p" in command_lower:
        if "this week" in command_lower or "latest" in command_lower or "recent" in command_lower:
            # Search for recent ASW releases
            results = await search_nyaa_anime("", "720p", "ASW")
            return {
                "command_understood": command,
                "action": "search_recent_asw_720p",
                "results": results[:3],
                "austrian_efficiency": True,
                "benny_approved": "🐕 Woof! (Good anime choice!)"
            }
    
    # Detective Conan specific (Sandra's favorite)
    if "detective conan" in command_lower or "conan" in command_lower:
        resolution = extract_resolution(command_lower) or "720p"
        group = extract_release_group(command_lower) or "ASW"
        results = await search_nyaa_anime("Detective Conan", resolution, group)
        return {
            "command_understood": command,
            "action": "search_detective_conan",
            "results": results[:2],
            "benny_approved": "🐕 Woof! (Detective Conan is the best!)",
            "sandra_favorite": True
        }
    
    # German language commands (Austrian context)
    if any(german_word in command_lower for german_word in ["lade", "herunterladen", "anime", "folge"]):
        return await process_german_command(command_lower)
    
    # General anime search pattern
    anime_name = extract_anime_name(command)
    if anime_name:
        resolution = extract_resolution(command_lower) or DEFAULT_RESOLUTION
        group = extract_release_group(command_lower) or DEFAULT_RELEASE_GROUP
        results = await search_nyaa_anime(anime_name, resolution, group)
        return {
            "command_understood": command,
            "action": f"search_{anime_name.lower().replace(' ', '_')}",
            "anime": anime_name,
            "resolution": resolution,
            "group": group,
            "results": results[:3]
        }
    
    # Fallback with suggestions
    return {
        "command": command,
        "status": "🚧 Natural language processing needs refinement",
        "understood": False,
        "suggestions": [
            "Try: 'asw detective conan 720p'",
            "Or: 'get me this weeks asw anime'",
            "Or: 'search one piece 1080p subsplease'",
            "German: 'lade detective conan asw 720p'"
        ],
        "examples": get_command_examples()
    }

async def process_german_command(command: str) -> Dict[str, Any]:
    """Process German language commands (Austrian context)"""
    
    # "lade detective conan asw 720p" → Download Detective Conan ASW 720p
    if "lade" in command:
        anime_name = extract_anime_name(command)
        resolution = extract_resolution(command) or "720p"
        group = extract_release_group(command) or "ASW"
        
        if anime_name:
            results = await search_nyaa_anime(anime_name, resolution, group)
            return {
                "command_understood": command,
                "language": "german",
                "action": "german_download_request",
                "anime": anime_name,
                "results": results[:2],
                "austrian_context": True,
                "german_efficiency": "Sehr gut! 🇦🇹"
            }
    
    return {
        "command": command,
        "language": "german",
        "status": "German command not understood",
        "suggestion": "Try: 'lade detective conan asw 720p'"
    }

def extract_anime_name(command: str) -> str:
    """Extract anime name from command"""
    # Common anime detection patterns
    anime_patterns = [
        r"detective conan",
        r"one piece",
        r"spy x family", 
        r"attack on titan",
        r"demon slayer",
        r"jujutsu kaisen",
        r"my hero academia",
        r"dragon ball"
    ]
    
    command_lower = command.lower()
    for pattern in anime_patterns:
        if re.search(pattern, command_lower):
            return pattern.replace(" ", " ").title()
    
    # Try to extract quoted anime names
    quoted_match = re.search(r'"([^"]+)"', command)
    if quoted_match:
        return quoted_match.group(1)
    
    # Try to extract anime names between common words
    anime_match = re.search(r'\b(?:search|get|download|lade)\s+([a-zA-Z\s]+?)\s+(?:asw|subsplease|720p|1080p)', command_lower)
    if anime_match:
        return anime_match.group(1).strip().title()
    
    return ""

def extract_resolution(command: str) -> str:
    """Extract video resolution from command"""
    resolutions = ["480p", "720p", "1080p", "4k", "2160p"]
    command_lower = command.lower()
    
    for res in resolutions:
        if res in command_lower:
            return res
    
    return ""

def extract_release_group(command: str) -> str:
    """Extract release group from command"""
    groups = ["asw", "subsplease", "erai-raws", "ember", "judas", "horriblesubs"]
    command_lower = command.lower()
    
    for group in groups:
        if group.replace("-", "") in command_lower.replace("-", ""):
            return group.upper() if group == "asw" else group.title()
    
    return ""

def get_command_examples() -> Dict[str, str]:
    """Get examples of Sandra's anime commands"""
    return {
        "recent_asw": "get me this weeks asw anime, 720p",
        "specific_anime": "asw detective conan latest episode",
        "with_resolution": "spy x family 1080p asw",
        "german": "lade detective conan asw 720p",
        "search_pattern": "search one piece subsplease 720p"
    }

def register_nlp_tools(mcp):
    """Register natural language processing tools with FastMCP server"""
    
    @mcp.tool()
    async def sandra_anime_command(command: str) -> dict:
        """Process Sandra's natural language anime commands
        
        Args:
            command: Natural language command like 'get me this weeks asw anime, 720p'
        """
        return await process_sandra_command(command)
    
    @mcp.tool()
    def parse_anime_command(command: str) -> dict:
        """Parse anime command and extract components without searching
        
        Args:
            command: Command to parse
        """
        return {
            "original_command": command,
            "anime_name": extract_anime_name(command),
            "resolution": extract_resolution(command),
            "release_group": extract_release_group(command),
            "language": "german" if any(word in command.lower() for word in ["lade", "herunterladen"]) else "english"
        }
    
    @mcp.tool()
    def get_command_help() -> dict:
        """Get help for Sandra's anime command patterns"""
        return {
            "examples": get_command_examples(),
            "supported_anime": [
                "Detective Conan", "One Piece", "Spy x Family",
                "Attack on Titan", "Demon Slayer", "Jujutsu Kaisen"
            ],
            "supported_groups": ["ASW", "SubsPlease", "Erai-raws", "EMBER"],
            "supported_resolutions": ["720p", "1080p", "4K"],
            "languages": ["English", "German (Austrian context)"],
            "german_commands": ["lade [anime] [group] [resolution]"]
        }
    
    @mcp.resource("nlp://examples")
    def command_examples() -> str:
        """Natural language command examples"""
        import json
        return json.dumps({
            "sandra_patterns": get_command_examples(),
            "austrian_context": True,
            "german_support": True,
            "benny_approved": "🐕 Woof! (Good commands!)"
        })
