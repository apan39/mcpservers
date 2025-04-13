FROM python:3.10-slim

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose port for SSE server
EXPOSE 3000

# Start the server
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "3000"]