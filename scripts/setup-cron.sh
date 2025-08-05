#!/bin/bash

# Setup daily cron job for MCP bug monitoring
# Run this script once to install the daily monitoring

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MONITOR_SCRIPT="$SCRIPT_DIR/monitor-mcp-bug.sh"

echo "Setting up daily MCP bug monitoring..."

# Check if jq is installed (required for JSON parsing)
if ! command -v jq &> /dev/null; then
    echo "Installing jq (required for JSON parsing)..."
    if command -v brew &> /dev/null; then
        brew install jq
    else
        echo "Please install jq manually: https://stedolan.github.io/jq/download/"
        exit 1
    fi
fi

# Add cron job (runs daily at 9 AM)
CRON_ENTRY="0 9 * * * $MONITOR_SCRIPT"

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "$MONITOR_SCRIPT"; then
    echo "Cron job already exists for MCP bug monitoring"
else
    # Add the cron job
    (crontab -l 2>/dev/null; echo "$CRON_ENTRY") | crontab -
    echo "✅ Daily cron job added: runs at 9 AM every day"
fi

# Test the script once
echo "Running initial check..."
"$MONITOR_SCRIPT"

echo ""
echo "Setup complete! The script will now:"
echo "  - Check GitHub issues daily at 9 AM"
echo "  - Update MCP_SETUP.md with latest status"
echo "  - Log all activity to logs/mcp-bug-monitor.log"
echo ""
echo "To view logs: tail -f $(dirname "$MONITOR_SCRIPT")/../logs/mcp-bug-monitor.log"
echo "To remove monitoring: crontab -e (then delete the line with $MONITOR_SCRIPT)"