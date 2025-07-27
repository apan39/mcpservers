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
    
    # Register navigation tools
    register_navigation_tools(tool_registry)
    
    # Register interaction tools
    register_interaction_tools(tool_registry)
    
    # Register content tools
    register_content_tools(tool_registry)
    
    # Register tab management tools
    register_tab_management_tools(tool_registry)
    
    # Register file operation tools
    register_file_operation_tools(tool_registry)
    
    # Register javascript tools
    register_javascript_tools(tool_registry)
    
    # Register waiting tools
    register_waiting_tools(tool_registry)
    
    # Register visual tools
    register_visual_tools(tool_registry)
    
    # Register state management tools
    register_state_management_tools(tool_registry)
    
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


def register_navigation_tools(tool_registry: Dict[str, Any]):
    """Register navigation tools."""
    
    # Go back
    tool_registry["go_back"] = {
        "definition": types.Tool(
            name="go_back",
            description="Navigate back in browser history",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Browser session ID"
                    }
                },
                "required": ["session_id"]
            }
        ),
        "handler": go_back
    }
    
    # Go forward
    tool_registry["go_forward"] = {
        "definition": types.Tool(
            name="go_forward",
            description="Navigate forward in browser history",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Browser session ID"
                    }
                },
                "required": ["session_id"]
            }
        ),
        "handler": go_forward
    }
    
    # Refresh page
    tool_registry["refresh_page"] = {
        "definition": types.Tool(
            name="refresh_page",
            description="Refresh the current page",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Browser session ID"
                    }
                },
                "required": ["session_id"]
            }
        ),
        "handler": refresh_page
    }


def register_interaction_tools(tool_registry: Dict[str, Any]):
    """Register interaction tools."""
    
    # Click element
    tool_registry["click_element"] = {
        "definition": types.Tool(
            name="click_element",
            description="Click on an element using selector",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Browser session ID"
                    },
                    "selector": {
                        "type": "string",
                        "description": "CSS selector or XPath for the element"
                    },
                    "selector_type": {
                        "type": "string",
                        "enum": ["css", "xpath", "text", "id"],
                        "description": "Type of selector",
                        "default": "css"
                    },
                    "wait_timeout": {
                        "type": "integer",
                        "description": "Timeout in milliseconds to wait for element",
                        "default": 5000
                    }
                },
                "required": ["session_id", "selector"]
            }
        ),
        "handler": click_element
    }
    
    # Input text
    tool_registry["input_text"] = {
        "definition": types.Tool(
            name="input_text",
            description="Type text into an input field",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Browser session ID"
                    },
                    "selector": {
                        "type": "string",
                        "description": "CSS selector for the input field"
                    },
                    "text": {
                        "type": "string",
                        "description": "Text to type"
                    },
                    "clear_first": {
                        "type": "boolean",
                        "description": "Clear field before typing",
                        "default": True
                    },
                    "press_enter": {
                        "type": "boolean",
                        "description": "Press Enter after typing",
                        "default": False
                    }
                },
                "required": ["session_id", "selector", "text"]
            }
        ),
        "handler": input_text
    }
    
    # Scroll
    tool_registry["scroll"] = {
        "definition": types.Tool(
            name="scroll",
            description="Scroll the page in specified direction",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Browser session ID"
                    },
                    "direction": {
                        "type": "string",
                        "enum": ["up", "down", "left", "right"],
                        "description": "Scroll direction",
                        "default": "down"
                    },
                    "amount": {
                        "type": "integer",
                        "description": "Amount to scroll in pixels",
                        "default": 500
                    }
                },
                "required": ["session_id"]
            }
        ),
        "handler": scroll
    }
    
    # Send keys
    tool_registry["send_keys"] = {
        "definition": types.Tool(
            name="send_keys",
            description="Send keyboard keys (e.g., Tab, Enter, Escape)",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Browser session ID"
                    },
                    "keys": {
                        "type": "string",
                        "description": "Keys to send (e.g., 'Tab', 'Enter', 'Escape', 'Control+a')"
                    },
                    "selector": {
                        "type": "string",
                        "description": "Optional selector to focus before sending keys"
                    }
                },
                "required": ["session_id", "keys"]
            }
        ),
        "handler": send_keys
    }


