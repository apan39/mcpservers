# Shared Project Context

## Ecosystem Overview

The apan39 Coolify ecosystem consists of interconnected applications that work together to provide a comprehensive AI-powered platform. All applications are deployed on Coolify v4.0.0-beta.420.6 at `135.181.149.150:8000`.

## Application Architecture

### Core Applications

| Application | Purpose | Repository | UUID | Status |
|-------------|---------|------------|------|--------|
| **projectadmincms** | PayloadCMS Admin Interface | `apan39/projectadmincms` | `akg0w8kc0kgsc0kc0k4wk0cc` | running:unhealthy |
| **mrmechanic** | AI Assistant Service | `apan39/mrmechanic` | `k4w4wgokwk8000owwgc408ow` | running:unhealthy |
| **generalvectorembed** | Vector Database Service | `apan39/generalvectorembed` | `skgo080ggw00gso4w8wc4ss4` | running:unhealthy |
| **flowise** | AI Workflow Builder | `apan39/flowise` | `w0cwck80owcgkw4s4kkos4ko` | running:unhealthy |

### Supporting Infrastructure

| Service | Purpose | UUID | Status |
|---------|---------|------|--------|
| **mcpservers-python** | Python MCP Server | `zs8sk0cgs4s8gsgwswsg88ko` | running:healthy |
| **mcpservers-typescript** | TypeScript MCP Server | `zw0o84skskgc8kgooswgo8k4` | running:healthy |
| **browser-use-mcp** | Browser Automation MCP | `w8wcwg48ok4go8g8swgwkgk8` | running:healthy |

## Technology Stack

### Common Technologies
- **Runtime**: Node.js 20.x
- **Package Manager**: pnpm >=9
- **Build System**: nixpacks (auto-detection)
- **Deployment**: Coolify v4.0.0-beta.420.6
- **Environment**: Production

### Application-Specific Stacks

#### ProjectAdminCMS
- **Framework**: PayloadCMS
- **Database**: SQLite (`./payloadcms.db`)
- **Port**: 3000

#### MrMechanic  
- **Framework**: PayloadCMS + AI Integration
- **AI Provider**: OpenAI API
- **Database**: SQLite
- **Port**: 3000

#### GeneralVectorEmbed
- **Framework**: Next.js + NextAuth
- **Database**: MongoDB
- **Vector DB**: Qdrant
- **Cache**: Redis
- **AI Provider**: OpenAI API
- **Port**: 3000

#### Flowise
- **Framework**: Express.js + React
- **Database**: SQLite (`/app/.flowise`)
- **Authentication**: Username/Password
- **Port**: 3000

## Service Communication

### Inter-Service APIs
Applications communicate via HTTP APIs using their Coolify-generated URLs:

- **ProjectAdminCMS**: `http://akg0w8kc0kgsc0kc0k4wk0cc.135.181.149.150.sslip.io`
- **MrMechanic**: `http://k4w4wgokwk8000owwgc408ow.135.181.149.150.sslip.io`
- **GeneralVectorEmbed**: `http://skgo080ggw00gso4w8wc4ss4.135.181.149.150.sslip.io`
- **Flowise**: `http://w0cwck80owcgkw4s4kkos4ko.135.181.149.150.sslip.io`

### MCP Integration
All applications can potentially integrate with the MCP servers for extended functionality:

- **Python MCP**: `http://zs8sk0cgs4s8gsgwswsg88ko.135.181.149.150.sslip.io`
- **TypeScript MCP**: `http://zw0o84skskgc8kgooswgo8k4.135.181.149.150.sslip.io`
- **Browser MCP**: `http://w8wcwg48ok4go8g8swgwkgk8.135.181.149.150.sslip.io`

## Security & Environment

### Common Environment Variables
- `NODE_ENV=production`
- `PORT=3000` (standard for all apps)
- Various `*_SECRET` variables (project-specific)

### Authentication Patterns
- **PayloadCMS Apps**: Built-in admin authentication
- **Flowise**: Username/password (`admin`/password)
- **GeneralVectorEmbed**: NextAuth integration
- **MCP Servers**: API key authentication

## Development Workflow

### Documentation Sync
**🚨 IMPORTANT**: At the start of every development session, run:
```bash
git docs-pull
```
This ensures you have the latest shared documentation across all projects.

**📤 AUTOMATIC PUSH**: When any files in the `docs/` directory are modified, **immediately run these commands**:
```bash
git add docs/
git commit -m "Update shared documentation"  
git subtree push --prefix=docs https://github.com/apan39/shared-docs.git main
```
This commits changes locally then pushes to the shared documentation repository for all other projects to use.

**⚠️ FOR CLAUDE**: After editing any file in `docs/`, you MUST automatically run all three commands above without being asked.

### Common Build Process
1. **nixpacks** auto-detection
2. **pnpm install** dependencies
3. **pnpm build** (if build script exists)
4. **pnpm start** production server

### Health Check Status
Currently all core applications show `running:unhealthy` status, which indicates they are functional but health checks may need configuration. This is a known issue that doesn't affect functionality.

## Monitoring & Maintenance

### Deployment Status Monitoring
Use Coolify MCP tools to monitor application status:
```bash
coolify-list-applications
coolify-get-application-info --app_uuid=<uuid>
coolify-get-application-logs --app_uuid=<uuid>
```

### Common Troubleshooting
1. Check application logs via Coolify
2. Verify environment variables are set
3. Ensure database connections are working
4. Test inter-service API connectivity

## Project Goals

This ecosystem supports:
- **Content Management** (ProjectAdminCMS)
- **AI-Powered Assistance** (MrMechanic)
- **Vector Search & Embeddings** (GeneralVectorEmbed)
- **AI Workflow Automation** (Flowise)
- **Extended Tool Integration** (MCP Servers)

Each application is designed to work independently while providing APIs for integration with the broader ecosystem.# Test change

# Test change for alias
# Testing semicolon alias
