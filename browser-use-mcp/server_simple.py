"""
Simple Browser-Use MCP Server

A simplified Model Context Protocol server that integrates with the browser-use library.
"""

from dotenv import load_dotenv
load_dotenv()

import asyncio
import json
import logging
import os
from typing import Any, Dict, List, Optional
from datetime import datetime

import mcp.types as types
from mcp.server.lowlevel import Server
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
API_KEY = os.environ.get("API_KEY", "demo-api-key-123")
PORT = int(os.environ.get("PORT", 3000))

# Global session storage
sessions = {}


class ApiKeyAuthMiddleware(BaseHTTPMiddleware):
    """API Key authentication middleware."""
    
    async def dispatch(self, request: Request, call_next):
        if request.url.path in ["/health"]:
            return await call_next(request)
        
        auth = request.headers.get("authorization")
        if auth and auth == f"Bearer {API_KEY}":
            return await call_next(request)
        
        api_key = request.query_params.get("api_key")
        if api_key and api_key == API_KEY:
            return await call_next(request)
        
        return JSONResponse({"detail": "Unauthorized"}, status_code=401)


def create_app():
    """Create the MCP server application."""
    
    # Create MCP server
    server = Server("browser-use-mcp-server")
    
    # Register tools
    @server.list_tools()
    async def list_tools() -> list[types.Tool]:
        return [
            types.Tool(
                name="create_browser_session",
                description="Create a new browser session",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "session_id": {
                            "type": "string",
                            "description": "Unique identifier for the session"
                        },
                        "headless": {
                            "type": "boolean",
                            "description": "Run browser in headless mode",
                            "default": True
                        }
                    },
                    "required": ["session_id"]
                }
            ),
            types.Tool(
                name="navigate_to_url",
                description="Navigate to a URL",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "session_id": {
                            "type": "string",
                            "description": "Session ID"
                        },
                        "url": {
                            "type": "string",
                            "description": "URL to navigate to"
                        }
                    },
                    "required": ["session_id", "url"]
                }
            ),
            types.Tool(
                name="get_page_content",
                description="Get the current page content",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "session_id": {
                            "type": "string",
                            "description": "Session ID"
                        }
                    },
                    "required": ["session_id"]
                }
            ),
            types.Tool(
                name="execute_task",
                description="Execute a task using AI agent",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "session_id": {
                            "type": "string",
                            "description": "Session ID"
                        },
                        "task": {
                            "type": "string",
                            "description": "Task description"
                        },
                        "provider": {
                            "type": "string",
                            "enum": ["openai", "anthropic"],
                            "description": "LLM provider",
                            "default": "openai"
                        }
                    },
                    "required": ["session_id", "task"]
                }
            ),
            types.Tool(
                name="close_session",
                description="Close a browser session",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "session_id": {
                            "type": "string",
                            "description": "Session ID to close"
                        }
                    },
                    "required": ["session_id"]
                }
            ),
            types.Tool(
                name="list_sessions",
                description="List all active sessions",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            )
        ]
    
    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
        try:
            if name == "create_browser_session":
                return await create_browser_session(**arguments)
            elif name == "navigate_to_url":
                return await navigate_to_url(**arguments)
            elif name == "get_page_content":
                return await get_page_content(**arguments)
            elif name == "execute_task":
                return await execute_task(**arguments)
            elif name == "close_session":
                return await close_session(**arguments)
            elif name == "list_sessions":
                return await list_sessions(**arguments)
            else:
                raise ValueError(f"Unknown tool: {name}")
        except Exception as e:
            logger.error(f"Error in tool {name}: {e}")
            return [types.TextContent(
                type="text",
                text=f"Error: {str(e)}"
            )]
    
    # Set up SSE transport
    sse = SseServerTransport("/messages/")
    
    # SSE handler
    async def handle_sse(request):
        logger.info(f"New SSE connection from {request.client.host}")
        try:
            async with sse.connect_sse(
                request.scope, request.receive, request._send
            ) as streams:
                await server.run(
                    streams[0], streams[1], server.create_initialization_options()
                )
        except Exception as e:
            logger.error(f"SSE error: {e}")
            raise
    
    # Health check endpoint
    async def health_check(request):
        return JSONResponse({
            "status": "healthy",
            "service": "browser-use-mcp-server",
            "active_sessions": len(sessions),
            "version": "1.0.0"
        })
    
    # Create Starlette app
    starlette_app = Starlette(
        debug=True,
        routes=[
            Route("/sse", endpoint=handle_sse),
            Route("/health", endpoint=health_check),
            Route("/messages/", endpoint=sse.handle_post_message, methods=["POST"])
        ],
        middleware=[
            (ApiKeyAuthMiddleware, [], {}),
            (CORSMiddleware, [], {
                "allow_origins": ["*"],
                "allow_methods": ["*"],
                "allow_headers": ["*"],
            })
        ]
    )
    
    return starlette_app


