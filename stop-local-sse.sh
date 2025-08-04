#!/bin/bash

# Stop Local SSE MCP Servers

echo "🛑 Stopping Local SSE MCP Servers..."

# Stop Python MCP Server
echo "🐍 Stopping Python MCP Server..."
pkill -f "python3 mcp_server.py" && echo "✅ Python server stopped" || echo "⚠️  Python server not running"

# Stop TypeScript MCP Server  
echo "📘 Stopping TypeScript MCP Server..."
pkill -f "node dist/server.js" && echo "✅ TypeScript server stopped" || echo "⚠️  TypeScript server not running"

# Stop Browser-Use MCP Server
echo "🌐 Stopping Browser-Use MCP Server..."
pkill -f "python3 server.py" && echo "✅ Browser-Use server stopped" || echo "⚠️  Browser-Use server not running"

echo ""
echo "🏁 All Local SSE MCP Servers stopped!"