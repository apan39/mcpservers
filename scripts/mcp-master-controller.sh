#!/bin/bash

# MCP Master Controller
# Unified command center for all MCP operations using Inspector integration

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
PURPLE='\033[0;35m'
NC='\033[0m'

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

# Functions
show_usage() {
    cat << EOF
🔧 MCP Master Controller - Unified MCP Management

USAGE:
    $0 <command> [options]

COMMANDS:
    validate        Run comprehensive validation of all MCP servers
    test-tools      Test tools across all working servers  
    monitor         Generate health monitoring dashboard
    inspector       Launch MCP Inspector for specific server
    start-local     Start all local MCP servers
    stop-local      Stop all local MCP servers
    status          Show quick status of all servers
    help            Show this help message

EXAMPLES:
    $0 validate                    # Validate all servers
    $0 test-tools                  # Test tools on working servers
    $0 monitor                     # Generate health dashboard
    $0 inspector python-local-http # Launch Inspector for specific server
    $0 start-local                 # Start local development servers
    $0 status                      # Quick status check

For detailed information about each command, use: $0 <command> --help
EOF
}

run_validation() {
    echo -e "${BLUE}🔍 Running comprehensive MCP validation...${NC}"
    "$SCRIPT_DIR/mcp-universal-validator-simple.sh"
}

run_tool_testing() {
    echo -e "${BLUE}🔧 Running tool testing suite...${NC}"
    "$SCRIPT_DIR/mcp-tool-tester.sh"
}

run_monitoring() {
    echo -e "${BLUE}📊 Generating health monitoring dashboard...${NC}"
    "$SCRIPT_DIR/mcp-health-monitor.sh"
}

launch_inspector() {
    local server_name="$1"
    
    if [[ -z "$server_name" ]]; then
        echo -e "${RED}❌ Server name required for Inspector${NC}"
        echo "Usage: $0 inspector <server-name>"
        echo "Available servers: python-local-http, typescript-local-sse, browser-use-local-http, etc."
        return 1
    fi
    
    # Create temporary MCP config for Inspector
    local config_file="/tmp/inspector_${server_name}.json"
    
    case "$server_name" in
        "python-local-http")
            cat > "$config_file" << 'EOF'
{
  "mcpServers": {
    "python-local-http": {
      "type": "http",
      "url": "http://localhost:3009/mcp",
      "headers": {
        "Authorization": "Bearer 4446e3ca599152c85fc96ecebb0367674e823694e5197a0ed8ca1262e825075f",
        "Content-Type": "application/json"
      }
    }
  }
}
EOF
            ;;
        "typescript-local-sse")
            cat > "$config_file" << 'EOF'
{
  "mcpServers": {
    "typescript-local-sse": {
      "type": "sse",
      "url": "http://localhost:3010/sse"
    }
  }
}
EOF
            ;;
        "browser-use-local-http")
            cat > "$config_file" << 'EOF'
{
  "mcpServers": {
    "browser-use-local-http": {
      "type": "http",
      "url": "http://localhost:3011/mcp",
      "headers": {
        "Authorization": "Bearer 4446e3ca599152c85fc96ecebb0367674e823694e5197a0ed8ca1262e825075f",
        "Content-Type": "application/json"
      }
    }
  }
}
EOF
            ;;
        *)
            echo -e "${RED}❌ Unknown server: $server_name${NC}"
            rm -f "$config_file"
            return 1
            ;;
    esac
    
    echo -e "${GREEN}🔍 Launching MCP Inspector for $server_name...${NC}"
    echo -e "${BLUE}Config file: $config_file${NC}"
    
    npx @modelcontextprotocol/inspector --config "$config_file" --server "$server_name"
    
    # Cleanup
    rm -f "$config_file"
}

start_local_servers() {
    echo -e "${BLUE}🚀 Starting local MCP servers...${NC}"
    
    if [[ -f "$ROOT_DIR/start-local-sse.sh" ]]; then
        cd "$ROOT_DIR"
        ./start-local-sse.sh
    else
        echo -e "${RED}❌ start-local-sse.sh not found${NC}"
        return 1
    fi
}

stop_local_servers() {
    echo -e "${BLUE}🛑 Stopping local MCP servers...${NC}"
    
    # Kill known server processes
    pkill -f "python.*mcp_server.py" 2>/dev/null || true
    pkill -f "node.*dist/server.js" 2>/dev/null || true
    pkill -f "python.*server.py" 2>/dev/null || true
    
    echo -e "${GREEN}✅ Local servers stopped${NC}"
}

quick_status() {
    echo -e "${BLUE}📊 Quick MCP Status Check${NC}"
    echo ""
    
    # Check a few key servers quickly
    local servers=(
        "python-local-http|http://localhost:3009/mcp"
        "typescript-local-sse|http://localhost:3010/sse"
        "browser-use-local-http|http://localhost:3011/mcp"
        "remote-python-tools|http://zs8sk0cgs4s8gsgwswsg88ko.135.181.149.150.sslip.io/mcp"
    )
    
    for server_config in "${servers[@]}"; do
        IFS='|' read -r name url <<< "$server_config"
        
        if [[ "$url" == *"/sse" ]]; then
            # SSE check
            if curl -N -H "Accept: text/event-stream" "$url" --max-time 2 2>/dev/null | head -1 | grep -q "event: endpoint" 2>/dev/null; then
                echo -e "${GREEN}✅ $name${NC}"
            else
                echo -e "${RED}❌ $name${NC}"
            fi
        else
            # HTTP check
            local response=$(curl -s -o /dev/null -w "%{http_code}" "$url" --max-time 5 2>/dev/null || echo "000")
            if [[ "$response" == "200" ]] || [[ "$response" == "405" ]]; then
                echo -e "${GREEN}✅ $name (HTTP $response)${NC}"
            else
                echo -e "${RED}❌ $name (HTTP $response)${NC}"
            fi
        fi
    done
}

# Main execution
main() {
    local command="$1"
    shift || true
    
    case "$command" in
        "validate")
            run_validation "$@"
            ;;
        "test-tools")
            run_tool_testing "$@"
            ;;
        "monitor")
            run_monitoring "$@"
            ;;
        "inspector")
            launch_inspector "$@"
            ;;
        "start-local")
            start_local_servers "$@"
            ;;
        "stop-local")
            stop_local_servers "$@"  
            ;;
        "status")
            quick_status "$@"
            ;;
        "help"|"--help"|"-h"|"")
            show_usage
            ;;
        *)
            echo -e "${RED}❌ Unknown command: $command${NC}"
            echo ""
            show_usage
            exit 1
            ;;
    esac
}

# Header
echo -e "${PURPLE}═══════════════════════════════════════════════════════════════════════════════${NC}"
echo -e "${PURPLE}🔧 MCP Master Controller - Universal MCP Management System${NC}"
echo -e "${PURPLE}═══════════════════════════════════════════════════════════════════════════════${NC}"
echo ""

# Run main function
main "$@"