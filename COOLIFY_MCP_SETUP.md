# Coolify MCP Remote Tools Setup Guide

This guide explains how to use the Coolify API management tools remotely via MCP (Model Context Protocol) in any project.

## Required Files to Copy

When setting up Coolify API access in a new project, copy these files:

### 1. Environment Configuration (.env)
```bash
# Coolify API Configuration
COOLIFY_BASE_URL=http://135.181.149.150:8000
COOLIFY_API_TOKEN=MQFql2g3WxGeGhFUZmeT8kypZvay9bnYciLyqmxFc0cd71bf

# Optional: MCP Server Configuration
MCP_API_KEY=your-mcp-api-key-here
PORT=3009
```

### 2. MCP Configuration (.mcp.json or claude_mcp_config.json)
```json
{
  "mcpServers": {
    "remote-python-tools": {
      "command": "uvx",
      "args": ["mcp", "serve", "http://135.181.149.150:3009/sse"],
      "env": {
        "MCP_API_KEY": "4446e3ca599152c85fc96ecebb0367674e823694e5197a0ed8ca1262e825075f"
      }
    }
  }
}
```

## Available Remote Coolify Tools

The remote MCP server provides these Coolify management tools:

### Core Management
- `coolify-get-version` - Get Coolify instance version
- `coolify-list-projects` - List all projects
- `coolify-list-servers` - List all servers
- `coolify-list-applications` - List applications in a project

### Application Lifecycle
- `coolify-create-github-app` - Create new app from GitHub repo
- `coolify-deploy-application` - Trigger deployment
- `coolify-restart-application` - Restart application
- `coolify-start-application` - Start application
- `coolify-stop-application` - Stop application
- `coolify-delete-application` - Delete application

### Monitoring & Debugging
- `coolify-get-application-info` - Get detailed app information
- `coolify-get-application-logs` - Get runtime logs
- `coolify-get-deployment-logs` - Get deployment logs with UUID

## Setup Instructions

### For Claude Desktop

1. Copy `.env` file to your project root
2. Update your Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "remote-python-tools": {
      "command": "uvx",
      "args": ["mcp", "serve", "http://135.181.149.150:3009/sse"],
      "env": {
        "MCP_API_KEY": "4446e3ca599152c85fc96ecebb0367674e823694e5197a0ed8ca1262e825075f"
      }
    }
  }
}
```

3. Restart Claude Desktop
4. Verify connection by testing `coolify-get-version`

### For Other MCP Clients

1. Copy `.env` file to your project root
2. Configure your MCP client to connect to: `http://135.181.149.150:3009/sse`
3. Set the `MCP_API_KEY` environment variable
4. Test connection with any Coolify tool

## Common Issues & Solutions

### Connection Problems
- **Issue**: "Cannot connect to MCP server"
- **Solution**: Verify the MCP server is running at `http://135.181.149.150:3009`
- **Test**: `curl http://135.181.149.150:3009/health`

### Authentication Errors
- **Issue**: "Unauthorized" or "401" errors
- **Solution**: Check that `MCP_API_KEY` matches the server configuration
- **Verify**: Ensure the API key in `.env` matches the server

### Coolify API Errors
- **Issue**: "COOLIFY_API_TOKEN not set" or "403 Forbidden"
- **Solution**: Verify the Coolify API token is valid and has proper permissions
- **Test**: `curl -H "Authorization: Bearer YOUR_TOKEN" http://135.181.149.150:8000/api/v1/version`

### Tool Not Found
- **Issue**: "Unknown tool: coolify-xxx"
- **Solution**: The MCP server may not be properly connected
- **Debug**: List available tools first to verify connection

## Testing the Setup

Run these commands to verify your setup:

```bash
# Test MCP server health
curl http://135.181.149.150:3009/health

# Test Coolify API directly
curl -H "Authorization: Bearer MQFql2g3WxGeGhFUZmeT8kypZvay9bnYciLyqmxFc0cd71bf" \
     "http://135.181.149.150:8000/api/v1/version"
```

In Claude or your MCP client:
1. Use `coolify-get-version` to test basic connectivity
2. Use `coolify-list-projects` to verify API access
3. Use `coolify-get-application-info` with a known app UUID

## Environment Variables Reference

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `COOLIFY_BASE_URL` | Yes | Coolify instance URL | `http://135.181.149.150:8000` |
| `COOLIFY_API_TOKEN` | Yes | Coolify API authentication token | `MQFql2g3...` |
| `MCP_API_KEY` | Yes | MCP server authentication key | `4446e3ca...` |
| `PORT` | No | Local port (if running own server) | `3009` |

## Known Working Applications

Current applications managed via these tools:
- **Python MCP** (UUID: `zs8sk0cgs4s8gsgwswsg88ko`): `running:healthy` - 15+ tools
- **TypeScript MCP** (UUID: `k8wco488444c8gw0sscs04k8`): `running:unhealthy` - 3 tools  
- **Browser-use MCP** (UUID: `w8wcwg48ok4go8g8swgwkgk8`): `running:healthy` - 36+ tools

## Project Integration

### Add to README.md
```markdown
## Coolify Integration

This project uses remote Coolify API tools via MCP for deployment management.

**Setup:**
1. Copy `.env` with Coolify credentials
2. Configure MCP client to connect to `http://135.181.149.150:3009/sse`
3. Use `coolify-get-version` to test connection

**Available Tools:** See [COOLIFY_MCP_SETUP.md](COOLIFY_MCP_SETUP.md)
```

### Add to CLAUDE.md
```markdown
## Coolify Deployment Tools

Access Coolify API remotely via MCP tools:
- Server: `http://135.181.149.150:3009/sse`
- Required: `MCP_API_KEY` environment variable
- Test with: `coolify-get-version`

See COOLIFY_MCP_SETUP.md for complete setup instructions.
```

## Security Notes

- The API tokens shown are for development/demo purposes
- In production, use proper secret management
- Coolify API tokens have full deployment access
- MCP connections should be secured appropriately

## Troubleshooting

For deployment issues, follow this debugging sequence:
1. Test MCP server connectivity
2. Verify Coolify API token validity  
3. Check application status with `coolify-get-application-info`
4. Review deployment logs with `coolify-get-deployment-logs`
5. Monitor application logs with `coolify-get-application-logs`

Refer to `COOLIFY_API_DEBUGGING.md` for comprehensive debugging patterns.