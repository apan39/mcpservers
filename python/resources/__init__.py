"""Resources module for MCP server."""

from .greeting import register_greeting_resources

def register_all_resources(mcp):
    """Register all resources with the MCP server."""
    register_greeting_resources(mcp)