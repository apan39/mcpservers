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
                    },
                    "max_length": {
                        "type": "integer",
                        "description": "Maximum length of extracted text (characters)",
                        "default": 50000
                    },
                    "selector": {
                        "type": "string",
                        "description": "CSS selector to extract specific content (e.g., 'article', '.content', '#main')"
                    },
                    "exclude_selectors": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "CSS selectors to exclude (e.g., ['.ads', '.sidebar', 'nav'])",
                        "default": ["nav", "header", "footer", ".ads", ".sidebar", ".menu"]
                    },
                    "extract_mode": {
                        "type": "string",
                        "enum": ["full", "summary", "headings", "main_content"],
                        "description": "What to extract: full page, summary, headings only, or main content",
                        "default": "full"
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
    max_length: int = 50000,
    selector: str = None,
    exclude_selectors: list = None,
    extract_mode: str = "full",
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
        
        # Set default exclude selectors if none provided
        if exclude_selectors is None:
            exclude_selectors = ["nav", "header", "footer", ".ads", ".sidebar", ".menu"]
        
        # Remove excluded elements
        for sel in exclude_selectors:
            for element in soup.select(sel):
                element.decompose()
        
        # Extract content based on mode and selector
        if selector:
            # Use specific selector
            elements = soup.select(selector)
            if elements:
                content_soup = elements[0]  # Take first match
            else:
                content_soup = soup
        else:
            # Auto-detect main content or use full page
            if extract_mode == "main_content":
                # Try common main content selectors
                main_selectors = ["main", "article", ".content", ".post", "#content", ".main-content"]
                content_soup = None
                for sel in main_selectors:
                    elements = soup.select(sel)
                    if elements:
                        content_soup = elements[0]
                        break
                if not content_soup:
                    content_soup = soup
            else:
                content_soup = soup
        
        # Extract text based on mode
        if extract_mode == "headings":
            # Extract only headings
            headings = []
            for h in content_soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                headings.append(f"{h.name.upper()}: {h.get_text().strip()}")
            text = '\n'.join(headings)
        elif extract_mode == "summary":
            # Extract first paragraph + headings
            headings = [h.get_text().strip() for h in content_soup.find_all(['h1', 'h2', 'h3'])]
            paragraphs = [p.get_text().strip() for p in content_soup.find_all('p')]
            
            summary_parts = []
            if headings:
                summary_parts.append("HEADINGS: " + " | ".join(headings[:5]))
            if paragraphs:
                # Take first few paragraphs that aren't empty
                good_paragraphs = [p for p in paragraphs if len(p) > 50]
                if good_paragraphs:
                    summary_parts.append("CONTENT: " + " ".join(good_paragraphs[:3]))
            
            text = '\n\n'.join(summary_parts)
        else:
            # Full text extraction
            text = content_soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        # Limit length if specified
        if max_length and len(text) > max_length:
            text = text[:max_length] + f"\n\n[Content truncated at {max_length} characters]"
        
        logger.info(f"Scraped {url} successfully.")
        return [types.TextContent(type="text", text=text)]
    except Exception as e:
        logger.error(f"Failed to scrape {url}: {e}")
        return [types.TextContent(type="text", text=f"Error scraping {url}: {e}")]
