# Project Context for Claude

## Shared Ecosystem Documentation
📚 **[Complete Ecosystem Documentation](docs/README.md)** - Shared documentation for all apan39 Coolify applications

- **[Shared Context](docs/SHARED_CONTEXT.md)** - Architecture overview and application relationships
- **[API Endpoints](docs/API_ENDPOINTS.md)** - Complete API documentation for all services  
- **[Deployment Guide](docs/DEPLOYMENT_GUIDE.md)** - Coolify deployment procedures and troubleshooting
- **[Configuration Patterns](docs/COOLIFY_CONFIG.md)** - Standard configuration templates

## Project-Specific Documentation Files
- README.md - Main project overview
- MCP_SETUP.md - MCP server setup instructions  
- DEPLOYMENT.md - Deployment guidelines
- COOLIFY_API_DEBUGGING.md - API debugging guide

## Project Structure
This is an MCP (Model Context Protocol) servers project with deployment automation, part of the apan39 Coolify ecosystem.

## Local/Remote Server Synchronization Protocol - CRITICAL ⚠️

**MANDATORY: Local and remote servers MUST stay in sync feature-wise**

### Feature Parity Requirements:
- ✅ **Code Changes**: All new features must be deployed to both local and remote
- ✅ **Tool Count**: Local and remote servers should have identical tool counts
- ✅ **SSE Capabilities**: Both environments must support the same SSE endpoints
- ✅ **API Compatibility**: Same tool names, parameters, and response formats
- ✅ **Environment Variables**: Consistent configuration across environments

### Synchronization Workflow:
```bash
# 1. Develop and test locally first
./start-local-sse.sh
# Test new features on local servers

# 2. Commit and push changes to git
git add .
git commit -m "Add new feature X"
git push origin main

# 3. Deploy to remote servers immediately using SSE monitoring
coolify-deploy-with-sse-monitoring --app_uuid zs8sk0cgs4s8gsgwswsg88ko --force true

# 4. Verify feature parity
# Compare tool counts and capabilities between local and remote
```

### Verification Commands:
```bash
# Check local server tool count
curl http://localhost:3009/mcp -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"list-tool-categories","arguments":{}}}'

# Check remote server tool count  
curl http://remote-server/mcp -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"list-tool-categories","arguments":{}}}'
```

**⚠️ CRITICAL RULES:**
- Never leave local features undeployed for more than 1 hour
- Always test on local before deploying to remote
- Document any temporary feature differences in this file
- Verify tool counts match after each deployment

## ⚠️ DEPLOYMENT TOOL PRIORITY MATRIX - CRITICAL FOR AI

**🚨 MANDATORY: Always use this tool selection hierarchy to avoid losing SSE monitoring capabilities**

### **✅ PRIMARY DEPLOYMENT TOOLS (Use These First):**

1. **`coolify-deploy-with-sse-monitoring`** 
   - **Usage:** Single application deployments with real-time monitoring
   - **Features:** ✅ SSE monitoring, ✅ Real-time status, ✅ Automatic completion detection
   - **When:** Default choice for ALL single app deployments

2. **`coolify-bulk-deploy`**
   - **Usage:** Multiple applications simultaneously
   - **Features:** ❌ No SSE monitoring, ✅ Batch operations
   - **When:** Only for deploying multiple apps at once

### **⚠️ LEGACY/FALLBACK TOOLS (Avoid When Possible):**

3. **`coolify-deploy-application`** 
   - **Usage:** Basic deployment without monitoring
   - **Features:** ❌ No SSE monitoring, ❌ No real-time status
   - **When:** ONLY when SSE tools are unavailable or broken

### **🎯 AI Tool Selection Rules:**

- **✅ DO:** Always try `coolify-deploy-with-sse-monitoring` first for single deployments
- **✅ DO:** Use `coolify-bulk-deploy` only for multiple app deployments
- **❌ DON'T:** Use `coolify-deploy-application` unless explicitly told it's a fallback
- **❌ DON'T:** Choose randomly between deployment tools - follow this hierarchy

### **🚀 Correct Usage Examples:**

```bash
# ✅ CORRECT: Single app deployment with SSE monitoring
coolify-deploy-with-sse-monitoring --app_uuid zs8sk0cgs4s8gsgwswsg88ko --force true

# ✅ CORRECT: Multiple apps with bulk deployment
coolify-bulk-deploy --app_uuids "uuid1,uuid2,uuid3" --parallel false

# ❌ WRONG: Using basic deploy when SSE is available
coolify-deploy-application --app_uuid zs8sk0cgs4s8gsgwswsg88ko --force true
```

