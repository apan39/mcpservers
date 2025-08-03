# Multi-Site Admin CMS - Claude Context

## ⚠️ IMPORTANT: Documentation Maintenance

**ALWAYS keep documentation current with implementation status:**

### 📝 Documentation Update Requirements
- **After every major feature implementation** → Update both CLAUDE.md and README.md
- **When collections are added/modified** → Update collections sections and roadmap
- **When access control changes** → Update security documentation
- **When architecture evolves** → Update technical specifications
- **When dependencies change** → Update tech stack and installation instructions

### 🔄 Update Process
1. **CLAUDE.md**: Update implementation status, move features from "Missing" to "Completed"
2. **README.md**: Update feature highlights, roadmap status, quick start if needed
3. **Commit both files together** with descriptive commit message
4. **Push to GitHub** to keep remote documentation current

### 📋 Regular Documentation Checks
- **Completed Features**: Move from 🚧 Missing to ✅ Completed sections
- **File Structure**: Update directory listings when new folders/files added
- **Commands**: Add new npm scripts, update environment variables
- **Dependencies**: Update version numbers and new packages
- **Roadmap**: Adjust priorities and add new planned features

**This ensures the documentation always reflects the true state of the application.**

---

## 📚 Shared Ecosystem Documentation

**[Complete Ecosystem Documentation](docs/README.md)** - Shared documentation for all apan39 Coolify applications

This project is part of a larger ecosystem. For comprehensive information about:
- **Application architecture** and inter-service communication → `docs/SHARED_CONTEXT.md`
- **API endpoints** across all services → `docs/API_ENDPOINTS.md` 
- **Deployment procedures** and troubleshooting → `docs/DEPLOYMENT_GUIDE.md`
- **Coolify configuration** patterns → `docs/COOLIFY_CONFIG.md`

**📍 Note**: The `docs/` directory is a git submodule pointing to the shared documentation repository. Run `git submodule update --init` if it's missing.

## Project Overview

This is a multi-site content management system built with PayloadCMS 3.x that allows managing multiple websites from a single admin interface with granular access control.

## Architecture

- **Backend**: PayloadCMS 3.x and TypeScript
- **Database**: SQLite with Drizzle ORM adapter
- **Authentication**: JWT-based with role-based access control
- **Rich Text Editor**: Lexical editor
- **Deployment**: Docker + Coolify ready

## Key Collections

### Core CMS Collections
1. **Users** (`/src/collections/Users.ts`): System administrators with roles (super-admin, site-admin, editor, viewer)
2. **Sites** (`/src/collections/Sites.ts`): Multi-site management with domain, theme, and SEO settings
3. **SiteUsers** (`/src/collections/SiteUsers.ts`): Frontend users for individual sites with site-specific roles
4. **Media** (`/src/collections/Media.ts`): File uploads with site-based access control and responsive images

### ✅ AI Services Collections
5. **MrMechanicSites** (`/src/collections/MrMechanicSites.ts`): Management of AI RAG agent deployments with Flowise integration
6. **FlowiseChatflows** (`/src/collections/FlowiseChatflows.ts`): Flowise chatflow configuration and management
7. **AIServiceLogs** (`/src/collections/AIServiceLogs.ts`): Monitoring and analytics for AI service usage

### 🚧 Missing Collections (To Be Implemented)
- **Pages**: Content management for website pages/posts with site-specific content
- **Navigation**: Menu management system for site navigation
- **Categories**: Content categorization and taxonomy
- **Posts/Articles**: Blog/news content management
- **Settings**: Global and site-specific configuration options

## User Roles & Access Control

### System Users (Admin Panel)
- **Super Admin**: Full system access, can manage all sites and users, create new sites
- **Site Admin**: Access to assigned sites only, can manage site users and content
- **Editor**: Content creation/editing for assigned sites, can upload media
- **Viewer**: Read-only access to assigned sites

### Site Users (Frontend)
- **Member**: Basic site membership
- **Moderator**: Can moderate content and manage other members
- **Contributor**: Can create and edit content

## API Structure

- Admin API: `/admin` (PayloadCMS admin panel)
- RESTful API: Auto-generated based on collections
- GraphQL API: Auto-generated based on collections

### ✅ AI Services API Endpoints
- `POST /api/mrmechanic/sync` - Sync configuration to mrmechanic deployments
- `GET /api/mrmechanic/sync?siteId={id}` - Get mrmechanic site configuration
- `POST /api/mrmechanic/deploy` - Deploy configuration changes to Coolify
- `GET /api/mrmechanic/deploy?mrMechanicSiteId={id}` - Get deployment status
- `GET /api/flowise/flows` - List Flowise chatflows with filtering
- `POST /api/flowise/flows` - Create new Flowise chatflow
- `POST /api/flowise/test` - Test Flowise chatflow functionality
- `GET /api/ai-logs` - Get AI service usage logs and analytics
- `POST /api/ai-logs` - Create AI service log entry
- `DELETE /api/ai-logs?olderThan={days}` - Cleanup old log entries

### 🚧 Missing API Features (To Be Implemented)
- **Multi-site API Resolution**: Domain-based site detection for API calls
- **Frontend Authentication**: Login/register endpoints for site users
- **Site-specific Content**: API filtering based on site context
- **Email Integration**: Password reset, verification, notifications
- **File Upload Enhancement**: Advanced media processing and optimization

## Environment Variables

- `DATABASE_URI`: SQLite database file path (default: file:./payloadcms.db)
- `PAYLOAD_SECRET`: PayloadCMS secret key
- `PORT`: Server port (default: 3000)

## Common Commands

- **Development**: `npm run dev`
- **Build**: `npm run build`
- **Production**: `npm start`
- **Type Generation**: `npm run generate:types`

This roadmap provides a clear path from the current role-based access control foundation to a fully-featured multi-site CMS.