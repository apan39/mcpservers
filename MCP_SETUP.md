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

## ⚡ Local SSE + Remote HTTP Hybrid Architecture

**🆕 NEW APPROACH**: All MCP servers now support both local SSE and remote HTTP for maximum flexibility:

- **Local SSE servers**: Fast, direct localhost access for development (no auth required)
- **Remote HTTP servers**: Production-ready, scalable, with authentication on Coolify

### 🚀 Quick Start - Local SSE Development

For **localhost PayloadCMS access** and development, use our new SSE endpoints:

```bash
# Start all local SSE servers
./start-local-sse.sh

# Configure Claude Desktop for local development
cp local-mcp-config.json ~/.claude-desktop/mcp.json

# Restart Claude Desktop - you now have direct localhost access!
```

**Local SSE Configuration:**
```json
{
  "mcpServers": {
    "python-local-sse": {
      "transport": {"type": "sse", "url": "http://localhost:3009/sse"}
    },
    "typescript-local-sse": {
      "transport": {"type": "sse", "url": "http://localhost:3010/sse"}
    },
    "browser-use-local-sse": {
      "transport": {"type": "sse", "url": "http://localhost:3000/sse"}
    }
  }
}
```

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

## 🛠 Available Tools (Total: 82+ tools)

### Python Server (python-tools) - 37 Tools

**Math & Calculation (3 tools):**
- `add-numbers` - Add two numbers: `{"a": 5, "b": 3}`
- `multiply-numbers` - Multiply numbers: `{"a": 4, "b": 7}` 
- `calculate-percentage` - Calculate percentage: `{"value": 100, "percentage": 20}`

**Text Processing (3 tools):**
- `string-operations` - Text operations: `{"text": "Hello", "operation": "uppercase"}`
- `word-count` - Count words: `{"text": "Hello world"}`
- `format-text` - Format text: `{"text": "hello world", "format_type": "title_case"}`

**Web Scraping (1 tool):**
- `crawl-url` - Smart web scraping with filtering options:
  - Basic: `{"url": "https://example.com"}`
  - Extract main content only: `{"url": "https://example.com", "extract_mode": "main_content"}`
  - Get headings only: `{"url": "https://example.com", "extract_mode": "headings"}`
  - Get summary: `{"url": "https://example.com", "extract_mode": "summary"}`
  - Specific element: `{"url": "https://example.com", "selector": "article"}`
  - Limit length: `{"url": "https://example.com", "max_length": 10000}`
  - Exclude sections: `{"url": "https://example.com", "exclude_selectors": [".ads", "nav", ".sidebar"]}`

**🚀 Coolify API Integration (25 tools):**

*Core Operations:*
- `coolify-get-version` - Get Coolify version: `{}`
- `coolify-list-projects` - List all projects: `{}`
- `coolify-list-servers` - List all servers: `{}`
- `coolify-list-applications` - List apps: `{"project_uuid": "abc-123"}`
- `coolify-create-github-app` - Deploy GitHub repo: `{"project_uuid": "abc", "server_uuid": "xyz", "git_repository": "https://github.com/user/repo", "name": "my-app"}`

*Application Management:*
- `coolify-get-application-info` - Get app details: `{"app_uuid": "abc-123"}`
- `coolify-restart-application` - Restart app: `{"app_uuid": "abc-123"}`
- `coolify-stop-application` - Stop app: `{"app_uuid": "abc-123"}`
- `coolify-start-application` - Start app: `{"app_uuid": "abc-123"}`
- `coolify-delete-application` - Delete app: `{"app_uuid": "abc-123"}`

*Deployment Operations:*
- `coolify-deploy-application` - Deploy app: `{"app_uuid": "abc-123"}`
- `coolify-get-deployment-logs` - Get deployment logs: `{"deployment_uuid": "xyz-789"}`
- `coolify-get-deployment-info` - Get deployment info: `{"deployment_uuid": "xyz-789"}`
- `coolify-watch-deployment` - Watch deployment progress: `{"deployment_uuid": "xyz-789"}`
- `coolify-get-recent-deployments` - Get recent deployments: `{"app_uuid": "abc-123"}`
- `coolify-deployment-metrics` - Get deployment metrics: `{"app_uuid": "abc-123"}`