## Coolify Deployment Protocol

**MANDATORY: Read this before any Coolify operations**

### 1. Pre-deployment Checks
- Read COOLIFY_API_DEBUGGING.md for comprehensive debugging patterns
- Verify environment variables are set correctly in .env file
- Use MCP Coolify tools to check server status: `coolify-get-version`
- Confirm target application UUID and current status

### 2. Deployment Process - USE SSE MONITORING TOOLS ⚡

**🚀 PREFERRED METHOD: Use SSE Deployment Monitoring Tools**
```bash
# 1. Start deployment with real-time monitoring (RECOMMENDED)
coolify-deploy-with-sse-monitoring --app_uuid APPLICATION_UUID --force true

# 2. Monitor real-time progress
coolify-get-sse-deployment-status --deployment_uuid DEPLOYMENT_UUID

# 3. List all active deployments being monitored
coolify-list-active-sse-deployments
```

**🔧 FALLBACK METHOD: Traditional API Deployment**
```bash
# Only use if SSE tools are unavailable
source .env
curl -X POST -H "Authorization: Bearer ${COOLIFY_API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"uuid": "APPLICATION_UUID"}' \
  "http://135.181.149.150:8000/api/v1/deploy"
```

**⚡ Benefits of SSE Method:**
- ✅ **Real-time Progress** - Live updates every 5 seconds
- ✅ **No Command Overlap** - Know exactly when deployment completes
- ✅ **Automatic Completion Detection** - Stops monitoring when done
- ✅ **Background Monitoring** - Non-blocking, continues in background
- ✅ **Rich Status Information** - Detailed deployment progress

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
- Python MCP (UUID: zs8sk0cgs4s8gsgwswsg88ko): `running:healthy` - 15+ tools (complete Coolify management suite)
- TypeScript MCP (UUID: k8wco488444c8gw0sscs04k8): `running:healthy` - 12+ tools (GitHub, PayloadCMS, Flowise, Context7, Playwright)
- Browser-use MCP (UUID: w8wcwg48ok4go8g8swgwkgk8): `running:healthy` - 6+ browser automation tools

**Last Update:** August 5, 2025 - Comprehensive MCP Inspector integration completed

### 5.1. Local Development Servers ✅
**All local MCP servers fully operational:**
- ✅ **Python Local SSE** (`http://localhost:3009/sse`) - Complete Coolify management suite (61 tools including SSE deployment monitoring)
- ✅ **TypeScript Local SSE** (`http://localhost:3010/sse`) - Multi-tool integration server  
- ✅ **Browser-use Local SSE** (`http://localhost:3011/sse`) - Browser automation tools

**SSE Implementation Status:**
- ✅ **Official MCP SDK Patterns** - Using proper `SSEServerTransport` 
- ✅ **Authentication Fixed** - Browser-use server now uses consistent `MCP_API_KEY`
- ✅ **TypeScript SSE Complete** - Proper session management, DNS protection, no auth required
- ✅ **All Start Scripts Working** - `./start-local-sse.sh` fully operational

### 5.2. Local Server Startup Rules ⚠️ **IMPORTANT**

**MANDATORY: Always use the proper startup/shutdown scripts when testing or developing:**

```bash
# ✅ CORRECT: Use the official startup script
./start-local-sse.sh

# ✅ CORRECT: Use the official shutdown script  
./stop-local-sse.sh

# ❌ WRONG: Never start servers individually
python3 python/mcp_server.py  # Don't do this
node typescript/dist/server.js  # Don't do this

# ❌ WRONG: Never kill servers manually
kill PID  # Don't do this
pkill -f "server"  # Don't do this
```

**Why use start-local-sse.sh:**
- ✅ **Proper Environment Variables** - Loads .env file correctly
- ✅ **Correct Host Binding** - Uses 127.0.0.1 for local development
- ✅ **Port Conflict Detection** - Checks for port availability first
- ✅ **Process Management** - Handles background processes properly
- ✅ **Coordinated Startup** - Starts all servers in correct order
- ✅ **Clean Shutdown** - Provides proper cleanup with Ctrl+C

**Server Management Commands:**
```bash
./start-local-sse.sh    # Start all local servers
./stop-local-sse.sh     # Stop all local servers
# Press Ctrl+C in terminal running start-local-sse.sh to stop
```

**Local Server URLs (after using start-local-sse.sh):**
- Python: `http://localhost:3009/mcp` (HTTP) + `http://localhost:3009/sse` (SSE)
- TypeScript: `http://localhost:3010/mcp-advanced` (HTTP) + `http://localhost:3010/sse` (SSE)  
- Browser-use: `http://localhost:3011/sse` (SSE only)

