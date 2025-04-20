import anyio
import uvicorn
import os
import mcp.types as types
from mcp.server.lowlevel import Server
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.routing import Mount, Route
from starlette.responses import JSONResponse

from tools.math_tools import register_math_tools
from tools.text_tools import register_text_tools
from resources.greeting import register_greeting_resources
from utils.logger import setup_logger
from tools.crawl4ai_tools import register_crawl4ai_tools

# Set up logging
logger = setup_logger()

def create_app(port: int = 3000):
    # Create server
    app = Server("python-mcp-server")

    # Tool registry to consolidate tools from multiple files
    tool_registry = {}

    # Register math tools
    register_math_tools(tool_registry)

    # Register text tools
    register_text_tools(tool_registry)

    # Register crawl4ai tools
    register_crawl4ai_tools(tool_registry)

    # Register greeting resources
    register_greeting_resources(app)

    # Consolidated call_tool handler
    @app.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
        if name not in tool_registry:
            raise ValueError(f"Unknown tool: {name}")
        # Retrieve the handler function from the tool registry and call it
        handler = tool_registry[name]["handler"]
        return await handler(**arguments)

    # Consolidated list_tools handler
    @app.list_tools()
    async def list_tools() -> list[types.Tool]:
        tools = []
        for tool_name, tool_info in tool_registry.items():
            tools.append(tool_info["definition"])
        return tools

    # Set up SSE transport
    sse = SseServerTransport("/messages/")

    # SSE handler
    async def handle_sse(request):
        logger.info(f"New SSE connection from {request.client.host}")
        try:
            async with sse.connect_sse(
                request.scope, request.receive, request._send
            ) as streams:
                await app.run(
                    streams[0], streams[1], app.create_initialization_options()
                )
        except anyio.BrokenResourceError:
            logger.warning("SSE connection closed by client.")
        except Exception as e:
            logger.error(f"Unexpected error in SSE handler: {e}")
            raise

    # Health check endpoint
    async def health_check(request):
        return JSONResponse({"status": "healthy", "service": "python-mcp-server"})

    # Create Starlette app
    starlette_app = Starlette(
        debug=True,
        routes=[
            Route("/sse", endpoint=handle_sse),
            Route("/health", endpoint=health_check),
            Mount("/messages/", app=sse.handle_post_message),
        ],
    )

    return starlette_app

starlette_app = create_app()

if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 3000))
    logger.info(f"Starting MCP server on port {PORT}")
    uvicorn.run(starlette_app, host="0.0.0.0", port=PORT)

