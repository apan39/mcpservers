# MCP Servers - Production Deployment Guide

## Overview

This repository contains production-ready MCP (Model Context Protocol) servers with **Coolify API integration**. The servers are hardened for network deployment with proper security, error handling, and monitoring. Includes full GitHub-to-Coolify deployment automation.

## Security Features

- **Environment-based configuration** - No hardcoded credentials
- **Proper authentication** - Bearer token authentication required
- **Rate limiting** - 100 requests per 15 minutes per IP
- **CORS protection** - Configurable allowed origins
- **Non-root containers** - Services run as non-privileged users
- **Health checks** - Built-in health monitoring
- **Input validation** - All tool inputs are validated

## Prerequisites

1. **Environment Variables** - Copy `.env.example` to `.env` and configure:
   ```bash
   cp .env.example .env
   
   # Generate a secure API key
   openssl rand -hex 32
   ```
   
   **Required variables:**
   - `MCP_API_KEY` - Cryptographically secure API key (generate with `openssl rand -hex 32`)
   
   **Coolify Integration (Optional):**
   - `COOLIFY_BASE_URL` - Your Coolify instance URL (e.g., https://coolify.example.com)
   - `COOLIFY_API_TOKEN` - API token from Coolify "Keys & Tokens"
   
   **Optional variables:**
   - `ALLOWED_ORIGINS` - Comma-separated list of allowed origins
   - `LOG_LEVEL` - Logging level (DEBUG, INFO, WARNING, ERROR)

2. **Coolify Setup** - Ensure your Coolify instance is configured and accessible

## Deployment Steps

### 1. Local Testing

First, test the services locally:

```bash
# Start all services
docker compose up --build

# Test health endpoints
curl http://localhost:3009/health
curl http://localhost:3010/health

# Test authentication (replace YOUR_API_KEY)
curl -H "Authorization: Bearer YOUR_API_KEY" http://localhost:3009/mcp
curl -H "Authorization: Bearer YOUR_API_KEY" http://localhost:3010/mcp
```

### 2. Coolify Deployment - WORKING! ✅

**🚀 Live Production Deployment**

This repository is successfully deployed and operational using Coolify API integration:

1. **Project**: "mcpservers" project (`l8cog4c48w48kckkcgos8cwg`)
2. **Services Status**: ✅ Both services are `running:healthy`
   - **Python MCP Server**: UUID `zs8sk0cgs4s8gsgwswsg88ko` (Port 3009) - **12 tools available**
   - **TypeScript MCP Server**: UUID `k8wco488444c8gw0sscs04k8` (Port 3010) - **3 tools available**

**Live URLs:**
- **Python Server**: `http://zs8sk0cgs4s8gsgwswsg88ko.135.181.149.150.sslip.io/mcp`
- **TypeScript Server**: `http://k8wco488444c8gw0sscs04k8.135.181.149.150.sslip.io/mcp`
- **Authentication**: `Authorization: Bearer <your-secure-token>`

**Recent Security Updates:**
- ✅ **Secure Token Implementation** - Generated cryptographically secure API keys
- ✅ **Environment Variable Protection** - Removed hardcoded demo tokens
- ✅ **Production Token Deployment** - Updated Coolify environment variables
- ✅ **Bearer token authentication** - Proper authentication middleware 
- ✅ **Simplified MCP protocol** - Removed session complexity for reliability
- ✅ **Enhanced error handling** - Comprehensive logging and monitoring

**Manual Deployment (Alternative)**

If you want to deploy manually:

1. **Create New Applications** (separate services)
   - **Python Service**:
     - Build Pack: "Nixpacks"
     - Base Directory: `python`
     - Port: 3009
   - **TypeScript Service**:
     - Build Pack: "Nixpacks" 
     - Base Directory: `typescript`
     - Port: 3010

2. **Environment Configuration**
   Set these environment variables for the Python service:
   ```
   MCP_API_KEY=<generated-with-openssl-rand-hex-32>
   COOLIFY_BASE_URL=http://your-coolify-instance.com:8000
   COOLIFY_API_TOKEN=your-coolify-api-token
   LOG_LEVEL=INFO
   ```

3. **Deploy**
   - Both services will build and deploy automatically
   - Monitor logs for successful startup

### 3. Production Verification - VERIFIED! ✅

The services are verified and working:

```bash
# Health checks - WORKING ✅
curl http://zs8sk0cgs4s8gsgwswsg88ko.135.181.149.150.sslip.io/health
# Returns: {"status":"healthy","timestamp":"2025-07-25T20:59:30.713240","service":"mcp-python-server"}

curl http://k8wco488444c8gw0sscs04k8.135.181.149.150.sslip.io/health  
# Returns: {"status":"ok","timestamp":"2025-07-25T20:59:32.094Z"}

# Test MCP initialization - WORKING ✅
curl -X POST -H "Content-Type: application/json" -H "Authorization: Bearer ${MCP_API_KEY}" \
     -d '{"jsonrpc": "2.0", "method": "initialize", "id": 1, "params": {}}' \
     http://zs8sk0cgs4s8gsgwswsg88ko.135.181.149.150.sslip.io/mcp

# Test tools list - WORKING ✅
curl -X POST -H "Content-Type: application/json" -H "Authorization: Bearer ${MCP_API_KEY}" \
     -d '{"jsonrpc": "2.0", "method": "tools/list", "id": 2, "params": {}}' \
     http://zs8sk0cgs4s8gsgwswsg88ko.135.181.149.150.sslip.io/mcp
```

**✅ Production Status:**
- **Python Server**: 12 tools including Coolify API, math, text, web scraping
- **TypeScript Server**: 3 tools including greet, multi-greet, scrape-dynamic-url
- **Authentication**: Bearer token working correctly
- **MCP Protocol**: Full initialize → tools/list → tools/call flow verified

## Available Tools

### Python Server (Port 3009)

- **Math Tools**
  - `add-numbers` - Add two numbers
  - `multiply-numbers` - Multiply two numbers  
  - `calculate-percentage` - Calculate percentage

- **Text Tools**
  - `string-operations` - String manipulation (uppercase, lowercase, reverse)
  - `word-count` - Count words in text
  - `format-text` - Format text (title, sentence, camel case)

- **Web Scraping Tools**
  - `crawl-url` - Extract text from web pages using BeautifulSoup

- **🚀 Coolify API Tools**
  - `coolify-get-version` - Get Coolify instance version
  - `coolify-list-projects` - List all Coolify projects
  - `coolify-list-servers` - List all Coolify servers
  - `coolify-list-applications` - List applications in a project
  - `coolify-create-github-app` - **Deploy GitHub repositories to Coolify**

### TypeScript Server (Port 3010)

- **Basic Tools**
  - `greet` - Simple greeting tool
  - `multi-greet` - Multiple greetings with notifications

- **Web Scraping Tools**
  - `scrape-dynamic-url` - Scrape dynamic web pages using Playwright

## API Usage

### Authentication

All requests require Bearer token authentication:

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"jsonrpc": "2.0", "method": "tools/list", "id": 1}' \
     https://YOUR_DOMAIN:3000/mcp
