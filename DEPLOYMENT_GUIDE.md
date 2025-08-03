# Coolify Deployment Guide

## Coolify Server Information

**Server**: `135.181.149.150:8000`  
**Version**: Coolify v4.0.0-beta.420.6  
**Project**: RAG (UUID: `loso8oo84sk80s008kwccock`)  
**Server UUID**: `csgkk88okkgkwg8w0g8og8c8`

## Standard Deployment Process

### 1. Pre-deployment Checklist

Before deploying any application:

- [ ] Repository is accessible and up-to-date
- [ ] Environment variables are configured
- [ ] Build configuration is verified
- [ ] Dependencies are properly defined

### 2. Application Configuration

#### Common Build Settings
- **Build Pack**: nixpacks (auto-detection)
- **Branch**: main
- **Port**: 3000 (standard)
- **Environment**: production

#### Environment Variables Pattern
```bash
# Core Settings
NODE_ENV=production
PORT=3000

# Application-specific secrets
PAYLOAD_SECRET=[generated-secret]
DATABASE_URI=[database-connection]

# External Services
OPENAI_API_KEY=[if-needed]
MONGODB_URI=[if-needed]
REDIS_URL=[if-needed]
```

### 3. Deployment Methods

#### Via Coolify Web Interface
1. Navigate to Coolify dashboard
2. Select project/application
3. Click "Deploy" button
4. Monitor deployment logs

#### Via API (Recommended for automation)
```bash
# Set environment variables
export COOLIFY_BASE_URL="http://135.181.149.150:8000"
export COOLIFY_API_TOKEN="your-api-token"

# Deploy application
curl -X POST \
  -H "Authorization: Bearer ${COOLIFY_API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"uuid": "APPLICATION_UUID"}' \
  "${COOLIFY_BASE_URL}/api/v1/deploy"
```

#### Via MCP Tools
```bash
# Using Python MCP Server
coolify-deploy-application --app_uuid=APPLICATION_UUID
coolify-watch-deployment --deployment_uuid=DEPLOYMENT_UUID
coolify-get-deployment-logs --deployment_uuid=DEPLOYMENT_UUID
```

## Application-Specific Deployment

### ProjectAdminCMS (PayloadCMS)

**Repository**: `apan39/projectadmincms`  
**UUID**: `akg0w8kc0kgsc0kc0k4wk0cc`

#### Configuration
```bash
# Required Environment Variables
PAYLOAD_SECRET=your-secret-key
DATABASE_URI=file:./payloadcms.db
NODE_ENV=production
PORT=3000
```

#### Build Process
1. nixpacks detects Node.js project
2. Runs `npm install` or `pnpm install`
3. Builds PayloadCMS admin interface
4. Starts production server

### MrMechanic (AI Assistant)

**Repository**: `apan39/mrmechanic`  
**UUID**: `k4w4wgokwk8000owwgc408ow`

#### Configuration
```bash
# Required Environment Variables
PAYLOAD_SECRET=your-secret-key
OPENAI_API_KEY=your-openai-key
NODE_ENV=production
```

#### Special Notes
- Requires OpenAI API key for AI functionality
- Uses PayloadCMS as backend
- May need additional AI service configurations

### GeneralVectorEmbed (Vector Database)

**Repository**: `apan39/generalvectorembed`  
**UUID**: `skgo080ggw00gso4w8wc4ss4`

#### Configuration
```bash
# Database & Services
MONGODB_URI=mongodb://admin:password@host:27017/database
QDRANT_URL=http://qdrant-service:port
REDIS_URL=redis://default:password@host:6379/0

# Authentication
NEXTAUTH_SECRET=your-nextauth-secret
NEXTAUTH_URL=https://your-domain.com

# External APIs
OPENAI_API_KEY=your-openai-key
PAYLOAD_SECRET=your-payload-secret
```

#### Dependencies
- MongoDB database service
- Qdrant vector database
- Redis cache
- Requires multiple service coordination

### Flowise (AI Workflow Builder)

**Repository**: `apan39/flowise`  
**UUID**: `w0cwck80owcgkw4s4kkos4ko`

#### Configuration
```bash
# Database
DATABASE_TYPE=sqlite
DATABASE_PATH=/app/.flowise

# Authentication
FLOWISE_USERNAME=admin
FLOWISE_PASSWORD=your-password
PASSPHRASE=your-passphrase

# Core Settings
PORT=3000
NODE_ENV=production
```

#### Special Notes
- Uses custom nixpacks.toml configuration
- Monorepo structure with pnpm workspaces
- Requires specific build optimization for memory

