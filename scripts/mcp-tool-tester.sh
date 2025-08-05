#!/bin/bash

# MCP Tool Tester
# Automated testing of specific tools across all working MCP servers

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Logging functions
log_info() { echo -e "${BLUE}🔧 $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
RESULTS_DIR="$ROOT_DIR/mcp-tool-testing-results"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

mkdir -p "$RESULTS_DIR"

# Working servers from validation results
WORKING_SERVERS=(
    "remote-python-tools|http://zs8sk0cgs4s8gsgwswsg88ko.135.181.149.150.sslip.io/mcp|http|Bearer 4446e3ca599152c85fc96ecebb0367674e823694e5197a0ed8ca1262e825075f"
    "remote-browser-use-mcp|http://w8wcwg48ok4go8g8swgwkgk8.135.181.149.150.sslip.io/mcp|http|Bearer 4446e3ca599152c85fc96ecebb0367674e823694e5197a0ed8ca1262e825075f"
    "python-local-http|http://localhost:3009/mcp|http|Bearer 4446e3ca599152c85fc96ecebb0367674e823694e5197a0ed8ca1262e825075f"
    "browser-use-local-http|http://localhost:3011/mcp|http|Bearer 4446e3ca599152c85fc96ecebb0367674e823694e5197a0ed8ca1262e825075f"
)

# Test specific tools with sample inputs
test_tool() {
    local server_name="$1"
    local url="$2"
    local auth="$3"
    local tool_name="$4"
    local tool_args="$5"
    
    log_info "Testing tool '$tool_name' on $server_name"
    
    local response_file="/tmp/${server_name}_${tool_name}_response.json"
    local json_payload="{\"jsonrpc\": \"2.0\", \"id\": 1, \"method\": \"tools/call\", \"params\": {\"name\": \"$tool_name\", \"arguments\": $tool_args}}"
    
    if curl -s -X POST "$url" \
        -H "Authorization: $auth" \
        -H "Content-Type: application/json" \
        -d "$json_payload" \
        --max-time 30 > "$response_file" 2>/dev/null; then
        
        if command -v jq >/dev/null 2>&1; then
            local error_check=$(jq -r '.error // empty' "$response_file" 2>/dev/null)
            if [[ -n "$error_check" ]]; then
                log_error "$tool_name failed: $(jq -r '.error.message' "$response_file" 2>/dev/null)"
                return 1
            else
                log_success "$tool_name executed successfully"
                # Save successful results
                cp "$response_file" "$RESULTS_DIR/${server_name}_${tool_name}_success_${TIMESTAMP}.json"
                return 0
            fi
        else
            if grep -q "error" "$response_file" 2>/dev/null; then
                log_error "$tool_name may have failed (no jq to verify)"
                return 1
            else
                log_success "$tool_name appears to have succeeded"
                cp "$response_file" "$RESULTS_DIR/${server_name}_${tool_name}_success_${TIMESTAMP}.json"
                return 0
            fi
        fi
    else
        log_error "$tool_name request failed"
        return 1
    fi
    
    rm -f "$response_file" 2>/dev/null
}

# Test suite for different tool categories
run_math_tools_test() {
    local server_name="$1"
    local url="$2"
    local auth="$3"
    
    log_info "=== Testing Math Tools on $server_name ==="
    
    # Test basic math operations
    test_tool "$server_name" "$url" "$auth" "add-numbers" '{"a": 5, "b": 3}'
    test_tool "$server_name" "$url" "$auth" "multiply-numbers" '{"a": 4, "b": 7}'
    test_tool "$server_name" "$url" "$auth" "calculate-percentage" '{"value": 100, "percentage": 15}'
}

run_text_tools_test() {
    local server_name="$1"
    local url="$2"
    local auth="$3"
    
    log_info "=== Testing Text Tools on $server_name ==="
    
    # Test text operations
    test_tool "$server_name" "$url" "$auth" "string-operations" '{"text": "Hello World", "operation": "uppercase"}'
    test_tool "$server_name" "$url" "$auth" "word-count" '{"text": "This is a sample text with multiple words"}'
    test_tool "$server_name" "$url" "$auth" "format-text" '{"text": "hello world test", "format_type": "title_case"}'
}

run_coolify_tools_test() {
    local server_name="$1"
    local url="$2" 
    local auth="$3"
    
    log_info "=== Testing Coolify Tools on $server_name ==="
    
    # Test safe Coolify operations (read-only)
    test_tool "$server_name" "$url" "$auth" "coolify-get-version" '{}'
    test_tool "$server_name" "$url" "$auth" "coolify-list-projects" '{}'
    test_tool "$server_name" "$url" "$auth" "coolify-list-servers" '{}'
    test_tool "$server_name" "$url" "$auth" "coolify-get-deployment-info" '{}'
}

run_browser_tools_test() {
    local server_name="$1"
    local url="$2"
    local auth="$3"
    
    log_info "=== Testing Browser Tools on $server_name ==="
    
    # Test browser session management (safe operations)
    test_tool "$server_name" "$url" "$auth" "create_browser_session" '{"session_id": "test-session-123", "headless": true}'
    
    # Clean up test session
    test_tool "$server_name" "$url" "$auth" "close_browser_session" '{"session_id": "test-session-123"}'
}

# Generate test report
generate_test_report() {
    local report_file="$RESULTS_DIR/mcp_tool_testing_report_${TIMESTAMP}.md"
    
    log_info "Generating tool testing report"
    
    cat > "$report_file" << EOF
# MCP Tool Testing Report
Generated: $(date)

## Test Overview
This report covers automated testing of tools across all working MCP servers.

## Servers Tested
EOF

    for server_config in "${WORKING_SERVERS[@]}"; do
        IFS='|' read -r server_name url transport auth <<< "$server_config"
        echo "- **$server_name**: $url" >> "$report_file"
    done
    
    cat >> "$report_file" << EOF

## Test Categories
- **Math Tools**: Basic arithmetic and calculations
- **Text Tools**: String manipulation and formatting  
- **Coolify Tools**: Infrastructure management (read-only tests)
- **Browser Tools**: Browser automation (session management)

## Test Results
Individual test results are saved as JSON files in the results directory.

## Files Generated
EOF
    
    if ls "$RESULTS_DIR"/*"$TIMESTAMP"* 1> /dev/null 2>&1; then
        for file in "$RESULTS_DIR"/*"$TIMESTAMP"*; do
            echo "- $(basename "$file")" >> "$report_file"
        done
    else
        echo "- No test result files generated" >> "$report_file"
    fi
    
    log_success "Test report generated: $report_file"
}

# Main test execution
main() {
    log_info "🚀 Starting MCP Tool Testing Suite"
    log_info "Testing $(echo ${#WORKING_SERVERS[@]}) working servers"
    
    local total_tests=0
    local successful_tests=0
    
    for server_config in "${WORKING_SERVERS[@]}"; do
        IFS='|' read -r server_name url transport auth <<< "$server_config"
        
        log_info "=== Testing Server: $server_name ==="
        
        # Determine which test suites to run based on server capabilities
        case "$server_name" in
            *python*)
                run_math_tools_test "$server_name" "$url" "$auth"
                run_text_tools_test "$server_name" "$url" "$auth"
                run_coolify_tools_test "$server_name" "$url" "$auth"
                total_tests=$((total_tests + 9))
                ;;
            *browser*)
                run_browser_tools_test "$server_name" "$url" "$auth"
                total_tests=$((total_tests + 2))
                ;;
            *)
                log_warning "Unknown server type: $server_name - skipping specific tests"
                ;;
        esac
        
        echo ""
    done
    
    # Count successful tests by looking at generated files
    if ls "$RESULTS_DIR"/*"success"*"$TIMESTAMP"* 1> /dev/null 2>&1; then
        successful_tests=$(ls "$RESULTS_DIR"/*"success"*"$TIMESTAMP"* | wc -l | tr -d ' ')
    fi
    
    generate_test_report
    
    log_info "=== TESTING SUMMARY ==="
    log_info "Total tests attempted: $total_tests"
    log_success "Successful tests: $successful_tests"
    
    if [[ $successful_tests -gt 0 ]]; then
        log_success "🎉 Tools are functioning across servers!"
    else
        log_warning "Some tool tests may have failed - check individual results"
    fi
    
    log_info "📊 Detailed results: $RESULTS_DIR"
}

# Check dependencies
if ! command -v curl >/dev/null 2>&1; then
    log_error "curl is required but not installed"
    exit 1
fi

if ! command -v jq >/dev/null 2>&1; then
    log_warning "jq not found - error detection will be limited"
fi

# Run main function
main "$@"