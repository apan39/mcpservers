#!/usr/bin/env python3
"""
MCP Server for stdio transport (Claude Desktop/CLI compatible).
"""

import asyncio
import logging
from mcp.server.stdio import stdio_server
from mcp.server.lowlevel import Server
from mcp.types import Tool, TextContent
from tools.math_tools import register_math_tools
from tools.text_tools import register_text_tools
from tools.crawl4ai_tools import register_crawl4ai_tools
from utils.logger import setup_logger

# Set up logging
logger = setup_logger("mcp_stdio_server", logging.INFO)


def create_server():
    """Create and configure the MCP server."""
    tool_registry = {}
    server = Server("python-mcp-tools")
    
    # Register all tools
    register_math_tools(tool_registry)
    register_text_tools(tool_registry)
    register_crawl4ai_tools(tool_registry)
    
    @server.list_tools()
    async def list_tools():
        """List all available tools."""
        return [tool_data["definition"] for tool_data in tool_registry.values()]
    
    @server.call_tool()
    async def call_tool(name: str, arguments: dict):
        """Call a tool with given arguments."""
        if name not in tool_registry:
            raise ValueError(f"Unknown tool: {name}")
        
        try:
            handler = tool_registry[name]["handler"]
            result = await handler(**arguments)
            logger.info(f"Successfully executed tool: {name}")
            return result
        except Exception as e:
            logger.error(f"Error executing tool {name}: {str(e)}")
            return [TextContent(
                type="text", 
                text=f"Error executing tool: {str(e)}"
            )]
    
    return server


async def main():
    """Main entry point."""
    server = create_server()
    async with stdio_server(server) as streams:
        await server.run(
            streams[0], streams[1], server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())