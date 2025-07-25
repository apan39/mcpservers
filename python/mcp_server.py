#!/usr/bin/env python3
"""
Simple HTTP MCP Server implementation.
"""

import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List

import uvicorn
from mcp.server.lowlevel import Server
from mcp.types import Tool, TextContent
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from tools.math_tools import register_math_tools
from tools.text_tools import register_text_tools
from tools.crawl4ai_tools import register_crawl4ai_tools
from tools.coolify_tools import register_coolify_tools
from utils.logger import setup_logger

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
logger = setup_logger("simple_http_server", logging.INFO)

# Global tool registry
tool_registry = {}

def setup_tools():
    """Setup all MCP tools."""
    register_math_tools(tool_registry)
    register_text_tools(tool_registry)
    register_crawl4ai_tools(tool_registry)
    register_coolify_tools(tool_registry)

async def handle_mcp_request(request: Request) -> JSONResponse:
    """Handle MCP JSON-RPC requests."""
    try:
        logger.info(f"Received MCP request: {request.method} {request.url}")
        
        # Check authorization header
        auth_header = request.headers.get('authorization')
        expected_key = os.getenv('MCP_API_KEY', 'demo-api-key-123')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            logger.warning("Missing or invalid Authorization header")
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32001, "message": "Missing or invalid Authorization header"}
            }, status_code=401)
        
        token = auth_header[7:]  # Remove 'Bearer ' prefix
        if token != expected_key:
            logger.warning("Invalid API key")
            return JSONResponse({
                "jsonrpc": "2.0", 
                "id": None,
                "error": {"code": -32001, "message": "Invalid API key"}
            }, status_code=401)
        
        data = await request.json()
        logger.info(f"Request data: {data}")
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
                        "name": "python-mcp-tools",
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
                    # Convert Tool object to dict for JSON serialization
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
                "result": {"tools": tools}
            })
        
        elif method == 'tools/call':
            tool_name = params.get('name')
            arguments = params.get('arguments', {})
            
            if tool_name not in tool_registry:
                return JSONResponse({
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {"code": -32601, "message": f"Unknown tool: {tool_name}"}
                })
            
            try:
                handler = tool_registry[tool_name]["handler"]
                result = await handler(**arguments)
                logger.info(f"Successfully executed tool: {tool_name}")
                
                # Convert result to JSON-serializable format
                if hasattr(result, '__dict__'):
                    result = [{"type": "text", "text": str(result)}]
                elif isinstance(result, list):
                    # Handle list of TextContent objects
                    json_result = []
                    for item in result:
                        if hasattr(item, 'type') and hasattr(item, 'text'):
                            json_result.append({"type": item.type, "text": item.text})
                        else:
                            json_result.append({"type": "text", "text": str(item)})
                    result = json_result
                else:
                    result = [{"type": "text", "text": str(result)}]
                
                return JSONResponse({
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {"content": result}
                })
                
            except Exception as e:
                logger.error(f"Error executing tool {tool_name}: {str(e)}")
                return JSONResponse({
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {"code": -32603, "message": f"Tool execution error: {str(e)}"}
                })
        
        else:
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32601, "message": f"Unknown method: {method}"}
            })
    
    except Exception as e:
        logger.error(f"Error handling MCP request: {str(e)}")
        logger.error(f"Error type: {type(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": None,
            "error": {"code": -32603, "message": f"Internal server error: {str(e)}"}
        })

async def health_check(request: Request) -> JSONResponse:
    """Health check endpoint."""
    return JSONResponse({
        "status": "healthy",
        "service": "simple-mcp-http-server"
    })

def create_app() -> Starlette:
    """Create the Starlette application."""
    setup_tools()
    
    app = Starlette(
        debug=False,
        routes=[
            Route("/mcp", handle_mcp_request, methods=["POST"]),
            Route("/mcp/", handle_mcp_request, methods=["POST"]),
            Route("/health", health_check, methods=["GET"]),
        ],
    )
    
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
    """CLI entry point."""
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "3009"))
    log_level = os.getenv("LOG_LEVEL", "INFO").lower()
    
    logger.info(f"Starting simple HTTP MCP server on {host}:{port}")
    
    app = create_app()
    uvicorn.run(app, host=host, port=port, log_level=log_level, access_log=True)

if __name__ == "__main__":
    main()