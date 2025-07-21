# MCP Servers - Production Ready

This repository contains production-ready MCP (Model Context Protocol) servers implemented in both Python and TypeScript. The servers are hardened for network deployment with proper security, authentication, and monitoring.

## Project Structure

```
.
├── .env.example                 # Environment configuration template  
├── docker-compose.yml          # Docker services configuration
├── DEPLOYMENT.md              # Detailed deployment guide
├── python/                    # Python MCP server
│   ├── Dockerfile
│   ├── mcp_server.py         # Main server implementation
│   ├── event_store.py        # Event storage for resumability  
│   ├── health.py            # Health check endpoints
│   ├── requirements.txt
│   ├── tools/               # MCP tools
│   │   ├── math_tools.py
│   │   ├── text_tools.py
│   │   └── crawl4ai_tools.py
│   └── utils/
│       └── logger.py
└── typescript/               # TypeScript MCP server
    ├── Dockerfile
    ├── package.json
    ├── tsconfig.json
    └── src/
        ├── server.ts         # Main server implementation
        └── playwrightTools.ts # Playwright web scraping tools
```

## Quick Start

### 1. Environment Setup

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your secure credentials
# Required: MCP_API_KEY, POSTGRES_PASSWORD
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

### 3. Local Development

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

1. **Repository Setup**: Connect your GitHub repository
2. **Environment Variables**: Set `MCP_API_KEY` and `POSTGRES_PASSWORD`
3. **Service Type**: Choose "Docker Compose"
4. **Deploy**: Coolify will build and deploy automatically

## Security Features

- ✅ **Bearer Token Authentication** - Secure API access
- ✅ **Rate Limiting** - 100 requests per 15 minutes per IP
- ✅ **CORS Protection** - Configurable allowed origins
- ✅ **Input Validation** - All tool inputs validated
- ✅ **Non-root Containers** - Enhanced security
- ✅ **Health Monitoring** - Built-in health checks

## Available Tools

### Python Server (Port 3009)
- **Math**: `add-numbers`, `multiply-numbers`, `calculate-percentage`
- **Text**: `string-operations`, `word-count`, `format-text`
- **Web**: `crawl-url` (crawl4ai-powered web scraping)

### TypeScript Server (Port 3010)
- **Basic**: `greet`, `multi-greet`, `start-notification-stream`
- **Web**: `scrape-dynamic-url` (Playwright-powered dynamic scraping)

## AI Assistant Commands

To use these tools with an AI assistant, use these specific commands:

### For Claude or Other AI Assistants:
```
Please use the add-numbers tool to calculate 25 + 37
Please use the scrape-dynamic-url tool to get content from https://example.com
Please use the string-operations tool to convert "Hello World" to uppercase
Please use the crawl-url tool to extract text from https://news.ycombinator.com
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
```

## Testing Tools

- **MCP Inspector**: `npx @modelcontextprotocol/inspector`
- **Claude Desktop**: Install servers locally
- **curl/Postman**: Direct HTTP API testing

## Support

For issues and detailed documentation, see [DEPLOYMENT.md](./DEPLOYMENT.md).

## License

MIT
