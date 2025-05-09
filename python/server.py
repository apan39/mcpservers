from dotenv import load_dotenv; load_dotenv()
import anyio
import uvicorn
import os
import mcp.types as types
from mcp.server.lowlevel import Server
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.routing import Mount, Route
from starlette.responses import JSONResponse
import datetime
from collections import defaultdict

from tools.math_tools import register_math_tools
from tools.text_tools import register_text_tools
from resources.greeting import register_greeting_resources
from utils.logger import setup_logger
from tools.crawl4ai_tools import register_crawl4ai_tools

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware

# API_KEY = os.environ.get("API_KEY")  # Set this in your environment for production
API_KEY = os.environ.get("MCP_API_KEY")  # Set this in your environment for production
# Global in-memory store for authorized IPs and their last auth date
AUTHORIZED_IPS = defaultdict(lambda: None)

class ApiKeyAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Get client IP (use X-Forwarded-For if behind proxy, else .client.host)
        client_ip = request.headers.get("x-forwarded-for") or request.client.host
        today = datetime.date.today()
        last_auth_date = AUTHORIZED_IPS[client_ip]
        # Allow health check without auth
        if request.url.path in ["/health"]:
            return await call_next(request)
        # If already authorized today, allow
        if last_auth_date == today:
            return await call_next(request)
        # Check Authorization header
        auth = request.headers.get("authorization")
        if auth and auth == f"Bearer {API_KEY}":
            AUTHORIZED_IPS[client_ip] = today
            return await call_next(request)
        # Check query parameter
        api_key = request.query_params.get("api_key")
        if api_key and api_key == API_KEY:
            AUTHORIZED_IPS[client_ip] = today
            return await call_next(request)
        return JSONResponse({"detail": "Unauthorized"}, status_code=401)

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
            import traceback
            logger.error(f"Unexpected error in SSE handler: {e}\n" + traceback.format_exc())
            # If the exception is a TaskGroupError, log sub-exceptions
            if hasattr(e, 'exceptions'):
                for idx, sub_exc in enumerate(e.exceptions):
                    logger.error(f"Sub-exception {idx+1}: {sub_exc}\n" + (getattr(sub_exc, 'traceback', None) or ''))
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
        middleware=[
            (ApiKeyAuthMiddleware, [], {}),
            (CORSMiddleware, [], {
                "allow_origins": ["*"],
                "allow_methods": ["*"],
                "allow_headers": ["*"],
            }),
        ]
    )
 
    return starlette_app
 
starlette_app = create_app()

if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 3002))
    logger.info(f"Starting MCP server on port {PORT}")
    uvicorn.run(starlette_app, host="0.0.0.0", port=PORT)

