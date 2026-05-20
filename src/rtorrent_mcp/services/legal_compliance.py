"""
legal_compliance.py - Legal compliance checking for RTorrent MCP
Austrian legal framework with international warnings
"""

import json
import logging
from typing import Any

from . import LEGAL_RISK

logger = logging.getLogger(__name__)


def check_country_legal_status(country: str) -> dict[str, Any]:
    """Check legal status of torrenting by country with Austrian context"""
    country_lower = country.lower()

    risk_level = LEGAL_RISK.get(country_lower, "unknown")

    warnings = {
        "safe": "[OK] Personal downloading generally tolerated",
        "medium": "[WARN] Use VPN recommended, avoid commercial content",
        "high": "[ALERT] High risk of EUR 500-2000 fines, VPN mandatory",
        "criminal": "[CRITICAL] Criminal penalties possible, prison sentences",
        "unknown": "[?] Legal status unclear, research local laws",
    }

    return {
        "country": country.title(),
        "risk_level": risk_level,
        "warning": warnings.get(risk_level, "Unknown status"),
        "sandra_location": country_lower == "austria",
        "recommendation": "Safe for Sandra in Vienna (AT)" if country_lower == "austria" else "Check local laws",
    }


def get_austrian_legal_framework() -> dict[str, Any]:
    """Get detailed Austrian legal framework for torrenting"""
    return {
        "country": "Austria (AT)",
        "sandra_location": "Vienna, 9th district",
        "legal_status": "Personal downloading generally tolerated",
        "enforcement": "Minimal for individual users",
        "focus": "Commercial distribution prosecuted",
        "practical_result": "Sandra can anime in peace",
        "updated": "2025-07-23",
        "sources": [
            "Austrian Copyright Act (UrhG)",
            "Personal use exemption §42b UrhG",
            "Enforcement practice analysis",
        ],
    }


def register_legal_tools(mcp):
    """Register legal compliance tools with FastMCP server"""

    @mcp.tool()
    async def check_legal_status(country: str = "austria") -> dict:
        """Check legal status of torrenting by country with Austrian context"""
        return check_country_legal_status(country)

    @mcp.tool()
    def get_legal_warning(country: str) -> dict:
        """Get detailed legal warning for specific country"""
        status = check_country_legal_status(country)

        detailed_warnings = {
            "germany": {
                "risk": "Very High",
                "details": "Abmahnung system with automatic detection by law firms",
                "typical_fine": "€500-€2000",
                "recommendation": "VPN mandatory, avoid all copyrighted content",
            },
            "japan": {
                "risk": "Criminal",
                "details": "Criminal penalties since 2012 amendments",
                "typical_penalty": "Up to 2 years prison or ¥2M fine",
                "recommendation": "Avoid all torrenting, use legal streaming only",
            },
            "austria": {
                "risk": "Low",
                "details": "Personal use generally tolerated by authorities",
                "enforcement": "Focus on commercial distribution",
                "recommendation": "Personal anime downloading acceptable",
            },
        }

        return {
            **status,
            "detailed_warning": detailed_warnings.get(
                country.lower(),
                {
                    "risk": "Unknown",
                    "details": "Legal status varies by jurisdiction",
                    "recommendation": "Research local copyright laws",
                },
            ),
        }

    @mcp.resource("legal://austria")
    def austrian_legal_info() -> str:
        """Austrian legal framework for torrenting"""
        return json.dumps(get_austrian_legal_framework())

    @mcp.resource("legal://overview")
    def legal_overview() -> str:
        """Overview of legal risks by country"""
        return json.dumps(
            {
                "risk_levels": LEGAL_RISK,
                "sandra_location": "Austria (Safe Zone)",
                "high_risk_countries": ["germany", "japan"],
                "recommendations": {
                    "austria": "Personal use OK",
                    "germany": "VPN mandatory",
                    "japan": "Avoid completely",
                    "unknown": "Research local laws",
                },
            }
        )