def register_content_tools(tool_registry: Dict[str, Any]):
    """Register content extraction tools."""
    
    # Extract content
    tool_registry["extract_content"] = {
        "definition": types.Tool(
            name="extract_content",
            description="Extract specific content from the page",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Browser session ID"
                    },
                    "selector": {
                        "type": "string",
                        "description": "CSS selector for content to extract"
                    },
                    "attribute": {
                        "type": "string",
                        "description": "Attribute to extract (e.g., 'text', 'href', 'src')",
                        "default": "text"
                    },
                    "all_matches": {
                        "type": "boolean",
                        "description": "Extract all matching elements",
                        "default": False
                    }
                },
                "required": ["session_id", "selector"]
            }
        ),
        "handler": extract_content
    }
    
    # Get page HTML
    tool_registry["get_page_html"] = {
        "definition": types.Tool(
            name="get_page_html",
            description="Get the HTML content of the current page",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Browser session ID"
                    },
                    "selector": {
                        "type": "string",
                        "description": "Optional selector to get HTML for specific element"
                    },
                    "outer_html": {
                        "type": "boolean",
                        "description": "Get outer HTML instead of inner HTML",
                        "default": False
                    }
                },
                "required": ["session_id"]
            }
        ),
        "handler": get_page_html
    }


def register_tab_management_tools(tool_registry: Dict[str, Any]):
    """Register tab management tools."""
    
    # Create new tab
    tool_registry["create_tab"] = {
        "definition": types.Tool(
            name="create_tab",
            description="Create a new browser tab",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Browser session ID"
                    },
                    "url": {
                        "type": "string",
                        "description": "Optional URL to navigate to in new tab"
                    }
                },
                "required": ["session_id"]
            }
        ),
        "handler": create_tab
    }
    
    # List tabs
    tool_registry["list_tabs"] = {
        "definition": types.Tool(
            name="list_tabs",
            description="List all open tabs in the browser session",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Browser session ID"
                    }
                },
                "required": ["session_id"]
            }
        ),
        "handler": list_tabs
    }
    
    # Switch tab
    tool_registry["switch_tab"] = {
        "definition": types.Tool(
            name="switch_tab",
            description="Switch to a specific tab",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Browser session ID"
                    },
                    "tab_index": {
                        "type": "integer",
                        "description": "Tab index to switch to (0-based)"
                    }
                },
                "required": ["session_id", "tab_index"]
            }
        ),
        "handler": switch_tab
    }
    
    # Close tab
    tool_registry["close_tab"] = {
        "definition": types.Tool(
            name="close_tab",
            description="Close the current tab or a specific tab",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Browser session ID"
                    },
                    "tab_index": {
                        "type": "integer",
                        "description": "Optional tab index to close (0-based). If not provided, closes current tab"
                    }
                },
                "required": ["session_id"]
            }
        ),
        "handler": close_tab
    }


def register_file_operation_tools(tool_registry: Dict[str, Any]):
    """Register file operation tools."""
    
    # Upload file
    tool_registry["upload_file"] = {
        "definition": types.Tool(
            name="upload_file",
            description="Upload a file using a file input element",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Browser session ID"
                    },
                    "selector": {
                        "type": "string",
                        "description": "CSS selector for the file input element"
                    },
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file to upload"
                    }
                },
                "required": ["session_id", "selector", "file_path"]
            }
        ),
        "handler": upload_file
    }
    
    # Download file
    tool_registry["download_file"] = {
        "definition": types.Tool(
            name="download_file",
            description="Download a file by clicking a download link",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Browser session ID"
                    },
                    "selector": {
                        "type": "string",
                        "description": "CSS selector for the download link/button"
                    },
                    "download_path": {
                        "type": "string",
                        "description": "Optional path to save the downloaded file"
                    }
                },
                "required": ["session_id", "selector"]
            }
        ),
        "handler": download_file
    }


def register_javascript_tools(tool_registry: Dict[str, Any]):
    """Register JavaScript execution tools."""
    
    # Execute JavaScript
    tool_registry["execute_javascript"] = {
        "definition": types.Tool(
            name="execute_javascript",
            description="Execute JavaScript code on the page",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Browser session ID"
                    },
                    "code": {
                        "type": "string",
                        "description": "JavaScript code to execute"
                    },
                    "return_result": {
                        "type": "boolean",
                        "description": "Whether to return the result of the execution",
                        "default": True
                    }
                },
                "required": ["session_id", "code"]
            }
        ),
        "handler": execute_javascript
    }


