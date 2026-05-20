"""
NLP Management Portmanteau Tool

Consolidates all natural language processing operations for anime commands.
Supports English and German command parsing for Austrian users.
"""

import logging
from typing import Any, Literal

from fastmcp import FastMCP

from ...services.natural_language import (
    extract_anime_name,
    extract_release_group,
    extract_resolution,
    process_sandra_command,
)

logger = logging.getLogger(__name__)

NLP_ACTIONS = {
    "command": "Execute a natural language anime command (EN/DE)",
    "parse": "Parse command without executing (preview mode)",
    "help": "Get command syntax help and examples",
}


def register_nlp_management_tool(mcp: FastMCP, settings) -> None:
    """Register the NLP management portmanteau tool."""

    @mcp.tool()
    async def nlp_management(
        action: Literal["command", "parse", "help"],
        text: str | None = None,
        language: str = "auto",
    ) -> dict[str, Any]:
        """
        Comprehensive NLP management portmanteau tool for natural language anime commands.

        PORTMANTEAU PATTERN RATIONALE:
        Instead of creating 3+ separate tools (one per operation), this tool consolidates related
        NLP operations into a single interface. Prevents tool explosion (3 tools → 1 tool) while maintaining
        full functionality and improving discoverability. Follows FastMCP 2.12+ best practices.

        LANGUAGE SUPPORT:
        - English: "get me this weeks asw anime, 720p"
        - German: "lade detective conan asw 720p"
        - Auto-detection enabled by default

        COMMAND PATTERNS:
        - "[get/download/lade] [anime name] [group] [resolution]"
        - "asw [anime name] [resolution]"
        - "this weeks anime [group] [resolution]"

        Args:
            action (Literal, required): The NLP operation to perform. Must be one of:
                - "command": Execute natural language command (requires: text)
                - "parse": Parse command without execution (requires: text)
                - "help": Get command help and examples (no params required)

            text (str | None): Natural language command text.
                Required for: command, parse
                Examples:
                    - "get me this weeks asw anime, 720p"
                    - "lade detective conan asw 720p"
                    - "download one piece subsplease 1080p"

            language (str): Language hint for parsing.
                Default: "auto" (auto-detect). Valid: "auto", "en", "de"

        Returns:
            dict[str, Any]: Dictionary containing:
                - success (bool): Boolean indicating if operation succeeded
                - action (str): The action that was performed
                - data (dict): Parsed command data or execution results
                - error (str | None): Error message if success is False

        Examples:
            # Execute English command
            result = await nlp_management(action="command", text="get me detective conan asw 720p")

            # Execute German command
            result = await nlp_management(action="command", text="lade one piece 1080p", language="de")

            # Parse without execution (preview mode)
            result = await nlp_management(action="parse", text="asw attack on titan 1080p")

            # Get help
            result = await nlp_management(action="help")
        """
        try:
            if action not in NLP_ACTIONS:
                return {
                    "success": False,
                    "action": action,
                    "error": f"Invalid action '{action}'. Available: {list(NLP_ACTIONS.keys())}",
                }

            logger.info(f"Executing NLP action: {action}")

            if action == "command":
                if not text:
                    return {
                        "success": False,
                        "action": action,
                        "error": "text is required for 'command' action",
                    }
                result = await process_sandra_command(text)
                return {"success": True, "action": action, "data": result}

            if action == "parse":
                if not text:
                    return {
                        "success": False,
                        "action": action,
                        "error": "text is required for 'parse' action",
                    }
                parsed = {
                    "original_command": text,
                    "anime_name": extract_anime_name(text),
                    "resolution": extract_resolution(text),
                    "release_group": extract_release_group(text),
                    "language": ("german" if any(w in text.lower() for w in ("lade", "herunterladen")) else "english"),
                }
                return {"success": True, "action": action, "data": parsed}

            if action == "help":
                return {
                    "success": True,
                    "action": action,
                    "data": {
                        "description": "Natural language anime command processor for Sandra in Vienna (AT)",
                        "languages": ["English", "German (Deutsch)"],
                        "command_patterns": [
                            "[get/download] [anime name] [group] [resolution]",
                            "[lade/hole] [anime name] [gruppe] [auflösung]",
                            "asw [anime name] [resolution]",
                            "this weeks anime [group]",
                        ],
                        "examples": {
                            "english": [
                                "get me detective conan asw 720p",
                                "download one piece subsplease 1080p",
                                "this weeks asw anime",
                            ],
                            "german": [
                                "lade detective conan asw 720p",
                                "hole one piece erai-raws 1080p",
                            ],
                        },
                        "release_groups": {
                            "ASW": "100pts - Austrian preference (AT)",
                            "SubsPlease": "90pts - Fast releases",
                            "Erai-raws": "85pts - Multi-language",
                            "EMBER": "80pts - Quality encodes",
                            "Judas": "75pts - Consistent releases",
                        },
                        "resolutions": ["480p", "720p", "1080p", "2160p"],
                        "default_resolution": "720p",
                        "default_group": "ASW",
                    },
                }

            return {
                "success": False,
                "action": action,
                "error": f"Action '{action}' not implemented",
            }

        except Exception as e:
            logger.error(f"Error in NLP action '{action}': {e}", exc_info=True)
            return {"success": False, "action": action, "error": f"NLP processing failed: {e!s}"}