*Configuration Management:*
- `coolify-update-health-check` - Update health check: `{"app_uuid": "abc-123", "health_check_enabled": true, "health_check_path": "/health"}`
- `coolify-test-health-endpoint` - Test health endpoint: `{"app_uuid": "abc-123"}`
- `coolify-set-env-variable` - Set env var: `{"app_uuid": "abc-123", "key": "PORT", "value": "3000"}`
- `coolify-delete-env-variable` - Delete env var: `{"app_uuid": "abc-123", "key": "OLD_VAR"}`
- `coolify-bulk-update-env` - Bulk update env vars: `{"app_uuid": "abc-123", "env_vars": [{"key": "PORT", "value": "3000"}]}`
- `coolify-update-build-settings` - Update build settings: `{"app_uuid": "abc-123", "build_pack": "dockerfile"}`
- `coolify-manage-domains` - Manage domains: `{"app_uuid": "abc-123", "domains": ["example.com"]}`
- `coolify-update-resource-limits` - Update resources: `{"app_uuid": "abc-123", "cpu_limit": "1000m", "memory_limit": "512Mi"}`

*Bulk Operations:*
- `coolify-bulk-restart` - Restart multiple apps: `{"app_uuids": ["abc-123", "def-456"]}`
- `coolify-bulk-deploy` - Deploy multiple apps: `{"app_uuids": ["abc-123", "def-456"]}`
- `coolify-project-status` - Get project status: `{"project_uuid": "abc-123"}`
- `coolify-get-application-logs` - Get app logs: `{"app_uuid": "abc-123"}`

**Help & Discovery (5 tools):**
- `list-tool-categories` - Show all tool categories: `{}`
- `get-tools-by-category` - Get tools by category: `{"category": "deployment"}`
- `search-tools` - Search tools: `{"query": "health", "category": "monitoring"}`
- `get-tool-info` - Get tool details: `{"tool_name": "coolify-deploy-application"}`
- `get-learning-path` - Get learning path: `{"focus": "beginner"}`

### TypeScript Server (typescript-tools) - 33+ Tools

**Basic Tools (3 tools):**
- `greet` - Simple greeting: `{"name": "Claude"}`
- `multi-greet` - Friendly greeting: `{"name": "Claude"}`
- `scrape-dynamic-url` - Dynamic scraping: `{"url": "https://example.com", "timeout": 10000}`

**🎯 PayloadCMS 3.x Integration (12 tools) - Now with Localhost Support!**

*🔗 Localhost Configuration (Auto-optimized):*
- **Simple localhost**: `{"config": {"baseUrl": "localhost"}}` → Auto-resolves to `http://localhost:3000`
- **Custom port**: `{"config": {"baseUrl": "localhost:3001"}}` → Auto-resolves to `http://localhost:3001`
- **Multiple instances**: Supports `localhost:3000`, `localhost:3001`, `localhost:4000`, `localhost:5000`
- **Auto-optimization**: Faster timeouts and simplified auth for localhost URLs

*Collection CRUD Operations (6 tools):*
- `payload-find-documents` - Query collection documents:
  - **🏠 Localhost**: `{"config": {"baseUrl": "localhost:3000"}, "collection": "posts", "where": {"status": {"equals": "published"}}, "limit": 10}`
  - **🌐 Remote**: `{"config": {"baseUrl": "https://cms.example.com", "token": "jwt"}, "collection": "posts", "where": {"status": {"equals": "published"}}, "limit": 10}`
- `payload-get-document` - Get document by ID: `{"config": {"baseUrl": "localhost"}, "collection": "posts", "id": "64a7b8c9d1234567890abcde"}`
- `payload-create-document` - Create new document: `{"config": {"baseUrl": "localhost:3001"}, "collection": "posts", "data": {"title": "New Post", "content": "Content here"}}`
- `payload-update-document` - Update existing document: `{"config": {"baseUrl": "localhost"}, "collection": "posts", "id": "64a7b8c9d1234567890abcde", "data": {"title": "Updated Title"}}`
- `payload-delete-document` - Delete document: `{"config": {"baseUrl": "localhost"}, "collection": "posts", "id": "64a7b8c9d1234567890abcde"}`
- `payload-count-documents` - Count documents: `{"config": {"baseUrl": "localhost"}, "collection": "posts", "where": {"status": {"equals": "published"}}}`

*Authentication (3 tools):*
- `payload-login` - Authenticate and get JWT: `{"config": {"baseUrl": "https://cms.example.com"}, "email": "admin@example.com", "password": "password"}`
- `payload-get-current-user` - Get current user info: `{"config": {"baseUrl": "https://cms.example.com", "token": "jwt"}}`
- `payload-logout` - Logout and clear token: `{"config": {"baseUrl": "https://cms.example.com", "token": "jwt"}}`

