"""Text-related tools for the MCP server."""

import mcp.types as types
from utils.logger import setup_logger

# Set up logging
logger = setup_logger("text_tools")

def register_text_tools(tool_registry):
    """Register text tools with the tool registry.
    
    Args:
        tool_registry: A dictionary to store tool definitions and handlers
    """
    tool_registry["string-operations"] = {
        "definition": types.Tool(
            name="string-operations",
            description="Perform basic string operations",
            inputSchema={
                "type": "object",
                "required": ["text", "operation"],
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The input text to process"
                    },
                    "operation": {
                        "type": "string",
                        "enum": ["uppercase", "lowercase", "reverse"],
                        "description": "The operation to perform"
                    }
                }
            }
        ),
        "handler": string_operations
    }

    tool_registry["word-count"] = {
        "definition": types.Tool(
            name="word-count",
            description="Count the number of words in a text",
            inputSchema={
                "type": "object",
                "required": ["text"],
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The input text to analyze"
                    }
                }
            }
        ),
        "handler": word_count
    }

    tool_registry["format-text"] = {
        "definition": types.Tool(
            name="format-text",
            description="Format text in different ways",
            inputSchema={
                "type": "object",
                "required": ["text", "format_type"],
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The input text to format"
                    },
                    "format_type": {
                        "type": "string",
                        "enum": ["title_case", "sentence_case", "camel_case"],
                        "description": "The format type to apply"
                    }
                }
            }
        ),
        "handler": format_text
    }

async def string_operations(text: str, operation: str) -> list[types.TextContent]:
    """Perform basic string operations."""
    if operation == "uppercase":
        result = text.upper()
    elif operation == "lowercase":
        result = text.lower()
    elif operation == "reverse":
        result = text[::-1]
    else:
        raise ValueError(f"Unknown operation: {operation}")
    
    logger.info(f"Performed {operation} on text")
    return [types.TextContent(type="text", text=result)]

async def word_count(text: str) -> list[types.TextContent]:
    """Count the number of words in a text."""
    words = len(text.split())
    logger.info(f"Counted {words} words in text")
    return [types.TextContent(type="text", text=str(words))]

async def format_text(text: str, format_type: str) -> list[types.TextContent]:
    """Format text in different ways."""
    if format_type == "title_case":
        result = text.title()
    elif format_type == "sentence_case":
        result = text.capitalize()
    elif format_type == "camel_case":
        words = text.split()
        if not words:
            result = ""
        else:
            result = words[0].lower() + ''.join(word.capitalize() for word in words[1:])
    else:
        raise ValueError(f"Unknown format type: {format_type}")
    
    logger.info(f"Formatted text as {format_type}")
    return [types.TextContent(type="text", text=result)]