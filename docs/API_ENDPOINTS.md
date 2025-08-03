# API Endpoints Documentation

## Application Base URLs

All applications follow the Coolify URL pattern: `http://{uuid}.135.181.149.150.sslip.io`

| Application | Base URL | Health Status |
|-------------|----------|---------------|
| **ProjectAdminCMS** | `http://akg0w8kc0kgsc0kc0k4wk0cc.135.181.149.150.sslip.io` | running:unhealthy |
| **MrMechanic** | `http://k4w4wgokwk8000owwgc408ow.135.181.149.150.sslip.io` | running:unhealthy |
| **GeneralVectorEmbed** | `http://skgo080ggw00gso4w8wc4ss4.135.181.149.150.sslip.io` | running:unhealthy |
| **Flowise** | `http://w0cwck80owcgkw4s4kkos4ko.135.181.149.150.sslip.io` | running:unhealthy |

## MCP Services

| Service | Base URL | Health Status |
|---------|----------|---------------|
| **Python MCP** | `http://zs8sk0cgs4s8gsgwswsg88ko.135.181.149.150.sslip.io` | running:healthy |
| **TypeScript MCP** | `http://zw0o84skskgc8kgooswgo8k4.135.181.149.150.sslip.io` | running:healthy |
| **Browser MCP** | `http://w8wcwg48ok4go8g8swgwkgk8.135.181.149.150.sslip.io` | running:healthy |

## Common API Patterns

### Authentication

#### PayloadCMS Applications (ProjectAdminCMS, MrMechanic)
```http
POST /api/users/login
Content-Type: application/json

{
  "email": "admin@example.com",
  "password": "your_password"
}
```

#### Flowise
```http
# Username/Password Authentication
# Default: admin/password
```

#### GeneralVectorEmbed
```http
# NextAuth Integration
GET /api/auth/session
```

### Health Checks

#### Standard Health Endpoint
```http
GET /health
GET /api/health
GET /
```

## Application-Specific APIs

### ProjectAdminCMS (PayloadCMS)

**Base URL**: `http://akg0w8kc0kgsc0kc0k4wk0cc.135.181.149.150.sslip.io`

#### Core Endpoints
```http
# Admin Panel
GET /admin

# API Authentication
POST /api/users/login
POST /api/users/logout
GET /api/users/me

# Collections (depends on Payload configuration)
GET /api/{collection-name}
POST /api/{collection-name}
GET /api/{collection-name}/{id}
PUT /api/{collection-name}/{id}
DELETE /api/{collection-name}/{id}

# Media
POST /api/media
GET /api/media/{id}
```

### MrMechanic (AI Assistant)

**Base URL**: `http://k4w4wgokwk8000owwgc408ow.135.181.149.150.sslip.io`

#### Core Endpoints
```http
# Admin Panel
GET /admin

# AI Chat/Assistant API (expected endpoints)
POST /api/chat
POST /api/assistant
GET /api/conversations
GET /api/conversations/{id}

# PayloadCMS Standard Endpoints
POST /api/users/login
GET /api/users/me
```

### GeneralVectorEmbed (Vector Database)

**Base URL**: `http://skgo080ggw00gso4w8wc4ss4.135.181.149.150.sslip.io`

#### Core Endpoints
```http
# Authentication (NextAuth)
GET /api/auth/session
POST /api/auth/signin
POST /api/auth/signout

# Vector Operations (expected endpoints)
POST /api/embed
POST /api/search
GET /api/collections
POST /api/collections
DELETE /api/collections/{id}

# Document Management
POST /api/documents
GET /api/documents
GET /api/documents/{id}
DELETE /api/documents/{id}
```

### Flowise (AI Workflow Builder)

**Base URL**: `http://w0cwck80owcgkw4s4kkos4ko.135.181.149.150.sslip.io`

#### Core Endpoints
```http
# Main Application
GET /

# API Endpoints
GET /api/v1/chatflows
POST /api/v1/chatflows
GET /api/v1/chatflows/{id}
PUT /api/v1/chatflows/{id}
DELETE /api/v1/chatflows/{id}

# Predictions/Chat
POST /api/v1/prediction/{id}

# Components and Nodes
GET /api/v1/nodes
GET /api/v1/components-credentials

# Authentication
GET /api/v1/apikey
POST /api/v1/apikey

# Admin Features
GET /api/v1/stats
GET /api/v1/version
```

