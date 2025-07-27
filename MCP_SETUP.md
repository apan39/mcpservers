# MCP Setup for Claude Desktop/CLI

## ✅ Production-Ready MCP Servers - WORKING!

Your MCP servers are now successfully deployed and operational with Claude Desktop/CLI, including full **Coolify API integration** for automated deployments!

### Current Working Configuration

```bash
claude mcp list
```

Shows **6 working servers** (following local + remote pattern):
- `python-tools`: Local STDIO server (12 tools)
- `typescript-tools`: Local HTTP server (3 tools) 
- `browser-use-mcp`: Local STDIO server (browser automation tools)
- `remote-python-tools`: **🚀 LIVE** Remote HTTP server (12 tools + Coolify API)
- `remote-typescript-tools`: **🚀 LIVE** Remote HTTP server (3 tools)
- `remote-browser-use-mcp`: **🚀 LIVE** Remote HTTP server (browser automation tools)

**✅ Remote servers are now fully functional with proper authentication and simplified protocols!**

### HTTP Transport Setup

**Local Development:**
```bash
# Add Python server (includes Coolify integration)
claude mcp add --transport http python-tools http://localhost:3009/mcp

# Add TypeScript server (Playwright tools)
claude mcp add --transport http typescript-tools http://localhost:3010/mcp
```

**🚀 Live Production URLs (Working!):**
```bash
# Remote Python server - 12 tools + Coolify API
Remote URL: http://zs8sk0cgs4s8gsgwswsg88ko.135.181.149.150.sslip.io/mcp
Auth: Bearer ${MCP_API_KEY}

# Remote TypeScript server - 3 tools (simplified protocol)
Remote URL: http://k8wco488444c8gw0sscs04k8.135.181.149.150.sslip.io/mcp  
Auth: Bearer ${MCP_API_KEY}
```

## ⚡ Local + Remote Architecture

**Standard Pattern**: Every MCP server should have both local and remote versions for maximum flexibility:

- **Local servers** (`stdio`): Fast, direct access for development and testing
- **Remote servers** (`http`): Production-ready, scalable, with authentication

**Current Remote Configuration in `.mcp.json`:**
```json
{
  "mcpServers": {
    "remote-python-tools": {
      "type": "http",
      "url": "http://zs8sk0cgs4s8gsgwswsg88ko.135.181.149.150.sslip.io/mcp",
      "headers": {
        "Authorization": "Bearer ${MCP_API_KEY}",
        "Accept": "application/json"
      }
    },
    "remote-typescript-tools": {
      "type": "http", 
      "url": "http://k8wco488444c8gw0sscs04k8.135.181.149.150.sslip.io/mcp",
      "headers": {
        "Authorization": "Bearer ${MCP_API_KEY}",
        "Accept": "application/json"
      }
    },
    "remote-browser-use-mcp": {
      "type": "http",
      "url": "http://browser-use-mcp.135.181.149.150.sslip.io/mcp",
      "headers": {
        "Authorization": "Bearer ${MCP_API_KEY}",
        "Accept": "application/json"
      }
    }
  }
}
```

### Quick Test

```bash
# Test math tool
claude mcp call python-tools add-numbers '{"a": 25, "b": 37}'

# Test text tool  
claude mcp call python-tools string-operations '{"text": "Hello World", "operation": "uppercase"}'

# Test web crawling
claude mcp call python-tools crawl-url '{"url": "https://example.com", "max_pages": 1}'

# 🚀 Test Coolify integration
claude mcp call python-tools coolify-list-projects '{}'

# Test Playwright scraping
claude mcp call typescript-tools scrape-dynamic-url '{"url": "https://example.com"}'
```

### If You Need to Reconfigure

**Local Development:**
```bash
# Remove existing connections
claude mcp remove python-tools
claude mcp remove typescript-tools

# Re-add with HTTP transport (local)
claude mcp add --transport http python-tools http://localhost:3009/mcp
claude mcp add --transport http typescript-tools http://localhost:3010/mcp
```

**Production Deployment:**
```bash
# Remove existing connections
claude mcp remove python-tools
claude mcp remove typescript-tools

# Re-add with production URLs (get from Coolify dashboard)
claude mcp add --transport http python-tools https://your-python-app.coolify-domain.com/mcp
claude mcp add --transport http typescript-tools https://your-typescript-app.coolify-domain.com/mcp
```

## 🛠 Available Tools

### Python Tools (python-tools server):

**Math & Text Processing:**
- `add-numbers` - Add two numbers: `{"a": 5, "b": 3}`
- `multiply-numbers` - Multiply numbers: `{"a": 4, "b": 7}` 
- `calculate-percentage` - Calculate percentage: `{"value": 100, "percentage": 20}`
- `string-operations` - Text operations: `{"text": "Hello", "operation": "uppercase"}`
- `word-count` - Count words: `{"text": "Hello world"}`
- `format-text` - Format text: `{"text": "hello world", "format_type": "title_case"}`

