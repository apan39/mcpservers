# PayloadCMS 3.x MCP Tools Documentation

## Overview

The PayloadCMS MCP tools provide comprehensive integration with PayloadCMS 3.x instances, enabling full UI-equivalent functionality through API calls. These tools are implemented in the TypeScript MCP server and provide access to all core PayloadCMS features.

## 🔧 Available Tools (12 Total)

### Collection CRUD Operations (6 tools)

#### `payload-find-documents`
Query and find documents in a PayloadCMS collection with filtering, pagination, and sorting.

**Usage:**
```json
{
  "config": {
    "baseUrl": "https://cms.example.com",
    "apiKey": "your-api-key"
  },
  "collection": "posts",
  "where": {"status": {"equals": "published"}},
  "limit": 10,
  "page": 1,
  "sort": "-createdAt",
  "depth": 2,
  "locale": "en"
}
```

#### `payload-get-document`
Get a specific document by ID from a PayloadCMS collection.

**Usage:**
```json
{
  "config": {
    "baseUrl": "https://cms.example.com",
    "token": "jwt-token"
  },
  "collection": "posts",
  "id": "64a7b8c9d1234567890abcde",
  "depth": 1,
  "locale": "en"
}
```

#### `payload-create-document`
Create a new document in a PayloadCMS collection.

**Usage:**
```json
{
  "config": {
    "baseUrl": "https://cms.example.com",
    "token": "jwt-token"
  },
  "collection": "posts",
  "data": {
    "title": "New Blog Post",
    "content": "This is the content of the blog post.",
    "status": "published"
  },
  "locale": "en",
  "draft": false
}
```

#### `payload-update-document`
Update an existing document in a PayloadCMS collection.

**Usage:**
```json
{
  "config": {
    "baseUrl": "https://cms.example.com",
    "token": "jwt-token"
  },
  "collection": "posts",
  "id": "64a7b8c9d1234567890abcde",
  "data": {
    "title": "Updated Blog Post Title",
    "status": "published"
  },
  "locale": "en"
}
```

#### `payload-delete-document`
Delete a document from a PayloadCMS collection.

**Usage:**
```json
{
  "config": {
    "baseUrl": "https://cms.example.com",
    "token": "jwt-token"
  },
  "collection": "posts",
  "id": "64a7b8c9d1234567890abcde"
}
```

#### `payload-count-documents`
Count documents in a PayloadCMS collection with optional filtering.

**Usage:**
```json
{
  "config": {
    "baseUrl": "https://cms.example.com",
    "apiKey": "your-api-key"
  },
  "collection": "posts",
  "where": {"status": {"equals": "published"}}
}
```

### Authentication Operations (3 tools)

#### `payload-login`
Authenticate with PayloadCMS and obtain JWT token.

**Usage:**
```json
{
  "config": {
    "baseUrl": "https://cms.example.com"
  },
  "collection": "users",
  "email": "admin@example.com",
  "password": "secure-password"
}
```

#### `payload-get-current-user`
Get information about the currently authenticated user.

**Usage:**
```json
{
  "config": {
    "baseUrl": "https://cms.example.com",
    "token": "jwt-token"
  },
  "collection": "users"
}
```

### Global Operations (2 tools)

#### `payload-get-global`
Get a PayloadCMS global configuration.

**Usage:**
```json
{
  "config": {
    "baseUrl": "https://cms.example.com",
    "token": "jwt-token"
  },
  "slug": "header",
  "locale": "en"
}
```

#### `payload-update-global`
Update a PayloadCMS global configuration.

**Usage:**
```json
{
  "config": {
    "baseUrl": "https://cms.example.com",
    "token": "jwt-token"
  },
  "slug": "header",
  "data": {
    "logo": "new-logo.png",
    "navigation": [
      {"label": "Home", "url": "/"},
      {"label": "About", "url": "/about"}
    ]
  }
}
```

### File Management (1 tool)

#### `payload-upload-file`
Upload a file to a PayloadCMS upload collection.

