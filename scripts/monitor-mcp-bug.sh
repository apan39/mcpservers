#!/bin/bash

# MCP Phantom Servers Bug Monitor
# Checks GitHub issues for updates on phantom server bug
# Run daily via cron: 0 9 * * * /path/to/monitor-mcp-bug.sh

set -e

LOG_FILE="$(dirname "$0")/../logs/mcp-bug-monitor.log"
DOCS_FILE="$(dirname "$0")/../MCP_SETUP.md"
ISSUE_1469="https://api.github.com/repos/anthropics/claude-code/issues/1469"
ISSUE_3095="https://api.github.com/repos/anthropics/claude-code/issues/3095"

# Create logs directory if it doesn't exist
mkdir -p "$(dirname "$LOG_FILE")"

# Function to log messages
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Function to check issue status
check_issue() {
    local issue_url="$1"
    local issue_number="$2"
    
    log "Checking issue #$issue_number..."
    
    # Get issue data from GitHub API
    local response=$(curl -s "$issue_url" || echo '{"state": "error"}')
    local state=$(echo "$response" | jq -r '.state // "error"')
    local updated_at=$(echo "$response" | jq -r '.updated_at // "unknown"')
    local comments=$(echo "$response" | jq -r '.comments // 0')
    
    if [ "$state" = "error" ]; then
        log "  ERROR: Failed to fetch issue #$issue_number"
        return 1
    fi
    
    log "  Issue #$issue_number status: $state"
    log "  Last updated: $updated_at"
    log "  Comments: $comments"
    
    # Check if issue is closed (resolved)
    if [ "$state" = "closed" ]; then
        log "  🎉 RESOLVED: Issue #$issue_number has been closed!"
        
        # Update documentation
        local current_date=$(date '+%Y-%m-%d')
        if grep -q "Last checked:" "$DOCS_FILE"; then
            sed -i '' "s/Last checked: [0-9-]*/Last checked: $current_date/" "$DOCS_FILE"
            sed -i '' "/### Current Status/a\\
- **✅ RESOLVED**: Issue #$issue_number was closed on $updated_at
" "$DOCS_FILE"
        fi
        
        return 0
    fi
    
    # Get recent comments to check for updates
    local comments_url=$(echo "$response" | jq -r '.comments_url // ""')
    if [ -n "$comments_url" ] && [ "$comments_url" != "null" ]; then
        local recent_comments=$(curl -s "$comments_url?since=$(date -d '1 day ago' '+%Y-%m-%dT%H:%M:%SZ' 2>/dev/null || date -v-1d '+%Y-%m-%dT%H:%M:%SZ')" || echo '[]')
        local new_comments=$(echo "$recent_comments" | jq -r 'length')
        
        if [ "$new_comments" -gt 0 ]; then
            log "  📝 NEW: $new_comments new comment(s) in the last 24 hours"
            
            # Extract latest comment for summary
            local latest_comment=$(echo "$recent_comments" | jq -r '.[0].body // ""' | head -c 200)
            if [ -n "$latest_comment" ]; then
                log "  Latest comment preview: ${latest_comment}..."
            fi
        fi
    fi
    
    return 1  # Still open
}

# Main monitoring logic
main() {
    log "Starting MCP phantom servers bug monitoring..."
    
    local resolved_count=0
    
    # Check both issues
    if check_issue "$ISSUE_1469" "1469"; then
        ((resolved_count++))
    fi
    
    if check_issue "$ISSUE_3095" "3095"; then
        ((resolved_count++))
    fi
    
    # Update last checked date in documentation
    local current_date=$(date '+%Y-%m-%d')
    if grep -q "Last checked:" "$DOCS_FILE"; then
        sed -i '' "s/Last checked: [0-9-]*/Last checked: $current_date/" "$DOCS_FILE"
        log "Updated documentation with last checked date: $current_date"
    fi
    
    if [ $resolved_count -eq 2 ]; then
        log "🎉 ALL ISSUES RESOLVED! Both phantom server bugs have been fixed."
        
        # Notify user (you can customize this)
        echo "MCP phantom server bugs have been resolved! Check the GitHub issues for details." | \
            osascript -e 'display notification with title "MCP Bug Monitor"' 2>/dev/null || true
    elif [ $resolved_count -eq 1 ]; then
        log "✅ One issue resolved, one still open"
    else
        log "📋 Both issues still open - monitoring continues"
    fi
    
    log "Monitoring complete"
}

# Run main function
main "$@"