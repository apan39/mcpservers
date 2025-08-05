# MCP Bug Monitoring System

Automated monitoring system for tracking Claude Code MCP phantom server bugs.

## Bug Issues Being Monitored

- **Issue #1469**: "Phantom Servers Persisting in MCP Status After Removal"
- **Issue #3095**: "MCP Server Cache Not Refreshing After Rebuild"

## Setup

```bash
# One-time setup (already done)
./setup-cron.sh
```

This will:
- Install daily cron job (runs at 9 AM)
- Install required dependencies (`jq`)
- Test the monitoring script

## What It Does

- **Daily checks** GitHub issues for status changes
- **Updates documentation** (`MCP_SETUP.md`) with latest status
- **Logs activity** to `logs/mcp-bug-monitor.log`
- **Notifies** when issues are resolved (macOS notification)

## Manual Usage

```bash
# Run check immediately
./monitor-mcp-bug.sh

# View monitoring logs
tail -f ../logs/mcp-bug-monitor.log

# Check cron job status  
crontab -l | grep monitor-mcp-bug
```

## Monitoring Status

**Current Status**: Both issues are still **open** as of 2025-08-05
- Issue #1469: Last updated 2025-05-31, 0 comments
- Issue #3095: Last updated 2025-07-07, 0 comments

## When Issues Are Resolved

The script will automatically:
1. Update `MCP_SETUP.md` with resolution status
2. Add resolved date and closing information  
3. Send macOS notification
4. Continue monitoring until both are resolved

## Removal

To stop monitoring:
```bash
crontab -e
# Delete the line containing 'monitor-mcp-bug.sh'
```