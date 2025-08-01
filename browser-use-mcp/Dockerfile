FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    gnupg \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Playwright dependencies
RUN apt-get update && apt-get install -y \
    libnss3 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libxkbcommon0 \
    libgtk-3-0 \
    libgbm1 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Create non-root user first
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Switch to appuser before installing Playwright
USER appuser

# Install Playwright browsers as appuser
RUN playwright install chromium

# Copy application code
COPY --chown=appuser:appuser . .

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000/health || exit 1

# Run the HTTP-compatible application  
CMD ["python", "server_http.py"]