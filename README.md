# MCP Servers - Production Ready with Coolify Integration

This repository contains production-ready MCP (Model Context Protocol) servers implemented in both Python and TypeScript. The servers are hardened for network deployment with proper security, authentication, and monitoring, including full **Coolify API integration** for automated GitHub deployments.

## 🌟 Key Features

- ✅ **Production-Ready Security** - Bearer token auth, rate limiting, CORS protection
- ✅ **Local + Remote Architecture** - Every server available both locally (stdio) and remotely (http)
- ✅ **Coolify Integration** - Deploy GitHub repos directly through MCP tools
- ✅ **Browser Automation** - Full browser automation with browser-use-mcp
- ✅ **Multi-Language Support** - Python and TypeScript servers
- ✅ **Web Scraping Tools** - Both simple and Playwright-based dynamic scraping
- ✅ **Math & Text Processing** - Comprehensive utility tools
- ✅ **Health Monitoring** - Built-in health check endpoints
- ✅ **Docker Deployment** - Lightweight, secure containers

## Project Structure

```
.
├── .env.example                 # Environment configuration template  
├── docker-compose.yml          # Docker services configuration (no database required)
├── DEPLOYMENT.md              # Detailed deployment guide
├── MCP_SETUP.md              # Claude MCP setup instructions
├── python/                    # Python MCP server
│   ├── Dockerfile
│   ├── mcp_server.py         # Main server implementation
│   ├── event_store.py        # In-memory event storage  
│   ├── health.py            # Health check endpoints
│   ├── requirements.txt     # Lightweight dependencies
│   ├── tools/               # MCP tools
│   │   ├── math_tools.py    # Math operations
│   │   ├── text_tools.py    # Text processing
│   │   ├── crawl4ai_tools.py # Web scraping (requests + BeautifulSoup)
│   │   └── coolify_tools.py  # 🚀 Coolify API integration
│   └── utils/
│       └── logger.py
├── typescript/               # TypeScript MCP server
│   ├── Dockerfile
│   ├── package.json
│   ├── tsconfig.json
│   └── src/
│       ├── server.ts         # Main server implementation
│       └── playwrightTools.ts # Playwright web scraping tools
└── browser-use-mcp/         # Browser automation MCP server
    ├── server_stdio.py      # STDIO server for local use
    ├── server.py           # HTTP server for remote deployment
    ├── requirements.txt
    └── integrations/       # Integration configurations
```

## Quick Start

### 1. Environment Setup

```bash
# Copy environment template
cp .env.example .env

# Generate a secure API key
openssl rand -hex 32

# Edit .env with your secure credentials
# Required: MCP_API_KEY=<your-generated-secure-token>
# Optional: COOLIFY_BASE_URL, COOLIFY_API_TOKEN (for Coolify integration)
```

### 2. Docker Deployment (Recommended)

```bash
# Start all services
docker compose up --build

# Test health endpoints
curl http://localhost:3009/health
curl http://localhost:3010/health

# Test with authentication
curl -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"jsonrpc": "2.0", "method": "tools/list", "id": 1}' \
     http://localhost:3009/mcp
```

### 3. Claude MCP Integration

Add your servers to Claude Desktop:

```bash
# Add Python server (includes Coolify tools)
claude mcp add --transport http python-tools http://localhost:3009/mcp

# Add TypeScript server (Playwright tools)  
claude mcp add --transport http typescript-tools http://localhost:3010/mcp

# Add Browser Use MCP server (Browser automation)
claude mcp add --transport stdio browser-use-mcp python3 /path/to/browser-use-mcp/server_stdio.py
```

### 4. Local Development

#### Python Server
```bash
cd python
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python mcp_server.py
```

#### TypeScript Server
```bash
cd typescript
npm install
npm run build
npm start
```

## Production Deployment

For detailed production deployment instructions, see [DEPLOYMENT.md](./DEPLOYMENT.md).

### Coolify Deployment Summary

**🚀 Live Deployment - WORKING!**

Both servers are successfully deployed and operational on Coolify:
- **Python MCP Server**: ✅ `running:healthy` - Full Coolify API integration, math, text, and web tools
- **TypeScript MCP Server**: ✅ `running:healthy` - Simplified MCP protocol with basic tools

