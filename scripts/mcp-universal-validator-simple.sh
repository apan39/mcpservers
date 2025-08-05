#!/bin/bash

# MCP Universal Validator (Compatible Version)
# Comprehensive testing and validation for all MCP servers and tools

set -e

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

# MCP Server Definitions (name|url|transport|auth)
MCP_SERVERS=(
    "remote-python-tools|http://zs8sk0cgs4s8gsgwswsg88ko.135.181.149.150.sslip.io/mcp|http|Bearer 4446e3ca599152c85fc96ecebb0367674e823694e5197a0ed8ca1262e825075f"
    "remote-typescript-tools|http://zw0o84skskgc8kgooswgo8k4.135.181.149.150.sslip.io/mcp|http|Bearer 4446e3ca599152c85fc96ecebb0367674e823694e5197a0ed8ca1262e825075f"
    "remote-browser-use-mcp|http://w8wcwg48ok4go8g8swgwkgk8.135.181.149.150.sslip.io/mcp|http|Bearer 4446e3ca599152c85fc96ecebb0367674e823694e5197a0ed8ca1262e825075f"
    "python-local-http|http://localhost:3009/mcp|http|Bearer 4446e3ca599152c85fc96ecebb0367674e823694e5197a0ed8ca1262e825075f"
    "python-local-sse|http://localhost:3009/sse|sse|none"
    "typescript-local-sse|http://localhost:3010/sse|sse|none"
    "typescript-local-http|http://localhost:3010/mcp|http|Bearer 4446e3ca599152c85fc96ecebb0367674e823694e5197a0ed8ca1262e825075f"
    "browser-use-local-http|http://localhost:3011/mcp|http|Bearer 4446e3ca599152c85fc96ecebb0367674e823694e5197a0ed8ca1262e825075f"
    "browser-use-local-sse|http://localhost:3011/sse|sse|none"
)

# Test basic connectivity
test_connectivity() {
    local server_name="$1"
    local url="$2"
    local transport="$3"
    local auth="$4"
    
    log_info "Testing connectivity for $server_name ($transport)"
    
    if [[ "$transport" == "http" ]]; then
        if [[ "$auth" == "none" ]]; then
            response=$(curl -s -o /dev/null -w "%{http_code}" "$url" --max-time 10 2>/dev/null|| echo "000")
        else
            response=$(curl -s -o /dev/null -w "%{http_code}" -H "Authorization: $auth" "$url" --max-time 10 2>/dev/null || echo "000")
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
        if timeout 5 curl -N -H "Accept: text/event-stream" "$url" --max-time 3 2>/dev/null | grep -q "event: endpoint" 2>/dev/null; then
            log_success "$server_name SSE connectivity OK"
            return 0
        else
            log_error "$server_name SSE connectivity FAILED"  
            return 1
        fi
    fi
    
    return 1
}

