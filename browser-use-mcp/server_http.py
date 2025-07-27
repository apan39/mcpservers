#!/usr/bin/env python3
"""
Browser-Use MCP HTTP Server implementation following the same pattern as other MCP servers.
Updated to trigger deployment - using JSON-RPC protocol instead of SSE.
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import uvicorn
from mcp.types import Tool, TextContent
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

# Load environment variables from .env file
def load_env_file():
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

load_env_file()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
MCP_API_KEY = os.environ.get("MCP_API_KEY", "demo-api-key-123")
PORT = int(os.environ.get("PORT", 3000))

# Global session storage
sessions = {}

# Tool registry
tool_registry = {}

class ApiKeyAuthMiddleware(BaseHTTPMiddleware):
    """API Key authentication middleware."""
    
    async def dispatch(self, request: Request, call_next):
        if request.url.path in ["/health"]:
            return await call_next(request)
        
        auth = request.headers.get("authorization")
        if auth and auth == f"Bearer {MCP_API_KEY}":
            return await call_next(request)
        
        return JSONResponse({"error": "Unauthorized"}, status_code=401)

def setup_tools():
    """Setup all browser automation tools."""
    
    # Create browser session tool
    tool_registry["create_browser_session"] = {
        "definition": Tool(
            name="create_browser_session",
            description="Create a new browser session for web automation",
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
        "handler": create_browser_session
    }
    
    # Navigate to URL tool
    tool_registry["navigate_to_url"] = {
        "definition": Tool(
            name="navigate_to_url",
            description="Navigate to a specific URL in the browser",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Browser session ID"
                    },
                    "url": {
                        "type": "string",
                        "description": "URL to navigate to"
                    }
                },
                "required": ["session_id", "url"]
            }
        ),
        "handler": navigate_to_url
    }
    
    # Get page content tool
    tool_registry["get_page_content"] = {
        "definition": Tool(
            name="get_page_content",
            description="Extract content from the current page",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Browser session ID"
                    },
                    "include_html": {
                        "type": "boolean",
                        "description": "Include HTML in the response",
                        "default": False
                    }
                },
                "required": ["session_id"]
            }
        ),
        "handler": get_page_content
    }
    
    # Execute browser task tool
    tool_registry["execute_browser_task"] = {
        "definition": Tool(
            name="execute_browser_task",
            description="Execute a complex browser task using AI agent",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Browser session ID"
                    },
                    "task": {
                        "type": "string",
                        "description": "Natural language description of the task to perform"
                    },
                    "provider": {
                        "type": "string",
                        "enum": ["openai", "anthropic"],
                        "description": "LLM provider to use for the AI agent",
                        "default": "openai"
                    }
                },
                "required": ["session_id", "task"]
            }
        ),
        "handler": execute_browser_task
    }
    
    # Close browser session tool
    tool_registry["close_browser_session"] = {
        "definition": Tool(
            name="close_browser_session",
            description="Close a browser session and cleanup resources",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Browser session ID to close"
                    }
                },
                "required": ["session_id"]
            }
        ),
        "handler": close_browser_session
    }
    
    # List browser sessions tool
    tool_registry["list_browser_sessions"] = {
        "definition": Tool(
            name="list_browser_sessions",
            description="List all active browser sessions",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        "handler": list_browser_sessions
    }

async def handle_mcp_request(request: Request) -> JSONResponse:
    """Handle MCP JSON-RPC requests."""
    try:
        data = await request.json()
        method = data.get('method')
        params = data.get('params', {})
        request_id = data.get('id')
        
        if method == 'initialize':
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "browser-use-mcp",
                        "version": "1.0.0"
                    }
                }
            })
        
        elif method == 'notifications/initialized':
            return JSONResponse({"jsonrpc": "2.0", "id": request_id, "result": {}})
        
        elif method == 'tools/list':
            logger.info(f"Tools registry has {len(tool_registry)} tools")
            tools = []
            for name, tool_data in tool_registry.items():
                try:
                    tool_def = tool_data["definition"]
                    tool_dict = {
                        "name": tool_def.name,
                        "description": tool_def.description,
                        "inputSchema": tool_def.inputSchema
                    }
                    tools.append(tool_dict)
                    logger.info(f"Added tool: {name}")
                except Exception as e:
                    logger.error(f"Error processing tool {name}: {e}")
            
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "tools": tools
                }
            })
        
        elif method == 'tools/call':
            tool_name = params.get('name')
            arguments = params.get('arguments', {})
            
            if tool_name not in tool_registry:
                return JSONResponse({
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Tool not found: {tool_name}"
                    }
                })
            
            try:
                handler = tool_registry[tool_name]["handler"]
                result = await handler(**arguments)
                
                # Convert string result to TextContent format
                if isinstance(result, str):
                    content = [{"type": "text", "text": result}]
                else:
                    content = result
                
                return JSONResponse({
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": content
                    }
                })
                
            except Exception as e:
                logger.error(f"Error executing tool {tool_name}: {e}")
                return JSONResponse({
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32603,
                        "message": f"Internal error: {str(e)}"
                    }
                })
        
        else:
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            })
    
    except Exception as e:
        logger.error(f"Error handling MCP request: {e}")
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": None,
            "error": {
                "code": -32700,
                "message": f"Parse error: {str(e)}"
            }
        }, status_code=400)

async def health_check(request: Request) -> JSONResponse:
    """Health check endpoint."""
    return JSONResponse({
        "status": "healthy",
        "service": "browser-use-mcp-server",
        "active_sessions": len(sessions),
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    })

# Tool implementations
async def create_browser_session(session_id: str, headless: bool = True) -> str:
    """Create a browser session using playwright."""
    try:
        from playwright.async_api import async_playwright
        
        if session_id in sessions:
            return f"Session {session_id} already exists"
        
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
        return f"Browser session '{session_id}' created successfully"
        
    except Exception as e:
        logger.error(f"Error creating session: {e}")
        return f"Error creating session: {str(e)}"

async def navigate_to_url(session_id: str, url: str) -> str:
    """Navigate to a URL."""
    try:
        if session_id not in sessions:
            return f"Session {session_id} not found"
        
        page = sessions[session_id]["page"]
        await page.goto(url)
        sessions[session_id]["current_url"] = url
        
        logger.info(f"Navigated to {url} in session {session_id}")
        return f"Successfully navigated to {url}"
        
    except Exception as e:
        logger.error(f"Error navigating: {e}")
        return f"Error navigating: {str(e)}"

async def get_page_content(session_id: str, include_html: bool = False) -> str:
    """Get page content."""
    try:
        if session_id not in sessions:
            return f"Session {session_id} not found"
        
        page = sessions[session_id]["page"]
        title = await page.title()
        url = page.url
        
        if include_html:
            content = await page.content()
            return f"Title: {title}\nURL: {url}\n\nHTML:\n{content[:2000]}..."
        else:
            text_content = await page.inner_text("body")
            return f"Title: {title}\nURL: {url}\n\nContent:\n{text_content[:1500]}..."
        
    except Exception as e:
        logger.error(f"Error getting content: {e}")
        return f"Error getting content: {str(e)}"

async def execute_browser_task(session_id: str, task: str, provider: str = "openai") -> str:
    """Execute a task using browser-use agent."""
    try:
        if session_id not in sessions:
            return f"Session {session_id} not found"
        
        # For now, return a simulated response since browser-use requires valid API keys
        page = sessions[session_id]["page"]
        current_url = page.url
        title = await page.title()
        
        return f"Task simulation: '{task}'\nCurrent page: {title} ({current_url})\nNote: Full AI agent execution requires valid {provider.upper()} API keys"
        
    except Exception as e:
        logger.error(f"Error executing task: {e}")
        return f"Error executing task: {str(e)}"

async def close_browser_session(session_id: str) -> str:
    """Close a browser session."""
    try:
        if session_id not in sessions:
            return f"Session {session_id} not found"
        
        session_data = sessions[session_id]
        await session_data["browser"].close()
        await session_data["playwright"].stop()
        del sessions[session_id]
        
        logger.info(f"Closed session: {session_id}")
        return f"Session '{session_id}' closed successfully"
        
    except Exception as e:
        logger.error(f"Error closing session: {e}")
        return f"Error closing session: {str(e)}"

async def list_browser_sessions() -> str:
    """List all active sessions."""
    try:
        if not sessions:
            return "No active browser sessions"
        
        session_list = []
        for session_id, session_data in sessions.items():
            session_info = {
                "session_id": session_id,
                "created_at": session_data["created_at"],
                "current_url": session_data.get("current_url", "None")
            }
            session_list.append(session_info)
        
        return json.dumps(session_list, indent=2)
        
    except Exception as e:
        logger.error(f"Error listing sessions: {e}")
        return f"Error listing sessions: {str(e)}"

def create_app():
    """Create and configure the Starlette application."""
    
    # Setup tools
    setup_tools()
    
    # Create Starlette app
    app = Starlette(
        debug=True,
        routes=[
            Route("/health", endpoint=health_check, methods=["GET"]),
            Route("/mcp", endpoint=handle_mcp_request, methods=["POST"])
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
    
    return app

# Create the application
app = create_app()

if __name__ == "__main__":
    logger.info(f"Starting Browser-Use MCP HTTP server on port {PORT}")
    uvicorn.run(app, host="0.0.0.0", port=PORT)