"""
Legal compliance tools for RTorrent MCP Server

MCP tools for Austrian legal compliance and risk assessment
"""

import logging

from fastmcp import FastMCP

from ..services import LEGAL_RISK
from ..services.legal_compliance import check_country_legal_status, get_austrian_legal_framework

logger = logging.getLogger(__name__)


def register_legal_tools(mcp: FastMCP, settings) -> None:
    """
    Register legal compliance tools with FastMCP server.

    Args:
        mcp: FastMCP server instance
        settings: Application settings
    """

    @mcp.tool(
        name="check_legal_status",
        description="Check legal status of torrenting by country with Austrian context. "
                   "Provides risk assessment for torrenting activities in different countries, "
                   "with special focus on Austrian legal requirements. "
                   "Args: country (str): Country name to check (default: 'austria'). "
                   "Returns: dict with legal status, risk level, warnings, and recommendations."
    )
    async def check_legal_status(country: str = "austria") -> dict:
        """Check legal status of torrenting by country with Austrian context"""
        try:
            return check_country_legal_status(country)
        except Exception as e:
            logger.error(f"Error checking legal status for {country}: {e}")
            return {
                "country": country.title(),
                "risk_level": "unknown",
                "warning": "Unable to determine legal status",
                "sandra_location": country.lower() == "austria",
                "recommendation": "Research local copyright laws",
                "error": str(e)
            }

    @mcp.tool(
        name="get_legal_warning",
        description="Get detailed legal warning for specific country. "
                   "Provides comprehensive legal information and warnings for torrenting "
                   "in specific jurisdictions, with Austrian legal framework as baseline. "
                   "Args: country (str): Country name to get detailed warning for. "
                   "Returns: dict with detailed legal warning, risk assessment, and recommendations."
    )
    async def get_legal_warning(country: str) -> dict:
        """Get detailed legal warning for specific country"""
        try:
            status = check_country_legal_status(country)

            detailed_warnings = {
                "germany": {
                    "risk": "Very High",
                    "details": "Abmahnung system with automatic detection by law firms",
                    "typical_fine": "€500-€2000",
                    "recommendation": "VPN mandatory, avoid all copyrighted content"
                },
                "japan": {
                    "risk": "Criminal",
                    "details": "Criminal penalties since 2012 amendments",
                    "typical_penalty": "Up to 2 years prison or ¥2M fine",
                    "recommendation": "Avoid all torrenting, use legal streaming only"
                },
                "austria": {
                    "risk": "Low",
                    "details": "Personal use generally tolerated by authorities",
                    "enforcement": "Focus on commercial distribution",
                    "recommendation": "Personal anime downloading acceptable"
                }
            }

            return {
                **status,
                "detailed_warning": detailed_warnings.get(country.lower(), {
                    "risk": "Unknown",
                    "details": "Legal status varies by jurisdiction",
                    "recommendation": "Research local copyright laws"
                })
            }
        except Exception as e:
            logger.error(f"Error getting legal warning for {country}: {e}")
            return {
                "country": country.title(),
                "risk_level": "unknown",
                "warning": "Unable to retrieve legal information",
                "sandra_location": country.lower() == "austria",
                "recommendation": "Consult local legal experts",
                "error": str(e)
            }

    # Resources for legal information
    @mcp.resource("legal://austria")
    def austrian_legal_info() -> str:
        """Austrian legal framework for torrenting"""
        try:
            import json
            return json.dumps(get_austrian_legal_framework())
        except Exception as e:
            logger.error(f"Error generating Austrian legal info: {e}")
            return json.dumps({"error": f"Failed to load legal information: {str(e)}"})

    @mcp.resource("legal://overview")
    def legal_overview() -> str:
        """Overview of legal risks by country"""
        try:
            import json
            return json.dumps({
                "risk_levels": LEGAL_RISK,
                "sandra_location": "Austria (Safe Zone)",
                "high_risk_countries": ["germany", "japan"],
                "recommendations": {
                    "austria": "Personal use OK",
                    "germany": "VPN mandatory",
                    "japan": "Avoid completely",
                    "unknown": "Research local laws"
                }
            })
        except Exception as e:
            logger.error(f"Error generating legal overview: {e}")
            return json.dumps({"error": f"Failed to load overview: {str(e)}"})