def register_waiting_tools(tool_registry: Dict[str, Any]):
    """Register waiting tools."""
    
    # Wait for element
    tool_registry["wait_for_element"] = {
        "definition": types.Tool(
            name="wait_for_element",
            description="Wait for an element to appear on the page",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Browser session ID"
                    },
                    "selector": {
                        "type": "string",
                        "description": "CSS selector for the element to wait for"
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Timeout in milliseconds",
                        "default": 10000
                    },
                    "state": {
                        "type": "string",
                        "enum": ["attached", "detached", "visible", "hidden"],
                        "description": "Element state to wait for",
                        "default": "visible"
                    }
                },
                "required": ["session_id", "selector"]
            }
        ),
        "handler": wait_for_element
    }
    
    # Wait for load
    tool_registry["wait_for_load"] = {
        "definition": types.Tool(
            name="wait_for_load",
            description="Wait for page to finish loading",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Browser session ID"
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Timeout in milliseconds",
                        "default": 30000
                    },
                    "wait_until": {
                        "type": "string",
                        "enum": ["load", "domcontentloaded", "networkidle"],
                        "description": "Load state to wait for",
                        "default": "load"
                    }
                },
                "required": ["session_id"]
            }
        ),
        "handler": wait_for_load
    }


def register_visual_tools(tool_registry: Dict[str, Any]):
    """Register visual tools."""
    
    # Take screenshot (enhanced)
    tool_registry["take_screenshot"] = {
        "definition": types.Tool(
            name="take_screenshot",
            description="Take a screenshot of the page or specific element",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Browser session ID"
                    },
                    "selector": {
                        "type": "string",
                        "description": "Optional CSS selector for element to screenshot"
                    },
                    "full_page": {
                        "type": "boolean",
                        "description": "Take full page screenshot",
                        "default": False
                    },
                    "save_path": {
                        "type": "string",
                        "description": "Optional path to save screenshot"
                    },
                    "quality": {
                        "type": "integer",
                        "description": "JPEG quality (0-100)",
                        "default": 90
                    }
                },
                "required": ["session_id"]
            }
        ),
        "handler": take_screenshot
    }


def register_state_management_tools(tool_registry: Dict[str, Any]):
    """Register state management tools."""
    
    # Get browser state
    tool_registry["get_browser_state"] = {
        "definition": types.Tool(
            name="get_browser_state",
            description="Get comprehensive browser state information",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Browser session ID"
                    },
                    "include_dom": {
                        "type": "boolean",
                        "description": "Include DOM structure in response",
                        "default": False
                    }
                },
                "required": ["session_id"]
            }
        ),
        "handler": get_browser_state
    }
    
    # Get DOM elements
    tool_registry["get_dom_elements"] = {
        "definition": types.Tool(
            name="get_dom_elements",
            description="Get clickable and interactive DOM elements",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Browser session ID"
                    },
                    "highlight": {
                        "type": "boolean",
                        "description": "Highlight elements on the page",
                        "default": True
                    },
                    "element_types": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Filter by element types (e.g., ['button', 'input', 'link'])"
                    }
                },
                "required": ["session_id"]
            }
        ),
        "handler": get_dom_elements
    }


# Tool handler implementations for new tools