*Global Configuration (2 tools):*
- `payload-get-global` - Get global config: `{"config": {"baseUrl": "https://cms.example.com", "token": "jwt"}, "slug": "header"}`
- `payload-update-global` - Update global config: `{"config": {"baseUrl": "https://cms.example.com", "token": "jwt"}, "slug": "header", "data": {"logo": "new-logo.png"}}`

*File Management (1 tool):*
- `payload-upload-file` - Upload files: `{"config": {"baseUrl": "https://cms.example.com", "token": "jwt"}, "collection": "media", "fileData": "data:image/png;base64,iVBORw0K...", "fileName": "image.png"}`

*Advanced Operations (2 tools):*
- `payload-graphql-query` - Execute GraphQL queries: `{"config": {"baseUrl": "https://cms.example.com", "token": "jwt"}, "query": "query { Posts { docs { id title } } }"}`
- `payload-health-check` - Check API connectivity: `{"config": {"baseUrl": "https://cms.example.com", "apiKey": "your-api-key"}}`

**GitHub Integration (18+ tools):**
- `github-get-user` - Get authenticated user: `{}`
- `github-list-repos` - List repositories: `{"username": "optional"}`
- `github-get-repo` - Get repository details: `{"owner": "user", "repo": "repository"}`
- `github-create-issue` - Create issue: `{"owner": "user", "repo": "repository", "title": "Issue Title", "body": "Description"}`
- `github-create-or-update-file` - Create/update files: `{"owner": "user", "repo": "repo", "path": "file.txt", "content": "content", "message": "commit message"}`
- And 13+ more GitHub management tools...

**Context7 Integration (6+ tools):**
- `context7-get-docs` - Get library documentation: `{"library": "react", "version": "18"}`
- `context7-search-examples` - Search code examples: `{"library": "next.js", "pattern": "API routes"}`
- `context7-ai-context` - Get AI coding context: `{"libraries": ["react", "typescript"], "task": "Build a dashboard"}`
- And 3+ more Context7 tools...

**Flowise Integration (4+ tools):**
- `flowise-list-chatflows` - List chatflows: `{}`
- `flowise-predict` - Send message to chatflow: `{"chatflowId": "abc", "question": "Hello"}`
- And 2+ more Flowise tools...

### Browser-Use MCP Server (browser-use-mcp) - 30 Tools

**Session Management (4 tools):**
- `create_browser_session` - Create session: `{"session_id": "my-session", "headless": true}`
- `close_browser_session` - Close session: `{"session_id": "my-session"}`
- `list_browser_sessions` - List sessions: `{}`
- `get_session_info` - Get session info: `{"session_id": "my-session"}`

**Navigation & Page Control (4 tools):**
- `navigate_to_url` - Navigate: `{"session_id": "my-session", "url": "https://example.com"}`
- `go_back` - Go back: `{"session_id": "my-session"}`
- `go_forward` - Go forward: `{"session_id": "my-session"}`
- `refresh_page` - Refresh: `{"session_id": "my-session"}`

**Content Extraction (3 tools):**
- `get_page_content` - Get content: `{"session_id": "my-session", "include_html": false}`
- `extract_content` - Extract specific content: `{"session_id": "my-session", "selector": ".main-content"}`
- `get_page_html` - Get HTML: `{"session_id": "my-session"}`

**User Interactions (4 tools):**
- `click_element` - Click element: `{"session_id": "my-session", "selector": "button.submit"}`
- `input_text` - Type text: `{"session_id": "my-session", "selector": "input[name='search']", "text": "hello world"}`
- `scroll` - Scroll page: `{"session_id": "my-session", "direction": "down", "amount": 500}`
- `send_keys` - Send keys: `{"session_id": "my-session", "keys": "Tab Enter"}`

**Tab Management (4 tools):**
- `create_tab` - Create tab: `{"session_id": "my-session", "url": "https://example.com"}`
- `list_tabs` - List tabs: `{"session_id": "my-session"}`
- `switch_tab` - Switch tab: `{"session_id": "my-session", "tab_id": "tab-1"}`
- `close_tab` - Close tab: `{"session_id": "my-session", "tab_id": "tab-1"}`

**File Operations (2 tools):**
- `upload_file` - Upload file: `{"session_id": "my-session", "selector": "input[type='file']", "file_path": "/path/to/file.pdf"}`
- `download_file` - Download file: `{"session_id": "my-session", "url": "https://example.com/file.pdf"}`