### 5.2. MCP Inspector Integration ✅
**Comprehensive debugging and validation platform:**
- ✅ **Universal Validator** - `scripts/mcp-universal-validator-simple.sh`
- ✅ **Automated Tool Testing** - `scripts/mcp-tool-tester.sh`
- ✅ **Health Monitoring Dashboard** - `scripts/mcp-health-monitor.sh`
- ✅ **Master Controller** - `scripts/mcp-master-controller.sh`

**Current Ecosystem Status (Live Monitoring):**
- 🟢 **4/9 Servers Healthy** - Remote Python (57 tools), Remote Browser-use (6 tools), Python Local HTTP (57 tools), Browser-use Local HTTP (30 tools)
- 🔴 **5/9 Servers Down** - Remote TypeScript, Local SSE servers (Python, TypeScript, Browser-use), TypeScript Local HTTP
- 📊 **Total Available Tools: 150+** across all healthy servers
- ⚡ **Response Times: 2-30ms** for healthy servers

### 6. MCP Coolify Tools Status - FULLY OPERATIONAL ✅

**Environment Variable Management (FIXED):**
- ✅ `coolify-set-env-variable` - Create/update variables (409 conflicts resolved)  
- ✅ `coolify-delete-env-variable` - Delete variables (404 errors resolved)
- ✅ `coolify-bulk-update-env` - Bulk operations (all issues resolved)

**Deployment Management (FIXED):**
- ✅ `coolify-get-recent-deployments` - Access deployment history (404 errors resolved)
- ✅ `coolify-get-deployment-logs` - Full log access working
- ✅ `coolify-deploy-application` - Trigger deployments working

**🆕 SSE Real-time Deployment Monitoring (NEW - August 5, 2025):**
- ✅ `coolify-deploy-with-sse-monitoring` - Start deployment with real-time monitoring
- ✅ `coolify-get-sse-deployment-status` - Get live deployment status updates
- ✅ `coolify-list-active-sse-deployments` - List all monitored deployments
- ✅ `coolify-stop-sse-deployment-monitoring` - Stop monitoring specific deployment
- ✅ **SSE Stream Endpoint:** `/sse/deployment/{deployment_uuid}` - Real-time event stream
- ✅ **Solves Command Overlap Problem:** Provides real-time status, eliminates deployment timing guesswork!

**All Core Operations:**
- ✅ `coolify-list-applications` - Working perfectly
- ✅ `coolify-get-application-info` - Working perfectly  
- ✅ `coolify-restart-application` - Working perfectly
- ✅ All 60+ Coolify management tools now fully operational (including 4 new SSE tools)

**API Compliance:** All tools now conform to official Coolify API specification

### 6.1 SSE Deployment Monitoring Usage - PRODUCTION READY ✅

**🚀 VERIFIED: All 4 SSE Tools Tested and Operational on Remote Server**

#### **Step-by-Step Deployment with SSE Monitoring:**

**1. Check Active Monitoring:**
```bash
# Always check what's currently being monitored
coolify-list-active-sse-deployments
# Expected: "📊 **No Active SSE Deployments**" (if nothing running)
```

**2. Start Deployment with Real-time Monitoring:**
```bash
# PRIMARY METHOD: Use SSE monitoring for all deployments
coolify-deploy-with-sse-monitoring --app_uuid YOUR_APP_UUID --force true

# FALLBACK: If SSE deploy fails, use regular deploy + monitor manually
coolify-deploy-application --app_uuid YOUR_APP_UUID --force true
# Then get deployment UUID from response and monitor separately
```

**3. Monitor Deployment Progress:**
```bash
# Check specific deployment status (get UUID from step 2)
coolify-get-sse-deployment-status --deployment_uuid DEPLOYMENT_UUID

# List all deployments currently being monitored
coolify-list-active-sse-deployments
```

**4. Stop Monitoring (Optional):**
```bash
# Stop SSE monitoring for a specific deployment
coolify-stop-sse-deployment-monitoring --deployment_uuid DEPLOYMENT_UUID
# Expected: "🛑 **SSE Deployment Monitoring Stopped**"
```

**5. Real-time SSE Stream (Advanced):**
```bash
# Local server SSE endpoint
curl -N -H "Authorization: Bearer YOUR_API_KEY" \
  "http://localhost:3009/sse/deployment/DEPLOYMENT_UUID"

# Remote server SSE endpoint  
curl -N -H "Authorization: Bearer YOUR_API_KEY" \
  "http://zs8sk0cgs4s8gsgwswsg88ko.135.181.149.150.sslip.io/sse/deployment/DEPLOYMENT_UUID"

# Expected response:
# event: connected
# data: {"message": "Connected to deployment DEPLOYMENT_UUID"}
```