async def go_back(session_id: str) -> list[types.TextContent]:
    """Go back in browser history."""
    if session_id not in browser_manager:
        return [types.TextContent(type="text", text=f"Session {session_id} not found")]
    
    try:
        browser = browser_manager[session_id]["browser"]
        page = await browser.get_current_page()
        await page.go_back()
        
        return [types.TextContent(type="text", text="Successfully navigated back")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error going back: {str(e)}")]


async def go_forward(session_id: str) -> list[types.TextContent]:
    """Go forward in browser history."""
    if session_id not in browser_manager:
        return [types.TextContent(type="text", text=f"Session {session_id} not found")]
    
    try:
        browser = browser_manager[session_id]["browser"]
        page = await browser.get_current_page()
        await page.go_forward()
        
        return [types.TextContent(type="text", text="Successfully navigated forward")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error going forward: {str(e)}")]


async def refresh_page(session_id: str) -> list[types.TextContent]:
    """Refresh the current page."""
    if session_id not in browser_manager:
        return [types.TextContent(type="text", text=f"Session {session_id} not found")]
    
    try:
        browser = browser_manager[session_id]["browser"]
        page = await browser.get_current_page()
        await page.reload()
        
        return [types.TextContent(type="text", text="Page refreshed successfully")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error refreshing page: {str(e)}")]


async def click_element(
    session_id: str,
    selector: str,
    selector_type: str = "css",
    wait_timeout: int = 5000
) -> list[types.TextContent]:
    """Click on an element."""
    if session_id not in browser_manager:
        return [types.TextContent(type="text", text=f"Session {session_id} not found")]
    
    try:
        browser = browser_manager[session_id]["browser"]
        page = await browser.get_current_page()
        
        # Wait for element and click
        if selector_type == "xpath":
            await page.wait_for_selector(f"xpath={selector}", timeout=wait_timeout)
            await page.click(f"xpath={selector}")
        elif selector_type == "text":
            await page.click(f"text={selector}")
        elif selector_type == "id":
            await page.click(f"#{selector}")
        else:  # css
            await page.wait_for_selector(selector, timeout=wait_timeout)
            await page.click(selector)
        
        return [types.TextContent(type="text", text=f"Successfully clicked element: {selector}")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error clicking element: {str(e)}")]


async def input_text(
    session_id: str,
    selector: str,
    text: str,
    clear_first: bool = True,
    press_enter: bool = False
) -> list[types.TextContent]:
    """Input text into a field."""
    if session_id not in browser_manager:
        return [types.TextContent(type="text", text=f"Session {session_id} not found")]
    
    try:
        browser = browser_manager[session_id]["browser"]
        page = await browser.get_current_page()
        
        if clear_first:
            await page.fill(selector, text)
        else:
            await page.type(selector, text)
        
        if press_enter:
            await page.press(selector, "Enter")
        
        return [types.TextContent(type="text", text=f"Successfully entered text into: {selector}")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error entering text: {str(e)}")]


async def scroll(
    session_id: str,
    direction: str = "down",
    amount: int = 500
) -> list[types.TextContent]:
    """Scroll the page."""
    if session_id not in browser_manager:
        return [types.TextContent(type="text", text=f"Session {session_id} not found")]
    
    try:
        browser = browser_manager[session_id]["browser"]
        page = await browser.get_current_page()
        
        if direction == "down":
            await page.mouse.wheel(0, amount)
        elif direction == "up":
            await page.mouse.wheel(0, -amount)
        elif direction == "right":
            await page.mouse.wheel(amount, 0)
        elif direction == "left":
            await page.mouse.wheel(-amount, 0)
        
        return [types.TextContent(type="text", text=f"Scrolled {direction} by {amount}px")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error scrolling: {str(e)}")]


async def send_keys(
    session_id: str,
    keys: str,
    selector: Optional[str] = None
) -> list[types.TextContent]:
    """Send keyboard keys."""
    if session_id not in browser_manager:
        return [types.TextContent(type="text", text=f"Session {session_id} not found")]
    
    try:
        browser = browser_manager[session_id]["browser"]
        page = await browser.get_current_page()
        
        if selector:
            await page.press(selector, keys)
        else:
            await page.keyboard.press(keys)
        
        return [types.TextContent(type="text", text=f"Successfully sent keys: {keys}")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error sending keys: {str(e)}")]


async def extract_content(
    session_id: str,
    selector: str,
    attribute: str = "text",
    all_matches: bool = False
) -> list[types.TextContent]:
    """Extract content from elements."""
    if session_id not in browser_manager:
        return [types.TextContent(type="text", text=f"Session {session_id} not found")]
    
    try:
        browser = browser_manager[session_id]["browser"]
        page = await browser.get_current_page()
        
        if all_matches:
            if attribute == "text":
                content = await page.locator(selector).all_text_contents()
            else:
                content = await page.locator(selector).get_attribute(attribute)
        else:
            if attribute == "text":
                content = await page.locator(selector).text_content()
            else:
                content = await page.locator(selector).get_attribute(attribute)
        
        return [types.TextContent(type="text", text=str(content))]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error extracting content: {str(e)}")]


async def get_page_html(
    session_id: str,
    selector: Optional[str] = None,
    outer_html: bool = False
) -> list[types.TextContent]:
    """Get HTML content."""
    if session_id not in browser_manager:
        return [types.TextContent(type="text", text=f"Session {session_id} not found")]
    
    try:
        browser = browser_manager[session_id]["browser"]
        page = await browser.get_current_page()
        
        if selector:
            if outer_html:
                html = await page.locator(selector).evaluate("el => el.outerHTML")
            else:
                html = await page.locator(selector).inner_html()
        else:
            html = await page.content()
        
        return [types.TextContent(type="text", text=html)]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error getting HTML: {str(e)}")]


async def create_tab(
    session_id: str,
    url: Optional[str] = None
) -> list[types.TextContent]:
    """Create a new tab."""
    if session_id not in browser_manager:
        return [types.TextContent(type="text", text=f"Session {session_id} not found")]
    
    try:
        browser = browser_manager[session_id]["browser"]
        context = await browser.new_context()
        page = await context.new_page()
        
        if url:
            await page.goto(url)
        
        return [types.TextContent(type="text", text=f"Created new tab{' and navigated to ' + url if url else ''}")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error creating tab: {str(e)}")]


async def list_tabs(session_id: str) -> list[types.TextContent]:
    """List all tabs."""
    if session_id not in browser_manager:
        return [types.TextContent(type="text", text=f"Session {session_id} not found")]
    
    try:
        browser = browser_manager[session_id]["browser"]
        contexts = browser.contexts
        
        tabs_info = []
        for i, context in enumerate(contexts):
            pages = context.pages
            for j, page in enumerate(pages):
                tabs_info.append({
                    "context_index": i,
                    "page_index": j,
                    "url": page.url,
                    "title": await page.title()
                })
        
        return [types.TextContent(type="text", text=json.dumps(tabs_info, indent=2))]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error listing tabs: {str(e)}")]


async def switch_tab(
    session_id: str,
    tab_index: int
) -> list[types.TextContent]:
    """Switch to a specific tab."""
    if session_id not in browser_manager:
        return [types.TextContent(type="text", text=f"Session {session_id} not found")]
    
    try:
        browser = browser_manager[session_id]["browser"]
        contexts = browser.contexts
        
        # Simple implementation - switch to page in first context
        if contexts and len(contexts[0].pages) > tab_index:
            page = contexts[0].pages[tab_index]
            await page.bring_to_front()
            return [types.TextContent(type="text", text=f"Switched to tab {tab_index}")]
        else:
            return [types.TextContent(type="text", text=f"Tab {tab_index} not found")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error switching tab: {str(e)}")]


async def close_tab(
    session_id: str,
    tab_index: Optional[int] = None
) -> list[types.TextContent]:
    """Close a tab."""
    if session_id not in browser_manager:
        return [types.TextContent(type="text", text=f"Session {session_id} not found")]
    
    try:
        browser = browser_manager[session_id]["browser"]
        
        if tab_index is not None:
            contexts = browser.contexts
            if contexts and len(contexts[0].pages) > tab_index:
                await contexts[0].pages[tab_index].close()
                return [types.TextContent(type="text", text=f"Closed tab {tab_index}")]
            else:
                return [types.TextContent(type="text", text=f"Tab {tab_index} not found")]
        else:
            page = await browser.get_current_page()
            await page.close()
            return [types.TextContent(type="text", text="Closed current tab")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error closing tab: {str(e)}")]


async def upload_file(
    session_id: str,
    selector: str,
    file_path: str
) -> list[types.TextContent]:
    """Upload a file."""
    if session_id not in browser_manager:
        return [types.TextContent(type="text", text=f"Session {session_id} not found")]
    
    try:
        browser = browser_manager[session_id]["browser"]
        page = await browser.get_current_page()
        
        await page.set_input_files(selector, file_path)
        
        return [types.TextContent(type="text", text=f"Successfully uploaded file: {file_path}")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error uploading file: {str(e)}")]


async def download_file(
    session_id: str,
    selector: str,
    download_path: Optional[str] = None
) -> list[types.TextContent]:
    """Download a file."""
    if session_id not in browser_manager:
        return [types.TextContent(type="text", text=f"Session {session_id} not found")]
    
    try:
        browser = browser_manager[session_id]["browser"]
        page = await browser.get_current_page()
        
        # Start waiting for download before clicking
        async with page.expect_download() as download_info:
            await page.click(selector)
        download = await download_info.value
        
        if download_path:
            await download.save_as(download_path)
            return [types.TextContent(type="text", text=f"Downloaded file to: {download_path}")]
        else:
            return [types.TextContent(type="text", text=f"Downloaded file: {download.suggested_filename}")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error downloading file: {str(e)}")]


async def execute_javascript(
    session_id: str,
    code: str,
    return_result: bool = True
) -> list[types.TextContent]:
    """Execute JavaScript code."""
    if session_id not in browser_manager:
        return [types.TextContent(type="text", text=f"Session {session_id} not found")]
    
    try:
        browser = browser_manager[session_id]["browser"]
        page = await browser.get_current_page()
        
        if return_result:
            result = await page.evaluate(code)
            return [types.TextContent(type="text", text=str(result))]
        else:
            await page.evaluate(code)
            return [types.TextContent(type="text", text="JavaScript executed successfully")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error executing JavaScript: {str(e)}")]


async def wait_for_element(
    session_id: str,
    selector: str,
    timeout: int = 10000,
    state: str = "visible"
) -> list[types.TextContent]:
    """Wait for an element."""
    if session_id not in browser_manager:
        return [types.TextContent(type="text", text=f"Session {session_id} not found")]
    
    try:
        browser = browser_manager[session_id]["browser"]
        page = await browser.get_current_page()
        
        await page.wait_for_selector(selector, timeout=timeout, state=state)
        
        return [types.TextContent(type="text", text=f"Element {selector} is now {state}")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error waiting for element: {str(e)}")]


async def wait_for_load(
    session_id: str,
    timeout: int = 30000,
    wait_until: str = "load"
) -> list[types.TextContent]:
    """Wait for page to load."""
    if session_id not in browser_manager:
        return [types.TextContent(type="text", text=f"Session {session_id} not found")]
    
    try:
        browser = browser_manager[session_id]["browser"]
        page = await browser.get_current_page()
        
        await page.wait_for_load_state(wait_until, timeout=timeout)
        
        return [types.TextContent(type="text", text=f"Page loaded ({wait_until})")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error waiting for load: {str(e)}")]


async def take_screenshot(
    session_id: str,
    selector: Optional[str] = None,
    full_page: bool = False,
    save_path: Optional[str] = None,
    quality: int = 90
) -> list[types.TextContent]:
    """Take a screenshot."""
    if session_id not in browser_manager:
        return [types.TextContent(type="text", text=f"Session {session_id} not found")]
    
    try:
        browser = browser_manager[session_id]["browser"]
        page = await browser.get_current_page()
        
        screenshot_options = {
            "full_page": full_page,
            "quality": quality,
            "type": "jpeg" if quality < 100 else "png"
        }
        
        if save_path:
            screenshot_options["path"] = save_path
        
        if selector:
            element = page.locator(selector)
            screenshot = await element.screenshot(**screenshot_options)
        else:
            screenshot = await page.screenshot(**screenshot_options)
        
        if save_path:
            return [types.TextContent(type="text", text=f"Screenshot saved to: {save_path}")]
        else:
            import base64
            screenshot_b64 = base64.b64encode(screenshot).decode()
            return [types.TextContent(type="text", text=screenshot_b64)]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error taking screenshot: {str(e)}")]


async def get_browser_state(
    session_id: str,
    include_dom: bool = False
) -> list[types.TextContent]:
    """Get browser state."""
    if session_id not in browser_manager:
        return [types.TextContent(type="text", text=f"Session {session_id} not found")]
    
    try:
        browser = browser_manager[session_id]["browser"]
        page = await browser.get_current_page()
        
        state = {
            "url": page.url,
            "title": await page.title(),
            "ready_state": await page.evaluate("document.readyState"),
            "viewport": page.viewport_size,
            "cookies": await page.context.cookies(),
        }
        
        if include_dom:
            # Get basic DOM information
            try:
                # Get all interactive elements
                elements = await page.evaluate("""
                    () => {
                        const clickable = document.querySelectorAll('a, button, input, select, textarea, [onclick], [role="button"]');
                        return Array.from(clickable).slice(0, 50).map((el, i) => ({
                            index: i,
                            tag: el.tagName.toLowerCase(),
                            type: el.type || '',
                            text: el.textContent?.trim().slice(0, 100) || '',
                            id: el.id || '',
                            class: el.className || ''
                        }));
                    }
                """)
                state["interactive_elements"] = elements
            except Exception as e:
                state["interactive_elements"] = f"Error getting elements: {str(e)}"
        
        return [types.TextContent(type="text", text=json.dumps(state, indent=2, default=str))]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error getting browser state: {str(e)}")]


async def get_dom_elements(
    session_id: str,
    highlight: bool = True,
    element_types: Optional[List[str]] = None
) -> list[types.TextContent]:
    """Get DOM elements."""
    if session_id not in browser_manager:
        return [types.TextContent(type="text", text=f"Session {session_id} not found")]
    
    try:
        browser = browser_manager[session_id]["browser"]
        page = await browser.get_current_page()
        
        # Get DOM elements using JavaScript evaluation
        elements = await page.evaluate("""
            () => {
                const all_elements = document.querySelectorAll('*');
                const interactive = [];
                
                all_elements.forEach((el, i) => {
                    const style = window.getComputedStyle(el);
                    const rect = el.getBoundingClientRect();
                    
                    // Check if element is interactive and visible
                    const isClickable = el.tagName.match(/^(A|BUTTON|INPUT|SELECT|TEXTAREA)$/) || 
                                       el.onclick || 
                                       el.getAttribute('role') === 'button' ||
                                       style.cursor === 'pointer';
                    
                    const isVisible = style.display !== 'none' && 
                                     style.visibility !== 'hidden' && 
                                     rect.width > 0 && rect.height > 0;
                    
                    if (isClickable && isVisible && interactive.length < 100) {
                        interactive.push({
                            index: interactive.length,
                            tag: el.tagName.toLowerCase(),
                            type: el.type || '',
                            text: (el.textContent || el.value || el.placeholder || '').trim().slice(0, 100),
                            id: el.id || '',
                            class: Array.from(el.classList).join(' '),
                            selector: `${el.tagName.toLowerCase()}${el.id ? '#' + el.id : ''}${el.className ? '.' + Array.from(el.classList).join('.') : ''}`,
                            position: {
                                x: Math.round(rect.left),
                                y: Math.round(rect.top),
                                width: Math.round(rect.width),
                                height: Math.round(rect.height)
                            }
                        });
                    }
                });
                
                return {
                    interactive_elements: interactive,
                    total_elements: all_elements.length,
                    page_title: document.title,
                    page_url: window.location.href
                };
            }
        """)
        
        # Add highlighting if requested
        if highlight:
            await page.evaluate("""
                () => {
                    // Remove existing highlights
                    document.querySelectorAll('.mcp-highlight').forEach(el => el.remove());
                    
                    // Add highlights to interactive elements
                    const clickable = document.querySelectorAll('a, button, input, select, textarea, [onclick], [role="button"]');
                    clickable.forEach((el, i) => {
                        if (i < 50) {  // Limit to first 50 elements
                            const highlight = document.createElement('div');
                            const rect = el.getBoundingClientRect();
                            highlight.className = 'mcp-highlight';
                            highlight.style.cssText = `
                                position: fixed;
                                top: ${rect.top}px;
                                left: ${rect.left}px;
                                width: ${rect.width}px;
                                height: ${rect.height}px;
                                border: 2px solid red;
                                background: rgba(255, 0, 0, 0.1);
                                pointer-events: none;
                                z-index: 10000;
                                box-sizing: border-box;
                            `;
                            document.body.appendChild(highlight);
                        }
                    });
                    
                    // Remove highlights after 3 seconds
                    setTimeout(() => {
                        document.querySelectorAll('.mcp-highlight').forEach(el => el.remove());
                    }, 3000);
                }
            """)
        
        return [types.TextContent(type="text", text=json.dumps(elements, indent=2))]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error getting DOM elements: {str(e)}")]


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