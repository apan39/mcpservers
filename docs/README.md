# Shared Documentation Repository

This repository contains shared documentation for the apan39 Coolify application ecosystem. It's designed to be included as a git submodule in each project to maintain consistent, centralized documentation.

## Structure

- `SHARED_CONTEXT.md` - Common project context and architecture overview
- `API_ENDPOINTS.md` - Inter-service API documentation and endpoints
- `DEPLOYMENT_GUIDE.md` - Coolify deployment procedures and troubleshooting
- `COOLIFY_CONFIG.md` - Shared Coolify configuration patterns

## Usage as Git Submodule

To add this shared documentation to a project:

```bash
# Add as submodule
git submodule add https://github.com/apan39/shared-docs.git docs

# Initialize and update
git submodule update --init --recursive

# Reference in your claude.md or documentation
<!-- Include shared content -->
```

## Updating Shared Documentation

When documentation is updated in this repository:

1. Update the content in this repo
2. Commit and push changes
3. Update submodules in dependent projects:

```bash
# In each project that uses this submodule
git submodule update --remote docs
git add docs
git commit -m "Update shared documentation"
```

## Projects Using This Documentation

- **projectadmincms** (PayloadCMS Admin)
- **mrmechanic** (AI Assistant)
- **generalvectorembed** (Vector Database Service)
- **flowise** (AI Workflow Builder)

## Maintenance

This repository should be kept minimal and focused on truly shared information that applies across multiple projects in the ecosystem.