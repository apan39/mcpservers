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

# Create non-root user for security first
RUN useradd --create-home --shell /bin/bash appuser

# Copy project files and set ownership
COPY --chown=appuser:appuser . .

# Switch to appuser for builds
USER appuser

# Build TypeScript code
RUN npm run build

# Install additional system dependencies needed for Playwright (as root temporarily)
USER root
RUN apt-get update && apt-get install -y \
    libnss3 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libxkbcommon0 \
    libgtk-3-0 \
    libgbm1 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

# Switch to appuser and install Playwright browsers
USER appuser

# Set Playwright environment variables
ENV PLAYWRIGHT_BROWSERS_PATH=/home/appuser/.cache/ms-playwright

# Install Playwright browsers as appuser
RUN npx playwright install chromium

# Also install as root (fallback)
USER root
RUN PLAYWRIGHT_BROWSERS_PATH=/root/.cache/ms-playwright npx playwright install chromium

# Switch back to appuser
USER appuser

# Expose port
EXPOSE 3010

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3010/health || exit 1

# Ensure we're running as appuser
USER appuser

# Start the server
CMD ["npm", "start"]