# pyright: reportUnusedFunction=false
"""
Legal Management Portmanteau Tool

Consolidates all Austrian legal compliance operations for torrent activities.
Designed specifically for Sandra in Vienna with Austrian copyright law context.
"""

import logging
from typing import Any, Literal

from fastmcp import FastMCP

from ...services.legal_compliance import (
    check_country_legal_status,
)

logger = logging.getLogger(__name__)

LEGAL_ACTIONS = {
    "risk": "Assess legal risk for a torrent/content",
    "check": "Check Austrian legal status for content type",
    "advice": "Get legal advice for specific country/activity",
    "status": "Get current legal compliance status",
}


def register_legal_management_tool(mcp: FastMCP, settings) -> None:
    """Register the legal management portmanteau tool."""

    @mcp.tool()
    async def legal_management(
        action: Literal["risk", "check", "advice", "status"],
        content_type: str | None = None,
        torrent_info: dict | None = None,
        country: str = "austria",
        activity: str = "personal_download",
    ) -> dict[str, Any]:
        """
        Comprehensive legal management portmanteau tool for Austrian copyright compliance.

        PORTMANTEAU PATTERN RATIONALE:
        Instead of creating 4+ separate tools (one per operation), this tool consolidates related
        legal compliance operations into a single interface. Prevents tool explosion (4 tools → 1 tool)
        while maintaining full functionality and improving discoverability. Follows FastMCP 2.12+ best practices.

        AUSTRIAN LEGAL CONTEXT (AT):
        - Sandra's Location: Vienna, 9th district
        - Personal downloading: Generally tolerated in Austria
        - Anime content: Low risk for personal consumption
        - Commercial use: NOT supported (high risk)
        - Germany/Japan: High risk, VPN mandatory

        RISK LEVELS:
        - LOW: Safe for personal use (anime, manga for personal library)
        - MEDIUM: Caution advised (newly released content)
        - HIGH: VPN recommended (commercial content, high-profile releases)
        - CRITICAL: Not recommended (recent theatrical releases, games)

        Args:
            action (Literal, required): The legal operation to perform. Must be one of:
                - "risk": Assess legal risk for content (optional: torrent_info, content_type)
                - "check": Check if content type is legal in Austria (requires: content_type)
                - "advice": Get legal advice for activity/country (optional: country, activity)
                - "status": Get current legal status overview (no params required)

            content_type (str | None): Type of content being assessed.
                Required for: check. Optional for: risk
                Valid: "anime", "manga", "movies", "tv", "ebooks", "software", "games"

            torrent_info (dict | None): Torrent details for risk assessment.
                Optional for: risk
                Should include: name, size, category, seeders

            country (str): Country for legal assessment.
                Default: "austria". Valid: "austria", "germany", "japan", "usa", etc.

            activity (str): Activity type for legal advice.
                Default: "personal_download"
                Valid: "personal_download", "seeding", "sharing", "commercial"

        Returns:
            dict[str, Any]: Dictionary containing:
                - success (bool): Boolean indicating if operation succeeded
                - action (str): The action that was performed
                - data (dict): Legal assessment results
                - risk_level (str): Risk level (for risk/check actions)
                - error (str | None): Error message if success is False

        Examples:
            # Assess risk for a torrent
            result = await legal_management(
                action="risk",
                torrent_info={"name": "Detective Conan", "category": "anime"},
            )

            # Check if anime is legal in Austria
            result = await legal_management(action="check", content_type="anime")

            # Get legal advice for Germany (high risk!)
            result = await legal_management(action="advice", country="germany", activity="personal_download")

            # Get overall legal status
            result = await legal_management(action="status")
        """
        try:
            if action not in LEGAL_ACTIONS:
                return {
                    "success": False,
                    "action": action,
                    "error": f"Invalid action '{action}'. Available: {list(LEGAL_ACTIONS.keys())}",
                }

            logger.info(f"Executing legal action: {action}")

            if action == "risk":
                # Assess legal risk based on content type and torrent info
                risk_assessment = {
                    "content_type": content_type or "unknown",
                    "torrent_info": torrent_info,
                    "risk_level": "LOW" if content_type in ["anime", "manga"] else "MEDIUM",
                    "austrian_context": True,
                    "recommendation": "Safe for personal use in Austria (AT)"
                    if content_type in ["anime", "manga", "ebooks"]
                    else "Use caution",
                }
                return {
                    "success": True,
                    "action": action,
                    "data": risk_assessment,
                    "risk_level": risk_assessment["risk_level"],
                }

            if action == "check":
                if not content_type:
                    return {
                        "success": False,
                        "action": action,
                        "error": "content_type is required for 'check' action",
                    }
                # Check legal status for specified country
                result = check_country_legal_status(country)
                content_risk = {
                    "anime": "LOW",
                    "manga": "LOW",
                    "movies": "MEDIUM",
                    "tv": "MEDIUM",
                    "ebooks": "LOW",
                    "software": "HIGH",
                    "games": "HIGH",
                }.get(content_type, "MEDIUM")
                result["content_type"] = content_type
                result["content_risk"] = content_risk
                return {
                    "success": True,
                    "action": action,
                    "data": result,
                    "risk_level": content_risk,
                }

            if action == "advice":
                result = check_country_legal_status(country)
                result["activity"] = activity
                result["advice"] = f"For {activity} in {country}: {result.get('recommendation', 'Check local laws')}"
                return {
                    "success": True,
                    "action": action,
                    "data": result,
                    "risk_level": result.get("risk_level", "unknown"),
                }

            if action == "status":
                return {
                    "success": True,
                    "action": action,
                    "data": {
                        "user_location": "Vienna, Austria (AT)",
                        "overall_status": "SAFE for personal anime consumption",
                        "legal_context": {
                            "austria": {
                                "risk": "LOW",
                                "status": "Personal downloading generally tolerated",
                                "vpn_required": False,
                                "recommendation": "Safe for anime, manga, ebooks",
                            },
                            "germany": {
                                "risk": "HIGH",
                                "status": "Strict enforcement, VPN mandatory",
                                "vpn_required": True,
                                "recommendation": "Use VPN, avoid German servers",
                            },
                            "japan": {
                                "risk": "HIGH",
                                "status": "Copyright strictly enforced",
                                "vpn_required": True,
                                "recommendation": "Legal streaming preferred",
                            },
                        },
                        "allowed_categories": settings.ALLOWED_CATEGORIES
                        if hasattr(settings, "ALLOWED_CATEGORIES")
                        else ["Anime"],
                        "max_torrent_size_gb": getattr(settings, "MAX_TORRENT_SIZE_GB", 10),
                        "disclaimer": "This tool provides general guidance only. Not legal advice.",
                    },
                }

            return {
                "success": False,
                "action": action,
                "error": f"Action '{action}' not implemented",
            }

        except Exception as e:
            logger.error(f"Error in legal action '{action}': {e}", exc_info=True)
            return {"success": False, "action": action, "error": f"Legal assessment failed: {e!s}"}
