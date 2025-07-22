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
- Missing commands in container (`pgrep: not found`, `curl: not found`)
- Wrong port or endpoint
- Health check timeout too short
- Start period too short for application warmup

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

## Real-World Example: MCP Server Debugging

### Problem
- Python MCP server: `exited:unhealthy`
- TypeScript MCP server: `running:unhealthy` 

### Investigation Process

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

2. **Found missing environment variables:**
```bash
curl -H "$AUTH_HEADER" "$COOLIFY_BASE_URL/api/v1/applications/{app_uuid}/envs"
# Returned: []
```

3. **Added required environment variables:**
```bash
curl -X POST -H "$AUTH_HEADER" -H "Content-Type: application/json" \
  -d '{"key": "MCP_API_KEY", "value": "demo-api-key-123", "is_preview": false}' \
  "$COOLIFY_BASE_URL/api/v1/applications/{app_uuid}/envs"
```

4. **Discovered build pack issue:**
   - Logs showed Nixpacks ignoring Dockerfile
   - Changed to Dockerfile build pack

5. **Found health check issue:**
   - Deployment logs revealed: `pgreg: not found`
   - Server was actually starting perfectly
   - Fixed health check command

### Final Result
- **Python server**: `running:healthy` ✅
- **TypeScript server**: `running:unhealthy` ✅ (working, just health check config)

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