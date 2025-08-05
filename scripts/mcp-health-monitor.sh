#!/bin/bash

# MCP Health Monitor
# Real-time monitoring and dashboard for all MCP servers

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
MONITOR_DIR="$ROOT_DIR/mcp-health-monitoring"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

mkdir -p "$MONITOR_DIR"

# All servers (including non-working for monitoring)
ALL_SERVERS=(
    "remote-python-tools|http://zs8sk0cgs4s8gsgwswsg88ko.135.181.149.150.sslip.io/mcp|http|Bearer 4446e3ca599152c85fc96ecebb0367674e823694e5197a0ed8ca1262e825075f|production"
    "remote-typescript-tools|http://zw0o84skskgc8kgooswgo8k4.135.181.149.150.sslip.io/mcp|http|Bearer 4446e3ca599152c85fc96ecebb0367674e823694e5197a0ed8ca1262e825075f|production"
    "remote-browser-use-mcp|http://w8wcwg48ok4go8g8swgwkgk8.135.181.149.150.sslip.io/mcp|http|Bearer 4446e3ca599152c85fc96ecebb0367674e823694e5197a0ed8ca1262e825075f|production"
    "python-local-http|http://localhost:3009/mcp|http|Bearer 4446e3ca599152c85fc96ecebb0367674e823694e5197a0ed8ca1262e825075f|development"
    "python-local-sse|http://localhost:3009/sse|sse|none|development"
    "typescript-local-sse|http://localhost:3010/sse|sse|none|development"
    "typescript-local-http|http://localhost:3010/mcp|http|Bearer 4446e3ca599152c85fc96ecebb0367674e823694e5197a0ed8ca1262e825075f|development"
    "browser-use-local-http|http://localhost:3011/mcp|http|Bearer 4446e3ca599152c85fc96ecebb0367674e823694e5197a0ed8ca1262e825075f|development"
    "browser-use-local-sse|http://localhost:3011/sse|sse|none|development"
)

# Health check functions
check_http_health() {
    local url="$1"
    local auth="$2"
    local timeout="$3"
    
    if [[ "$auth" == "none" ]]; then
        response=$(curl -s -o /dev/null -w "%{http_code}|%{time_total}" "$url" --max-time "$timeout" 2>/dev/null || echo "000|0")
    else
        response=$(curl -s -o /dev/null -w "%{http_code}|%{time_total}" -H "Authorization: $auth" "$url" --max-time "$timeout" 2>/dev/null || echo "000|0")
    fi
    
    echo "$response"
}

check_sse_health() {
    local url="$1"
    local timeout="$3"
    
    local start_time=$(date +%s.%N)
    if timeout "$timeout" curl -N -H "Accept: text/event-stream" "$url" --max-time "$timeout" 2>/dev/null | head -1 | grep -q "event: endpoint"; then
        local end_time=$(date +%s.%N)
        local duration=$(echo "$end_time - $start_time" | bc 2>/dev/null || echo "0")
        echo "200|$duration"
    else
        echo "000|0"
    fi
}

get_tool_count() {
    local server_name="$1"
    local url="$2"
    local transport="$3"
    local auth="$4"
    
    if [[ "$transport" == "http" ]]; then
        local response_file="/tmp/${server_name}_tools_count.json"
        if [[ "$auth" == "none" ]]; then
            curl_cmd="curl -s -X POST '$url' -H 'Content-Type: application/json' -d '{\"jsonrpc\": \"2.0\", \"id\": 1, \"method\": \"tools/list\"}' --max-time 10"
        else
            curl_cmd="curl -s -X POST '$url' -H 'Authorization: $auth' -H 'Content-Type: application/json' -d '{\"jsonrpc\": \"2.0\", \"id\": 1, \"method\": \"tools/list\"}' --max-time 10"
        fi
        
        if eval "$curl_cmd" > "$response_file" 2>/dev/null && command -v jq >/dev/null 2>&1; then
            local count=$(jq -r '.result.tools | length' "$response_file" 2>/dev/null || echo "0")
            rm -f "$response_file"
            echo "$count"
        else
            rm -f "$response_file" 2>/dev/null
            echo "N/A"
        fi
    else
        echo "N/A"  # SSE tool counting not implemented yet
    fi
}

