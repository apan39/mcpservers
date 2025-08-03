# Coolify Configuration Patterns

## Standard Configuration Templates

### Basic Node.js Application

```yaml
# Standard environment variables
NODE_ENV: production
PORT: 3000

# Build configuration (nixpacks auto-detects)
build_pack: nixpacks
branch: main
```

### PayloadCMS Application Template

```yaml
# Environment Variables
NODE_ENV: production
PORT: 3000
PAYLOAD_SECRET: [generate-32-char-secret]
DATABASE_URI: file:./payloadcms.db

# Build Configuration
build_pack: nixpacks
start_command: npm start
```

Example for ProjectAdminCMS and MrMechanic applications.

### Next.js with External Services Template

```yaml
# Core Settings
NODE_ENV: production
NEXTAUTH_SECRET: [generate-32-char-secret]
NEXTAUTH_URL: https://your-app-url.sslip.io

# Database Connections
MONGODB_URI: mongodb://user:pass@host:27017/database
REDIS_URL: redis://default:password@host:6379/0

# External Services
QDRANT_URL: http://qdrant-service-url
OPENAI_API_KEY: [your-openai-key]

# Build Configuration
build_pack: nixpacks
dockerfile_location: /Dockerfile  # if custom dockerfile
```

Used by GeneralVectorEmbed application.

### Monorepo Template (Flowise)

```toml
# nixpacks.toml
[variables]
NODE_VERSION="20"
NODE_OPTIONS="--max-old-space-size=4096"
COREPACK_ENABLE_NETWORK="0"
COREPACK_ENABLE_DOWNLOAD_PROMPT="0"

[phases.install]
cmds = [
    "npm install -g pnpm@9.15.9",
    "pnpm install --frozen-lockfile"
]

[phases.build]
cmds = ["pnpm build"]

[start]
cmd = "pnpm start"
```

```yaml
# Environment Variables
NODE_ENV: production
PORT: 3000
DATABASE_TYPE: sqlite
DATABASE_PATH: /app/.flowise
FLOWISE_USERNAME: admin
FLOWISE_PASSWORD: [secure-password]
PASSPHRASE: [encryption-key]
```

## Resource Allocation Patterns

### Memory Configuration

#### Standard Applications
```yaml
# Default nixpacks memory allocation
memory_limit: 1GB
memory_reservation: 512MB
```

#### Memory-Intensive Applications (Flowise, Vector Services)
```yaml
# Custom memory allocation
NODE_OPTIONS: "--max-old-space-size=4096"
memory_limit: 2GB
memory_reservation: 1GB
```

### CPU Configuration

#### Standard Web Applications
```yaml
cpu_limit: "1.0"
cpu_reservation: "0.5"
```

#### AI/ML Applications
```yaml
cpu_limit: "2.0"
cpu_reservation: "1.0"
```

## Network Configuration

### Internal Service Communication

#### Service Discovery Pattern
```yaml
# Applications communicate via UUID-based URLs
internal_url: http://{uuid}.135.181.149.150.sslip.io
external_url: https://{custom-domain}  # if custom domain configured
```

#### Port Configuration
```yaml
# Standard port mapping
container_port: 3000
exposed_port: 3000  # Coolify handles external routing
```

### CORS Configuration

#### Development CORS
```javascript
// For development/testing
cors: {
  origin: ['http://localhost:3000', 'https://*.sslip.io'],
  credentials: true
}
```

#### Production CORS
```javascript
// For production
cors: {
  origin: process.env.ALLOWED_ORIGINS?.split(',') || ['https://your-domain.com'],
  credentials: true
}
```

## Database Configuration Patterns

### SQLite (Local File Database)

#### PayloadCMS Pattern
```yaml
DATABASE_URI: file:./payloadcms.db
```

#### Flowise Pattern
```yaml
DATABASE_TYPE: sqlite
DATABASE_PATH: /app/.flowise
```

**Pros**: Simple, no external dependencies  
**Cons**: Not suitable for scaling, backup complexity

### MongoDB (External Service)

#### Connection Pattern
```yaml
MONGODB_URI: mongodb://username:password@host:27017/database?directConnection=true
```

#### With Connection Pooling
```yaml
MONGODB_URI: mongodb://user:pass@host:27017/db?maxPoolSize=10&retryWrites=true
```

**Used by**: GeneralVectorEmbed

### Redis (Caching/Session Storage)

#### Standard Pattern
```yaml
REDIS_URL: redis://default:password@host:6379/0
```

#### With TLS
```yaml
REDIS_URL: rediss://default:password@host:6380/0
```

**Used by**: GeneralVectorEmbed

## Build Optimization Patterns

### Package Manager Optimization

#### PNPM Configuration
```toml
# nixpacks.toml
[phases.install]
cmds = [
    "npm install -g pnpm@latest",
    "pnpm install --frozen-lockfile"
]
```

#### NPM with Cache
```toml
[phases.install]
cmds = [
    "npm ci --only=production"
]
```

### Build Caching

#### Layer Caching Strategy
```dockerfile
# If using custom Dockerfile
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
```

### Multi-stage Builds

#### Next.js Optimization
```dockerfile
# Build stage
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Production stage
FROM node:20-alpine AS runner
WORKDIR /app
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/package*.json ./
RUN npm ci --only=production
CMD ["npm", "start"]
```

## Security Configuration

### Environment Variable Security

#### Secret Management
```yaml
# Always use strong secrets
PAYLOAD_SECRET: [min-32-chars-alphanumeric]
NEXTAUTH_SECRET: [min-32-chars-random]
DATABASE_PASSWORD: [strong-password]

# API Keys (external services)
OPENAI_API_KEY: [service-provided-key]
GITHUB_TOKEN: [personal-access-token]
```