**Advanced Features (9 tools):**
- `execute_javascript` - Execute JS: `{"session_id": "my-session", "script": "document.title"}`
- `wait_for_element` - Wait for element: `{"session_id": "my-session", "selector": ".loading", "timeout": 5000}`
- `wait_for_load` - Wait for load: `{"session_id": "my-session", "timeout": 10000}`
- `take_screenshot` - Take screenshot: `{"session_id": "my-session", "selector": "body"}`
- `get_browser_state` - Get browser state: `{"session_id": "my-session"}`
- `get_dom_elements` - Get DOM elements: `{"session_id": "my-session", "selector": "button, a, input"}`
- `create_agent` - Create AI agent: `{"session_id": "my-session", "agent_id": "my-agent"}`
- `execute_agent_task` - Execute with agent: `{"session_id": "my-session", "agent_id": "my-agent", "task": "Click the login button"}`
- `get_agent_history` - Get agent history: `{"session_id": "my-session", "agent_id": "my-agent"}`

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

**🔍 Tool Discovery & Help:**

*Getting Started:*
```
Please list all available tool categories to see what's available
Please show me all deployment tools to understand what I can do
Please search for tools related to "monitoring" to track my applications
```

*Learning & Information:*
```
Please get detailed information about the coolify-deploy-application tool
Please get a beginner learning path to understand the tools step by step
Please get a deployment learning path to master application deployment
```

**🚀 Coolify Deployment & Management:**

*Basic Operations:*
```
Please use the coolify-list-projects tool to see all my projects
Please use the coolify-list-servers tool to see available servers
Please use the coolify-list-applications tool to show all apps in project abc-123
```

*GitHub Deployment:*
```
Please use the coolify-create-github-app tool to deploy https://github.com/myuser/myapp to project UUID abc123 and server UUID xyz789 with name "my-new-app"
```

*Application Management:*
```
Please check the status of application abc-123
Please restart my crashed application abc-123
Please deploy the latest changes to application abc-123
Please stop application abc-123 for maintenance
```

*Environment & Configuration:*
```
Please set environment variable PORT=3000 for application abc-123
Please update multiple env vars for app abc-123: PORT=3000, NODE_ENV=production
Please delete the OLD_API_KEY environment variable from application abc-123
Please update the health check for app abc-123 to use /api/health endpoint
```

*Deployment Monitoring:*
```
Please watch the deployment progress for deployment xyz-789
Please get the deployment logs for my latest deployment
Please show recent deployments for application abc-123
Please test the health endpoint for application abc-123
```

*Bulk Operations:*
```
Please restart all applications in project abc-123
Please deploy multiple applications: abc-123, def-456, ghi-789
Please show complete project status for project abc-123
```

**🌐 Advanced Web Scraping:**

*Smart Content Extraction:*
```
Please crawl this article and extract only the main content
Please get just the headings from this documentation page
Please crawl this e-commerce page but exclude ads and navigation
Please get a summary of this long news article
```

*Playwright Dynamic Scraping:*
```
Please use Playwright to scrape this single-page application
Please scrape this JavaScript-heavy page with custom timeout
Please extract content from this dynamically loaded page
```

**🎯 PayloadCMS Backend Management (Now with Localhost Support!):**

*🏠 Localhost Development:*
```
Please check connectivity to my local PayloadCMS at localhost
Please create a new blog post in my localhost PayloadCMS 'posts' collection
Please find all published posts from localhost:3001
Please upload an image to my local PayloadCMS media collection
Please update the header global in my localhost PayloadCMS
```

*🌐 Remote Production:*
```
Please use payload-login to authenticate with my PayloadCMS instance at https://cms.example.com
Please check the connectivity to my PayloadCMS API using payload-health-check
Please get my current user information using payload-get-current-user
```

*Content Management:*
```
Please create a new blog post in the 'posts' collection with title "Getting Started" and content "This is a guide..."
Please find all published posts in the 'posts' collection, sorted by creation date
Please update the blog post with ID "64a7b8c9d1234567890abcde" to change its status to published
Please upload an image to the 'media' collection from https://example.com/image.jpg
Please get the header global configuration and show me the current navigation menu
```

*Advanced Operations:*
```
Please execute a GraphQL query to get all posts with their authors and featured images
Please count how many published posts I have in the 'posts' collection
Please update the footer global with new social media links
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