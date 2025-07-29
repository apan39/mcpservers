"""Enhanced error handling with common solutions and troubleshooting guidance."""

import logging
import re
from typing import Dict, List, Tuple
import requests

def get_common_solutions() -> Dict[str, Dict]:
    """Return common error patterns and their solutions."""
    return {
        "connection_error": {
            "patterns": [
                r"Connection refused",
                r"Failed to establish a new connection",
                r"Name or service not known",
                r"No route to host",
                r"Connection timed out"
            ],
            "title": "🚫 **Connection Error**",
            "description": "Cannot connect to the service",
            "solutions": [
                "• Check if the service is running and accessible",
                "• Verify the URL/hostname is correct",
                "• Check your network connection",
                "• Ensure firewall/proxy settings allow the connection",
                "• Try accessing the service from a browser first"
            ],
            "debug_steps": [
                "• Test connectivity: `ping [hostname]`",
                "• Check service status: `curl -I [url]`",
                "• Verify DNS resolution: `nslookup [hostname]`"
            ]
        },
        
        "authentication_error": {
            "patterns": [
                r"401.*Unauthorized",
                r"403.*Forbidden",
                r"Invalid.*token",
                r"Authentication.*failed",
                r"API.*key.*invalid"
            ],
            "title": "🔐 **Authentication Error**",
            "description": "Authentication failed or insufficient permissions",
            "solutions": [
                "• Check if your API token/key is correct",
                "• Verify the token hasn't expired",
                "• Ensure proper authorization headers are set",
                "• Check if you have the required permissions",
                "• Regenerate API token if necessary"
            ],
            "debug_steps": [
                "• Verify environment variables: `echo $MCP_API_KEY`",
                "• Test authentication manually with curl",
                "• Check token format and length",
                "• Verify token permissions in service dashboard"
            ]
        },
        
        "coolify_api_error": {
            "patterns": [
                r"Coolify.*not.*found",
                r"Application.*not.*found",
                r"Project.*not.*found",
                r"Server.*not.*found",
                r"Deployment.*not.*found"
            ],
            "title": "🚀 **Coolify API Error**",
            "description": "Coolify resource not found or API issue",
            "solutions": [
                "• Verify the UUID/ID is correct and exists",
                "• Check if you have access to the resource",
                "• Ensure the resource hasn't been deleted",
                "• Try listing parent resources first (e.g., projects → applications)",
                "• Check Coolify dashboard to confirm resource exists"
            ],
            "debug_steps": [
                "• List projects: Use `coolify-list-projects`",
                "• List applications: Use `coolify-list-applications`",
                "• Check Coolify version: Use `coolify-get-version`",
                "• Verify base URL and API token configuration"
            ]
        },
        
        "json_decode_error": {
            "patterns": [
                r"JSON.*decode.*error",
                r"Expecting.*value",
                r"Invalid.*JSON",
                r"JSONDecodeError"
            ],
            "title": "📄 **JSON Parsing Error**",
            "description": "Invalid or malformed JSON response",
            "solutions": [
                "• The API returned non-JSON content",
                "• Check if the endpoint URL is correct",
                "• Verify the service is healthy and responding properly",
                "• Check if the service is returning HTML error pages",
                "• Ensure request headers are set correctly"
            ],
            "debug_steps": [
                "• Check raw response content",
                "• Verify Content-Type header in response",
                "• Test endpoint with curl to see raw output",
                "• Check service logs for errors"
            ]
        },
        
        "timeout_error": {
            "patterns": [
                r"Read.*timed.*out",
                r"Connection.*timeout",
                r"Request.*timeout",
                r"timeout.*exceeded"
            ],
            "title": "⏱️ **Timeout Error**",
            "description": "Operation took too long to complete",
            "solutions": [
                "• The service is slow or overloaded",
                "• Try increasing timeout if possible",
                "• Check if the service is experiencing high load",
                "• Break large operations into smaller chunks",
                "• Retry the operation after a short delay"
            ],
            "debug_steps": [
                "• Check service performance metrics",
                "• Monitor network latency",
                "• Try simpler operations first",
                "• Check service logs for performance issues"
            ]
        },
        
        "ssl_certificate_error": {
            "patterns": [
                r"SSL.*certificate.*verify.*failed",
                r"CERTIFICATE_VERIFY_FAILED",
                r"SSL.*handshake.*failed",
                r"certificate.*invalid"
            ],
            "title": "🔒 **SSL Certificate Error**",
            "description": "SSL/TLS certificate validation failed",
            "solutions": [
                "• Certificate may be expired or invalid",
                "• Try using HTTP instead of HTTPS for development",
                "• Check if certificate is self-signed",
                "• Verify system time is correct",
                "• Update certificate store if needed"
            ],
            "debug_steps": [
                "• Check certificate: `openssl s_client -connect [host:port]`",
                "• Verify certificate dates",
                "• Check if certificate matches hostname",
                "• Test with curl: `curl -k [url]` (insecure)"
            ]
        },
        
        "rate_limit_error": {
            "patterns": [
                r"429.*Too.*Many.*Requests",
                r"Rate.*limit.*exceeded",
                r"API.*rate.*limit"
            ],
            "title": "🚦 **Rate Limit Error**",
            "description": "API rate limit exceeded",
            "solutions": [
                "• Wait before retrying the request",
                "• Reduce request frequency",
                "• Check API rate limit documentation",
                "• Consider upgrading API plan if available",
                "• Batch multiple operations when possible"
            ],
            "debug_steps": [
                "• Check rate limit headers in response",
                "• Monitor request frequency",
                "• Check if multiple processes are making requests",
                "• Review API usage in service dashboard"
            ]
        },
        
        "web_scraping_error": {
            "patterns": [
                r"Failed.*to.*fetch",
                r"Page.*not.*found",
                r"404.*Not.*Found",
                r"Robot.*detection",
                r"Access.*denied"
            ],
            "title": "🌐 **Web Scraping Error**",
            "description": "Failed to scrape web content",
            "solutions": [
                "• Check if the URL is accessible in a browser",
                "• Website may be blocking automated requests",
                "• Try with different User-Agent headers",
                "• Check if website requires JavaScript",
                "• Verify URL format and spelling"
            ],
            "debug_steps": [
                "• Test URL manually in browser",
                "• Check robots.txt: `[url]/robots.txt`",
                "• Inspect page source for anti-bot measures",
                "• Try with different request headers"
            ]
        }
    }

