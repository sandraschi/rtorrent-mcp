"""HTTP bridge for the web_sota SPA (Starlette routes on the same ASGI app as MCP)."""

from .web_routes import register_web_api

__all__ = ["register_web_api"]
