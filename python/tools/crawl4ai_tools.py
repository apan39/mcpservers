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
                    },
                    "depth": {
                        "type": "integer",
                        "description": "How deep to crawl from the starting URL",
                        "default": 1
                    },
                    "max_pages": {
                        "type": "integer",
                        "description": "Maximum number of pages to crawl",
                        "default": 10
                    },
                    "user_agent": {
                        "type": "string",
                        "description": "Custom user agent string for crawling"
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Timeout for crawling in seconds",
                        "default": 30
                    },
                    "headless": {
                        "type": "boolean",
                        "description": "Whether to use headless browser mode",
                        "default": False
                    }
                }
            }
        ),
        "handler": crawl_url_with_options
    }

async def crawl_url_with_options(
    url: str,
    depth: int = 1,
    max_pages: int = 10,
    user_agent: str = None,
    timeout: int = 30,
    headless: bool = False
) -> list[types.TextContent]:
    """Crawl a URL with crawl4ai options and return extracted text content."""
    try:
        from crawl4ai import AsyncWebCrawler
        crawler_kwargs = {
            "depth": depth,
            "max_pages": max_pages,
            "timeout": timeout,
            "headless": headless
        }
        if user_agent:
            crawler_kwargs["user_agent"] = user_agent
        crawler = AsyncWebCrawler(**crawler_kwargs)
        result = await crawler.arun(url)
        # Assume result is a dict with a 'text' field or similar
        try:
            text = result.text
        except AttributeError:
            text = str(result)
        logger.info(f"Crawled {url} successfully with options {crawler_kwargs}.")
        return [types.TextContent(type="text", text=text)]
    except Exception as e:
        logger.error(f"Failed to crawl {url}: {e}")
        return [types.TextContent(type="text", text=f"Error crawling {url}: {e}")]