# Generate status symbols
get_status_symbol() {
    local status="$1"
    case "$status" in
        "HEALTHY") echo "🟢" ;;
        "DEGRADED") echo "🟡" ;;
        "DOWN") echo "🔴" ;;
        *) echo "⚪" ;;
    esac
}

get_transport_symbol() {
    local transport="$1"
    case "$transport" in
        "http") echo "🌐" ;;
        "sse") echo "⚡" ;;
        "stdio") echo "📟" ;;
        *) echo "❓" ;;
    esac
}

# Main monitoring function
monitor_server() {
    local server_config="$1"
    IFS='|' read -r server_name url transport auth environment <<< "$server_config"
    
    local status="DOWN"
    local response_time="0"
    local tool_count="N/A"
    local health_data
    
    # Check connectivity based on transport type
    if [[ "$transport" == "http" ]]; then
        health_data=$(check_http_health "$url" "$auth" 10)
        IFS='|' read -r http_code response_time <<< "$health_data"
        
        if [[ "$http_code" == "200" ]] || [[ "$http_code" == "405" ]]; then
            status="HEALTHY"
            tool_count=$(get_tool_count "$server_name" "$url" "$transport" "$auth")
        elif [[ "$http_code" == "401" ]]; then
            status="DEGRADED"  # Authentication issues
        else
            status="DOWN"
        fi
    elif [[ "$transport" == "sse" ]]; then
        health_data=$(check_sse_health "$url" "$auth" 5)
        IFS='|' read -r sse_status response_time <<< "$health_data"
        
        if [[ "$sse_status" == "200" ]]; then
            status="HEALTHY"
        else
            status="DOWN"
        fi
    fi
    
    # Format response time
    if command -v bc >/dev/null 2>&1 && [[ "$response_time" != "0" ]]; then
        response_time=$(echo "scale=3; $response_time * 1000" | bc)ms
    else
        response_time="N/A"
    fi
    
    echo "$server_name|$status|$response_time|$tool_count|$environment|$transport|$url"
}

