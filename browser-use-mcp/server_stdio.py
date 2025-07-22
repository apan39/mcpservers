#!/usr/bin/env python3
"""
Browser-Use MCP Server (STDIO version)

A Model Context Protocol server that integrates with the browser-use library
using STDIO transport for compatibility with Cursor and Claude Desktop.
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
from mcp.server import Server
from mcp.server.stdio import stdio_server

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
API_KEY = os.environ.get("API_KEY", "demo-api-key-123")

# Global session storage
sessions = {}


def create_server():
    """Create the MCP server."""
    
    server = Server("browser-use-mcp-server")
    
    # Register tools
    @server.list_tools()
    async def list_tools() -> list[types.Tool]:
        return [
            types.Tool(
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
            types.Tool(
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
            types.Tool(
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
            types.Tool(
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
            types.Tool(
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
            types.Tool(
                name="list_browser_sessions",
                description="List all active browser sessions",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            )
        ]
    
    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
        try:
            logger.info(f"Executing tool: {name} with arguments: {arguments}")
            
            if name == "create_browser_session":
                return await create_browser_session(**arguments)
            elif name == "navigate_to_url":
                return await navigate_to_url(**arguments)
            elif name == "get_page_content":
                return await get_page_content(**arguments)
            elif name == "execute_browser_task":
                return await execute_browser_task(**arguments)
            elif name == "close_browser_session":
                return await close_browser_session(**arguments)
            elif name == "list_browser_sessions":
                return await list_browser_sessions(**arguments)
            else:
                raise ValueError(f"Unknown tool: {name}")
                
        except Exception as e:
            logger.error(f"Error in tool {name}: {e}")
            return [types.TextContent(
                type="text",
                text=f"Error executing {name}: {str(e)}"
            )]
    
    return server


# Tool implementations
async def create_browser_session(session_id: str, headless: bool = True) -> list[types.TextContent]:
    """Create a browser session using playwright."""
    try:
        if session_id in sessions:
            return [types.TextContent(
                type="text",
                text=f"Session '{session_id}' already exists. Use a different session ID or close the existing session first."
            )]
        
        from playwright.async_api import async_playwright
        
        # Start playwright
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=headless)
        page = await browser.new_page()
        
        sessions[session_id] = {
            "playwright": playwright,
            "browser": browser,
            "page": page,
            "created_at": datetime.now().isoformat(),
            "current_url": None,
            "headless": headless
        }
        
        logger.info(f"Created browser session: {session_id}")
        return [types.TextContent(
            type="text",
            text=f"✅ Browser session '{session_id}' created successfully ({'headless' if headless else 'with UI'})"
        )]
        
    except Exception as e:
        logger.error(f"Error creating browser session: {e}")
        return [types.TextContent(
            type="text",
            text=f"❌ Failed to create browser session: {str(e)}"
        )]


async def navigate_to_url(session_id: str, url: str) -> list[types.TextContent]:
    """Navigate to a URL in the specified session."""
    try:
        if session_id not in sessions:
            return [types.TextContent(
                type="text",
                text=f"❌ Session '{session_id}' not found. Create a session first using create_browser_session."
            )]
        
        page = sessions[session_id]["page"]
        
        # Navigate to URL
        await page.goto(url, wait_until="load")
        sessions[session_id]["current_url"] = url
        
        # Get page title for confirmation
        title = await page.title()
        
        logger.info(f"Navigated to {url} in session {session_id}")
        return [types.TextContent(
            type="text",
            text=f"✅ Successfully navigated to {url}\nPage title: {title}"
        )]
        
    except Exception as e:
        logger.error(f"Error navigating to URL: {e}")
        return [types.TextContent(
            type="text",
            text=f"❌ Failed to navigate to {url}: {str(e)}"
        )]


async def get_page_content(session_id: str, include_html: bool = False) -> list[types.TextContent]:
    """Extract content from the current page."""
    try:
        if session_id not in sessions:
            return [types.TextContent(
                type="text",
                text=f"❌ Session '{session_id}' not found. Create a session first using create_browser_session."
            )]
        
        page = sessions[session_id]["page"]
        
        # Get page information
        title = await page.title()
        url = page.url
        
        # Get text content
        text_content = await page.inner_text("body")
        
        # Prepare response
        content_parts = [
            f"📄 Page Title: {title}",
            f"🔗 URL: {url}",
            f"📝 Text Content ({len(text_content)} characters):",
            "=" * 50,
            text_content[:2000] + ("..." if len(text_content) > 2000 else "")
        ]
        
        if include_html:
            html_content = await page.content()
            content_parts.extend([
                "",
                "🏷️ HTML Content:",
                "=" * 50,
                html_content[:1000] + ("..." if len(html_content) > 1000 else "")
            ])
        
        return [types.TextContent(
            type="text",
            text="\n".join(content_parts)
        )]
        
    except Exception as e:
        logger.error(f"Error getting page content: {e}")
        return [types.TextContent(
            type="text",
            text=f"❌ Failed to get page content: {str(e)}"
        )]


async def execute_browser_task(session_id: str, task: str, provider: str = "openai") -> list[types.TextContent]:
    """Execute a browser task using AI agent."""
    try:
        if session_id not in sessions:
            return [types.TextContent(
                type="text",
                text=f"❌ Session '{session_id}' not found. Create a session first using create_browser_session."
            )]
        
        # Import browser-use components
        try:
            from browser_use import Agent
            from browser_use.llm import ChatOpenAI, ChatAnthropic
        except ImportError as e:
            return [types.TextContent(
                type="text",
                text=f"❌ Browser-use library not properly installed: {str(e)}"
            )]
        
        # Get the page from session
        page = sessions[session_id]["page"]
        
        # Create LLM instance based on provider
        try:
            if provider == "openai":
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key or api_key.startswith("demo-"):
                    return [types.TextContent(
                        type="text",
                        text="❌ Valid OpenAI API key required. Set OPENAI_API_KEY environment variable."
                    )]
                llm = ChatOpenAI(
                    model="gpt-4o-mini",
                    api_key=api_key
                )
            elif provider == "anthropic":
                api_key = os.getenv("ANTHROPIC_API_KEY")
                if not api_key or api_key.startswith("demo-"):
                    return [types.TextContent(
                        type="text",
                        text="❌ Valid Anthropic API key required. Set ANTHROPIC_API_KEY environment variable."
                    )]
                llm = ChatAnthropic(
                    model="claude-3-5-sonnet-20241022",
                    api_key=api_key
                )
            else:
                return [types.TextContent(
                    type="text",
                    text=f"❌ Unsupported provider: {provider}. Use 'openai' or 'anthropic'."
                )]
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"❌ Failed to initialize {provider} LLM: {str(e)}"
            )]
        
        # Create and run agent
        try:
            agent = Agent(
                task=task,
                llm=llm,
                page=page
            )
            
            logger.info(f"Starting AI task in session {session_id}: {task}")
            result = await agent.run()
            
            logger.info(f"AI task completed in session {session_id}")
            return [types.TextContent(
                type="text",
                text=f"🤖 AI Task Completed Successfully!\n\n📋 Task: {task}\n\n✅ Result: {str(result)}"
            )]
            
        except Exception as e:
            logger.error(f"Error running AI agent: {e}")
            return [types.TextContent(
                type="text",
                text=f"❌ AI agent execution failed: {str(e)}"
            )]
        
    except Exception as e:
        logger.error(f"Error in execute_browser_task: {e}")
        return [types.TextContent(
            type="text",
            text=f"❌ Failed to execute browser task: {str(e)}"
        )]


async def close_browser_session(session_id: str) -> list[types.TextContent]:
    """Close a browser session and cleanup resources."""
    try:
        if session_id not in sessions:
            return [types.TextContent(
                type="text",
                text=f"❌ Session '{session_id}' not found."
            )]
        
        session_data = sessions[session_id]
        
        # Close browser and playwright
        await session_data["browser"].close()
        await session_data["playwright"].stop()
        
        # Remove from sessions
        del sessions[session_id]
        
        logger.info(f"Closed browser session: {session_id}")
        return [types.TextContent(
            type="text",
            text=f"✅ Browser session '{session_id}' closed successfully"
        )]
        
    except Exception as e:
        logger.error(f"Error closing session: {e}")
        return [types.TextContent(
            type="text",
            text=f"❌ Failed to close session: {str(e)}"
        )]


async def list_browser_sessions() -> list[types.TextContent]:
    """List all active browser sessions."""
    try:
        if not sessions:
            return [types.TextContent(
                type="text",
                text="📋 No active browser sessions"
            )]
        
        session_list = []
        for session_id, session_data in sessions.items():
            session_info = {
                "session_id": session_id,
                "created_at": session_data["created_at"],
                "current_url": session_data.get("current_url", "None"),
                "headless": session_data.get("headless", True)
            }
            session_list.append(session_info)
        
        # Format as a nice table
        output = ["📋 Active Browser Sessions:", "=" * 40]
        for i, session in enumerate(session_list, 1):
            output.extend([
                f"{i}. Session ID: {session['session_id']}",
                f"   Created: {session['created_at']}",
                f"   Current URL: {session['current_url']}",
                f"   Mode: {'Headless' if session['headless'] else 'UI'}",
                ""
            ])
        
        return [types.TextContent(
            type="text",
            text="\n".join(output)
        )]
        
    except Exception as e:
        logger.error(f"Error listing sessions: {e}")
        return [types.TextContent(
            type="text",
            text=f"❌ Failed to list sessions: {str(e)}"
        )]


async def main():
    """Main function to run the server."""
    server = create_server()
    
    # Run the server using stdio transport
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream, write_stream, server.create_initialization_options()
        )


if __name__ == "__main__":
    logger.info("Starting Browser-Use MCP Server (STDIO)")
    asyncio.run(main())