#### **Verified Tool Capabilities:**

✅ **coolify-list-active-sse-deployments** (Basic)
- Lists all deployments currently being monitored in real-time
- Returns empty list when no deployments active

✅ **coolify-deploy-with-sse-monitoring** (Advanced) 
- Starts deployment AND begins real-time monitoring
- Handles API errors gracefully (e.g., no changes to deploy)
- Returns deployment UUID for tracking

✅ **coolify-get-sse-deployment-status** (Intermediate)
- Gets current status of a specific deployment
- Validates deployment UUID exists in monitoring system
- Provides detailed error messages for invalid UUIDs

✅ **coolify-stop-sse-deployment-monitoring** (Intermediate)
- Stops real-time monitoring for specific deployment  
- Provides confirmation with deployment details
- Graceful handling of non-existent deployments

#### **When to Use SSE vs Traditional Deployment:**

**✅ USE SSE MONITORING WHEN:**
- Deploying critical applications requiring monitoring
- Need to know exact completion time
- Running multiple deployments simultaneously  
- Building deployment dashboards or automation
- Want to eliminate "deployment still running?" guesswork

**⚠️ USE TRADITIONAL DEPLOYMENT WHEN:**
- SSE tools temporarily unavailable
- Simple one-off deployments  
- Legacy scripts that haven't been updated yet

#### **Example Integration:** 
Complete working example: `python/examples/sse_deployment_client.py`
- Shows full workflow from deployment to completion
- Demonstrates SSE stream consumption
- Includes proper error handling

#### **🚨 KNOWN ISSUES & WORKAROUNDS:**

**Issue:** `coolify-deploy-with-sse-monitoring` returns "No deployment UUID returned from API"
- **Root Cause:** SSE deployment tool may not properly handle the deployment API response
- **Workaround:** Use `coolify-deploy-application` to start deployment, then manually monitor with SSE tools
- **Status:** Investigated 2025-08-06 - Regular deployment tools work fine, SSE variant needs debugging

**Correct Workaround Pattern:**
```bash
# Step 1: Start deployment with regular tool
coolify-deploy-application --app_uuid YOUR_APP_UUID --force true

# Step 2: Get deployment UUID from response  
# Expected output: "Deployment UUID: abc123def456"

# Step 3: Monitor with SSE tools (if needed)
coolify-get-deployment-logs --deployment_uuid abc123def456
```

### 7. Communication Guidelines - SSE First Approach 🚀

**PRIMARY DEPLOYMENT METHOD: Always use SSE monitoring tools**
- ✅ **Use `coolify-deploy-with-sse-monitoring`** as default deployment method
- ✅ **Check `coolify-list-active-sse-deployments`** before starting new deployments  
- ✅ **Monitor with `coolify-get-sse-deployment-status`** instead of guessing completion
- ✅ **Use SSE streaming endpoint** for real-time dashboard integration
- ⚠️ **Fallback to traditional tools** only when SSE unavailable

**VERIFICATION PROTOCOL:**
- **Never assume deployment success** without explicit status verification
- **Always check logs** when deployments fail using `coolify-get-deployment-logs`
- **Use systematic debugging** approach from COOLIFY_API_DEBUGGING.md
- **Verify local/remote feature parity** after each deployment
- **Update status** in this document after major changes

**LOCAL/REMOTE SYNCHRONIZATION:**
- **Test locally first** using `./start-local-sse.sh`
- **Deploy immediately** to maintain feature parity  
- **Verify tool counts match** between local and remote servers
- **Document any temporary differences** in this file

### 8. Code Development Protocol
**MANDATORY: Follow this sequence when implementing new features**

1. **Code Implementation**
   - Implement new features locally
   - Test TypeScript compilation with `npm run build`
   - Verify syntax and imports are correct

2. **Git Operations (CRITICAL)**
   - **ALWAYS commit code changes to git first**
   - **ALWAYS push commits to remote repository**
   - **NEVER attempt to test deployed features without committed code**
   - Coolify deploys from the git repository, not local files

3. **Deployment & Testing**
   - Deploy application via Coolify API
   - Wait for deployment to complete successfully
   - Then test new MCP tools on remote server
   - Verify tools are available and functioning

**⚠️ IMPORTANT:** Remote MCP servers pull code from git repository. Local changes that aren't committed and pushed will NOT be deployed.