# Tool implementations
async def create_browser_session(session_id: str, headless: bool = True) -> list[types.TextContent]:
    """Create a browser session using playwright directly."""
    try:
        from playwright.async_api import async_playwright
        
        if session_id in sessions:
            return [types.TextContent(
                type="text",
                text=f"Session {session_id} already exists"
            )]
        
        # Start playwright
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=headless)
        page = await browser.new_page()
        
        sessions[session_id] = {
            "playwright": playwright,
            "browser": browser,
            "page": page,
            "created_at": datetime.now().isoformat(),
            "current_url": None
        }
        
        logger.info(f"Created browser session: {session_id}")
        return [types.TextContent(
            type="text",
            text=f"Browser session '{session_id}' created successfully"
        )]
        
    except Exception as e:
        logger.error(f"Error creating session: {e}")
        return [types.TextContent(
            type="text",
            text=f"Error creating session: {str(e)}"
        )]


async def navigate_to_url(session_id: str, url: str) -> list[types.TextContent]:
    """Navigate to a URL."""
    try:
        if session_id not in sessions:
            return [types.TextContent(
                type="text",
                text=f"Session {session_id} not found"
            )]
        
        page = sessions[session_id]["page"]
        await page.goto(url)
        sessions[session_id]["current_url"] = url
        
        logger.info(f"Navigated to {url} in session {session_id}")
        return [types.TextContent(
            type="text",
            text=f"Successfully navigated to {url}"
        )]
        
    except Exception as e:
        logger.error(f"Error navigating: {e}")
        return [types.TextContent(
            type="text",
            text=f"Error navigating: {str(e)}"
        )]


async def get_page_content(session_id: str) -> list[types.TextContent]:
    """Get page content."""
    try:
        if session_id not in sessions:
            return [types.TextContent(
                type="text",
                text=f"Session {session_id} not found"
            )]
        
        page = sessions[session_id]["page"]
        title = await page.title()
        url = page.url
        text_content = await page.inner_text("body")
        
        content = f"Title: {title}\nURL: {url}\n\nContent:\n{text_content[:1000]}..."
        
        return [types.TextContent(
            type="text",
            text=content
        )]
        
    except Exception as e:
        logger.error(f"Error getting content: {e}")
        return [types.TextContent(
            type="text",
            text=f"Error getting content: {str(e)}"
        )]


async def execute_task(session_id: str, task: str, provider: str = "openai") -> list[types.TextContent]:
    """Execute a task using browser-use agent."""
    try:
        if session_id not in sessions:
            return [types.TextContent(
                type="text",
                text=f"Session {session_id} not found"
            )]
        
        # Import browser-use components
        from browser_use import Agent
        from browser_use.llm import ChatOpenAI, ChatAnthropic
        
        # Get the page from session
        page = sessions[session_id]["page"]
        
        # Create LLM instance
        if provider == "openai":
            llm = ChatOpenAI(
                model="gpt-4o-mini",
                api_key=os.getenv("OPENAI_API_KEY", "demo-key")
            )
        elif provider == "anthropic":
            llm = ChatAnthropic(
                model="claude-3-5-sonnet-20241022",
                api_key=os.getenv("ANTHROPIC_API_KEY", "demo-key")
            )
        else:
            return [types.TextContent(
                type="text",
                text=f"Unsupported provider: {provider}"
            )]
        
        # Create and run agent
        agent = Agent(
            task=task,
            llm=llm,
            page=page
        )
        
        result = await agent.run()
        
        logger.info(f"Task completed in session {session_id}: {task}")
        return [types.TextContent(
            type="text",
            text=f"Task completed: {str(result)}"
        )]
        
    except Exception as e:
        logger.error(f"Error executing task: {e}")
        return [types.TextContent(
            type="text",
            text=f"Error executing task: {str(e)}. Note: This requires valid API keys for LLM providers."
        )]


async def close_session(session_id: str) -> list[types.TextContent]:
    """Close a browser session."""
    try:
        if session_id not in sessions:
            return [types.TextContent(
                type="text",
                text=f"Session {session_id} not found"
            )]
        
        session_data = sessions[session_id]
        await session_data["browser"].close()
        await session_data["playwright"].stop()
        del sessions[session_id]
        
        logger.info(f"Closed session: {session_id}")
        return [types.TextContent(
            type="text",
            text=f"Session '{session_id}' closed successfully"
        )]
        
    except Exception as e:
        logger.error(f"Error closing session: {e}")
        return [types.TextContent(
            type="text",
            text=f"Error closing session: {str(e)}"
        )]


async def list_sessions() -> list[types.TextContent]:
    """List all active sessions."""
    try:
        session_list = []
        for session_id, session_data in sessions.items():
            session_info = {
                "session_id": session_id,
                "created_at": session_data["created_at"],
                "current_url": session_data.get("current_url", "None")
            }
            session_list.append(session_info)
        
        return [types.TextContent(
            type="text",
            text=json.dumps(session_list, indent=2)
        )]
        
    except Exception as e:
        logger.error(f"Error listing sessions: {e}")
        return [types.TextContent(
            type="text",
            text=f"Error listing sessions: {str(e)}"
        )]


# Create the app
starlette_app = create_app()

if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting Browser-Use MCP server on port {PORT}")
    uvicorn.run(starlette_app, host="0.0.0.0", port=PORT)