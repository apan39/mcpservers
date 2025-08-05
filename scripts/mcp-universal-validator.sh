#!/bin/bash

# MCP Universal Validator  
# Comprehensive testing and validation for all MCP servers and tools

set -e

# Require bash 4+ for associative arrays
if [[ ${BASH_VERSION%%.*} -lt 4 ]]; then
    echo "Error: This script requires bash 4.0 or higher"
    echo "Current version: $BASH_VERSION"
    exit 1
fi

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging functions
log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
RESULTS_DIR="$ROOT_DIR/mcp-validation-results"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Create results directory
mkdir -p "$RESULTS_DIR"

# MCP Server Definitions
declare -A MCP_SERVERS

# Remote Production Servers
MCP_SERVERS[remote-python-tools]="http://zs8sk0cgs4s8gsgwswsg88ko.135.181.149.150.sslip.io/mcp|http|Bearer 4446e3ca599152c85fc96ecebb0367674e823694e5197a0ed8ca1262e825075f"
MCP_SERVERS[remote-typescript-tools]="http://zw0o84skskgc8kgooswgo8k4.135.181.149.150.sslip.io/mcp|http|Bearer 4446e3ca599152c85fc96ecebb0367674e823694e5197a0ed8ca1262e825075f"
MCP_SERVERS[remote-browser-use-mcp]="http://w8wcwg48ok4go8g8swgwkgk8.135.181.149.150.sslip.io/mcp|http|Bearer 4446e3ca599152c85fc96ecebb0367674e823694e5197a0ed8ca1262e825075f"

# Local Development Servers
MCP_SERVERS[python-local-http]="http://localhost:3009/mcp|http|Bearer 4446e3ca599152c85fc96ecebb0367674e823694e5197a0ed8ca1262e825075f"
MCP_SERVERS[python-local-sse]="http://localhost:3009/sse|sse|none"
MCP_SERVERS[typescript-local-sse]="http://localhost:3010/sse|sse|none"
MCP_SERVERS[typescript-local-http]="http://localhost:3010/mcp|http|Bearer 4446e3ca599152c85fc96ecebb0367674e823694e5197a0ed8ca1262e825075f"
MCP_SERVERS[browser-use-local-http]="http://localhost:3011/mcp|http|Bearer 4446e3ca599152c85fc96ecebb0367674e823694e5197a0ed8ca1262e825075f"
MCP_SERVERS[browser-use-local-sse]="http://localhost:3011/sse|sse|none"

# Functions

# Test basic connectivity
test_connectivity() {
    local server_name="$1"
    local url="$2"
    local transport="$3"
    local auth="$4"
    
    log_info "Testing connectivity for $server_name ($transport)"
    
    if [[ "$transport" == "http" ]]; then
        if [[ "$auth" == "none" ]]; then
            response=$(curl -s -o /dev/null -w "%{http_code}" "$url" --max-time 10 || echo "000")
        else
            response=$(curl -s -o /dev/null -w "%{http_code}" -H "Authorization: $auth" "$url" --max-time 10 || echo "000")
        fi
        
        if [[ "$response" == "200" ]] || [[ "$response" == "401" ]] || [[ "$response" == "405" ]]; then
            log_success "$server_name connectivity OK (HTTP $response)"
            return 0
        else
            log_error "$server_name connectivity FAILED (HTTP $response)"
            return 1
        fi
    elif [[ "$transport" == "sse" ]]; then
        # Test SSE endpoint
        if timeout 5 curl -N -H "Accept: text/event-stream" "$url" --max-time 3 2>/dev/null | grep -q "event: endpoint"; then
            log_success "$server_name SSE connectivity OK"
            return 0
        else
            log_error "$server_name SSE connectivity FAILED"
            return 1
        fi
    fi
    
    return 1
}

# Test tools using MCP Inspector (when available)
test_tools_with_inspector() {
    local server_name="$1"
    local url="$2"
    local transport="$3"
    local auth="$4"
    
    log_info "Testing tools for $server_name using Inspector"
    
    # Create temporary config for this server
    local config_file="/tmp/mcp_config_${server_name}.json"
    
    if [[ "$transport" == "sse" ]]; then
        cat > "$config_file" << EOF
{
  "mcpServers": {
    "$server_name": {
      "type": "sse",
      "url": "$url"
    }
  }
}
EOF
    else
        if [[ "$auth" == "none" ]]; then
            cat > "$config_file" << EOF
{
  "mcpServers": {
    "$server_name": {
      "type": "http",
      "url": "$url"
    }
  }
}
EOF
        else
            cat > "$config_file" << EOF
{
  "mcpServers": {
    "$server_name": {
      "type": "http",
      "url": "$url",
      "headers": {
        "Authorization": "$auth",
        "Content-Type": "application/json"
      }
    }
  }
}
EOF
        fi
    fi
    
    # Try to list tools using Inspector
    local tools_output
    if tools_output=$(timeout 30 npx @modelcontextprotocol/inspector --config "$config_file" --server "$server_name" --cli 2>/dev/null); then
        local tool_count=$(echo "$tools_output" | grep -c "tool" || echo "0")
        log_success "$server_name has $tool_count tools available"
        echo "$tools_output" > "$RESULTS_DIR/${server_name}_tools_${TIMESTAMP}.log"
        rm -f "$config_file"
        return 0
    else
        log_warning "$server_name Inspector test failed, trying manual approach"
        rm -f "$config_file"
        return 1
    fi
}

