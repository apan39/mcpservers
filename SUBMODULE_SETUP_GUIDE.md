# Git Submodule Integration Guide

## Setting up shared-docs in your Coolify projects

This guide shows how to integrate the `apan39/shared-docs` repository as a git submodule in your Coolify applications.

## Quick Setup Commands

### 1. Add Submodule to Project

```bash
# Navigate to your project root
cd /path/to/your/project

# Add shared-docs as submodule in 'docs' directory
git submodule add https://github.com/apan39/shared-docs.git docs

# Commit the submodule addition
git add .gitmodules docs
git commit -m "Add shared-docs as git submodule"

# Push to remote
git push origin main
```

### 2. Update claude.md to Reference Shared Docs

Add these references to your project's `claude.md` file:

```markdown
# Project-Specific Documentation

<!-- Include shared ecosystem context -->
For complete ecosystem documentation, see [shared documentation](docs/README.md):

- **[Shared Context](docs/SHARED_CONTEXT.md)** - Architecture overview and application relationships
- **[API Endpoints](docs/API_ENDPOINTS.md)** - Complete API documentation for all services
- **[Deployment Guide](docs/DEPLOYMENT_GUIDE.md)** - Coolify deployment procedures and troubleshooting
- **[Configuration Patterns](docs/COOLIFY_CONFIG.md)** - Standard configuration templates

## Application-Specific Context

[Your project-specific documentation continues here...]
```

### 3. Team Setup (Cloning Projects with Submodules)

When team members clone a project with submodules:

```bash
# Option 1: Clone with submodules
git clone --recurse-submodules https://github.com/apan39/your-project.git

# Option 2: Initialize submodules after cloning
git clone https://github.com/apan39/your-project.git
cd your-project
git submodule update --init --recursive
```

## Updating Shared Documentation

### When shared-docs is updated:

```bash
# Update submodule to latest version
git submodule update --remote docs

# Commit the update
git add docs
git commit -m "Update shared documentation"
git push origin main
```

### Automatic updates with git hooks:

Create `.git/hooks/post-merge` (make executable):

```bash
#!/bin/bash
git submodule update --init --recursive
```

## Project-Specific Implementation

### For ProjectAdminCMS (apan39/projectadmincms)

```bash
cd projectadmincms
git submodule add https://github.com/apan39/shared-docs.git docs
```

Update `claude.md`:
```markdown
# ProjectAdminCMS - PayloadCMS Admin Interface

<!-- Shared Documentation -->
📚 **[Complete Ecosystem Documentation](docs/README.md)**

## Project Overview
PayloadCMS-based administration interface for the apan39 ecosystem.

## Configuration
- **UUID**: `akg0w8kc0kgsc0kc0k4wk0cc`
- **URL**: http://akg0w8kc0kgsc0kc0k4wk0cc.135.181.149.150.sslip.io
- **Technology**: PayloadCMS + Node.js
- **Database**: SQLite (`./payloadcms.db`)

## Local Development
\```bash
npm install
npm run dev
\```

<!-- Reference shared deployment guide -->
For deployment procedures, see [Deployment Guide](docs/DEPLOYMENT_GUIDE.md#projectadmincms-payloadcms).
```

### For MrMechanic (apan39/mrmechanic)

```bash
cd mrmechanic
git submodule add https://github.com/apan39/shared-docs.git docs
```

Update `claude.md`:
```markdown
# MrMechanic - AI Assistant Service

<!-- Shared Documentation -->
📚 **[Complete Ecosystem Documentation](docs/README.md)**

## Project Overview
AI-powered assistant service with PayloadCMS backend and OpenAI integration.

## Configuration
- **UUID**: `k4w4wgokwk8000owwgc408ow`
- **URL**: http://k4w4wgokwk8000owwgc408ow.135.181.149.150.sslip.io
- **Technology**: PayloadCMS + OpenAI API
- **AI Features**: Chat assistance, automation

## Environment Variables
\```bash
PAYLOAD_SECRET=your-secret
OPENAI_API_KEY=your-openai-key
\```

<!-- Reference shared API documentation -->
For API endpoints, see [API Documentation](docs/API_ENDPOINTS.md#mrmechanic-ai-assistant).
```

