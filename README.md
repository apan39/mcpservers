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

### Python Server (Port 3009)
- **Math**: `add-numbers`, `multiply-numbers`, `calculate-percentage`
- **Text**: `string-operations`, `word-count`, `format-text`
- **Web**: `crawl-url` (BeautifulSoup-powered web scraping)
- **🚀 Coolify API**: 
  - `coolify-get-version` - Get Coolify version
  - `coolify-list-projects` - List all projects
  - `coolify-list-servers` - List all servers
  - `coolify-list-applications` - List apps in a project
  - `coolify-create-github-app` - **Deploy GitHub repos to Coolify**

### TypeScript Server (Port 3010)
- **Basic**: `greet`, `multi-greet`
- **Web**: `scrape-dynamic-url` (Playwright-powered dynamic scraping)

## 🤖 AI Assistant Commands

### Basic Tools:
```
Please use the add-numbers tool to calculate 25 + 37
Please use the string-operations tool to convert "Hello World" to uppercase
Please use the crawl-url tool to extract text from https://news.ycombinator.com
Please use the scrape-dynamic-url tool to get content from https://example.com
```

### 🚀 Coolify Integration Examples:
```
Please use the coolify-list-projects tool
Please use the coolify-list-servers tool
Please use the coolify-create-github-app tool to deploy https://github.com/user/repo to project UUID abc123 and server UUID xyz789 with name "my-new-app"
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
