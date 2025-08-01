# Coolify API Debugging Guide

This guide documents how to effectively debug deployment issues using the Coolify API, based on successfully resolving MCP server deployment failures.

## Overview

When applications show `exited:unhealthy` or `restarting:unhealthy` in Coolify, the web interface often lacks detailed diagnostics. The Coolify API provides powerful endpoints for deep debugging.

## Authentication Setup

```bash
COOLIFY_BASE_URL="http://your-coolify-server:8000"
COOLIFY_API_TOKEN="your-api-token"
AUTH_HEADER="Authorization: Bearer $COOLIFY_API_TOKEN"
```

## Essential API Endpoints for Debugging

### 1. Application Status and Configuration

```bash
# Get detailed application info
curl -H "$AUTH_HEADER" "$COOLIFY_BASE_URL/api/v1/applications/{app_uuid}"

# Key fields to check:
# - status: current application state
# - build_pack: nixpacks vs dockerfile vs static
# - start_command, build_command: custom commands
# - dockerfile_location: dockerfile path
# - last_online_at: when it was last working
```

### 2. Environment Variables

```bash
# List all environment variables
curl -H "$AUTH_HEADER" "$COOLIFY_BASE_URL/api/v1/applications/{app_uuid}/envs"

# Add missing environment variable
curl -X POST -H "$AUTH_HEADER" -H "Content-Type: application/json" \
  -d '{"key": "PORT", "value": "3000", "is_preview": false}' \
  "$COOLIFY_BASE_URL/api/v1/applications/{app_uuid}/envs"
```

### 3. Deployment History and Logs

```bash
# Get specific deployment details and logs
curl -H "$AUTH_HEADER" "$COOLIFY_BASE_URL/api/v1/deployments/{deployment_uuid}"

# Parse logs to find issues:
# - Build failures
# - Health check problems  
# - Container startup errors
# - Environment variable issues
```

### 4. Build Configuration Management

```bash
# Change build pack (crucial for Dockerfile vs Nixpacks issues)
curl -X PATCH -H "$AUTH_HEADER" -H "Content-Type: application/json" \
  -d '{"build_pack": "dockerfile"}' \
  "$COOLIFY_BASE_URL/api/v1/applications/{app_uuid}"

# Deploy with new configuration
curl -X POST -H "$AUTH_HEADER" -H "Content-Type: application/json" \
  -d '{"uuid": "{app_uuid}"}' \
  "$COOLIFY_BASE_URL/api/v1/deploy"
```

## Common Issues and API Solutions

### Issue 1: Server Works Locally But Fails in Coolify

**Symptoms:**
- `exited:unhealthy` or `restarting:unhealthy` status
- Build completes successfully
- Container starts then immediately stops

**Debugging Steps:**

1. **Check deployment logs:**
```bash
curl -H "$AUTH_HEADER" "$COOLIFY_BASE_URL/api/v1/deployments/{deployment_uuid}" | \
python3 -c "
import sys, json
data = json.load(sys.stdin)
logs = json.loads(data['logs']) if isinstance(data['logs'], str) else data['logs']
for log in logs[-20:]:  # Last 20 logs
    if not log.get('hidden', False):
        print(f\"{log.get('type', 'INFO').upper()}: {log.get('output', '')}\")
"
```

2. **Check environment variables:**
```bash
curl -H "$AUTH_HEADER" "$COOLIFY_BASE_URL/api/v1/applications/{app_uuid}/envs"
# Often returns [] indicating missing required env vars
```

**Common Solutions:**
- Add missing environment variables (PORT, API keys, etc.)
- Ensure build pack matches your deployment type

### Issue 2: Nixpacks vs Dockerfile Confusion

**Symptoms:**
- Deployment logs show Nixpacks when you expect Dockerfile
- Custom startup commands ignored
- Health checks not working as expected

**Debugging:**
```bash
# Check current build configuration
curl -H "$AUTH_HEADER" "$COOLIFY_BASE_URL/api/v1/applications/{app_uuid}" | \
python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f'Build pack: {data.get(\"build_pack\")}')
print(f'Dockerfile location: {data.get(\"dockerfile_location\")}')
print(f'Start command: {data.get(\"start_command\")}')
"
```

