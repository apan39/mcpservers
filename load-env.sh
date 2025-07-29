#!/bin/bash
# Quick script to load environment variables in current shell
# Usage: source load-env.sh

if [ -f .env ]; then
    set -a
    source .env
    set +a
    echo "✅ Environment variables loaded from .env"
    echo "MCP_API_KEY: ${MCP_API_KEY:0:10}..."
else
    echo "❌ .env file not found"
fi