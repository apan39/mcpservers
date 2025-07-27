# Project Context for Claude

## Key Documentation Files
- README.md - Main project overview
- MCP_SETUP.md - MCP server setup instructions  
- DEPLOYMENT.md - Deployment guidelines
- COOLIFY_API_DEBUGGING.md - API debugging guide

## Project Structure
This is an MCP (Model Context Protocol) servers project with deployment automation.

## Coolify Deployment Protocol

**MANDATORY: Read this before any Coolify operations**

### 1. Pre-deployment Checks
- Read COOLIFY_API_DEBUGGING.md for comprehensive debugging patterns
- Verify environment variables are set correctly in .env file
- Use MCP Coolify tools to check server status: `coolify-get-version`
- Confirm target application UUID and current status

### 2. Deployment Process
```bash
# 1. Trigger deployment via API (ensure correct authentication)
source .env
curl -X POST -H "Authorization: Bearer ${COOLIFY_API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"uuid": "APPLICATION_UUID"}' \
  "http://135.181.149.150:8000/api/v1/deploy"

# 2. Capture deployment UUID from response
# 3. Monitor deployment progress with logs
```

### 3. Deployment Verification Protocol
**Always perform these checks after deployment:**
- [ ] Deployment API returns success status  
- [ ] Deployment logs show container start without errors
- [ ] Application responds to HTTP health check
- [ ] MCP endpoint responds correctly
- [ ] Environment variables are properly loaded

### 4. Error Investigation Protocol  
**Follow this exact sequence for failures:**
1. **Use MCP Coolify tools first** (coolify-list-applications, etc.)
2. **Check deployment logs** via API with deployment UUID:
   ```bash
   curl -H "Authorization: Bearer ${COOLIFY_API_TOKEN}" \
     "http://135.181.149.150:8000/api/v1/deployments/DEPLOYMENT_UUID"
   ```
3. **Verify application configuration** (build pack, env vars, dockerfile)
4. **Common issues**: 
   - Missing MCP_API_KEY environment variable
   - Health check failures (`curl: not found` - add curl to Dockerfile)
   - Wrong CMD in Dockerfile
   - Missing dependencies in requirements.txt
5. **Test basic connectivity** before assuming application issues

### 5. Known Working Applications
- Python MCP (UUID: zs8sk0cgs4s8gsgwswsg88ko): `running:healthy` - 19 tools (complete Coolify management suite)
- TypeScript MCP (UUID: k8wco488444c8gw0sscs04k8): `running:healthy` - 3 tools
- Browser-use MCP (UUID: w8wcwg48ok4go8g8swgwkgk8): `running:healthy` - 6 browser automation tools

### 6. Communication Guidelines
- **Never assume deployment success** without explicit verification
- **Always check logs** when deployments fail
- **Use systematic debugging** approach from COOLIFY_API_DEBUGGING.md
- **Update status** in this document after major changes