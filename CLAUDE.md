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
- Python MCP (UUID: zs8sk0cgs4s8gsgwswsg88ko): `running:healthy` - 15+ tools (complete Coolify management suite)
- TypeScript MCP (UUID: k8wco488444c8gw0sscs04k8): `running:healthy` - 12+ tools (GitHub, PayloadCMS, Flowise, Context7, Playwright)
- Browser-use MCP (UUID: w8wcwg48ok4go8g8swgwkgk8): `running:healthy` - 6+ browser automation tools

**Last Update:** August 5, 2025 - Comprehensive MCP Inspector integration completed

### 5.1. Local Development Servers ✅
**All local MCP servers fully operational:**
- ✅ **Python Local SSE** (`http://localhost:3009/sse`) - Complete Coolify management suite (57 tools)
- ✅ **TypeScript Local SSE** (`http://localhost:3010/sse`) - Multi-tool integration server  
- ✅ **Browser-use Local SSE** (`http://localhost:3011/sse`) - Browser automation tools

**SSE Implementation Status:**
- ✅ **Official MCP SDK Patterns** - Using proper `SSEServerTransport` 
- ✅ **Authentication Fixed** - Browser-use server now uses consistent `MCP_API_KEY`
- ✅ **TypeScript SSE Complete** - Proper session management, DNS protection, no auth required
- ✅ **All Start Scripts Working** - `./start-local-sse.sh` fully operational

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

### 6.1 SSE Deployment Monitoring Usage

**🚀 How to Use Real-time Deployment Monitoring:**

1. **Start Deployment with Monitoring:**
   ```bash
   # Use the new SSE-enabled deployment tool instead of regular deploy
   coolify-deploy-with-sse-monitoring --app_uuid YOUR_APP_UUID --force true
   ```

2. **Monitor Real-time Progress:**
   ```bash
   # Check current status (includes deployment UUID)
   coolify-get-sse-deployment-status --deployment_uuid DEPLOYMENT_UUID
   
   # List all active deployments being monitored
   coolify-list-active-sse-deployments
   ```

3. **Stream Live Updates (Optional):**
   ```bash
   # Connect to SSE stream for real-time events
   curl -N -H "Authorization: Bearer YOUR_API_KEY" \
     "http://localhost:3009/sse/deployment/DEPLOYMENT_UUID"
   ```

4. **Benefits Over Traditional Deployment:**
   - ✅ **No Command Overlap** - Know exactly when deployment finishes
   - ✅ **Real-time Status** - Live progress updates every 5 seconds
   - ✅ **Automatic Completion Detection** - Stops monitoring when done
   - ✅ **Background Monitoring** - Non-blocking, continues in background
   - ✅ **SSE Stream Available** - For real-time dashboard integration

5. **Example Client:** See `python/examples/sse_deployment_client.py` for complete usage example

### 7. Communication Guidelines
- **Use SSE deployment monitoring** to eliminate command overlap issues
- **Never assume deployment success** without explicit verification
- **Always check logs** when deployments fail
- **Use systematic debugging** approach from COOLIFY_API_DEBUGGING.md
- **Update status** in this document after major changes

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