## MCP Service APIs

### Python MCP Server

**Base URL**: `http://zs8sk0cgs4s8gsgwswsg88ko.135.181.149.150.sslip.io`

#### Available Tools (15+ tools)
```http
# Coolify Management
POST /tools/coolify-list-applications
POST /tools/coolify-get-application-info
POST /tools/coolify-deploy-application
POST /tools/coolify-restart-application
POST /tools/coolify-get-application-logs

# Environment Management
POST /tools/coolify-set-env-variable
POST /tools/coolify-delete-env-variable
POST /tools/coolify-bulk-update-env

# Deployment Management
POST /tools/coolify-get-recent-deployments
POST /tools/coolify-get-deployment-logs
POST /tools/coolify-watch-deployment

# Basic Math Tools
POST /tools/add-numbers
POST /tools/multiply-numbers
POST /tools/calculate-percentage

# Text Processing
POST /tools/string-operations
POST /tools/word-count
POST /tools/format-text

# Web Scraping
POST /tools/crawl-url
```

### TypeScript MCP Server

**Base URL**: `http://zw0o84skskgc8kgooswgo8k4.135.181.149.150.sslip.io`

#### Available Tools
```http
# GitHub Integration
POST /tools/github-get-user
POST /tools/github-list-repos
POST /tools/github-get-repo
POST /tools/github-get-contents

# Flowise Integration
POST /tools/flowise-list-chatflows
POST /tools/flowise-get-chatflow
POST /tools/flowise-predict

# Context7 Documentation
POST /tools/context7-get-docs
POST /tools/context7-search-examples

# Web Scraping
POST /tools/scrape-dynamic-url

# Utilities
POST /tools/greet
POST /tools/multi-greet
```

### Browser MCP Server

**Base URL**: `http://w8wcwg48ok4go8g8swgwkgk8.135.181.149.150.sslip.io`

#### Available Tools
```http
# Browser Automation
POST /tools/create_browser_session
POST /tools/navigate_to_url
POST /tools/get_page_content
POST /tools/execute_browser_task
POST /tools/close_browser_session
POST /tools/list_browser_sessions
```

## Inter-Service Communication

### Example Integration Patterns

#### Using MrMechanic with GeneralVectorEmbed
```javascript
// From MrMechanic, search vectors in GeneralVectorEmbed
const response = await fetch('http://skgo080ggw00gso4w8wc4ss4.135.181.149.150.sslip.io/api/search', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: "user question",
    collection: "knowledge_base"
  })
});
```

#### Using Flowise with MCP Tools
```javascript
// Execute Coolify operations from Flowise workflow
const response = await fetch('http://zs8sk0cgs4s8gsgwswsg88ko.135.181.149.150.sslip.io/tools/coolify-list-applications', {
  method: 'POST',
  headers: { 'Authorization': 'Bearer MCP_API_KEY' }
});
```

## Error Handling

### Common HTTP Status Codes
- `200` - Success
- `400` - Bad Request (invalid parameters)
- `401` - Unauthorized (missing/invalid authentication)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `500` - Internal Server Error

### Standard Error Response Format
```json
{
  "error": {
    "message": "Error description",
    "code": "ERROR_CODE",
    "details": {}
  }
}
```

## Rate Limiting

Most applications implement rate limiting. Check response headers:
- `X-RateLimit-Limit`
- `X-RateLimit-Remaining`
- `X-RateLimit-Reset`

## CORS Configuration

All applications are configured for production CORS. For development, ensure proper origin headers are set when making cross-origin requests.

## Testing APIs

### Using curl
```bash
# Test health endpoint
curl http://akg0w8kc0kgsc0kc0k4wk0cc.135.181.149.150.sslip.io/

# Test with authentication
curl -H "Authorization: Bearer <token>" \
     http://zs8sk0cgs4s8gsgwswsg88ko.135.181.149.150.sslip.io/tools/coolify-list-applications
```

### Using the Browser MCP
You can use the Browser MCP server to automate API testing:
```bash
# Create browser session and test APIs
curl -X POST http://w8wcwg48ok4go8g8swgwkgk8.135.181.149.150.sslip.io/tools/create_browser_session \
  -d '{"session_id": "test", "headless": true}'
```