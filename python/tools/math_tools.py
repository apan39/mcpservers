"""Math-related tools for the MCP server."""

import mcp.types as types
from utils.logger import setup_logger

# Set up logging
logger = setup_logger("math_tools")

def register_math_tools(tool_registry):
    """Register math tools with the tool registry.
    
    Args:
        tool_registry: A dictionary to store tool definitions and handlers
    """
    tool_registry["add-numbers"] = {
        "definition": types.Tool(
            name="add-numbers",
            description="Add two numbers together",
            inputSchema={
                "type": "object",
                "required": ["a", "b"],
                "properties": {
                    "a": {
                        "type": "number",
                        "description": "First number"
                    },
                    "b": {
                        "type": "number",
                        "description": "Second number"
                    }
                }
            }
        ),
        "handler": add_numbers
    }

    tool_registry["multiply-numbers"] = {
        "definition": types.Tool(
            name="multiply-numbers",
            description="Multiply two numbers together",
            inputSchema={
                "type": "object",
                "required": ["a", "b"],
                "properties": {
                    "a": {
                        "type": "number",
                        "description": "First number"
                    },
                    "b": {
                        "type": "number",
                        "description": "Second number"
                    }
                }
            }
        ),
        "handler": multiply_numbers
    }

    tool_registry["calculate-percentage"] = {
        "definition": types.Tool(
            name="calculate-percentage",
            description="Calculate percentage of a value",
            inputSchema={
                "type": "object",
                "required": ["value", "percentage"],
                "properties": {
                    "value": {
                        "type": "number",
                        "description": "The base value"
                    },
                    "percentage": {
                        "type": "number",
                        "description": "The percentage to calculate"
                    }
                }
            }
        ),
        "handler": calculate_percentage
    }

async def add_numbers(a: float, b: float) -> list[types.TextContent]:
    """Add two numbers together."""
    result = a + b
    logger.info(f"Calculated {a} + {b} = {result}")
    return [types.TextContent(type="text", text=str(result))]

async def multiply_numbers(a: float, b: float) -> list[types.TextContent]:
    """Multiply two numbers together."""
    result = a * b
    logger.info(f"Calculated {a} × {b} = {result}")
    return [types.TextContent(type="text", text=str(result))]

async def calculate_percentage(value: float, percentage: float) -> list[types.TextContent]:
    """Calculate percentage of a value."""
    result = (value * percentage) / 100
    logger.info(f"Calculated {percentage}% of {value} = {result}")
    return [types.TextContent(type="text", text=str(result))]