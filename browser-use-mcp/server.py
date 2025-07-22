"""
Browser-Use MCP Server

A comprehensive Model Context Protocol server that integrates with the browser-use library
to provide AI agents with powerful browser automation capabilities.
"""

from dotenv import load_dotenv
load_dotenv()

import asyncio
import json
import logging
import os
from typing import Any, Dict, List, Optional, Union
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

from browser_use import Agent, Browser, BrowserConfig
from browser_use.dom.service import DOMService
from browser_use.browser.service import BrowserService
from browser_use.agent.service import AgentService
from browser_use.agent.views import AgentHistoryList, ActionResult
from browser_use.controller.service import Controller

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
API_KEY = os.environ.get("API_KEY", "changeme")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# Global browser manager
browser_manager = {}
agent_manager = {}


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


def create_app(port: int = 3000):
    """Create the MCP server application."""
    
    # Create MCP server
    server = Server("browser-use-mcp-server")
    
    # Tool registry
    tool_registry = {}
    
    # Register browser control tools
    register_browser_tools(tool_registry)
    
    # Register agent tools
    register_agent_tools(tool_registry)
    
    # Register session management tools
    register_session_tools(tool_registry)
    
    # Consolidated call_tool handler
    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
        if name not in tool_registry:
            raise ValueError(f"Unknown tool: {name}")
        
        handler = tool_registry[name]["handler"]
        try:
            return await handler(**arguments)
        except Exception as e:
            logger.error(f"Error executing tool {name}: {str(e)}")
            return [types.TextContent(
                type="text",
                text=f"Error: {str(e)}"
            )]
    
    # Consolidated list_tools handler
    @server.list_tools()
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
            "version": "1.0.0",
            "protocol_version": "2025-06-18"
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


def register_browser_tools(tool_registry: Dict[str, Any]):
    """Register browser control tools."""
    
    # Create browser session
    tool_registry["create_browser_session"] = {
        "definition": types.Tool(
            name="create_browser_session",
            description="Create a new browser session for automation",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Unique identifier for the browser session"
                    },
                    "headless": {
                        "type": "boolean",
                        "description": "Run browser in headless mode",
                        "default": True
                    },
                    "browser_type": {
                        "type": "string",
                        "enum": ["chromium", "firefox", "webkit"],
                        "description": "Type of browser to use",
                        "default": "chromium"
                    },
                    "viewport_width": {
                        "type": "integer",
                        "description": "Browser viewport width",
                        "default": 1920
                    },
                    "viewport_height": {
                        "type": "integer",
                        "description": "Browser viewport height",
                        "default": 1080
                    }
                },
                "required": ["session_id"]
            }
        ),
        "handler": create_browser_session
    }
    
    # Close browser session
    tool_registry["close_browser_session"] = {
        "definition": types.Tool(
            name="close_browser_session",
            description="Close a browser session",
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
    
    # Navigate to URL
    tool_registry["navigate_to_url"] = {
        "definition": types.Tool(
            name="navigate_to_url",
            description="Navigate to a specific URL",
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
                    },
                    "wait_for_load": {
                        "type": "boolean",
                        "description": "Wait for page to fully load",
                        "default": True
                    }
                },
                "required": ["session_id", "url"]
            }
        ),
        "handler": navigate_to_url
    }
    
    # Get page content
    tool_registry["get_page_content"] = {
        "definition": types.Tool(
            name="get_page_content",
            description="Get the current page content (HTML, text, or screenshot)",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Browser session ID"
                    },
                    "content_type": {
                        "type": "string",
                        "enum": ["html", "text", "screenshot"],
                        "description": "Type of content to retrieve",
                        "default": "text"
                    },
                    "full_page": {
                        "type": "boolean",
                        "description": "For screenshots, capture full page",
                        "default": False
                    }
                },
                "required": ["session_id"]
            }
        ),
        "handler": get_page_content
    }


