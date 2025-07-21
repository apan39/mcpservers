# MCP Setup for Claude Desktop/CLI

## ✅ Production-Ready MCP Servers with Coolify Integration!

Your MCP servers are now configured and ready to use with Claude Desktop or CLI, including full **Coolify API integration** for automated deployments!

### Current Configuration

```bash
claude mcp list
```

Shows:
- `python-tools`: Math, text, web crawling, and **🚀 Coolify API tools**
- `typescript-tools`: Playwright dynamic web scraping tools

### HTTP Transport Setup

**Local Development:**
```bash
# Add Python server (includes Coolify integration)
claude mcp add --transport http python-tools http://localhost:3009/mcp

# Add TypeScript server (Playwright tools)
claude mcp add --transport http typescript-tools http://localhost:3010/mcp
```

**🚀 Production Deployment (Coolify):**
```bash
# Add production Python server (replace with your Coolify domain)
claude mcp add --transport http python-tools https://your-python-app.coolify-domain.com/mcp

# Add production TypeScript server (replace with your Coolify domain)  
claude mcp add --transport http typescript-tools https://your-typescript-app.coolify-domain.com/mcp
```

**Finding Your Production URLs:**
1. Go to your Coolify dashboard
2. Navigate to the "mcpservers" project
3. Check the domains assigned to:
   - Python Server: `zs8sk0cgs4s8gsgwswsg88ko`
   - TypeScript Server: `k8wco488444c8gw0sscs04k8`

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

**Web Scraping:**
- `crawl-url` - Web scraping: `{"url": "https://example.com", "max_pages": 1}`

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

## Usage in Claude Desktop/CLI

Once configured, you can use these in natural language:

**Basic Tools:**
```
Please use the add-numbers tool to calculate 25 + 37
Please use the string-operations tool to make "Hello World" uppercase  
Please use the crawl-url tool to get content from https://example.com
Please use the scrape-dynamic-url tool to get content from https://spa-app.com
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
3. **Check authentication**: Verify your `MCP_API_KEY` in `.env`
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