**Usage:**
```json
{
  "config": {
    "baseUrl": "https://cms.example.com",
    "token": "jwt-token"
  },
  "collection": "media",
  "fileData": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
  "fileName": "image.png",
  "mimeType": "image/png",
  "data": {
    "alt": "Alt text for the image"
  }
}
```

**File Data Formats:**
- **Data URL**: `"data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA..."`
- **HTTP URL**: `"https://example.com/image.png"`
- **Base64**: Raw base64 encoded data

### GraphQL Operations (1 tool)

#### `payload-graphql-query`
Execute a GraphQL query against PayloadCMS.

**Usage:**
```json
{
  "config": {
    "baseUrl": "https://cms.example.com",
    "token": "jwt-token"
  },
  "query": "query { Posts { docs { id title status } } }",
  "variables": {
    "limit": 10
  }
}
```

### Utility Operations (1 tool)

#### `payload-health-check`
Check PayloadCMS API connectivity and get version information.

**Usage:**
```json
{
  "config": {
    "baseUrl": "https://cms.example.com",
    "apiKey": "your-api-key"
  }
}
```

## 🔐 Authentication

PayloadCMS MCP tools support multiple authentication methods:

### 1. JWT Token Authentication
```json
{
  "config": {
    "baseUrl": "https://cms.example.com",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

### 2. API Key Authentication
```json
{
  "config": {
    "baseUrl": "https://cms.example.com",
    "apiKey": "your-collection-api-key"
  }
}
```

### 3. Automatic Token Management
The tools automatically store and reuse JWT tokens after successful login:

1. Use `payload-login` to authenticate
2. Token is automatically stored and used for subsequent requests
3. Token is associated with the `baseUrl`
4. Use `payload-logout` to clear stored tokens

## 📁 Configuration Patterns

### Basic Configuration
```json
{
  "baseUrl": "https://cms.example.com",
  "timeout": 30000
}
```

### With API Key
```json
{
  "baseUrl": "https://cms.example.com",
  "apiKey": "users API-Key your-api-key-here",
  "timeout": 30000
}
```

### With JWT Token
```json
{
  "baseUrl": "https://cms.example.com",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "timeout": 30000
}
```

### Multiple Instances
```json
// Production
{
  "baseUrl": "https://cms.production.com",
  "token": "prod-jwt-token"
}

// Staging
{
  "baseUrl": "https://cms.staging.com",
  "token": "staging-jwt-token"
}
```

## 🌐 Environment Configuration

Add to your `.env` file:

```bash
# PayloadCMS API Integration
PAYLOAD_BASE_URL=https://cms.example.com
PAYLOAD_API_KEY=your-api-key
PAYLOAD_JWT_TOKEN=jwt-token

# Secondary PayloadCMS instance
PAYLOAD_STAGING_BASE_URL=https://cms.staging.com
PAYLOAD_STAGING_API_KEY=staging-api-key
PAYLOAD_STAGING_JWT_TOKEN=staging-jwt-token
```

## 🚀 Usage Examples

### Complete Blog Management Workflow

```bash
# 1. Login and authenticate
claude mcp call typescript-tools payload-login '{
  "config": {"baseUrl": "https://cms.example.com"},
  "email": "admin@example.com",
  "password": "secure-password"
}'

# 2. Get current user info
claude mcp call typescript-tools payload-get-current-user '{
  "config": {"baseUrl": "https://cms.example.com"}
}'

# 3. Create a new blog post
claude mcp call typescript-tools payload-create-document '{
  "config": {"baseUrl": "https://cms.example.com"},
  "collection": "posts",
  "data": {
    "title": "Getting Started with PayloadCMS",
    "content": "This is a comprehensive guide...",
    "status": "draft",
    "author": "64a7b8c9d1234567890abcde"
  }
}'

# 4. Upload a featured image
claude mcp call typescript-tools payload-upload-file '{
  "config": {"baseUrl": "https://cms.example.com"},
  "collection": "media",
  "fileData": "https://example.com/featured-image.jpg",
  "fileName": "featured-image.jpg",
  "data": {"alt": "Featured image for blog post"}
}'