**Web Scraping (Enhanced for Large Pages):**
- `crawl-url` - Smart web scraping with filtering options:
  - Basic: `{"url": "https://example.com"}`
  - Extract main content only: `{"url": "https://example.com", "extract_mode": "main_content"}`
  - Get headings only: `{"url": "https://example.com", "extract_mode": "headings"}`
  - Get summary: `{"url": "https://example.com", "extract_mode": "summary"}`
  - Specific element: `{"url": "https://example.com", "selector": "article"}`
  - Limit length: `{"url": "https://example.com", "max_length": 10000}`
  - Exclude sections: `{"url": "https://example.com", "exclude_selectors": [".ads", "nav", ".sidebar"]}`

**🚀 Coolify API Integration:**
- `coolify-get-version` - Get Coolify version: `{}`
- `coolify-list-projects` - List all projects: `{}`
- `coolify-list-servers` - List all servers: `{}`
- `coolify-list-applications` - List apps: `{"project_uuid": "abc-123"}`
- `coolify-create-github-app` - Deploy GitHub repo: `{"project_uuid": "abc", "server_uuid": "xyz", "git_repository": "https://github.com/user/repo", "name": "my-app"}`

### TypeScript Tools (typescript-tools server):
- `greet` - Simple greeting: `{"name": "Claude"}`
- `multi-greet` - Friendly greeting: `{"name": "Claude"}`
- `scrape-dynamic-url` - Dynamic scraping: `{"url": "https://example.com", "timeout": 10000}`

### Browser Automation Tools (browser-use-mcp server):
- `create_browser_session` - Create new browser session: `{"session_id": "my-session", "headless": true}`
- `navigate_to_url` - Navigate to URL: `{"session_id": "my-session", "url": "https://example.com"}`
- `click_element` - Click element: `{"session_id": "my-session", "selector": "button.submit"}`
- `type_text` - Type text: `{"session_id": "my-session", "selector": "input[name='search']", "text": "hello world"}`
- `get_page_content` - Get page content: `{"session_id": "my-session"}`
- `take_screenshot` - Take screenshot: `{"session_id": "my-session"}`
- `close_browser_session` - Close session: `{"session_id": "my-session"}`

## Usage in Claude Desktop/CLI

Once configured, you can use these in natural language:

**Basic Tools:**
```
Please use the add-numbers tool to calculate 25 + 37
Please use the string-operations tool to make "Hello World" uppercase  
Please use the crawl-url tool to get content from https://example.com
Please use the scrape-dynamic-url tool to get content from https://spa-app.com
```

**Smart Web Scraping (for Large Pages):**
```
Please crawl this article but only get the main content: https://longblog.com/post
Please get just the headings from this documentation page: https://docs.example.com
Please get a summary of this news article: https://news.com/long-article
Please crawl this page but exclude ads and navigation: https://cluttered-site.com
Please extract only the product description from this e-commerce page
```

**Browser Automation:**
```
Please create a browser session and navigate to google.com, then search for "MCP servers"
Please use browser automation to take a screenshot of the current page
Please automate filling out a form on example.com/contact
```

**🚀 Coolify Deployment:**
```
Please use the coolify-list-projects tool to see all my projects
Please use the coolify-create-github-app tool to deploy https://github.com/myuser/myapp to project UUID abc123 and server UUID xyz789 with name "my-new-app"
```

## Troubleshooting

If tools don't work:

1. **Check servers are running**: `docker compose ps` or visit http://localhost:3009/health
2. **Check HTTP connection**: Ensure you added with `--transport http`
3. **Check authentication**: Verify your secure `MCP_API_KEY` in `.env` (generated with `openssl rand -hex 32`)
4. **Check logs**: `docker compose logs` for server logs
5. **Run diagnostics**: `claude mcp doctor` for Claude CLI diagnostics

## 🚀 Coolify Integration Setup

For Coolify tools to work:

1. **Get API Token**: In your Coolify instance, go to "Keys & Tokens" → "API Tokens"
2. **Update .env**: Set `COOLIFY_BASE_URL` and `COOLIFY_API_TOKEN`
3. **Restart servers**: `docker compose down && docker compose up -d`
4. **Test**: Use `coolify-list-projects` to verify connection

## Deployment Information

**🚀 Live Production Deployment:**
- **Project**: mcpservers (`l8cog4c48w48kckkcgos8cwg`)
- **Python Server**: `zs8sk0cgs4s8gsgwswsg88ko` (Coolify API + tools)
- **TypeScript Server**: `k8wco488444c8gw0sscs04k8` (Playwright tools)
- **Repository**: https://github.com/apan39/mcpservers.git

**Environment Files:**
- `.env` - Local environment configuration  
- `docker-compose.yml` - Local container orchestration
- Production uses separate Nixpacks deployments via Coolify API
- Health check endpoints available at `/health` on all servers