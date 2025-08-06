#!/bin/bash

# Stop Local SSE MCP Servers

echo "🛑 Stopping Local SSE MCP Servers..."

# PID directory from start script
PID_DIR="/tmp/mcp-servers"

# First try to stop using stored PIDs if available
if [ -d "$PID_DIR" ]; then
    echo "📁 Using stored PIDs for graceful shutdown..."
    
    for pid_file in "$PID_DIR"/*.pid; do
        if [ -f "$pid_file" ]; then
            PID=$(cat "$pid_file")
            SERVER=$(basename "$pid_file" .pid)
            
            if kill -0 "$PID" 2>/dev/null; then
                echo "🔄 Stopping $SERVER server (PID: $PID)..."
                kill "$PID" 2>/dev/null
                sleep 2
                
                if kill -0 "$PID" 2>/dev/null; then
                    echo "🔧 Force stopping $SERVER server..."
                    kill -9 "$PID" 2>/dev/null
                fi
                
                if ! kill -0 "$PID" 2>/dev/null; then
                    echo "✅ $SERVER server stopped"
                fi
            fi
            
            rm -f "$pid_file"
        fi
    done
    
    # Remove PID directory
    rm -rf "$PID_DIR"
    
    echo ""
fi

echo "🔄 Process pattern-based cleanup..."

# Function to check if process is running on a port
check_port_process() {
    local port=$1
    lsof -ti:$port > /dev/null 2>&1
}

# Function to kill processes by pattern with verification
kill_process_pattern() {
    local pattern=$1
    local name=$2
    
    if pgrep -f "$pattern" > /dev/null; then
        pkill -f "$pattern"
        sleep 1
        if pgrep -f "$pattern" > /dev/null; then
            pkill -9 -f "$pattern"
            sleep 1
        fi
        
        if pgrep -f "$pattern" > /dev/null; then
            echo "⚠️  $name still running after kill attempt"
            return 1
        else
            echo "✅ $name stopped"
            return 0
        fi
    else
        echo "⚠️  $name not running"
        return 0
    fi
}

# Stop Python MCP Server (runs as uvicorn on port 3009)
echo "🐍 Stopping Python MCP Server..."
kill_process_pattern "uvicorn.*mcp_server.*3009" "Python MCP server"
# Fallback pattern for different uvicorn process names
kill_process_pattern "python.*mcp_server.py" "Python MCP server (fallback)"

# Stop TypeScript MCP Server (runs as node on port 3010)
echo "📘 Stopping TypeScript MCP Server..."
kill_process_pattern "node.*dist/server.js" "TypeScript MCP server"
# Alternative pattern
kill_process_pattern "node.*typescript.*server" "TypeScript MCP server (fallback)"

# Stop Browser-Use MCP Server (runs as uvicorn on port 3011)
echo "🌐 Stopping Browser-Use MCP Server..."
kill_process_pattern "uvicorn.*server.*3011" "Browser-Use MCP server"
# Fallback patterns
kill_process_pattern "python.*server.py.*3011" "Browser-Use MCP server (fallback 1)"
kill_process_pattern "python.*browser-use-mcp" "Browser-Use MCP server (fallback 2)"

# Port-based cleanup as final fallback
echo "🔧 Port-based cleanup (final fallback)..."
PORTS_KILLED=()

for port in 3009 3010 3011; do
    if check_port_process $port; then
        echo "🔄 Killing remaining processes on port $port..."
        if lsof -ti:$port | xargs kill -9 2>/dev/null; then
            PORTS_KILLED+=($port)
            echo "✅ Port $port cleaned up"
        else
            echo "⚠️  Could not clean up port $port"
        fi
    fi
done

# Final verification
echo ""
echo "📋 Final verification:"
STILL_RUNNING=()

if check_port_process 3009; then
    STILL_RUNNING+=("Python MCP (port 3009)")
fi

if check_port_process 3010; then
    STILL_RUNNING+=("TypeScript MCP (port 3010)")
fi

if check_port_process 3011; then
    STILL_RUNNING+=("Browser-Use MCP (port 3011)")
fi

if [ ${#STILL_RUNNING[@]} -eq 0 ]; then
    echo "✅ All MCP server ports are clear"
    echo ""
    echo "🏁 All Local SSE MCP Servers stopped successfully!"
else
    echo "⚠️  Some servers may still be running:"
    for server in "${STILL_RUNNING[@]}"; do
        echo "   - $server"
    done
    echo ""
    echo "💡 Try running the script again or manually kill with:"
    echo "   lsof -ti:3009,3010,3011 | xargs kill -9"
fi