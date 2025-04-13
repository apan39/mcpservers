"""Tools module for MCP server."""

from .math_tools import register_math_tools
from .text_tools import register_text_tools

def register_all_tools(mcp):
    """Register all tools with the MCP server."""
    register_math_tools(mcp)
    register_text_tools(mcp)