### For GeneralVectorEmbed (apan39/generalvectorembed)

```bash
cd generalvectorembed
git submodule add https://github.com/apan39/shared-docs.git docs
```

Update `claude.md`:
```markdown
# GeneralVectorEmbed - Vector Database Service

<!-- Shared Documentation -->
📚 **[Complete Ecosystem Documentation](docs/README.md)**

## Project Overview
Next.js application with vector search capabilities using Qdrant, MongoDB, and Redis.

## Configuration
- **UUID**: `skgo080ggw00gso4w8wc4ss4`
- **URL**: http://skgo080ggw00gso4w8wc4ss4.135.181.149.150.sslip.io
- **Technology**: Next.js + NextAuth + Qdrant + MongoDB + Redis

## Services
- **Vector DB**: Qdrant
- **Primary DB**: MongoDB
- **Cache**: Redis
- **Auth**: NextAuth.js

<!-- Reference shared configuration -->
For configuration patterns, see [Configuration Guide](docs/COOLIFY_CONFIG.md#next-js-with-external-services-template).
```

### For Flowise (apan39/flowise)

```bash
cd flowise
git submodule add https://github.com/apan39/shared-docs.git docs
```

Update `claude.md`:
```markdown
# Flowise Project - AI Workflow Builder

<!-- Shared Documentation -->
📚 **[Complete Ecosystem Documentation](docs/README.md)**

## Project Overview
**Flowise** is a drag & drop UI to build customized LLM flow using LangChain, written in Node.js. This is a forked version maintained by \`apan39\` with custom configurations for deployment on Coolify.

## Configuration
- **UUID**: `w0cwck80owcgkw4s4kkos4ko`
- **URL**: http://w0cwck80owcgkw4s4kkos4ko.135.181.149.150.sslip.io
- **Technology**: Express.js + React + SQLite

<!-- Reference shared deployment guide -->
For detailed deployment procedures, see [Deployment Guide](docs/DEPLOYMENT_GUIDE.md#flowise-ai-workflow-builder).

[... rest of existing flowise documentation ...]
```

## Benefits of This Approach

### ✅ Centralized Documentation
- Single source of truth for ecosystem information
- Consistent documentation across all projects
- Easy to maintain and update

### ✅ Version Control
- Track documentation changes across projects
- Each project can pin to specific documentation versions
- Clear history of documentation updates

### ✅ Automatic Updates
- Update documentation once, propagate to all projects
- Git submodules provide controlled updates
- Team members always have latest documentation

### ✅ Development Workflow
- Documentation stays in sync with code
- Easy to reference during development
- Claude can access all shared context

## Troubleshooting

### Submodule not updating
```bash
# Force update submodule
git submodule update --remote --force docs
```

### Submodule showing as modified
```bash
# Reset submodule to latest commit
cd docs
git checkout main
git pull origin main
cd ..
git add docs
git commit -m "Update shared documentation"
```

### Removing submodule (if needed)
```bash
# Remove submodule
git submodule deinit docs
git rm docs
rm -rf .git/modules/docs
git commit -m "Remove shared-docs submodule"
```

## Next Steps

1. **Implement in each project** following the project-specific guides above
2. **Update Coolify deployments** to ensure submodules are pulled during builds
3. **Train team** on submodule workflow
4. **Set up automation** for documentation updates

## Coolify Deployment Notes

### Ensure submodules are pulled during deployment:

#### For nixpacks (automatic):
Most nixpacks configurations automatically handle submodules during git clone.

#### For custom Dockerfile:
```dockerfile
# In your Dockerfile
RUN git submodule update --init --recursive
```

#### For custom build commands:
```bash
# Add to your build process
git submodule update --init --recursive
```