# 5. Update the post with the featured image
claude mcp call typescript-tools payload-update-document '{
  "config": {"baseUrl": "https://cms.example.com"},
  "collection": "posts",
  "id": "64a7b8c9d1234567890abcde",
  "data": {
    "featuredImage": "64a7b8c9d1234567890abcdf",
    "status": "published"
  }
}'

# 6. Query published posts
claude mcp call typescript-tools payload-find-documents '{
  "config": {"baseUrl": "https://cms.example.com"},
  "collection": "posts",
  "where": {"status": {"equals": "published"}},
  "limit": 10,
  "sort": "-createdAt"
}'
```

### Global Configuration Management

```bash
# Get current header configuration
claude mcp call typescript-tools payload-get-global '{
  "config": {"baseUrl": "https://cms.example.com"},
  "slug": "header"
}'

# Update navigation menu
claude mcp call typescript-tools payload-update-global '{
  "config": {"baseUrl": "https://cms.example.com"},
  "slug": "header",
  "data": {
    "navigation": [
      {"label": "Home", "url": "/"},
      {"label": "Blog", "url": "/blog"},
      {"label": "About", "url": "/about"},
      {"label": "Contact", "url": "/contact"}
    ]
  }
}'
```

### GraphQL Advanced Queries

```bash
# Complex GraphQL query with relationships
claude mcp call typescript-tools payload-graphql-query '{
  "config": {"baseUrl": "https://cms.example.com"},
  "query": "query GetPostsWithAuthor($limit: Int) { Posts(limit: $limit) { docs { id title status author { name email } featuredImage { url alt } } } }",
  "variables": {"limit": 5}
}'
```

## 🛠 Local vs Remote Usage

### Local Development
```bash
# Use local TypeScript MCP server
claude mcp call typescript-tools payload-health-check '{
  "config": {"baseUrl": "http://localhost:3000"}
}'
```

### Remote Deployment
```bash
# Use remote TypeScript MCP server
claude mcp call remote-typescript-tools payload-health-check '{
  "config": {"baseUrl": "https://cms.production.com"}
}'
```

## ⚠️ Error Handling

Common error scenarios and solutions:

### Authentication Errors
```
❌ PayloadCMS API Error 401: Unauthorized
```
**Solution:** Check your API key or JWT token, or use `payload-login` to authenticate.

### Collection Not Found
```
❌ PayloadCMS API Error 404: Collection 'posts' not found
```
**Solution:** Verify the collection slug exists in your PayloadCMS configuration.

### Validation Errors
```
❌ PayloadCMS API Error 400: Validation failed
```
**Solution:** Check required fields and field types in your data payload.

### Connection Errors
```
❌ Error: fetch failed
```
**Solution:** Verify the `baseUrl` is correct and the PayloadCMS instance is accessible.

## 🔄 Token Management

The tools automatically manage JWT tokens:

1. **Login**: `payload-login` stores the token for the instance
2. **Auto-use**: Subsequent requests automatically use the stored token
3. **Refresh**: `payload-refresh-token` updates the stored token
4. **Logout**: `payload-logout` clears the stored token
5. **Multi-instance**: Tokens are stored per `baseUrl`

## 📊 Performance Tips

1. **Use pagination** for large datasets with `limit` and `page`
2. **Limit depth** for relationship queries to avoid over-fetching
3. **Use GraphQL** for complex queries with specific field selection
4. **Cache frequently accessed globals** in your application
5. **Use API keys** for read-only operations to avoid token expiration

## 🎯 Best Practices

1. **Environment separation**: Use different configurations for dev/staging/prod
2. **Error handling**: Always wrap API calls in try-catch blocks
3. **Authentication**: Use JWT tokens for user-specific operations, API keys for general access
4. **Validation**: Validate data before sending to avoid 400 errors
5. **Security**: Never expose API keys or tokens in client-side code
6. **Monitoring**: Use `payload-health-check` for uptime monitoring

This comprehensive tool suite enables full PayloadCMS backend management through MCP tools, supporting both local development and remote deployment scenarios with VS Code multi-window support.