#### Development vs Production
```yaml
# Development
NODE_ENV: development
DEBUG: true
VERBOSE_LOGGING: true

# Production
NODE_ENV: production
DEBUG: false
VERBOSE_LOGGING: false
```

### Authentication Patterns

#### PayloadCMS Auth
```javascript
// Built-in authentication
auth: {
  tokenExpiration: 7200, // 2 hours
  verify: true,
  maxLoginAttempts: 5,
  lockTime: 600000, // 10 minutes
}
```

#### NextAuth Configuration
```javascript
// NextAuth.js setup
providers: [
  // Configure your providers
],
session: {
  strategy: "jwt",
  maxAge: 30 * 24 * 60 * 60, // 30 days
},
```

## Health Check Patterns

### Standard Health Endpoints

#### Express/PayloadCMS
```javascript
app.get('/health', (req, res) => {
  res.status(200).json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    service: process.env.SERVICE_NAME || 'unknown'
  });
});
```

#### Next.js API Route
```javascript
// pages/api/health.js
export default function handler(req, res) {
  res.status(200).json({
    status: 'healthy',
    timestamp: new Date().toISOString()
  });
}
```

### Comprehensive Health Checks

#### Database Connectivity
```javascript
app.get('/health', async (req, res) => {
  try {
    // Check database
    await database.ping();
    
    // Check external services
    const externalChecks = await Promise.allSettled([
      checkRedis(),
      checkMongoDB(),
      checkQdrant()
    ]);
    
    res.status(200).json({
      status: 'healthy',
      timestamp: new Date().toISOString(),
      services: {
        database: 'connected',
        external: externalChecks.map(result => 
          result.status === 'fulfilled' ? 'connected' : 'disconnected'
        )
      }
    });
  } catch (error) {
    res.status(503).json({
      status: 'unhealthy',
      error: error.message
    });
  }
});
```

## Monitoring Configuration

### Application Logging

#### Standard Logging Pattern
```javascript
const logger = {
  info: (message, meta) => console.log(JSON.stringify({ level: 'info', message, meta, timestamp: new Date().toISOString() })),
  error: (message, error) => console.error(JSON.stringify({ level: 'error', message, error: error.message, stack: error.stack, timestamp: new Date().toISOString() })),
  warn: (message, meta) => console.warn(JSON.stringify({ level: 'warn', message, meta, timestamp: new Date().toISOString() }))
};
```

#### Environment-based Logging
```javascript
const logLevel = process.env.LOG_LEVEL || 'info';
const isDevelopment = process.env.NODE_ENV === 'development';

if (isDevelopment) {
  // Pretty logging for development
  console.log(message);
} else {
  // Structured logging for production
  console.log(JSON.stringify(logEntry));
}
```

### Metrics Collection

#### Basic Application Metrics
```javascript
// Track basic application metrics
const metrics = {
  requests: 0,
  errors: 0,
  uptime: process.uptime(),
  memory: process.memoryUsage(),
  cpu: process.cpuUsage()
};

app.get('/metrics', (req, res) => {
  res.json(metrics);
});
```

## Deployment Automation

### Git Hooks Pattern

#### Pre-deployment Validation
```bash
#!/bin/bash
# .github/workflows/deploy.yml or similar

# 1. Run tests
npm test

# 2. Build check
npm run build

# 3. Security scan
npm audit

# 4. Deploy if all pass
curl -X POST "${COOLIFY_API_URL}/deploy" \
  -H "Authorization: Bearer ${COOLIFY_TOKEN}" \
  -d '{"uuid": "${APP_UUID}"}'
```

### Environment Promotion

#### Staging to Production
```yaml
# Staging environment
staging_env:
  NODE_ENV: staging
  DATABASE_URI: staging_database
  
# Production environment  
production_env:
  NODE_ENV: production
  DATABASE_URI: production_database
```

## Troubleshooting Configuration

### Debug Mode Configuration

#### Development Debug
```yaml
NODE_ENV: development
DEBUG: "*"
VERBOSE: true
LOG_LEVEL: debug
```

#### Production Debug (temporary)
```yaml
NODE_ENV: production
DEBUG: "app:*"  # Specific debug namespaces
LOG_LEVEL: info  # Keep production log level
```

### Common Configuration Issues

#### Port Binding
```javascript
// Incorrect (localhost only)
app.listen(3000, 'localhost');

// Correct (all interfaces)
app.listen(3000, '0.0.0.0');
```

#### Environment Variable Types
```javascript
// String to number conversion
const port = parseInt(process.env.PORT || '3000', 10);

// Boolean conversion
const enableFeature = process.env.ENABLE_FEATURE === 'true';

// Array conversion
const allowedOrigins = process.env.ALLOWED_ORIGINS?.split(',') || [];
```

## Best Practices Summary

### Configuration Management
1. **Use environment variables** for all configuration
2. **Validate required variables** at startup
3. **Provide sensible defaults** where possible
4. **Document all variables** in README

### Security
1. **Never commit secrets** to repositories
2. **Use strong, unique secrets** for each environment
3. **Implement proper authentication** for all endpoints
4. **Regular security updates** and audits

### Performance
1. **Optimize build processes** with proper caching
2. **Monitor resource usage** and adjust limits
3. **Implement health checks** for reliability
4. **Use appropriate logging** levels

### Maintainability
1. **Consistent configuration** patterns across projects
2. **Clear documentation** for all settings
3. **Automated deployment** processes
4. **Regular backup** procedures