```

### Example Tool Calls

```bash
# Math tool example
curl -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "jsonrpc": "2.0",
       "method": "tools/call",
       "params": {
         "name": "add-numbers",
         "arguments": {"a": 5, "b": 3}
       },
       "id": 1
     }' \
     https://YOUR_DOMAIN:3009/mcp

# Web scraping example
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
     https://YOUR_DOMAIN:3010/mcp
```

## Security Best Practices

1. **API Keys**
   - Generate cryptographically secure API keys with `openssl rand -hex 32`
   - Use environment variables (never hardcode tokens)
   - Rotate keys regularly in production
   - Never commit keys to version control

2. **Network Security**
   - Use HTTPS in production
   - Configure firewall rules
   - Limit access to necessary IPs only

3. **Monitoring**
   - Monitor the `/health` endpoints
   - Set up log aggregation
   - Monitor resource usage

4. **Database Security**
   - Use strong database passwords
   - Enable database SSL/TLS
   - Regular database backups

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Verify `MCP_API_KEY` is set correctly
   - Ensure Bearer token format: `Authorization: Bearer YOUR_API_KEY`

2. **CORS Issues**
   - Check `ALLOWED_ORIGINS` configuration
   - Ensure your client domain is included

3. **Health Check Failures**
   - Verify containers are running
   - Check container logs for errors
   - Ensure ports are accessible

### Debug Commands

```bash
# View container logs
docker compose logs python-mcp
docker compose logs typescript-mcp
docker compose logs postgres

# Test database connectivity
docker compose exec postgres psql -U mcpuser -d mcpdb -c "SELECT 1;"

# Restart services
docker compose restart python-mcp typescript-mcp
```

## Performance Tuning

### Resource Limits

Consider setting resource limits in production:

```yaml
# Add to docker-compose.yml services
deploy:
  resources:
    limits:
      memory: 512M
      cpus: '0.5'
    reservations:
      memory: 256M
      cpus: '0.25'
```

### Scaling

For high traffic, consider:
- Running multiple instances behind a load balancer
- Using external PostgreSQL service
- Implementing Redis for session storage
- Setting up horizontal pod autoscaling (if using Kubernetes)

## Accessing Local Development Servers

When your MCP servers are deployed externally but you want to scrape a local development page, you have several options:

### Option 1: ngrok (Recommended)
```bash
# Install ngrok
npm install -g ngrok

# Expose your local dev server
ngrok http 3000

# Use the generated URL in your scraping requests
# https://abc123.ngrok.io instead of http://localhost:3000
```

### Option 2: Use Your Local Network IP
```bash
# Find your local IP
# Linux/macOS: ip addr show or ifconfig
# Windows: ipconfig

# Start your dev server on all interfaces
npm run dev -- --host 0.0.0.0 --port 3000
# Then use: http://YOUR_LOCAL_IP:3000
```

### Option 3: Deploy to Same Network
- Deploy both your app and MCP servers to the same cloud provider
- Use internal networking between services

### Option 4: Run MCP Servers Locally
- Keep MCP servers running locally for development
- Deploy only for production use

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review container logs
3. Verify environment configuration
4. Test with minimal examples