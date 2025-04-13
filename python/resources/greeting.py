"""Greeting resources for the MCP server."""

import mcp.types as types
from utils.logger import setup_logger

# Set up logging
logger = setup_logger("greeting_resources")

# Define sample resources as simple text
SAMPLE_RESOURCES = {
    "greeting": "Hello! Welcome to the Python MCP server.",
    "help": "This server provides various tools and resources for testing the MCP protocol.",
    "about": "This is a simple MCP server implementation based on the Python SDK example."
}

def register_greeting_resources(app):
    """Register greeting resources with the MCP server."""

    @app.list_resources()
    async def list_resources() -> list[types.Resource]:
        """List available resources."""
        logger.info("Listing resources")
        return [
            types.Resource(
                name=name,
                uri=f"resource:///{name}",
                description=f"A sample text resource named {name}"
            )
            for name in SAMPLE_RESOURCES.keys()
        ]

    @app.read_resource()
    async def read_resource(uri: str) -> str:
        """Read a specific resource."""
        logger.info(f"Reading resource: {uri}")
        
        # Ensure the URI is a string
        uri_str = str(uri)
        logger.info(f"Processing resource URI: {uri_str}")

        # Extract the resource name from the URI
        parts = uri_str.split("/")
        name = parts[-1] if parts else ""
        
        if name not in SAMPLE_RESOURCES:
            logger.error(f"Resource not found: {uri}")
            raise ValueError(f"Unknown resource: {uri}")
        
        # Return the content directly as a string
        content = SAMPLE_RESOURCES[name]
        logger.info(f"Returning content for resource {name}: {content[:30]}...")
        return content