def register_agent_tools(tool_registry: Dict[str, Any]):
    """Register AI agent tools."""
    
    # Create agent
    tool_registry["create_agent"] = {
        "definition": types.Tool(
            name="create_agent",
            description="Create an AI agent for browser automation",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent_id": {
                        "type": "string",
                        "description": "Unique identifier for the agent"
                    },
                    "session_id": {
                        "type": "string",
                        "description": "Browser session ID to use"
                    },
                    "llm_provider": {
                        "type": "string",
                        "enum": ["anthropic", "openai", "google", "groq", "ollama"],
                        "description": "LLM provider to use",
                        "default": "anthropic"
                    },
                    "model_name": {
                        "type": "string",
                        "description": "Specific model to use (e.g., claude-3-5-sonnet-20241022)"
                    },
                    "max_actions": {
                        "type": "integer",
                        "description": "Maximum number of actions the agent can take",
                        "default": 100
                    },
                    "temperature": {
                        "type": "number",
                        "description": "Model temperature (0.0 to 1.0)",
                        "default": 0.1
                    }
                },
                "required": ["agent_id", "session_id"]
            }
        ),
        "handler": create_agent
    }
    
    # Execute agent task
    tool_registry["execute_agent_task"] = {
        "definition": types.Tool(
            name="execute_agent_task",
            description="Execute a task using the AI agent",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent_id": {
                        "type": "string",
                        "description": "Agent ID to use"
                    },
                    "task": {
                        "type": "string",
                        "description": "Natural language description of the task"
                    },
                    "max_steps": {
                        "type": "integer",
                        "description": "Maximum number of steps to execute",
                        "default": 50
                    }
                },
                "required": ["agent_id", "task"]
            }
        ),
        "handler": execute_agent_task
    }
    
    # Get agent history
    tool_registry["get_agent_history"] = {
        "definition": types.Tool(
            name="get_agent_history",
            description="Get the action history for an agent",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent_id": {
                        "type": "string",
                        "description": "Agent ID"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of history items to return",
                        "default": 10
                    }
                },
                "required": ["agent_id"]
            }
        ),
        "handler": get_agent_history
    }


def register_session_tools(tool_registry: Dict[str, Any]):
    """Register session management tools."""
    
    # List active sessions
    tool_registry["list_active_sessions"] = {
        "definition": types.Tool(
            name="list_active_sessions",
            description="List all active browser sessions and agents",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        "handler": list_active_sessions
    }
    
    # Get session info
    tool_registry["get_session_info"] = {
        "definition": types.Tool(
            name="get_session_info",
            description="Get detailed information about a session",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Session ID to get info for"
                    }
                },
                "required": ["session_id"]
            }
        ),
        "handler": get_session_info
    }


# Tool handler implementations

async def create_browser_session(
    session_id: str,
    headless: bool = True,
    browser_type: str = "chromium",
    viewport_width: int = 1920,
    viewport_height: int = 1080
) -> list[types.TextContent]:
    """Create a new browser session."""
    
    if session_id in browser_manager:
        return [types.TextContent(
            type="text",
            text=f"Session {session_id} already exists"
        )]
    
    try:
        # Create browser config
        config = BrowserConfig(
            headless=headless,
            browser_type=browser_type,
            viewport_width=viewport_width,
            viewport_height=viewport_height
        )
        
        # Create and start browser
        browser = Browser(config=config)
        await browser.start()
        
        browser_manager[session_id] = {
            "browser": browser,
            "config": config,
            "created_at": datetime.now().isoformat(),
            "current_url": None
        }
        
        logger.info(f"Created browser session: {session_id}")
        
        return [types.TextContent(
            type="text",
            text=f"Browser session '{session_id}' created successfully"
        )]
        
    except Exception as e:
        logger.error(f"Error creating browser session: {e}")
        return [types.TextContent(
            type="text",
            text=f"Error creating browser session: {str(e)}"
        )]


async def close_browser_session(session_id: str) -> list[types.TextContent]:
    """Close a browser session."""
    
    if session_id not in browser_manager:
        return [types.TextContent(
            type="text",
            text=f"Session {session_id} not found"
        )]
    
    try:
        browser_info = browser_manager[session_id]
        await browser_info["browser"].close()
        del browser_manager[session_id]
        
        # Also remove associated agents
        agents_to_remove = [
            agent_id for agent_id, agent_info in agent_manager.items()
            if agent_info.get("session_id") == session_id
        ]
        for agent_id in agents_to_remove:
            del agent_manager[agent_id]
        
        logger.info(f"Closed browser session: {session_id}")
        
        return [types.TextContent(
            type="text",
            text=f"Browser session '{session_id}' closed successfully"
        )]
        
    except Exception as e:
        logger.error(f"Error closing browser session: {e}")
        return [types.TextContent(
            type="text",
            text=f"Error closing browser session: {str(e)}"
        )]


