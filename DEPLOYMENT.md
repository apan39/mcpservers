# MCP Servers - Production Deployment Guide

## Overview

This repository contains production-ready MCP (Model Context Protocol) servers implemented in both Python and TypeScript. The servers have been hardened for network deployment with proper security, error handling, and monitoring.

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
   ```
   
   **Required variables:**
   - `MCP_API_KEY` - Strong API key for authentication
   - `POSTGRES_PASSWORD` - Secure database password
   
   **Optional variables:**
   - `ALLOWED_ORIGINS` - Comma-separated list of allowed origins
   - `LOG_LEVEL` - Logging level (DEBUG, INFO, WARNING, ERROR)

2. **Coolify Setup** - Ensure your Coolify instance is configured

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

### 2. Coolify Deployment

1. **Create New Service**
   - Choose "Docker Compose"
   - Connect your repository
   - Set branch to `main`

2. **Environment Configuration**
   In Coolify, set these environment variables:
   ```
   MCP_API_KEY=your-secure-api-key-here
   POSTGRES_PASSWORD=your-secure-postgres-password
   ALLOWED_ORIGINS=https://your-domain.com,https://other-allowed-domain.com
   LOG_LEVEL=INFO
   ```

3. **Deploy**
   - Click "Deploy" in Coolify
   - Monitor logs for successful startup

### 3. Production Verification

After deployment, verify the services:

```bash
# Health checks (replace YOUR_DOMAIN)
curl https://YOUR_DOMAIN:3009/health
curl https://YOUR_DOMAIN:3010/health

# Test authentication
curl -H "Authorization: Bearer YOUR_API_KEY" https://YOUR_DOMAIN:3009/mcp
```

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
  - `crawl-url` - Extract text from web pages using crawl4ai

### TypeScript Server (Port 3010)

- **Basic Tools**
  - `greet` - Simple greeting tool
  - `multi-greet` - Multiple greetings with notifications
  - `start-notification-stream` - Test streaming notifications

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
   - Use strong, randomly generated API keys
   - Rotate keys regularly
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