# Coolify Deployment Fix Guide

## Identified Issue
The Coolify MCP tools were showing "N/A" for server UUID, but the actual server information is available via direct API calls.

## Correct Server Information
**Server UUID**: `csgkk88okkgkwg8w0g8og8c8`  
**Server Name**: localhost (host.docker.internal)  
**Status**: reachable and usable  
**Coolify Version**: 4.0.0-beta.420.6

## Working Project UUIDs
- **mcpservers**: `l8cog4c48w48kckkcgos8cwg`
- **Rag**: `loso8oo84sk80s008kwccock` (cleaned)
- **Zuperinvoice**: `kg44484o0s0kc8k4sg40wkwc`

## Deployment Command Template

When deploying applications in other projects, use this exact format:

```bash
# Via MCP Tools (if available)
coolify-create-github-app \
  --project_uuid "YOUR_PROJECT_UUID" \
  --server_uuid "csgkk88okkgkwg8w0g8og8c8" \
  --git_repository "https://github.com/username/repo" \
  --name "app-name" \
  --git_branch "main" \
  --build_pack "dockerfile"

# Via Direct API Call (backup method)
curl -X POST "http://135.181.149.150:8000/api/v1/applications/public" \
  -H "Authorization: Bearer MQFql2g3WxGeGhFUZmeT8kypZvay9bnYciLyqmxFc0cd71bf" \
  -H "Content-Type: application/json" \
  -d '{
    "project_uuid": "YOUR_PROJECT_UUID",
    "server_uuid": "csgkk88okkgkwg8w0g8og8c8",
    "git_repository": "https://github.com/username/repo",
    "name": "app-name",
    "git_branch": "main",
    "build_pack": "dockerfile",
    "environment_name": "production",
    "instant_deploy": true
  }'
```

## Project-Specific Examples

### For RAG Project
```bash
# Clean RAG project ready for deployment
PROJECT_UUID="loso8oo84sk80s008kwccock"
SERVER_UUID="csgkk88okkgkwg8w0g8og8c8"
```

### For New Projects
1. Get project UUID: `coolify-list-projects`
2. Use server UUID: `csgkk88okkgkwg8w0g8og8c8`
3. Deploy with proper UUIDs

## Common Deployment Errors & Fixes

### Error: "Server not found"
**Cause**: Using wrong server identifier  
**Fix**: Use `csgkk88okkgkwg8w0g8og8c8` (not "localhost" or "N/A")

### Error: "Project not found" 
**Cause**: Invalid project UUID  
**Fix**: Run `coolify-list-projects` to get correct UUID

### Error: "404 Not Found" on application listing
**Cause**: Projects may be empty or API endpoint format issue  
**Fix**: Use direct application creation instead of listing first

## Verification Steps

1. **Test server connectivity**:
   ```bash
   curl -H "Authorization: Bearer MQFql2g3WxGeGhFUZmeT8kypZvay9bnYciLyqmxFc0cd71bf" \
        "http://135.181.149.150:8000/api/v1/servers"
   ```

2. **Verify project exists**:
   ```bash
   coolify-list-projects
   ```

3. **Check deployment status**:
   ```bash
   coolify-get-application-info --app_uuid "NEW_APP_UUID"
   ```

## Working Application Examples

Current successful deployments using these UUIDs:
- **Python MCP** (UUID: `zs8sk0cgs4s8gsgwswsg88ko`): `running:healthy`
- **Browser-use MCP** (UUID: `w8wcwg48ok4go8g8swgwkgk8`): `running:healthy`

## Backup Deployment Method

If MCP tools fail, use direct curl commands:

```bash
# 1. Create application
RESPONSE=$(curl -s -X POST "http://135.181.149.150:8000/api/v1/applications/public" \
  -H "Authorization: Bearer MQFql2g3WxGeGhFUZmeT8kypZvay9bnYciLyqmxFc0cd71bf" \
  -H "Content-Type: application/json" \
  -d '{
    "project_uuid": "YOUR_PROJECT_UUID",
    "server_uuid": "csgkk88okkgkwg8w0g8og8c8",
    "git_repository": "https://github.com/username/repo",
    "name": "app-name",
    "git_branch": "main",
    "build_pack": "dockerfile",
    "instant_deploy": true
  }')

# 2. Extract app UUID from response
APP_UUID=$(echo $RESPONSE | jq -r '.uuid')

# 3. Monitor deployment
curl -H "Authorization: Bearer MQFql2g3WxGeGhFUZmeT8kypZvay9bnYciLyqmxFc0cd71bf" \
     "http://135.181.149.150:8000/api/v1/applications/$APP_UUID"
```

## Updated CLAUDE.md Addition

Add this to your project's CLAUDE.md:

```markdown
## Coolify Deployment Protocol - FIXED

**Correct Server UUID**: `csgkk88okkgkwg8w0g8og8c8`  
**Projects Available**: 
- mcpservers: `l8cog4c48w48kckkcgos8cwg`
- Rag: `loso8oo84sk80s008kwccock` 
- Zuperinvoice: `kg44484o0s0kc8k4sg40wkwc`

**Deployment Template**:
```
coolify-create-github-app \
  --project_uuid "PROJECT_UUID_HERE" \
  --server_uuid "csgkk88okkgkwg8w0g8og8c8" \
  --git_repository "REPO_URL" \
  --name "APP_NAME"
```

If MCP tools show server as "N/A", ignore this - the UUID `csgkk88okkgkwg8w0g8og8c8` is correct and working.
```

## Summary

The issue was incorrect UUID parsing in the MCP tool display. The actual server UUID `csgkk88okkgkwg8w0g8og8c8` works correctly for deployments. Use this UUID for all future deployments in any project.