async def navigate_to_url(
    session_id: str,
    url: str,
    wait_for_load: bool = True
) -> list[types.TextContent]:
    """Navigate to a URL."""
    
    if session_id not in browser_manager:
        return [types.TextContent(
            type="text",
            text=f"Session {session_id} not found"
        )]
    
    try:
        browser_info = browser_manager[session_id]
        browser = browser_info["browser"]
        
        # Get the active page
        page = await browser.get_current_page()
        
        # Navigate to URL
        await page.goto(url, wait_until="load" if wait_for_load else "domcontentloaded")
        
        # Update current URL
        browser_manager[session_id]["current_url"] = url
        
        logger.info(f"Navigated to {url} in session {session_id}")
        
        return [types.TextContent(
            type="text",
            text=f"Successfully navigated to {url}"
        )]
        
    except Exception as e:
        logger.error(f"Error navigating to URL: {e}")
        return [types.TextContent(
            type="text",
            text=f"Error navigating to URL: {str(e)}"
        )]


async def get_page_content(
    session_id: str,
    content_type: str = "text",
    full_page: bool = False
) -> list[types.TextContent]:
    """Get page content."""
    
    if session_id not in browser_manager:
        return [types.TextContent(
            type="text",
            text=f"Session {session_id} not found"
        )]
    
    try:
        browser_info = browser_manager[session_id]
        browser = browser_info["browser"]
        page = await browser.get_current_page()
        
        if content_type == "html":
            content = await page.content()
        elif content_type == "text":
            content = await page.inner_text("body")
        elif content_type == "screenshot":
            screenshot = await page.screenshot(full_page=full_page)
            # Convert to base64 for transmission
            import base64
            content = base64.b64encode(screenshot).decode()
        else:
            content = "Invalid content type"
        
        return [types.TextContent(
            type="text",
            text=content
        )]
        
    except Exception as e:
        logger.error(f"Error getting page content: {e}")
        return [types.TextContent(
            type="text",
            text=f"Error getting page content: {str(e)}"
        )]


async def create_agent(
    agent_id: str,
    session_id: str,
    llm_provider: str = "anthropic",
    model_name: Optional[str] = None,
    max_actions: int = 100,
    temperature: float = 0.1
) -> list[types.TextContent]:
    """Create an AI agent."""
    
    if agent_id in agent_manager:
        return [types.TextContent(
            type="text",
            text=f"Agent {agent_id} already exists"
        )]
    
    if session_id not in browser_manager:
        return [types.TextContent(
            type="text",
            text=f"Browser session {session_id} not found"
        )]
    
    try:
        # Configure LLM based on provider
        llm_config = configure_llm(llm_provider, model_name, temperature)
        
        # Get browser from session
        browser = browser_manager[session_id]["browser"]
        
        # Create agent
        agent = Agent(
            task="",  # Will be set when executing tasks
            llm=llm_config,
            browser=browser,
            max_actions=max_actions
        )
        
        agent_manager[agent_id] = {
            "agent": agent,
            "session_id": session_id,
            "llm_provider": llm_provider,
            "model_name": model_name,
            "created_at": datetime.now().isoformat(),
            "history": []
        }
        
        logger.info(f"Created agent: {agent_id}")
        
        return [types.TextContent(
            type="text",
            text=f"Agent '{agent_id}' created successfully"
        )]
        
    except Exception as e:
        logger.error(f"Error creating agent: {e}")
        return [types.TextContent(
            type="text",
            text=f"Error creating agent: {str(e)}"
        )]