## Health Check Configuration

### Current Status Issue
All applications show `running:unhealthy` despite being functional. This is typically due to:

1. **Missing health endpoints**: Applications may not have `/health` routes
2. **Incorrect health check paths**: Coolify checking wrong endpoints
3. **Authentication required**: Health checks failing due to auth requirements
4. **Port configuration**: Health checks on wrong port

### Recommended Health Check Setup

#### For PayloadCMS Apps
```javascript
// Add to your server setup
app.get('/health', (req, res) => {
  res.status(200).json({ 
    status: 'healthy', 
    timestamp: new Date().toISOString(),
    service: 'payloadcms'
  });
});
```

#### For Next.js Apps
```javascript
// pages/api/health.js or app/api/health/route.js
export default function handler(req, res) {
  res.status(200).json({ 
    status: 'healthy',
    timestamp: new Date().toISOString()
  });
}
```

#### For Express Apps
```javascript
app.get('/health', (req, res) => {
  res.json({ status: 'healthy' });
});
```

## Troubleshooting Common Issues

### 1. Build Failures

#### Memory Issues
```toml
# nixpacks.toml
[variables]
NODE_OPTIONS="--max-old-space-size=4096"
```

#### Package Manager Issues
```toml
# nixpacks.toml
[phases.install]
cmds = [
    "npm install -g pnpm@latest",
    "pnpm install --frozen-lockfile"
]
```

### 2. Runtime Issues

#### Port Binding
- Ensure `PORT=3000` environment variable is set
- Application must bind to `0.0.0.0:3000`, not `localhost:3000`

#### Database Connections
- Verify database URLs are accessible from container
- Check firewall rules for external databases
- Ensure database services are running

### 3. Environment Variable Issues

#### Missing Secrets
```bash
# Check via MCP tools
coolify-get-application-info --app_uuid=YOUR_UUID

# Add missing variables
coolify-set-env-variable --app_uuid=YOUR_UUID --key=KEY --value=VALUE
```

#### Masked Values
- Sensitive values show as `***MASKED***` in logs
- Use Coolify dashboard to verify actual values
- Re-set if corrupted during deployment

## Monitoring & Maintenance

### Regular Health Checks
```bash
# Via MCP tools
coolify-list-applications
coolify-get-application-info --app_uuid=UUID

# Via curl
curl -f http://UUID.135.181.149.150.sslip.io/health
```

### Log Monitoring
```bash
# Recent logs
coolify-get-application-logs --app_uuid=UUID --lines=100

# Deployment logs
coolify-get-recent-deployments --app_uuid=UUID
coolify-get-deployment-logs --deployment_uuid=DEPLOYMENT_UUID
```

### Performance Monitoring
- Monitor memory usage during builds
- Check application response times
- Monitor database connections and queries

## Rollback Procedures

### Quick Rollback
```bash
# Deploy previous commit
# 1. Find last working commit in repository
# 2. Reset to that commit
# 3. Force deployment

git log --oneline -10
git reset --hard COMMIT_HASH
git push --force-with-lease
coolify-deploy-application --app_uuid=UUID
```

### Emergency Stops
```bash
# Stop application
coolify-stop-application --app_uuid=UUID

# Restart when ready
coolify-start-application --app_uuid=UUID
```

## Scaling & Optimization

### Resource Optimization
- Monitor container resource usage
- Optimize build processes
- Use appropriate caching strategies

### Database Optimization
- Regular SQLite maintenance for file-based DBs
- Monitor MongoDB/Redis performance
- Implement proper indexing

## Security Considerations

### Environment Variables
- Never commit secrets to repositories
- Use strong, unique passwords/keys
- Rotate secrets periodically

### Network Security
- Applications are exposed via Coolify URLs
- Consider implementing additional authentication
- Monitor access logs for suspicious activity

## Backup Procedures

### Database Backups
- SQLite: Regular file backups of `.db` files
- MongoDB: Use mongodump/mongorestore
- Redis: Use Redis persistence or snapshots

### Configuration Backups
- Export Coolify configurations
- Backup environment variable configurations
- Document custom deployment procedures

## Support & Resources

### Coolify Documentation
- [Official Coolify Docs](https://coolify.io/docs)
- [API Reference](https://coolify.io/docs/api)

### Internal Resources
- MCP Python Tools for Coolify management
- Shared documentation (this repository)
- Project-specific documentation in each repository

### Emergency Contacts
- Review application logs first
- Check Coolify server status
- Consult project-specific documentation
- Use MCP tools for automated diagnosis