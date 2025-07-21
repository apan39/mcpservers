"""
MCP Server implementation following MCP standards.
This server provides math, text, and web crawling tools.
"""

import asyncio
import logging
import os
from typing import Any, Dict, List

import mcp.types as types
from mcp.server.lowlevel import Server
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.routing import Mount
from starlette.types import Receive, Scope, Send

from health import add_health_routes

from tools.math_tools import register_math_tools
from tools.text_tools import register_text_tools
from tools.crawl4ai_tools import register_crawl4ai_tools
from tools.coolify_tools import register_coolify_tools
from utils.logger import setup_logger

# Set up logging
logger = setup_logger("mcp_server", logging.INFO)

class MCPServer:
    """MCP Server with proper tool registration and error handling."""
    
    def __init__(self, server_name: str = "mcp-production-server"):
        self.server_name = server_name
        self.tool_registry: Dict[str, Dict[str, Any]] = {}
        self.app = Server(server_name)
        self._setup_server()
    
    def _setup_server(self):
        """Set up the MCP server with all tools."""
        # Register all tools
        register_math_tools(self.tool_registry)
        register_text_tools(self.tool_registry)
        register_crawl4ai_tools(self.tool_registry)
        register_coolify_tools(self.tool_registry)
        
        # Register tools with the server
        @self.app.list_tools()
        async def list_tools() -> List[types.Tool]:
            return [tool_data["definition"] for tool_data in self.tool_registry.values()]
        
        @self.app.call_tool()
        async def call_tool(
            name: str, 
            arguments: dict
        ) -> List[types.TextContent | types.ImageContent | types.EmbeddedResource]:
            if name not in self.tool_registry:
                raise ValueError(f"Unknown tool: {name}")
            
            try:
                handler = self.tool_registry[name]["handler"]
                result = await handler(**arguments)
                logger.info(f"Successfully executed tool: {name}")
                return result
            except Exception as e:
                logger.error(f"Error executing tool {name}: {str(e)}")
                return [types.TextContent(
                    type="text", 
                    text=f"Error executing tool: {str(e)}"
                )]
    
    def get_server(self) -> Server:
        """Get the configured MCP server."""
        return self.app


def create_app() -> Starlette:
    """Create the Starlette application with proper middleware and configuration."""
    
    # Initialize MCP server
    mcp_server = MCPServer()
    server = mcp_server.get_server()
    
    # Create session manager
    from event_store import InMemoryEventStore
    event_store = InMemoryEventStore()
    session_manager = StreamableHTTPSessionManager(
        app=server,
        event_store=event_store,
        json_response=False,
    )
    
    async def handle_mcp_request(scope: Scope, receive: Receive, send: Send) -> None:
        """Handle MCP requests."""
        try:
            await session_manager.handle_request(scope, receive, send)
        except Exception as e:
            logger.error(f"Error handling MCP request: {str(e)}")
            # Send error response
            await send({
                'type': 'http.response.start',
                'status': 500,
                'headers': [[b'content-type', b'application/json']],
            })
            await send({
                'type': 'http.response.body',
                'body': b'{"error": "Internal server error"}',
            })
    
    # Create Starlette app
    app = Starlette(
        debug=False,  # Production setting
        routes=[
            Mount("/mcp", app=handle_mcp_request),
        ],
    )
    
    # Add health routes
    add_health_routes(app)
    
    # Add CORS middleware
    allowed_origins = os.getenv("ALLOWED_ORIGINS", "").split(",") if os.getenv("ALLOWED_ORIGINS") else ["*"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )
    
    return app


def main():
    """CLI entry point for development."""
    import uvicorn
    
    # Get configuration from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "3009"))
    log_level = os.getenv("LOG_LEVEL", "INFO").lower()
    
    logger.info(f"Starting MCP server on {host}:{port}")
    
    app = create_app()
    uvicorn.run(
        app, 
        host=host, 
        port=port,
        log_level=log_level,
        access_log=True
    )


if __name__ == "__main__":
    main()