def categorize_error(error_message: str) -> Tuple[str, Dict]:
    """Categorize error and return appropriate guidance."""
    error_str = str(error_message).lower()
    solutions = get_common_solutions()
    
    for category, info in solutions.items():
        for pattern in info["patterns"]:
            if re.search(pattern.lower(), error_str):
                return category, info
    
    # Default generic error handling
    return "generic", {
        "title": "❌ **Unexpected Error**",
        "description": "An unexpected error occurred",
        "solutions": [
            "• Check the error message for specific details",
            "• Ensure all required parameters are provided",
            "• Verify your configuration and credentials",
            "• Try the operation again after a short delay",
            "• Check service status and availability"
        ],
        "debug_steps": [
            "• Enable debug logging for more details",
            "• Check service documentation",
            "• Verify network connectivity",
            "• Review recent changes to configuration"
        ]
    }

def format_enhanced_error(error: Exception, context: str = "", tool_name: str = "") -> str:
    """Format an error with enhanced information and solutions."""
    error_category, error_info = categorize_error(str(error))
    
    result = f"{error_info['title']}\n\n"
    result += f"**Error Details:** {str(error)}\n\n"
    
    if context:
        result += f"**Context:** {context}\n\n"
    
    result += f"**Description:** {error_info['description']}\n\n"
    
    result += "**💡 Common Solutions:**\n"
    for solution in error_info['solutions']:
        result += f"{solution}\n"
    
    result += "\n**🔧 Debug Steps:**\n"
    for step in error_info['debug_steps']:
        result += f"{step}\n"
    
    if tool_name:
        result += f"\n**📖 Need Help?** Use `get-tool-info {tool_name}` for detailed usage information.\n"
    
    # Add context-specific help
    if "coolify" in tool_name.lower():
        result += "\n**🚀 Coolify Specific:**\n"
        result += "• Check COOLIFY_BASE_URL and COOLIFY_API_TOKEN in environment\n"
        result += "• Verify Coolify service is running and accessible\n"
        result += "• Use `coolify-get-version` to test basic connectivity\n"
    
    return result