# Generate dashboard
generate_dashboard() {
    local dashboard_file="$MONITOR_DIR/mcp_health_dashboard_${TIMESTAMP}.html"
    local csv_file="$MONITOR_DIR/mcp_health_status_${TIMESTAMP}.csv"
    
    # Create CSV header
    echo "Server Name,Status,Response Time,Tools,Environment,Transport,URL,Timestamp" > "$csv_file"
    
    # HTML Dashboard header
    cat > "$dashboard_file" << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>MCP Health Dashboard</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 20px; }
        .header { text-align: center; margin-bottom: 30px; }
        .status-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .server-card { border: 1px solid #ddd; border-radius: 8px; padding: 15px; }
        .server-card.healthy { border-left: 4px solid #28a745; }
        .server-card.degraded { border-left: 4px solid #ffc107; }
        .server-card.down { border-left: 4px solid #dc3545; }
        .server-name { font-weight: bold; font-size: 1.2em; margin-bottom: 10px; }
        .server-details { font-size: 0.9em; color: #666; }
        .status-badge { padding: 4px 8px; border-radius: 4px; color: white; font-size: 0.8em; }
        .status-healthy { background-color: #28a745; }
        .status-degraded { background-color: #ffc107; color: black; }
        .status-down { background-color: #dc3545; }
        .summary { background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 30px; }
        .summary-stats { display: flex; justify-content: space-around; text-align: center; }
        .stat { margin: 0 10px; }
        .stat-number { font-size: 2em; font-weight: bold; }
        .stat-label { color: #666; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🔍 MCP Health Dashboard</h1>
        <p>Real-time monitoring of all Model Context Protocol servers</p>
EOF
    
    echo "        <p>Last updated: $(date)</p>" >> "$dashboard_file"
    echo "    </div>" >> "$dashboard_file"
    
    # Collect server statuses
    local total_servers=0
    local healthy_servers=0
    local degraded_servers=0
    local down_servers=0
    local total_tools=0
    
    local server_data=()
    
    printf "${BLUE}🔍 Monitoring MCP Server Health...${NC}\n"
    
    for server_config in "${ALL_SERVERS[@]}"; do
        IFS='|' read -r server_name url transport auth environment <<< "$server_config"
        printf "${CYAN}Checking $server_name...${NC}\n"
        
        local result=$(monitor_server "$server_config")
        server_data+=("$result")
        
        IFS='|' read -r name status response_time tool_count env trans url <<< "$result"
        
        # Update counters
        ((total_servers++))
        case "$status" in
            "HEALTHY") ((healthy_servers++)) ;;
            "DEGRADED") ((degraded_servers++)) ;;
            "DOWN") ((down_servers++)) ;;
        esac
        
        if [[ "$tool_count" != "N/A" ]] && [[ "$tool_count" -gt 0 ]]; then
            total_tools=$((total_tools + tool_count))
        fi
        
        # Add to CSV
        echo "$name,$status,$response_time,$tool_count,$env,$trans,$url,$(date)" >> "$csv_file"
    done
    
    # Add summary to HTML
    cat >> "$dashboard_file" << EOF
    <div class="summary">
        <h2>📊 Summary</h2>
        <div class="summary-stats">
            <div class="stat">
                <div class="stat-number" style="color: #28a745;">$healthy_servers</div>
                <div class="stat-label">Healthy</div>
            </div>
            <div class="stat">
                <div class="stat-number" style="color: #ffc107;">$degraded_servers</div>
                <div class="stat-label">Degraded</div>
            </div>
            <div class="stat">
                <div class="stat-number" style="color: #dc3545;">$down_servers</div>
                <div class="stat-label">Down</div>
            </div>
            <div class="stat">
                <div class="stat-number" style="color: #007bff;">$total_tools</div>
                <div class="stat-label">Total Tools</div>
            </div>
        </div>
    </div>
    
    <div class="status-grid">
EOF
    
    # Add server cards
    for result in "${server_data[@]}"; do
        IFS='|' read -r name status response_time tool_count env trans url <<< "$result"
        
        local status_class=$(echo "$status" | tr '[:upper:]' '[:lower:]')
        local status_symbol=$(get_status_symbol "$status")
        local transport_symbol=$(get_transport_symbol "$trans")
        
        cat >> "$dashboard_file" << EOF
        <div class="server-card $status_class">
            <div class="server-name">$status_symbol $name</div>
            <div class="server-details">
                <span class="status-badge status-$status_class">$status</span><br><br>
                <strong>Transport:</strong> $transport_symbol $trans<br>
                <strong>Environment:</strong> $env<br>
                <strong>Response Time:</strong> $response_time<br>
                <strong>Tools:</strong> $tool_count<br>
                <strong>URL:</strong> <code>$(echo "$url" | cut -c1-50)$([ ${#url} -gt 50 ] && echo "...")</code>
            </div>
        </div>
EOF
    done
    
    cat >> "$dashboard_file" << 'EOF'
    </div>
    
    <footer style="margin-top: 40px; text-align: center; color: #666; font-size: 0.9em;">
        <p>Generated by MCP Health Monitor | Refresh this page for updated status</p>
    </footer>
</body>
</html>
EOF
    
    echo "$dashboard_file|$csv_file"
}

# Main execution
main() {
    printf "${PURPLE}🚀 MCP Health Monitor Starting...${NC}\n"
    printf "${BLUE}📊 Monitoring ${#ALL_SERVERS[@]} MCP servers${NC}\n"
    
    local files=$(generate_dashboard)
    IFS='|' read -r dashboard_file csv_file <<< "$files"
    
    printf "\n"
    printf "${GREEN}✅ Health monitoring complete!${NC}\n"
    printf "${BLUE}📄 Dashboard: %s${NC}\n" "$dashboard_file"
    printf "${BLUE}📊 CSV Data: %s${NC}\n" "$csv_file"
    
    # Try to open dashboard in browser if on macOS
    if [[ "$OSTYPE" == "darwin"* ]] && command -v open >/dev/null 2>&1; then
        printf "${CYAN}🌐 Opening dashboard in browser...${NC}\n"
        open "$dashboard_file"
    fi
}

# Check dependencies
if ! command -v curl >/dev/null 2>&1; then
    echo -e "${RED}❌ curl is required but not installed${NC}"
    exit 1
fi

# Run main function
main "$@"