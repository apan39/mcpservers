"""crawl4ai tools for the MCP server."""

import mcp.types as types
from utils.logger import setup_logger

# Set up logging
logger = setup_logger("crawl4ai_tools")

def register_crawl4ai_tools(tool_registry):
    """Register crawl4ai tools with the tool registry."""
    tool_registry["crawl-url"] = {
        "definition": types.Tool(
            name="crawl-url",
            description="Crawl a URL and return extracted text content using crawl4ai.",
            inputSchema={
                "type": "object",
                "required": ["url"],
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL to crawl"
                    }
                }
            }
        ),
        "handler": crawl_url
    }

async def crawl_url(url: str) -> list[types.TextContent]:
    """Crawl a URL and return extracted text content."""
    try:
        from crawl4ai import Crawler
        crawler = Crawler()
        result = crawler.crawl(url)
        # Assume result is a dict with a 'text' field or similar
        text = result.get("text", str(result))
        logger.info(f"Crawled {url} successfully.")
        return [types.TextContent(type="text", text=text)]
    except Exception as e:
        logger.error(f"Failed to crawl {url}: {e}")
        return [types.TextContent(type="text", text=f"Error crawling {url}: {e}")]