**Solution:**
```bash
# Force Dockerfile usage
curl -X PATCH -H "$AUTH_HEADER" -H "Content-Type: application/json" \
  -d '{"build_pack": "dockerfile"}' \
  "$COOLIFY_BASE_URL/api/v1/applications/{app_uuid}"
```

### Issue 3: Health Check Failures

**Symptoms:**
- Logs show "Healthcheck status: unhealthy"
- Container starts successfully but gets rolled back
- Health check commands fail

**Debugging Deployment Logs:**
```bash
curl -H "$AUTH_HEADER" "$COOLIFY_BASE_URL/api/v1/deployments/{deployment_uuid}" | \
python3 -c "
import sys, json
data = json.load(sys.stdin)
logs = json.loads(data['logs'])
for log in logs:
    output = log.get('output', '')
    if 'health' in output.lower() or 'unhealthy' in output.lower():
        print(f'HEALTH: {output}')
"
```

**Common Health Check Issues:**
- **Missing commands in container** (`pgrep: not found`, `curl: not found`)
  - Fix: Add required commands to Dockerfile (e.g., `RUN apt-get install -y curl`)
- **Wrong port or endpoint**
  - Fix: Verify HEALTHCHECK in Dockerfile matches actual application port
- **Health check timeout too short**
  - Fix: Increase timeout in Dockerfile HEALTHCHECK directive
- **Start period too short for application warmup**
  - Fix: Increase --start-period in HEALTHCHECK directive

**Real Example - Browser-Use MCP Health Check Fix:**
```dockerfile
# Problem: curl: not found
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000/health || exit 1

# Solution: Install curl in Dockerfile
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
```

### Issue 4: Runtime Logs When Application Crashes

**Problem:** Application is not running, can't get runtime logs directly.

**Solution:** Get deployment logs that show the actual startup:
```bash
curl -H "$AUTH_HEADER" "$COOLIFY_BASE_URL/api/v1/deployments/{deployment_uuid}" | \
python3 -c "
import sys, json
data = json.load(sys.stdin)
logs = json.loads(data['logs'])
# Look for application startup logs between 'Container Started' and health check failure
startup_phase = False
for log in logs:
    output = log.get('output', '')
    if 'Container' in output and 'Started' in output:
        startup_phase = True
    elif 'unhealthy' in output.lower():
        startup_phase = False
    
    if startup_phase and ('INFO:' in output or 'ERROR:' in output or 'Exception' in output):
        print(f'STARTUP: {output}')
"
```

## Real-World Success Story: MCP Server Debugging

### Initial Problem (RESOLVED!)
- Python MCP server: `exited:unhealthy` → **Fixed ✅**
- TypeScript MCP server: `running:unhealthy` → **Fixed ✅**

### Investigation Process That Led to Success

1. **Check application status:**
```bash
curl -H "$AUTH_HEADER" "$COOLIFY_BASE_URL/api/v1/applications" | \
python3 -c "
import sys, json
data = json.load(sys.stdin)
for app in data:
    if 'mcpservers' in app['name']:
        print(f\"{app['name']}: {app['status']}\")
"
```

2. **Found and fixed missing environment variables:**
```bash
curl -H "$AUTH_HEADER" "$COOLIFY_BASE_URL/api/v1/applications/{app_uuid}/envs"
# Initial result: []
# Added all required environment variables via API
```

3. **Identified MCP protocol issues:**
   - Python server: Missing authentication middleware
   - TypeScript server: Complex session management preventing basic MCP operations
   - Route handling problems (redirects not handled)

4. **Applied comprehensive fixes:**
   - ✅ **Python server**: Added Bearer token authentication middleware
   - ✅ **TypeScript server**: Simplified MCP endpoint, removed session complexity
   - ✅ **Route handling**: Added support for both `/mcp` and `/mcp/` endpoints
   - ✅ **Error handling**: Enhanced logging and error messages
   - ✅ **Deployment process**: Fixed git commit/push workflow for Coolify

5. **Verified full MCP protocol compliance:**
   - ✅ `initialize` method working
   - ✅ `tools/list` method working  
   - ✅ `tools/call` method working
   - ✅ Authentication working correctly

### Final Result - SUCCESS! 🎉
- **Python server**: `running:healthy` ✅ (12 tools available including Coolify API)
- **TypeScript server**: `running:healthy` ✅ (3 tools available with simplified protocol)

