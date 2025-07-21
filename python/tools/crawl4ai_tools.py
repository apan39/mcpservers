"""Simple web scraping tools for the MCP server."""

import mcp.types as types
import requests
from bs4 import BeautifulSoup
from utils.logger import setup_logger

# Set up logging
logger = setup_logger("web_tools")

def register_crawl4ai_tools(tool_registry):
    """Register web scraping tools with the tool registry."""
    tool_registry["crawl-url"] = {
        "definition": types.Tool(
            name="crawl-url",
            description="Scrape a URL and return extracted text content.",
            inputSchema={
                "type": "object",
                "required": ["url"],
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL to scrape"
                    },
                    "max_pages": {
                        "type": "integer",
                        "description": "Maximum number of pages to scrape (currently ignored)",
                        "default": 1
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Timeout for scraping in seconds",
                        "default": 30
                    }
                }
            }
        ),
        "handler": crawl_url_with_options
    }

async def crawl_url_with_options(
    url: str,
    max_pages: int = 1,
    timeout: int = 30,
    **kwargs
) -> list[types.TextContent]:
    """Scrape a URL and return extracted text content."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text content
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        logger.info(f"Scraped {url} successfully.")
        return [types.TextContent(type="text", text=text)]
    except Exception as e:
        logger.error(f"Failed to scrape {url}: {e}")
        return [types.TextContent(type="text", text=f"Error scraping {url}: {e}")]
