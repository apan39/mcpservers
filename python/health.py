"""
Health check endpoint for MCP server.
"""

from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
import json
from datetime import datetime


async def health_check(request):
    """Health check endpoint."""
    return JSONResponse({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "mcp-python-server"
    })


async def metrics(request):
    """Basic metrics endpoint."""
    return JSONResponse({
        "uptime": "unknown",  # Could implement actual uptime tracking
        "requests_total": 0,  # Could implement request counting
        "errors_total": 0,    # Could implement error counting
        "timestamp": datetime.utcnow().isoformat()
    })


def add_health_routes(app: Starlette):
    """Add health and monitoring routes to the Starlette app."""
    app.routes.extend([
        Route("/health", health_check, methods=["GET"]),
        Route("/metrics", metrics, methods=["GET"]),
    ])