**Live URLs Working:**
- Python: `http://zs8sk0cgs4s8gsgwswsg88ko.135.181.149.150.sslip.io/mcp`
- TypeScript: `http://k8wco488444c8gw0sscs04k8.135.181.149.150.sslip.io/mcp`

**Testing Commands That Now Work:**
```bash
# Initialize - SUCCESS ✅
curl -X POST -H "Content-Type: application/json" -H "Authorization: Bearer ${MCP_API_KEY}" \
  -d '{"jsonrpc": "2.0", "method": "initialize", "id": 1, "params": {}}' \
  http://zs8sk0cgs4s8gsgwswsg88ko.135.181.149.150.sslip.io/mcp

# Tools list - SUCCESS ✅  
curl -X POST -H "Content-Type: application/json" -H "Authorization: Bearer ${MCP_API_KEY}" \
  -d '{"jsonrpc": "2.0", "method": "tools/list", "id": 2, "params": {}}' \
  http://zs8sk0cgs4s8gsgwswsg88ko.135.181.149.150.sslip.io/mcp
```

### Key Lessons Learned

1. **Git workflow is critical**: Coolify deploys from git repository, changes must be committed/pushed
2. **MCP protocol simplicity**: Complex session management can break basic MCP operations  
3. **Authentication security**: Both servers use cryptographically secure Bearer tokens from environment variables
4. **Route handling**: Handle both `/mcp` and `/mcp/` to avoid redirect issues
5. **Deployment logs are essential**: Use deployment logs to debug actual application startup
6. **API-first debugging**: Coolify API provides more detailed diagnostics than web interface

## API Debugging Script Template

```bash
#!/bin/bash
# Coolify API Debugging Script

COOLIFY_BASE_URL="http://your-coolify-server:8000"
COOLIFY_API_TOKEN="your-token"
APP_UUID="your-app-uuid"

echo "=== Application Status ==="
curl -s -H "Authorization: Bearer $COOLIFY_API_TOKEN" \
  "$COOLIFY_BASE_URL/api/v1/applications/$APP_UUID" | \
  python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f'Status: {data.get(\"status\")}')
print(f'Build Pack: {data.get(\"build_pack\")}') 
print(f'Last Online: {data.get(\"last_online_at\")}')
"

echo -e "\n=== Environment Variables ==="
curl -s -H "Authorization: Bearer $COOLIFY_API_TOKEN" \
  "$COOLIFY_BASE_URL/api/v1/applications/$APP_UUID/envs" | \
  python3 -c "
import sys, json
data = json.load(sys.stdin)
if data:
    for env in data:
        print(f'{env[\"key\"]}: {env[\"value\"]}')
else:
    print('No environment variables set')
"

echo -e "\n=== Recent Deployment Logs ==="
# Get latest deployment
DEPLOYMENT_UUID=$(curl -s -H "Authorization: Bearer $COOLIFY_API_TOKEN" \
  "$COOLIFY_BASE_URL/api/v1/applications/$APP_UUID" | \
  python3 -c "import sys, json; data = json.load(sys.stdin); print('latest-deployment-uuid')")

if [ "$DEPLOYMENT_UUID" != "null" ]; then
    curl -s -H "Authorization: Bearer $COOLIFY_API_TOKEN" \
      "$COOLIFY_BASE_URL/api/v1/deployments/$DEPLOYMENT_UUID" | \
      python3 -c "
import sys, json
data = json.load(sys.stdin)
if 'logs' in data:
    logs = json.loads(data['logs']) if isinstance(data['logs'], str) else data['logs']
    for log in logs[-10:]:
        if not log.get('hidden', False):
            print(f'{log.get(\"type\", \"INFO\").upper()}: {log.get(\"output\", \"\")}')
"
fi
```

## Key Takeaways

1. **Coolify API provides detailed diagnostics** unavailable in the web interface
2. **Deployment logs contain actual application startup output** - crucial for debugging
3. **Build pack selection critically affects deployment behavior** - always verify
4. **Environment variables are often the root cause** of deployment failures
5. **Health check failures don't mean the application isn't working** - check the actual startup logs
6. **Container rollbacks hide successful startups** - look at deployment logs to see if app actually started

## Useful API Endpoints Reference