async def execute_agent_task(
    agent_id: str,
    task: str,
    max_steps: int = 50
) -> list[types.TextContent]:
    """Execute a task using the AI agent."""
    
    if agent_id not in agent_manager:
        return [types.TextContent(
            type="text",
            text=f"Agent {agent_id} not found"
        )]
    
    try:
        agent_info = agent_manager[agent_id]
        agent = agent_info["agent"]
        
        # Set the task
        agent.task = task
        
        # Execute the task
        result = await agent.run(max_steps=max_steps)
        
        # Store result in history
        agent_info["history"].append({
            "task": task,
            "result": str(result),
            "timestamp": datetime.now().isoformat(),
            "max_steps": max_steps
        })
        
        logger.info(f"Executed task for agent {agent_id}: {task}")
        
        return [types.TextContent(
            type="text",
            text=f"Task completed. Result: {result}"
        )]
        
    except Exception as e:
        logger.error(f"Error executing agent task: {e}")
        return [types.TextContent(
            type="text",
            text=f"Error executing task: {str(e)}"
        )]


async def get_agent_history(
    agent_id: str,
    limit: int = 10
) -> list[types.TextContent]:
    """Get agent history."""
    
    if agent_id not in agent_manager:
        return [types.TextContent(
            type="text",
            text=f"Agent {agent_id} not found"
        )]
    
    try:
        agent_info = agent_manager[agent_id]
        history = agent_info["history"][-limit:]
        
        history_text = json.dumps(history, indent=2)
        
        return [types.TextContent(
            type="text",
            text=history_text
        )]
        
    except Exception as e:
        logger.error(f"Error getting agent history: {e}")
        return [types.TextContent(
            type="text",
            text=f"Error getting agent history: {str(e)}"
        )]


async def list_active_sessions() -> list[types.TextContent]:
    """List all active sessions."""
    
    sessions = {
        "browser_sessions": list(browser_manager.keys()),
        "agents": list(agent_manager.keys()),
        "total_browsers": len(browser_manager),
        "total_agents": len(agent_manager)
    }
    
    return [types.TextContent(
        type="text",
        text=json.dumps(sessions, indent=2)
    )]


async def get_session_info(session_id: str) -> list[types.TextContent]:
    """Get session information."""
    
    if session_id not in browser_manager:
        return [types.TextContent(
            type="text",
            text=f"Session {session_id} not found"
        )]
    
    try:
        browser_info = browser_manager[session_id]
        
        # Get associated agents
        associated_agents = [
            agent_id for agent_id, agent_info in agent_manager.items()
            if agent_info.get("session_id") == session_id
        ]
        
        session_info = {
            "session_id": session_id,
            "created_at": browser_info["created_at"],
            "current_url": browser_info["current_url"],
            "config": {
                "headless": browser_info["config"].headless,
                "browser_type": browser_info["config"].browser_type,
                "viewport": f"{browser_info['config'].viewport_width}x{browser_info['config'].viewport_height}"
            },
            "associated_agents": associated_agents
        }
        
        return [types.TextContent(
            type="text",
            text=json.dumps(session_info, indent=2)
        )]
        
    except Exception as e:
        logger.error(f"Error getting session info: {e}")
        return [types.TextContent(
            type="text",
            text=f"Error getting session info: {str(e)}"
        )]


def configure_llm(provider: str, model_name: Optional[str], temperature: float):
    """Configure LLM based on provider."""
    
    if provider == "anthropic":
        from anthropic import Anthropic
        if not ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY not set")
        return Anthropic(api_key=ANTHROPIC_API_KEY)
    
    elif provider == "openai":
        from openai import OpenAI
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not set")
        return OpenAI(api_key=OPENAI_API_KEY)
    
    elif provider == "google":
        import google.generativeai as genai
        if not GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY not set")
        genai.configure(api_key=GOOGLE_API_KEY)
        return genai
    
    elif provider == "groq":
        from groq import Groq
        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY not set")
        return Groq(api_key=GROQ_API_KEY)
    
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")


# Create the Starlette app
starlette_app = create_app()

if __name__ == "__main__":
    import uvicorn
    PORT = int(os.environ.get("PORT", 3000))
    logger.info(f"Starting Browser-Use MCP server on port {PORT}")
    uvicorn.run(starlette_app, host="0.0.0.0", port=PORT)