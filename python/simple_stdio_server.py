#!/usr/bin/env python3
"""
Simple MCP stdio server for Claude Code CLI.
"""

import asyncio
import json
import sys
from tools.math_tools import add_numbers, multiply_numbers, calculate_percentage
from tools.text_tools import string_operations, word_count, format_text
from tools.crawl4ai_tools import crawl_url_with_options


TOOLS = {
    "add-numbers": {
        "name": "add-numbers",
        "description": "Add two numbers together",
        "inputSchema": {
            "type": "object",
            "required": ["a", "b"],
            "properties": {
                "a": {"type": "number", "description": "First number"},
                "b": {"type": "number", "description": "Second number"}
            }
        }
    },
    "multiply-numbers": {
        "name": "multiply-numbers",
        "description": "Multiply two numbers together",
        "inputSchema": {
            "type": "object",
            "required": ["a", "b"],
            "properties": {
                "a": {"type": "number", "description": "First number"},
                "b": {"type": "number", "description": "Second number"}
            }
        }
    },
    "calculate-percentage": {
        "name": "calculate-percentage",
        "description": "Calculate percentage of a value",
        "inputSchema": {
            "type": "object",
            "required": ["value", "percentage"],
            "properties": {
                "value": {"type": "number", "description": "The base value"},
                "percentage": {"type": "number", "description": "The percentage to calculate"}
            }
        }
    },
    "string-operations": {
        "name": "string-operations",
        "description": "Perform basic string operations",
        "inputSchema": {
            "type": "object",
            "required": ["text", "operation"],
            "properties": {
                "text": {"type": "string", "description": "The input text to process"},
                "operation": {"type": "string", "enum": ["uppercase", "lowercase", "reverse"], "description": "The operation to perform"}
            }
        }
    },
    "word-count": {
        "name": "word-count",
        "description": "Count the number of words in a text",
        "inputSchema": {
            "type": "object",
            "required": ["text"],
            "properties": {
                "text": {"type": "string", "description": "The input text to analyze"}
            }
        }
    },
    "format-text": {
        "name": "format-text",
        "description": "Format text in different ways",
        "inputSchema": {
            "type": "object",
            "required": ["text", "format_type"],
            "properties": {
                "text": {"type": "string", "description": "The input text to format"},
                "format_type": {"type": "string", "enum": ["title_case", "sentence_case", "camel_case"], "description": "The format type to apply"}
            }
        }
    },
    "crawl-url": {
        "name": "crawl-url",
        "description": "Crawl a URL and return extracted text content using crawl4ai",
        "inputSchema": {
            "type": "object",
            "required": ["url"],
            "properties": {
                "url": {"type": "string", "description": "The URL to crawl"},
                "max_pages": {"type": "integer", "description": "Maximum number of pages to crawl", "default": 1}
            }
        }
    }
}

TOOL_HANDLERS = {
    "add-numbers": add_numbers,
    "multiply-numbers": multiply_numbers,
    "calculate-percentage": calculate_percentage,
    "string-operations": string_operations,
    "word-count": word_count,
    "format-text": format_text,
    "crawl-url": crawl_url_with_options
}


async def handle_request(request):
    """Handle a JSON-RPC request."""
    try:
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")

        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {},
                        "logging": {}
                    },
                    "serverInfo": {
                        "name": "python-mcp-tools",
                        "version": "1.0.0"
                    }
                }
            }
        
        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "tools": list(TOOLS.values())
                }
            }
        
        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            if tool_name not in TOOL_HANDLERS:
                raise ValueError(f"Unknown tool: {tool_name}")
            
            handler = TOOL_HANDLERS[tool_name]
            result = await handler(**arguments)
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [{"type": "text", "text": content.text} for content in result]
                }
            }
        
        else:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }

    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "error": {
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            }
        }


async def main():
    """Main stdio loop."""
    while True:
        try:
            line = await asyncio.to_thread(sys.stdin.readline)
            if not line:
                break
                
            line = line.strip()
            if not line:
                continue
                
            request = json.loads(line)
            response = await handle_request(request)
            
            print(json.dumps(response), flush=True)
            
        except json.JSONDecodeError:
            continue
        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32700,
                    "message": f"Parse error: {str(e)}"
                }
            }
            print(json.dumps(error_response), flush=True)


if __name__ == "__main__":
    asyncio.run(main())