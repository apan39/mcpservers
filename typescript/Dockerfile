FROM node:20-slim

WORKDIR /app

# Install system dependencies for Playwright
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy package files first for better caching
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy project files
COPY . .

# Build TypeScript code
RUN npm run build

# Create non-root user for security first
RUN useradd --create-home --shell /bin/bash appuser
RUN chown -R appuser:appuser /app

# Switch to appuser before installing Playwright
USER appuser

# Install Playwright browsers and dependencies as appuser
RUN npx playwright install --with-deps chromium

# Expose port
EXPOSE 3010

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3010/health || exit 1

# Start the server
CMD ["npm", "start"]