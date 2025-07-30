# Documentation Update Routine

This document outlines the systematic process for keeping project documentation accurate and up-to-date after code changes, API fixes, or deployment updates.

## When to Update Documentation

### Trigger Events
- ✅ API endpoint fixes or changes
- ✅ New features or tools added
- ✅ Bug fixes that affect functionality
- ✅ Deployment status changes
- ✅ Configuration or setup changes
- ✅ Breaking changes or deprecations

### Documentation Files That Require Updates

#### 1. CLAUDE.md - Project Context & Status
**Update when:**
- Application deployment status changes
- Tool functionality is fixed or broken
- New applications are deployed
- API compliance status changes

**Key sections to maintain:**
- `Known Working Applications` - deployment status and health
- `Last Deployment` date and description
- Tool status sections with ✅/❌ indicators
- API compliance notes

#### 2. COOLIFY_API_DEBUGGING.md - Technical Debugging Guide
**Update when:**
- API endpoints change
- New debugging techniques are discovered
- Issues are resolved and solutions documented
- Error patterns and fixes are identified

**Key sections to maintain:**
- `Recent Fixes and Updates` - chronological fix log
- API endpoint examples and patterns
- Error investigation procedures
- Working command examples

#### 3. README.md - Project Overview
**Update when:**
- Project scope changes
- Installation procedures change
- Major feature additions
- Architecture changes

#### 4. MCP_SETUP.md - Setup Instructions
**Update when:**
- Installation steps change
- Dependencies are updated
- Configuration requirements change
- Environment setup procedures change

## Documentation Update Checklist

### After Code Changes

- [ ] **Identify Impact**: What functionality was changed/fixed?
- [ ] **Update Status**: Mark tools as working (✅) or broken (❌)
- [ ] **Update Examples**: Ensure code examples still work
- [ ] **Update Dates**: Add current date to relevant sections
- [ ] **Verify Links**: Check that all referenced URLs/endpoints are correct

### After API Fixes

- [ ] **Document Root Cause**: What was the underlying issue?
- [ ] **Document Solution**: What exactly was changed?
- [ ] **Update Endpoint References**: Correct API paths and methods
- [ ] **Add Testing Results**: Show verified working examples
- [ ] **Update Troubleshooting**: Remove outdated workarounds

### After Deployments

- [ ] **Update Deployment Date**: Latest deployment timestamp
- [ ] **Update Application Status**: Health status of each service
- [ ] **Update Tool Availability**: Which tools are operational
- [ ] **Update URLs**: Working service endpoints
- [ ] **Update UUIDs**: Current application identifiers

## Documentation Structure Standards

### Date Format
Use: `July 30, 2025` (Month DD, YYYY)

### Status Indicators
- ✅ Working/Fixed/Operational
- ❌ Broken/Failed/Non-operational  
- ⏳ In Progress/Deploying
- ℹ️ Information/Note
- 🔧 Fix Applied
- 🚀 Deployment/Launch

### Section Organization
```markdown
### [Date]: [Brief Description]

**Problem Identified:**
- Bullet points describing issues

**Root Cause:**  
- Technical explanation

**Solution Implemented:**
- Detailed fix description

**Verification Results:**
- Testing evidence with status indicators

**Impact:**
- Business/functional impact summary
```

## Automation Opportunities

### Automated Updates (Future)
- Git hooks to update deployment dates
- Status monitoring to update health indicators
- API endpoint validation
- Link checking

### Manual Reviews (Current)
- Monthly documentation review
- Post-deployment documentation sync
- After major fixes documentation update

## Quality Assurance

### Before Committing Documentation Changes
- [ ] All dates are current and accurate
- [ ] All status indicators reflect reality  
- [ ] All code examples have been tested
- [ ] All links and endpoints are verified
- [ ] Spelling and grammar checked
- [ ] Consistent formatting applied

### Cross-Reference Validation
- [ ] CLAUDE.md status matches actual tool functionality
- [ ] COOLIFY_API_DEBUGGING.md examples match current API
- [ ] README.md reflects current project state
- [ ] All documentation files are internally consistent

## Responsibility Matrix

| Document | Primary Maintainer | Update Frequency |
|----------|-------------------|------------------|
| CLAUDE.md | Development Team | After each deployment |
| COOLIFY_API_DEBUGGING.md | API Team | After API changes |
| README.md | Project Lead | Monthly or major changes |
| MCP_SETUP.md | DevOps Team | After infrastructure changes |

## Success Metrics

### Documentation Quality Indicators
- ✅ All examples work when tested
- ✅ Status indicators match reality
- ✅ Dates are current (within 30 days)
- ✅ No broken links or references
- ✅ Consistent formatting throughout

### Documentation Coverage
- ✅ Every major feature is documented
- ✅ Every known issue has troubleshooting steps
- ✅ Every API endpoint has usage examples
- ✅ Every tool has status and description

## Implementation Notes

This routine should be executed:
1. **Immediately** after API fixes or major changes
2. **Within 24 hours** of deployments
3. **Weekly** for general maintenance
4. **Monthly** for comprehensive review

The goal is to ensure that documentation always accurately reflects the current state of the system and provides useful, up-to-date information for users and developers.