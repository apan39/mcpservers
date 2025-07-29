"""Core Coolify API tools - version, projects, servers, and deployment info."""

import os
import mcp.types as types
import requests
from utils.logger import setup_logger
from utils.error_handler import handle_requests_error, format_enhanced_error
from .base import get_coolify_headers, get_coolify_base_url

# Set up logging
logger = setup_logger("coolify_core")

# Core Functions

async def get_coolify_version() -> list[types.TextContent]:
    """Get Coolify version information."""
    try:
        base_url = get_coolify_base_url()
        headers = get_coolify_headers()
        
        response = requests.get(f"{base_url}/version", headers=headers, timeout=30)
        response.raise_for_status()
        
        # Handle both JSON and plain text responses
        try:
            result = response.json()
        except:
            result = response.text.strip()
        
        logger.info("Successfully retrieved Coolify version")
        return [types.TextContent(type="text", text=f"Coolify Version: {result}")]
        
    except requests.RequestException as e:
        logger.error(f"Failed to get Coolify version: {e}")
        error_msg = handle_requests_error(e, "Unable to connect to Coolify API", "coolify-get-version")
        return [types.TextContent(type="text", text=error_msg)]
    except Exception as e:
        logger.error(f"Failed to get Coolify version: {e}")
        error_msg = format_enhanced_error(e, "Unexpected error while getting Coolify version", "coolify-get-version")
        return [types.TextContent(type="text", text=error_msg)]

async def list_coolify_projects() -> list[types.TextContent]:
    """List all projects in Coolify."""
    try:
        base_url = get_coolify_base_url()
        headers = get_coolify_headers()
        
        response = requests.get(f"{base_url}/projects", headers=headers, timeout=30)
        response.raise_for_status()
        
        projects = response.json()
        logger.info(f"Successfully retrieved {len(projects)} projects")
        
        if isinstance(projects, list):
            project_info = []
            for project in projects:
                name = project.get('name', 'N/A')
                uuid = project.get('uuid', 'N/A')
                description = project.get('description', 'No description')
                project_info.append(f"• {name} (UUID: {uuid}): {description}")
            
            result = "Projects:\n" + "\n".join(project_info)
        else:
            result = f"Projects: {projects}"
            
        return [types.TextContent(type="text", text=result)]
        
    except requests.RequestException as e:
        logger.error(f"Failed to list Coolify projects: {e}")
        error_msg = handle_requests_error(e, "Unable to retrieve projects from Coolify API", "coolify-list-projects")
        return [types.TextContent(type="text", text=error_msg)]
    except Exception as e:
        logger.error(f"Failed to list Coolify projects: {e}")
        error_msg = format_enhanced_error(e, "Unexpected error while listing projects", "coolify-list-projects")
        return [types.TextContent(type="text", text=error_msg)]

async def list_coolify_servers() -> list[types.TextContent]:
    """List all servers in Coolify."""
    try:
        base_url = get_coolify_base_url()
        headers = get_coolify_headers()
        
        response = requests.get(f"{base_url}/servers", headers=headers, timeout=30)
        response.raise_for_status()
        
        servers = response.json()
        logger.info(f"Successfully retrieved servers")
        
        if isinstance(servers, list):
            server_info = []
            for server in servers:
                name = server.get('name', 'N/A')
                ip = server.get('ip', 'N/A')
                uuid = server.get('uuid', 'N/A')
                is_reachable = server.get('is_reachable', False)
                is_usable = server.get('is_usable', False)
                status = "reachable+usable" if (is_reachable and is_usable) else "unavailable"
                server_info.append(f"• {name} ({ip}) - UUID: {uuid} - Status: {status}")
            
            result = "Servers:\n" + "\n".join(server_info)
            result += f"\n\n💡 Use UUID 'csgkk88okkgkwg8w0g8og8c8' for deployments (main server)"
        else:
            result = f"Servers: {servers}"
            
        return [types.TextContent(type="text", text=result)]
        
    except Exception as e:
        logger.error(f"Failed to list Coolify servers: {e}")
        return [types.TextContent(type="text", text=f"Error listing servers: {e}")]

async def get_deployment_info() -> list[types.TextContent]:
    """Get the correct server UUID and project information for deployments."""
    try:
        base_url = get_coolify_base_url()
        headers = get_coolify_headers()
        
        # Get projects and servers
        projects_response = requests.get(f"{base_url}/projects", headers=headers, timeout=30)
        servers_response = requests.get(f"{base_url}/servers", headers=headers, timeout=30)
        
        projects_response.raise_for_status()
        servers_response.raise_for_status()
        
        projects = projects_response.json()
        servers = servers_response.json()
        
        result = "🚀 Coolify Deployment Information\n\n"
        
        # Server info with correct UUID
        result += "📡 **Server Information**:\n"
        if isinstance(servers, list) and servers:
            main_server = servers[0]  # Usually the first/main server
            server_uuid = main_server.get('uuid', 'N/A')
            server_name = main_server.get('name', 'N/A')
            server_ip = main_server.get('ip', 'N/A')
            is_usable = main_server.get('is_usable', False)
            
            result += f"• Server UUID: `{server_uuid}` ✅\n"
            result += f"• Name: {server_name} ({server_ip})\n"
            result += f"• Status: {'✅ Usable' if is_usable else '❌ Not usable'}\n\n"
        
        # Project info
        result += "📁 **Available Projects**:\n"
        if isinstance(projects, list):
            for project in projects:
                name = project.get('name', 'N/A')
                uuid = project.get('uuid', 'N/A')
                description = project.get('description', 'No description')
                result += f"• **{name}** (UUID: `{uuid}`): {description}\n"
        
        result += "\n💡 **Usage:**\n"
        result += "• Create GitHub App: `coolify-create-github-app --project_uuid PROJECT_UUID --server_uuid SERVER_UUID --git_repository REPO_URL --name APP_NAME`\n"
        result += "• List applications: `coolify-list-applications`\n"
        result += "• Deploy app: `coolify-deploy-application --app_uuid APP_UUID`\n"
        
        logger.info("Successfully retrieved deployment information")
        return [types.TextContent(type="text", text=result)]
        
    except Exception as e:
        logger.error(f"Failed to get deployment info: {e}")
        error_msg = handle_requests_error(e, "Unable to retrieve deployment information", "coolify-get-deployment-info")
        return [types.TextContent(type="text", text=error_msg)]

# Core Tools Registry
CORE_TOOLS = {
    "coolify-get-version": {
        "definition": types.Tool(
            name="coolify-get-version",
            description="Get Coolify instance version information.",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        ),
        "handler": get_coolify_version
    },
    
    "coolify-list-projects": {
        "definition": types.Tool(
            name="coolify-list-projects",
            description="List all projects in Coolify.",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        ),
        "handler": list_coolify_projects
    },
    
    "coolify-list-servers": {
        "definition": types.Tool(
            name="coolify-list-servers",
            description="List all servers in Coolify.",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        ),
        "handler": list_coolify_servers
    },
    
    "coolify-get-deployment-info": {
        "definition": types.Tool(
            name="coolify-get-deployment-info",
            description="Get the correct server UUID and project information for deployments.",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        ),
        "handler": get_deployment_info
    }
}