**Live URLs:**
- **Python Server**: `http://zs8sk0cgs4s8gsgwswsg88ko.135.181.149.150.sslip.io/mcp`
- **TypeScript Server**: `http://k8wco488444c8gw0sscs04k8.135.181.149.150.sslip.io/mcp`

**Authentication:** Secure Bearer token required (`Authorization: Bearer <your-secure-token>`)

**Service Details:**
- Python Server UUID: `zs8sk0cgs4s8gsgwswsg88ko` (Port 3009) - 12 tools available
- TypeScript Server UUID: `k8wco488444c8gw0sscs04k8` (Port 3010) - 3 tools available  
- Project UUID: `l8cog4c48w48kckkcgos8cwg`

**Recent Fixes Applied:**
- ✅ Added proper authentication middleware to Python server
- ✅ Simplified TypeScript server MCP protocol (removed complex session management)
- ✅ Fixed route handling for both `/mcp` and `/mcp/` endpoints
- ✅ Enhanced error handling and logging
- ✅ Verified deployment process with git commit/push workflow

> 💡 **Meta Feature**: Once deployed, you can use the Coolify integration tools to deploy *other* GitHub repositories from anywhere!

## Security Features

- ✅ **Bearer Token Authentication** - Cryptographically secure API tokens
- ✅ **Environment Variable Protection** - No hardcoded secrets
- ✅ **Secure Token Generation** - 64-character hex tokens
- ✅ **Rate Limiting** - 100 requests per 15 minutes per IP
- ✅ **CORS Protection** - Configurable allowed origins
- ✅ **Input Validation** - All tool inputs validated
- ✅ **Non-root Containers** - Enhanced security
- ✅ **Health Monitoring** - Built-in health checks

## 🛠 Available Tools

### Python Server (Port 3009) - 32 Tools Total
**Math & Calculation (3 tools):**
- `add-numbers` - Add two numbers together
- `multiply-numbers` - Multiply two numbers together  
- `calculate-percentage` - Calculate percentage of a value

**Text Processing (3 tools):**
- `string-operations` - Perform string operations (uppercase, lowercase, reverse)
- `word-count` - Count words in text
- `format-text` - Format text (title_case, sentence_case, camel_case)

**Web Scraping (1 tool):**
- `crawl-url` - Advanced web scraping with content filtering and extraction modes

**🚀 Coolify API Management (25 tools):**
*Core Operations:*
- `coolify-get-version` - Get Coolify instance version
- `coolify-list-projects` - List all projects
- `coolify-list-servers` - List all servers  
- `coolify-list-applications` - List applications (filterable by project)
- `coolify-create-github-app` - **Deploy GitHub repositories**

*Application Management:*
- `coolify-get-application-info` - Get detailed application information
- `coolify-restart-application` - Restart an application
- `coolify-stop-application` - Stop an application
- `coolify-start-application` - Start an application
- `coolify-delete-application` - Delete an application

*Deployment Operations:*
- `coolify-deploy-application` - Deploy an application
- `coolify-get-deployment-logs` - Get deployment logs
- `coolify-get-deployment-info` - Get deployment information
- `coolify-watch-deployment` - Watch deployment progress in real-time
- `coolify-get-recent-deployments` - Get recent deployment history
- `coolify-deployment-metrics` - Get deployment metrics and statistics

*Configuration Management:*
- `coolify-update-health-check` - Update health check settings
- `coolify-test-health-endpoint` - Test application health endpoints
- `coolify-set-env-variable` - Set environment variables
- `coolify-delete-env-variable` - Delete environment variables
- `coolify-bulk-update-env` - Bulk update multiple environment variables
- `coolify-update-build-settings` - Update build configuration
- `coolify-manage-domains` - Manage application domains
- `coolify-update-resource-limits` - Update CPU/memory limits

*Bulk Operations:*
- `coolify-bulk-restart` - Restart multiple applications
- `coolify-bulk-deploy` - Deploy multiple applications
- `coolify-project-status` - Get comprehensive project status
- `coolify-get-application-logs` - Get application runtime logs

### TypeScript Server (Port 3010) - 3 Tools Total
- `greet` - Simple greeting tool
- `multi-greet` - Friendly greeting with delays
- `scrape-dynamic-url` - Playwright-powered dynamic web scraping