def handle_requests_error(error: requests.RequestException, context: str = "", tool_name: str = "") -> str:
    """Handle requests-specific errors with enhanced information."""
    if isinstance(error, requests.exceptions.ConnectionError):
        return format_enhanced_error(error, f"Connection failed. {context}", tool_name)
    elif isinstance(error, requests.exceptions.Timeout):
        return format_enhanced_error(error, f"Request timed out. {context}", tool_name)
    elif isinstance(error, requests.exceptions.HTTPError):
        status_code = getattr(error.response, 'status_code', 'unknown')
        return format_enhanced_error(error, f"HTTP {status_code} error. {context}", tool_name)
    elif isinstance(error, requests.exceptions.SSLError):
        return format_enhanced_error(error, f"SSL certificate error. {context}", tool_name)
    else:
        return format_enhanced_error(error, context, tool_name)

def get_validation_error_message(missing_params: List[str], tool_name: str = "") -> str:
    """Generate user-friendly validation error message."""
    result = "📝 **Parameter Validation Error**\n\n"
    
    if len(missing_params) == 1:
        result += f"**Missing Required Parameter:** `{missing_params[0]}`\n\n"
    else:
        result += "**Missing Required Parameters:**\n"
        for param in missing_params:
            result += f"• `{param}`\n"
        result += "\n"
    
    result += "**💡 Solutions:**\n"
    result += "• Check the tool documentation for required parameters\n"
    result += "• Ensure all required fields are provided in your request\n"
    result += "• Verify parameter names are spelled correctly\n"
    result += "• Check parameter types match the expected format\n"
    
    if tool_name:
        result += f"\n**📖 Get Help:** Use `get-tool-info {tool_name}` for detailed parameter information and examples.\n"
    
    return result

def get_resource_not_found_message(resource_type: str, resource_id: str, tool_name: str = "") -> str:
    """Generate user-friendly resource not found message."""
    result = f"🔍 **{resource_type.title()} Not Found**\n\n"
    result += f"**Resource ID:** `{resource_id}`\n\n"
    
    result += "**💡 Common Causes:**\n"
    result += f"• The {resource_type} ID/UUID is incorrect or mistyped\n"
    result += f"• The {resource_type} has been deleted or moved\n"
    result += f"• You don't have permission to access this {resource_type}\n"
    result += f"• The {resource_type} belongs to a different project/organization\n\n"
    
    result += "**🔧 Troubleshooting Steps:**\n"
    
    if resource_type.lower() == "application":
        result += "• Use `coolify-list-applications` to see all available applications\n"
        result += "• Check if you're looking in the right project with `coolify-list-projects`\n"
        result += "• Verify the application UUID in the Coolify dashboard\n"
    elif resource_type.lower() == "project":
        result += "• Use `coolify-list-projects` to see all available projects\n"
        result += "• Check your access permissions in Coolify\n"
    elif resource_type.lower() == "server":
        result += "• Use `coolify-list-servers` to see all available servers\n"
        result += "• Verify the server is still active and accessible\n"
    elif resource_type.lower() == "deployment":
        result += "• Use `coolify-get-recent-deployments` to see recent deployments\n"
        result += "• Check if the deployment ID is from the correct application\n"
    
    result += "• Double-check the resource ID for typos\n"
    result += "• Confirm you have the necessary permissions\n"
    
    if tool_name:
        result += f"\n**📖 Need Help?** Use `get-tool-info {tool_name}` for detailed usage examples.\n"
    
    return result