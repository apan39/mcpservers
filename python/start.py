#!/usr/bin/env python3
"""
Simple startup script for the MCP server.
"""
import os
import sys

if __name__ == "__main__":
    # Add current directory to path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    from mcp_server import main
    main()