### Browser-Use MCP Server - 30 Tools Total
**Session Management (4 tools):**
- `create_browser_session` - Create new browser session
- `close_browser_session` - Close browser session
- `list_browser_sessions` - List all active sessions
- `get_session_info` - Get detailed session information

**Navigation & Page Control (4 tools):**
- `navigate_to_url` - Navigate to specific URL
- `go_back` - Navigate back in browser history
- `go_forward` - Navigate forward in browser history
- `refresh_page` - Refresh current page

**Content Extraction (3 tools):**
- `get_page_content` - Extract page content (text/HTML)
- `extract_content` - Extract specific content using selectors
- `get_page_html` - Get raw HTML content

**User Interactions (4 tools):**
- `click_element` - Click elements using CSS selectors
- `input_text` - Type text into input fields
- `scroll` - Scroll page in specified direction
- `send_keys` - Send keyboard keys (Tab, Enter, Escape, etc.)

**Tab Management (4 tools):**
- `create_tab` - Create new browser tab
- `list_tabs` - List all open tabs
- `switch_tab` - Switch to specific tab
- `close_tab` - Close current or specific tab

**File Operations (2 tools):**
- `upload_file` - Upload files using file input elements
- `download_file` - Download files by clicking download links

**Advanced Features (9 tools):**
- `execute_javascript` - Execute custom JavaScript code
- `wait_for_element` - Wait for elements to appear
- `wait_for_load` - Wait for page loading completion
- `take_screenshot` - Capture page or element screenshots
- `get_browser_state` - Get comprehensive browser state
- `get_dom_elements` - Get clickable/interactive DOM elements
- `create_agent` - Create AI agent for browser automation
- `execute_agent_task` - Execute tasks using AI agents
- `get_agent_history` - Get AI agent action history

### Help & Discovery Tools - 5 Tools Total
**Tool Categorization & Help System:**
- `list-tool-categories` - Show all available tool categories with descriptions
- `get-tools-by-category` - List tools in a specific category (math, text, web, coolify, etc.)
- `search-tools` - Search for tools by name, description, or tags
- `get-tool-info` - Get detailed information about a specific tool with examples
- `get-learning-path` - Get recommended learning paths (beginner, deployment, monitoring, etc.)

**Total Available Tools: 70 tools across all servers**

## 🤖 AI Assistant Commands

### Tool Discovery & Help:
```
Please list all available tool categories
Please show me all deployment tools
Please search for tools related to "health"
Please get detailed information about the coolify-deploy-application tool
Please get a beginner learning path for using these tools
```

### Basic Tools:
```
Please use the add-numbers tool to calculate 25 + 37
Please use the string-operations tool to convert "Hello World" to uppercase
Please use the crawl-url tool to extract text from https://news.ycombinator.com
Please use the scrape-dynamic-url tool to get content from https://example.com
```

### 🚀 Coolify Integration Examples:

**Basic Operations:**
```
Please use the coolify-list-projects tool
Please use the coolify-list-servers tool  
Please use the coolify-list-applications tool to show all apps in project abc-123
```

**GitHub Deployment:**
```
Please use the coolify-create-github-app tool to deploy https://github.com/user/repo to project UUID abc123 and server UUID xyz789 with name "my-new-app"
```

**Application Management:**
```
Please check the status of application abc-123 using coolify-get-application-info
Please restart application abc-123 using coolify-restart-application
Please deploy application abc-123 using coolify-deploy-application
```

**Environment Configuration:**
```
Please set environment variable PORT=3000 for application abc-123
Please bulk update these environment variables for app abc-123: PORT=3000, NODE_ENV=production, API_URL=https://api.example.com
Please delete the OLD_API_KEY environment variable from application abc-123
```

**Deployment Monitoring:**
```
Please watch the deployment progress for deployment xyz-789
Please get the deployment logs for deployment xyz-789
Please show recent deployments for application abc-123
Please get deployment metrics for application abc-123
```

**Health Check Management:**
```
Please test the health endpoint for application abc-123
Please update the health check for app abc-123 to use path /api/health with 30 second interval
```

**Bulk Operations:**
```
Please restart these applications: abc-123, def-456, ghi-789
Please deploy multiple applications: abc-123, def-456
Please show the complete status for project abc-123
```

