FROM python:3.10-slim

WORKDIR /app

# Install system dependencies for crawl4ai and other tools
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash appuser
RUN chown -R appuser:appuser /app
USER appuser

# Copy project files
COPY --chown=appuser:appuser . .

# Expose port
EXPOSE 3009

# Health check - HTTP check since curl/wget available in base image
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:3009/health', timeout=5)" || exit 1

# Start the production server
CMD ["python", "start.py"]