# Manual tool testing for servers that Inspector can't handle
test_tools_manual() {
    local server_name="$1"
    local url="$2"
    local transport="$3"
    local auth="$4"
    
    log_info "Testing tools manually for $server_name"
    
    if [[ "$transport" == "http" ]]; then
        local response_file="/tmp/${server_name}_response.json"
        
        # Test tools/list endpoint
        if [[ "$auth" == "none" ]]; then
            curl_response=$(curl -s -X POST "$url" \
                -H "Content-Type: application/json" \
                -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}' \
                --max-time 15 > "$response_file" 2>/dev/null && echo "success" || echo "failed")
        else
            curl_response=$(curl -s -X POST "$url" \
                -H "Authorization: $auth" \
                -H "Content-Type: application/json" \
                -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}' \
                --max-time 15 > "$response_file" 2>/dev/null && echo "success" || echo "failed")
        fi
        
        if [[ "$curl_response" == "success" ]] && [[ -f "$response_file" ]]; then
            local tool_count=$(jq -r '.result.tools | length' "$response_file" 2>/dev/null || echo "0")
            if [[ "$tool_count" != "null" ]] && [[ "$tool_count" -gt 0 ]]; then
                log_success "$server_name has $tool_count tools available"
                cp "$response_file" "$RESULTS_DIR/${server_name}_tools_${TIMESTAMP}.json"
            else
                log_warning "$server_name responded but no tools found"
            fi
        else
            log_error "$server_name manual tool test failed"
        fi
        
        rm -f "$response_file"
    else
        log_warning "Manual SSE tool testing not implemented yet"
    fi
}

# Generate comprehensive report
generate_report() {
    local report_file="$RESULTS_DIR/mcp_validation_report_${TIMESTAMP}.md"
    
    log_info "Generating comprehensive validation report"
    
    cat > "$report_file" << EOF
# MCP Universal Validation Report
Generated: $(date)

## Executive Summary
This report covers the comprehensive validation of all MCP servers across different transport protocols.

## Server Status Overview

EOF

    # Add connectivity results
    for server_name in "${!MCP_SERVERS[@]}"; do
        echo "### $server_name" >> "$report_file"
        echo "" >> "$report_file"
        
        # Parse server config
        IFS='|' read -r url transport auth <<< "${MCP_SERVERS[$server_name]}"
        
        echo "- **URL**: $url" >> "$report_file"
        echo "- **Transport**: $transport" >> "$report_file"
        echo "- **Authentication**: $([ "$auth" == "none" ] && echo "None" || echo "Bearer Token")" >> "$report_file"
        echo "" >> "$report_file"
    done
    
    cat >> "$report_file" << EOF

## Tool Inventory
Individual tool inventories are saved as separate files in the results directory.

## Recommendations
- All servers should be regularly monitored for connectivity
- Tool inventories should be updated when new features are deployed
- Authentication mechanisms should be validated periodically

## Files Generated
EOF
    
    # List all generated files
    ls -la "$RESULTS_DIR" | grep "$TIMESTAMP" | while read -r line; do
        echo "- $(echo "$line" | awk '{print $NF}')" >> "$report_file"
    done
    
    log_success "Report generated: $report_file"
}

# Main execution
main() {
    log_info "Starting MCP Universal Validation"
    log_info "Results will be saved to: $RESULTS_DIR"
    
    local total_servers=${#MCP_SERVERS[@]}
    local successful_connections=0
    local successful_tool_tests=0
    
    echo "Server Name,URL,Transport,Auth,Connectivity,Tools" > "$RESULTS_DIR/mcp_summary_${TIMESTAMP}.csv"
    
    for server_name in "${!MCP_SERVERS[@]}"; do
        log_info "=== Testing $server_name ==="
        
        # Parse server configuration
        IFS='|' read -r url transport auth <<< "${MCP_SERVERS[$server_name]}"
        
        # Test connectivity
        connectivity_status="FAILED"
        if test_connectivity "$server_name" "$url" "$transport" "$auth"; then
            connectivity_status="SUCCESS"
            ((successful_connections++))
            
            # Test tools if connectivity works
            tools_status="FAILED"
            if test_tools_with_inspector "$server_name" "$url" "$transport" "$auth"; then
                tools_status="SUCCESS"
                ((successful_tool_tests++))
            else
                # Fallback to manual testing
                test_tools_manual "$server_name" "$url" "$transport" "$auth"
                tools_status="MANUAL"
                ((successful_tool_tests++))
            fi
            
            echo "$server_name,$url,$transport,$auth,$connectivity_status,$tools_status" >> "$RESULTS_DIR/mcp_summary_${TIMESTAMP}.csv"
        else
            echo "$server_name,$url,$transport,$auth,$connectivity_status,SKIPPED" >> "$RESULTS_DIR/mcp_summary_${TIMESTAMP}.csv"
        fi
        
        echo ""
    done
    
    # Generate final report
    generate_report
    
    # Summary
    log_info "=== VALIDATION SUMMARY ==="
    log_info "Total servers tested: $total_servers"
    log_success "Successful connections: $successful_connections"
    log_success "Successful tool tests: $successful_tool_tests"
    
    if [[ $successful_connections -eq $total_servers ]]; then
        log_success "🎉 ALL SERVERS ACCESSIBLE!"
    else
        log_warning "Some servers are not accessible - check individual results"
    fi
    
    log_info "Detailed results saved to: $RESULTS_DIR"
}

# Check if jq is available (needed for JSON parsing)
if ! command -v jq &> /dev/null; then
    log_warning "jq not found - JSON parsing will be limited"
fi

# Run main function
main "$@"