```
GET /api/v1/applications/{uuid}           # Detailed application info
GET /api/v1/applications                  # List all applications
GET/POST /api/v1/applications/{uuid}/envs # Environment variables
GET /api/v1/deployments/{uuid}            # Deployment details and logs
POST /api/v1/deploy                       # Trigger deployment
PATCH /api/v1/applications/{uuid}         # Update application config
POST /api/v1/applications/{uuid}/restart  # Restart application
```

This systematic approach using the Coolify API enables precise diagnosis and resolution of complex deployment issues that would be very difficult to debug through the web interface alone.

## Recent Fixes and Updates

### July 29, 2025: Fixed Deployment Logs Access Issue

**Problem Identified:**
- MCP Coolify tools `coolify-get-recent-deployments` was failing to find deployment records
- Tool was using incorrect API endpoint `/applications/{uuid}` and expecting embedded deployment data
- This prevented access to deployment logs for failed deployments

**Root Cause:**
- The function was calling `GET /applications/{uuid}` and looking for `deployments` field in the response
- According to Coolify API documentation, deployments should be retrieved from dedicated endpoint
- Embedded deployment data in application response was empty or non-existent

**Solution Implemented:**
- Updated `get_recent_deployments()` function in `/python/tools/coolify_tools.py`
- Changed from: `GET /applications/{uuid}` → `GET /deployments/applications/{uuid}`
- Added proper response format handling for both dict and list responses
- Updated `deployment_metrics()` function with same fix
- Enhanced UUID field extraction to handle different field names (`uuid`, `id`, `deployment_uuid`)

**Verification:**
- Successfully retrieved deployment record for failed deployment `skgo080ggw00gso4w8wc4ss4`
- Deployment UUID `yg00gcc488ocsww4c4o8wc4ss4` was correctly identified
- Full deployment logs now accessible showing exact failure: missing npm package `@radix-ui/react-button@^1.0.4`

**Impact:**
- MCP Coolify tools now properly retrieve deployment logs for both successful and failed deployments
- Enables effective debugging of deployment failures that were previously invisible
- Resolves the core issue where deployment logs appeared to be missing from the API

This fix ensures that the MCP Coolify tools work as intended for deployment troubleshooting and monitoring.

### July 30, 2025: Comprehensive API Endpoint Fixes

**Problems Identified:**
1. Environment variable management returning 409 Conflict errors on updates
2. Environment variable deletion returning 404 errors with malformed URLs
3. Remaining deployment endpoint issues
4. Incorrect HTTP methods being used for API operations

**Root Causes:**
1. **Environment Variable Updates**: Using PUT method instead of PATCH as specified in official Coolify API documentation
2. **Environment Variable Deletion**: Using incorrect field name (`id` instead of `uuid`) in DELETE URLs
3. **API Method Mismatch**: Implementation didn't match official Coolify API specification

**Solutions Implemented:**

**Environment Variable API Corrections:**
- **UPDATE Operations**: Changed from `PUT /applications/{uuid}/envs/{env_id}` → `PATCH /applications/{uuid}/envs`
- **DELETE Operations**: Changed from `DELETE /applications/{uuid}/envs/{env_id}` → `DELETE /applications/{uuid}/envs/{env_uuid}`
- **Bulk Operations**: Updated to use PATCH method consistently
- **Request Handler**: Added PATCH method support to HTTP request retry logic

**Official API Compliance:**
- Consulted official Coolify API documentation at https://coolify.io/docs/api-reference/api/
- Verified correct endpoint patterns for all environment variable operations
- Implemented proper request body schemas as specified in documentation

**Verification Results:**
```bash
# All operations now work correctly:
✅ coolify-set-env-variable (CREATE) - Success
✅ coolify-set-env-variable (UPDATE) - Success (no more 409 conflicts)
✅ coolify-delete-env-variable - Success (no more 404 errors)
✅ coolify-bulk-update-env - Success (all variables processed)
✅ coolify-get-recent-deployments - Success (no more 404 errors)
```

**Testing Results:**
- Created TEST_VAR successfully
- Updated TEST_VAR to new value successfully  
- Deleted TEST_VAR successfully
- Bulk created 3 variables (TEST_BULK_1, TEST_BULK_2, TEST_BULK_3) successfully
- Retrieved recent deployments successfully

**Impact:**
- All reported MCP Coolify tool issues are now resolved
- Environment variable management is fully functional
- Deployment monitoring and logs access working correctly
- Tools now fully comply with official Coolify API specification
- Enables complete CI/CD automation and environment management through MCP tools