### 🌐 Advanced Web Scraping Examples:

**Smart Content Extraction:**
```
Please crawl this article but only get the main content: https://longblog.com/post
Please get just the headings from this documentation page: https://docs.example.com
Please get a summary of this news article: https://news.com/long-article
Please crawl this page but exclude ads and navigation: https://cluttered-site.com
Please extract only the product description from this e-commerce page
```

**Dynamic Content Scraping:**
```
Please use the scrape-dynamic-url tool to get content from this SPA: https://spa-app.com
Please scrape this JavaScript-heavy page with 15 second timeout: https://dynamic-content.com
```

### 🤖 Browser Automation Examples:

**Session Management:**
```
Please create a browser session called "shopping" in headless mode
Please create a browser session called "testing" with visible browser window
Please list all active browser sessions
Please get detailed info about session "shopping"
```

**Navigation & Interaction:**
```
Please navigate to google.com in session "search"
Please click the search button with class "search-btn" in session "search"
Please type "MCP servers" into the search input in session "search"
Please scroll down 500 pixels in session "search"
Please go back to the previous page in session "search"
```

**Advanced Interactions:**
```
Please take a screenshot of the current page in session "search"
Please execute JavaScript to get the page title in session "search"
Please wait for element with class "results" to appear in session "search"
Please upload file "/path/to/document.pdf" to the file input in session "search"
```

**Tab Management:**
```
Please create a new tab and navigate to example.com in session "multi"
Please list all open tabs in session "multi"
Please switch to tab 2 in session "multi"
Please close the current tab in session "multi"
```

**AI Agent Automation:**
```
Please create an AI agent called "form-filler" in session "automation"
Please use agent "form-filler" to fill out the contact form on this page
Please use agent "navigator" to find and click the login button
Please get the action history for agent "form-filler"
```

**Complex Workflows:**
```
Please create a browser session, navigate to a shopping site, search for "laptops", take a screenshot of the results, and then close the session
Please automate logging into a website and then navigate to the dashboard
Please create an agent to automatically fill out a multi-step form
```

### For Direct API Testing:

```bash
# List available tools
curl -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"jsonrpc": "2.0", "method": "tools/list", "id": 1}' \
     http://localhost:3009/mcp

# Math calculation
curl -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "jsonrpc": "2.0",
       "method": "tools/call",
       "params": {
         "name": "add-numbers",
         "arguments": {"a": 25, "b": 37}
       },
       "id": 1
     }' \
     http://localhost:3009/mcp

# Text processing
curl -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "jsonrpc": "2.0",
       "method": "tools/call",
       "params": {
         "name": "string-operations",
         "arguments": {
           "text": "Hello World",
           "operation": "uppercase"
         }
       },
       "id": 1
     }' \
     http://localhost:3009/mcp

# Web scraping (TypeScript server)
curl -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "jsonrpc": "2.0",
       "method": "tools/call",
       "params": {
         "name": "scrape-dynamic-url",
         "arguments": {
           "url": "https://example.com",
           "timeout": 10000
         }
       },
       "id": 1
     }' \
     http://localhost:3010/mcp

# Web crawling (Python server)
curl -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "jsonrpc": "2.0",
       "method": "tools/call",
       "params": {
         "name": "crawl-url",
         "arguments": {
           "url": "https://news.ycombinator.com",
           "max_pages": 1
         }
       },
       "id": 1
     }' \
     http://localhost:3009/mcp

# Deploy GitHub repo via Coolify (Python server)
curl -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "jsonrpc": "2.0",
       "method": "tools/call",
       "params": {
         "name": "coolify-create-github-app",
         "arguments": {
           "project_uuid": "your-project-uuid",
           "server_uuid": "your-server-uuid",
           "git_repository": "https://github.com/user/repo",
           "name": "my-app",
           "git_branch": "main",
           "build_pack": "nixpacks"
         }
       },
       "id": 1
     }' \
     http://localhost:3009/mcp
```

## Testing Tools

- **MCP Inspector**: `npx @modelcontextprotocol/inspector`
- **Claude Desktop**: Install servers locally
- **curl/Postman**: Direct HTTP API testing

## Support

For issues and detailed documentation, see [DEPLOYMENT.md](./DEPLOYMENT.md).

## License

MIT