# Manual tool testing for HTTP servers
test_tools_manual() {
    local server_name="$1"
    local url="$2"
    local transport="$3"
    local auth="$4"
    
    log_info "Testing tools for $server_name"
    
    if [[ "$transport" == "http" ]]; then
        local response_file="/tmp/${server_name}_response.json"
        
        # Test tools/list endpoint
        if [[ "$auth" == "none" ]]; then
            curl_cmd="curl -s -X POST '$url' -H 'Content-Type: application/json' -d '{\"jsonrpc\": \"2.0\", \"id\": 1, \"method\": \"tools/list\"}' --max-time 15"
        else
            curl_cmd="curl -s -X POST '$url' -H 'Authorization: $auth' -H 'Content-Type: application/json' -d '{\"jsonrpc\": \"2.0\", \"id\": 1, \"method\": \"tools/list\"}' --max-time 15"
        fi
        
        if eval "$curl_cmd" > "$response_file" 2>/dev/null; then
            if command -v jq >/dev/null 2>&1; then
                local tool_count=$(jq -r '.result.tools | length' "$response_file" 2>/dev/null || echo "0")
                if [[ "$tool_count" != "null" ]] && [[ "$tool_count" != "0" ]] && [[ "$tool_count" -gt 0 ]]; then
                    log_success "$server_name has $tool_count tools available"
                    cp "$response_file" "$RESULTS_DIR/${server_name}_tools_${TIMESTAMP}.json"
                    
                    # List first few tool names
                    local tool_names=$(jq -r '.result.tools[0:3] | .[].name' "$response_file" 2>/dev/null | tr '\n' ', ' | sed 's/,$//')
                    log_info "Sample tools: $tool_names"
                else
                    log_warning "$server_name responded but no tools found"
                fi
            else
                # Without jq, just check if response contains "tools"
                if grep -q "tools" "$response_file" 2>/dev/null; then
                    log_success "$server_name responded with tools data"
                    cp "$response_file" "$RESULTS_DIR/${server_name}_tools_${TIMESTAMP}.json"
                else
                    log_warning "$server_name responded but format unclear (no jq)"
                fi
            fi
        else
            log_error "$server_name tool test failed"
        fi
        
        rm -f "$response_file"
    elif [[ "$transport" == "sse" ]]; then
        log_warning "$server_name SSE tool testing requires Inspector (skipping for now)"
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

## Servers Tested
EOF

    for server_config in "${MCP_SERVERS[@]}"; do
        IFS='|' read -r server_name url transport auth <<< "$server_config"
        echo "- **$server_name**: $url ($transport)" >> "$report_file"
    done
    
    cat >> "$report_file" << EOF

## Test Results
Individual test results and tool inventories are saved as separate files in the results directory.

## Files Generated
EOF
    
    # List all generated files
    if ls "$RESULTS_DIR"/*"$TIMESTAMP"* 1> /dev/null 2>&1; then
        for file in "$RESULTS_DIR"/*"$TIMESTAMP"*; do
            echo "- $(basename "$file")" >> "$report_file"
        done
    else
        echo "- No additional files generated" >> "$report_file"
    fi
    
    log_success "Report generated: $report_file"
}

# Main execution
main() {
    log_info "🚀 Starting MCP Universal Validation"
    log_info "Results will be saved to: $RESULTS_DIR"
    
    local total_servers=${#MCP_SERVERS[@]}
    local successful_connections=0
    local successful_tool_tests=0
    
    echo "Server Name,URL,Transport,Auth,Connectivity,Tools,Notes" > "$RESULTS_DIR/mcp_summary_${TIMESTAMP}.csv"
    
    for server_config in "${MCP_SERVERS[@]}"; do
        # Parse server configuration
        IFS='|' read -r server_name url transport auth <<< "$server_config"
        
        log_info "=== Testing $server_name ==="
        
        # Test connectivity
        connectivity_status="FAILED"
        tools_status="SKIPPED"
        notes=""
        
        if test_connectivity "$server_name" "$url" "$transport" "$auth"; then
            connectivity_status="SUCCESS"
            ((successful_connections++))
            
            # Test tools if connectivity works
            test_tools_manual "$server_name" "$url" "$transport" "$auth"
            tools_status="TESTED"
            ((successful_tool_tests++))
        else
            notes="Connection failed"
        fi
        
        echo "$server_name,$url,$transport,$auth,$connectivity_status,$tools_status,$notes" >> "$RESULTS_DIR/mcp_summary_${TIMESTAMP}.csv"
        echo ""
    done
    
    # Generate final report
    generate_report
    
    # Summary
    log_info "=== VALIDATION SUMMARY ==="
    log_info "Total servers tested: $total_servers"
    log_success "Successful connections: $successful_connections"
    log_success "Tool tests completed: $successful_tool_tests"
    
    if [[ $successful_connections -eq $total_servers ]]; then
        log_success "🎉 ALL SERVERS ACCESSIBLE!"
    else
        log_warning "Some servers are not accessible - check individual results"
    fi
    
    log_info "📊 Detailed results saved to: $RESULTS_DIR"
    log_info "📋 Summary CSV: $RESULTS_DIR/mcp_summary_${TIMESTAMP}.csv"
    log_info "📄 Full report: $RESULTS_DIR/mcp_validation_report_${TIMESTAMP}.md"
}

# Check for required tools
if ! command -v curl >/dev/null 2>&1; then
    log_error "curl is required but not installed"
    exit 1
fi

if ! command -v jq >/dev/null 2>&1; then
    log_warning "jq not found - JSON parsing will be limited (install with: brew install jq)"
fi

# Run main function
main "$@"