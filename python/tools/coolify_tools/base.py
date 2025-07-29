"""Common utilities for Coolify API tools."""

import os
from utils.logger import setup_logger
from utils.error_handler import handle_requests_error, format_enhanced_error

# Set up logging
logger = setup_logger("coolify_tools")

def get_coolify_headers():
    """Get headers for Coolify API requests."""
    api_token = os.getenv('COOLIFY_API_TOKEN')
    if not api_token:
        raise ValueError("COOLIFY_API_TOKEN environment variable not set")
    
    return {
        'Authorization': f'Bearer {api_token}',
        'Content-Type': 'application/json'
    }

def get_coolify_base_url():
    """Get the base URL for Coolify API."""
    base_url = os.getenv('COOLIFY_BASE_URL')
    if not base_url:
        raise ValueError("COOLIFY_BASE_URL environment variable not set")
    
    return f"{base_url.rstrip('/')}/api/v1"