#!/bin/bash

# Start Local SSE MCP Servers for Development
# This script starts all three MCP servers with SSE support for localhost development

echo "🚀 Starting Local SSE MCP Servers..."

# Set local development environment
export HOST="127.0.0.1" 
export NODE_ENV="development"
export LOG_LEVEL="INFO"

# Load environment variables
if [ -f .env ]; then
    echo "📁 Loading environment variables from .env"
    source .env
else
    echo "⚠️  No .env file found, using defaults"
fi

# Check if ports are available
check_port() {
    if lsof -i :$1 > /dev/null 2>&1; then
        echo "❌ Port $1 is already in use"
        return 1
    fi
    return 0
}

# Start Python MCP Server (SSE + HTTP)
echo "🐍 Starting Python MCP Server on port 3009..."
if check_port 3009; then
    cd python && python3 mcp_server.py &
    PYTHON_PID=$!
    echo "✅ Python MCP Server started (PID: $PYTHON_PID)"
    echo "   - SSE: http://localhost:3009/sse"
    echo "   - HTTP: http://localhost:3009/mcp"
    cd ..
else
    echo "⚠️  Skipping Python server - port 3009 in use"
fi

# Wait a moment
sleep 2

# Start TypeScript MCP Server (SSE + HTTP)
echo "📘 Starting TypeScript MCP Server on port 3010..."
if check_port 3010; then
    cd typescript
    if [ ! -d "dist" ]; then
        echo "🔧 Building TypeScript server..."
        npm run build
    fi
    node dist/server.js &
    TYPESCRIPT_PID=$!
    echo "✅ TypeScript MCP Server started (PID: $TYPESCRIPT_PID)"
    echo "   - SSE: http://localhost:3010/sse"
    echo "   - HTTP: http://localhost:3010/mcp-advanced"
    cd ..
else
    echo "⚠️  Skipping TypeScript server - port 3010 in use"
fi

# Wait a moment
sleep 2

# Start Browser-Use MCP Server (SSE)
echo "🌐 Starting Browser-Use MCP Server on port 3000..."
if check_port 3000; then
    cd browser-use-mcp && python3 server.py &
    BROWSER_PID=$!
    echo "✅ Browser-Use MCP Server started (PID: $BROWSER_PID)"
    echo "   - SSE: http://localhost:3000/sse"
    cd ..
else
    echo "⚠️  Skipping Browser-Use server - port 3000 in use"
fi

echo ""
echo "🎉 Local SSE MCP Servers are running!"
echo ""
echo "📋 Configuration for Claude Desktop (~/.claude-desktop/local-mcp.json):"
echo "{"
echo '  "mcpServers": {'
echo '    "python-local-sse": {'
echo '      "transport": {"type": "sse", "url": "http://localhost:3009/sse"}'
echo '    },'
echo '    "typescript-local-sse": {'
echo '      "transport": {"type": "sse", "url": "http://localhost:3010/sse"}'
echo '    },'
echo '    "browser-use-local-sse": {'
echo '      "transport": {"type": "sse", "url": "http://localhost:3000/sse"}'
echo '    }'
echo '  }'
echo "}"
echo ""
echo "🔧 To use:"
echo "1. Copy the configuration above to ~/.claude-desktop/local-mcp.json"
echo "2. Restart Claude Desktop"
echo "3. Access localhost PayloadCMS instances directly via SSE!"
echo ""
echo "🛑 To stop all servers: ./stop-local-sse.sh"
echo ""
echo "Press Ctrl+C to stop all servers"

# Keep script running and handle shutdown
trap 'echo ""; echo "🛑 Stopping all MCP servers..."; kill $PYTHON_PID $TYPESCRIPT_PID $BROWSER_PID 2>/dev/null; exit' INT

# Wait for background processes
wait