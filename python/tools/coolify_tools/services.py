"""Coolify Services Management Tools."""

import os
import mcp.types as types
import requests
from utils.logger import setup_logger
from utils.error_handler import handle_requests_error, format_enhanced_error, get_resource_not_found_message
from .base import get_coolify_headers, get_coolify_base_url

# Set up logging
logger = setup_logger("coolify_services")

# Service Management Functions

async def list_coolify_services() -> list[types.TextContent]:
    """List all services in Coolify."""
    try:
        base_url = get_coolify_base_url()
        headers = get_coolify_headers()
        
        response = requests.get(f"{base_url}/services", headers=headers, timeout=30)
        response.raise_for_status()
        
        services = response.json()
        
        if not services:
            return [types.TextContent(type="text", text="✅ No services found in Coolify.")]
        
        result = f"🔧 **Coolify Services** ({len(services)} found)\n\n"
        
        for service in services:
            name = service.get('name', 'N/A')
            uuid = service.get('uuid', 'N/A')
            type_name = service.get('type', 'N/A')
            status = service.get('status', 'N/A')
            
            # Status emoji
            status_emoji = "✅" if status == "running" else "❌" if status == "stopped" else "⚠️"
            
            result += f"**{status_emoji} {name}** ({type_name})\n"
            result += f"   • UUID: `{uuid}`\n"
            result += f"   • Status: {status}\n"
            result += f"   • Actions: `coolify-get-service-by-uuid --service_uuid {uuid}`\n\n"
        
        result += f"💡 **Available Actions:**\n"
        result += f"• Get details: `coolify-get-service-by-uuid --service_uuid UUID`\n"
        result += f"• Create service: `coolify-create-service --name NAME --type TYPE`\n"
        result += f"• Start/Stop: `coolify-start-service` / `coolify-stop-service`\n"
        
        logger.info(f"Successfully listed {len(services)} services")
        return [types.TextContent(type="text", text=result)]
        
    except Exception as e:
        logger.error(f"Failed to list services: {e}")
        error_msg = handle_requests_error(e, "Unable to list services", "coolify-list-services")
        return [types.TextContent(type="text", text=error_msg)]

async def get_coolify_service_by_uuid(service_uuid: str) -> list[types.TextContent]:
    """Get detailed information about a specific service by UUID."""
    try:
        base_url = get_coolify_base_url()
        headers = get_coolify_headers()
        
        response = requests.get(f"{base_url}/services/{service_uuid}", headers=headers, timeout=30)
        response.raise_for_status()
        
        service_data = response.json()
        
        name = service_data.get('name', 'N/A')
        service_type = service_data.get('type', 'N/A')
        status = service_data.get('status', 'N/A')
        environment = service_data.get('environment', {}).get('name', 'N/A')
        server_name = service_data.get('destination', {}).get('name', 'N/A')
        
        result = f"""🔧 **Service Information:**
Name: {name}
UUID: {service_uuid}
Type: {service_type}
Status: {status}
Environment: {environment}
Server: {server_name}

🛠️ **Available Actions:**
• Start: `coolify-start-service --service_uuid {service_uuid}`
• Stop: `coolify-stop-service --service_uuid {service_uuid}`
• Restart: `coolify-restart-service --service_uuid {service_uuid}`
• Delete: `coolify-delete-service --service_uuid {service_uuid} --confirm true`
• Manage env vars: `coolify-manage-service-env --service_uuid {service_uuid} --action list`
"""
        
        logger.info(f"Successfully retrieved service info for {service_uuid}")
        return [types.TextContent(type="text", text=result)]
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            logger.error(f"Service {service_uuid} not found")
            error_msg = get_resource_not_found_message("service", service_uuid, "coolify-get-service-by-uuid")
            return [types.TextContent(type="text", text=error_msg)]
        else:
            logger.error(f"Failed to get service info for {service_uuid}: {e}")
            error_msg = handle_requests_error(e, f"Unable to retrieve service {service_uuid}", "coolify-get-service-by-uuid")
            return [types.TextContent(type="text", text=error_msg)]
    except Exception as e:
        logger.error(f"Failed to get service info for {service_uuid}: {e}")
        return [types.TextContent(type="text", text=f"❌ Failed to get service info: {str(e)}")]

async def create_coolify_service(name: str, type: str, project_uuid: str, server_uuid: str, 
                               description: str = None, environment_name: str = "production", 
                               docker_compose_raw: str = None, instant_deploy: bool = True) -> list[types.TextContent]:
    """Create a new service in Coolify."""
    try:
        base_url = get_coolify_base_url()
        headers = get_coolify_headers()
        
        # Build payload according to Coolify API specification
        payload = {
            "name": name,
            "type": type,
            "project_uuid": project_uuid,
            "server_uuid": server_uuid,
            "environment_name": environment_name,
            "instant_deploy": instant_deploy
        }
        
        if description:
            payload["description"] = description
        if docker_compose_raw:
            payload["docker_compose_raw"] = docker_compose_raw
        
        response = requests.post(f"{base_url}/services", headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        result_data = response.json()
        
        # Extract UUID and domains from response
        service_uuid = result_data.get('uuid', 'N/A')
        domains = result_data.get('domains', [])
        
        result = f"""✅ **Service Created Successfully!**

📋 **Service Details:**
Name: {name}
Type: {type}
Environment: {environment_name}
UUID: {service_uuid}
Project UUID: {project_uuid}
Server UUID: {server_uuid}
{f"Domains: {', '.join(domains)}" if domains else ""}

💡 **Next Steps:**
• Get service info: `coolify-get-service-by-uuid --service_uuid {service_uuid}`
• Start service: `coolify-start-service --service_uuid {service_uuid}`
• List all services: `coolify-list-services`
"""
        
        logger.info(f"Successfully created {type} service: {name}")
        return [types.TextContent(type="text", text=result)]
        
    except Exception as e:
        logger.error(f"Failed to create service {name}: {e}")
        error_msg = handle_requests_error(e, f"Unable to create {type} service '{name}'", "coolify-create-service")
        return [types.TextContent(type="text", text=error_msg)]

async def start_coolify_service(service_uuid: str) -> list[types.TextContent]:
    """Start a service in Coolify."""
    try:
        base_url = get_coolify_base_url()
        headers = get_coolify_headers()
        
        response = requests.get(f"{base_url}/services/{service_uuid}/start", headers=headers, timeout=30)
        response.raise_for_status()
        
        result = f"""✅ **Service Started Successfully!**

UUID: {service_uuid}

💡 **Next Steps:**
• Check status: `coolify-get-service-by-uuid --service_uuid {service_uuid}`
• View all services: `coolify-list-services`
"""
        
        logger.info(f"Successfully started service {service_uuid}")
        return [types.TextContent(type="text", text=result)]
        
    except Exception as e:
        logger.error(f"Failed to start service {service_uuid}: {e}")
        error_msg = handle_requests_error(e, f"Unable to start service {service_uuid}", "coolify-start-service")
        return [types.TextContent(type="text", text=error_msg)]

async def stop_coolify_service(service_uuid: str) -> list[types.TextContent]:
    """Stop a service in Coolify."""
    try:
        base_url = get_coolify_base_url()
        headers = get_coolify_headers()
        
        response = requests.get(f"{base_url}/services/{service_uuid}/stop", headers=headers, timeout=30)
        response.raise_for_status()
        
        result = f"""✅ **Service Stopped Successfully!**

UUID: {service_uuid}

💡 **Next Steps:**
• Check status: `coolify-get-service-by-uuid --service_uuid {service_uuid}`
• Start service: `coolify-start-service --service_uuid {service_uuid}`
"""
        
        logger.info(f"Successfully stopped service {service_uuid}")
        return [types.TextContent(type="text", text=result)]
        
    except Exception as e:
        logger.error(f"Failed to stop service {service_uuid}: {e}")
        error_msg = handle_requests_error(e, f"Unable to stop service {service_uuid}", "coolify-stop-service")
        return [types.TextContent(type="text", text=error_msg)]

async def restart_coolify_service(service_uuid: str) -> list[types.TextContent]:
    """Restart a service in Coolify."""
    try:
        base_url = get_coolify_base_url()
        headers = get_coolify_headers()
        
        response = requests.get(f"{base_url}/services/{service_uuid}/restart", headers=headers, timeout=30)
        response.raise_for_status()
        
        result = f"""✅ **Service Restarted Successfully!**

UUID: {service_uuid}

💡 **Next Steps:**
• Check status: `coolify-get-service-by-uuid --service_uuid {service_uuid}`
• View all services: `coolify-list-services`
"""
        
        logger.info(f"Successfully restarted service {service_uuid}")
        return [types.TextContent(type="text", text=result)]
        
    except Exception as e:
        logger.error(f"Failed to restart service {service_uuid}: {e}")
        error_msg = handle_requests_error(e, f"Unable to restart service {service_uuid}", "coolify-restart-service")
        return [types.TextContent(type="text", text=error_msg)]

async def delete_coolify_service(service_uuid: str, confirm: bool = False) -> list[types.TextContent]:
    """Delete a service in Coolify."""
    if not confirm:
        return [types.TextContent(type="text", text=f"⚠️ **Service deletion requires confirmation!**\n\nTo delete the service, use:\n`coolify-delete-service --service_uuid {service_uuid} --confirm true`\n\n❌ **Warning:** This action cannot be undone!")]
    
    try:
        base_url = get_coolify_base_url()
        headers = get_coolify_headers()
        
        response = requests.delete(f"{base_url}/services/{service_uuid}", headers=headers, timeout=30)
        response.raise_for_status()
        
        result = f"""✅ **Service Deleted Successfully!**

UUID: {service_uuid}

💡 **Next Steps:**
• View remaining services: `coolify-list-services`
"""
        
        logger.info(f"Successfully deleted service {service_uuid}")
        return [types.TextContent(type="text", text=result)]
        
    except Exception as e:
        logger.error(f"Failed to delete service {service_uuid}: {e}")
        error_msg = handle_requests_error(e, f"Unable to delete service {service_uuid}", "coolify-delete-service")
        return [types.TextContent(type="text", text=error_msg)]

async def manage_coolify_service_env(service_uuid: str, action: str, key: str = None, value: str = None) -> list[types.TextContent]:
    """Manage environment variables for a service in Coolify."""
    try:
        base_url = get_coolify_base_url()
        headers = get_coolify_headers()
        
        if action == "list":
            response = requests.get(f"{base_url}/services/{service_uuid}/envs", headers=headers, timeout=30)
            response.raise_for_status()
            
            env_vars = response.json()
            
            if not env_vars:
                return [types.TextContent(type="text", text=f"✅ No environment variables found for service {service_uuid}.")]
            
            result = f"🔧 **Service Environment Variables** ({len(env_vars)} found)\n\n"
            
            for env_var in env_vars:
                env_key = env_var.get('key', 'N/A')
                env_value = env_var.get('value', 'N/A')
                
                # Mask sensitive values
                if any(sensitive in env_key.lower() for sensitive in ['token', 'key', 'secret', 'password']):
                    env_value = '***MASKED***'
                
                result += f"**{env_key}:** {env_value}\n"
            
            result += f"\n💡 **Available Actions:**\n"
            result += f"• Create: `coolify-manage-service-env --service_uuid {service_uuid} --action create --key KEY --value VALUE`\n"
            result += f"• Update: `coolify-manage-service-env --service_uuid {service_uuid} --action update --key KEY --value VALUE`\n"
            result += f"• Delete: `coolify-manage-service-env --service_uuid {service_uuid} --action delete --key KEY`\n"
            
            return [types.TextContent(type="text", text=result)]
        
        elif action in ["create", "update"]:
            if not key or not value:
                return [types.TextContent(type="text", text="❌ Both 'key' and 'value' are required for create/update actions.")]
            
            payload = {"key": key, "value": value}
            
            if action == "create":
                response = requests.post(f"{base_url}/services/{service_uuid}/envs", headers=headers, json=payload, timeout=30)
            else:  # update
                response = requests.patch(f"{base_url}/services/{service_uuid}/envs", headers=headers, json=payload, timeout=30)
            
            response.raise_for_status()
            
            result = f"""✅ **Environment Variable {action.capitalize()}d Successfully!**

Service UUID: {service_uuid}
Key: {key}
Value: {'***MASKED***' if any(sensitive in key.lower() for sensitive in ['token', 'key', 'secret', 'password']) else value}

💡 **Next Steps:**
• List all vars: `coolify-manage-service-env --service_uuid {service_uuid} --action list`
"""
            
            logger.info(f"Successfully {action}d environment variable {key} for service {service_uuid}")
            return [types.TextContent(type="text", text=result)]
        
        elif action == "delete":
            if not key:
                return [types.TextContent(type="text", text="❌ 'key' is required for delete action.")]
            
            response = requests.delete(f"{base_url}/services/{service_uuid}/envs/{key}", headers=headers, timeout=30)
            response.raise_for_status()
            
            result = f"""✅ **Environment Variable Deleted Successfully!**

Service UUID: {service_uuid}
Deleted Key: {key}

💡 **Next Steps:**
• List remaining vars: `coolify-manage-service-env --service_uuid {service_uuid} --action list`
"""
            
            logger.info(f"Successfully deleted environment variable {key} for service {service_uuid}")
            return [types.TextContent(type="text", text=result)]
        
        else:
            return [types.TextContent(type="text", text="❌ Invalid action. Use: list, create, update, or delete.")]
            
    except Exception as e:
        logger.error(f"Failed to manage service environment variables for {service_uuid}: {e}")
        error_msg = handle_requests_error(e, f"Unable to {action} environment variables for service {service_uuid}", "coolify-manage-service-env")
        return [types.TextContent(type="text", text=error_msg)]

# Service Tools Registry
SERVICE_TOOLS = {
    "coolify-list-services": {
        "definition": types.Tool(
            name="coolify-list-services",
            description="List all services in Coolify.",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        ),
        "handler": list_coolify_services
    },
    
    "coolify-get-service-by-uuid": {
        "definition": types.Tool(
            name="coolify-get-service-by-uuid",
            description="Get detailed information about a specific service by UUID.",
            inputSchema={
                "type": "object",
                "required": ["service_uuid"],
                "properties": {
                    "service_uuid": {
                        "type": "string",
                        "description": "The UUID of the service to get information for"
                    }
                },
                "additionalProperties": False
            }
        ),
        "handler": get_coolify_service_by_uuid
    },
    
    "coolify-create-service": {
        "definition": types.Tool(
            name="coolify-create-service",
            description="Create a new service in Coolify from the 200+ available service templates.",
            inputSchema={
                "type": "object",
                "required": ["name", "type", "project_uuid", "server_uuid"],
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name for the service"
                    },
                    "type": {
                        "type": "string",
                        "description": "Type of service to create (e.g., 'wordpress', 'mysql', 'redis', 'nginx', etc.)"
                    },
                    "project_uuid": {
                        "type": "string",
                        "description": "UUID of the project to deploy to (required)"
                    },
                    "server_uuid": {
                        "type": "string",
                        "description": "UUID of the server to deploy on (required)"
                    },
                    "description": {
                        "type": "string",
                        "description": "Optional description for the service"
                    },
                    "environment_name": {
                        "type": "string",
                        "default": "production",
                        "description": "Environment name (default: production)"
                    },
                    "docker_compose_raw": {
                        "type": "string",
                        "description": "Raw Docker Compose configuration for custom services"
                    },
                    "instant_deploy": {
                        "type": "boolean",
                        "default": True,
                        "description": "Whether to deploy the service immediately after creation"
                    }
                },
                "additionalProperties": False
            }
        ),
        "handler": create_coolify_service
    },
    
    "coolify-start-service": {
        "definition": types.Tool(
            name="coolify-start-service",
            description="Start a service in Coolify.",
            inputSchema={
                "type": "object",
                "required": ["service_uuid"],
                "properties": {
                    "service_uuid": {
                        "type": "string",
                        "description": "The UUID of the service to start"
                    }
                },
                "additionalProperties": False
            }
        ),
        "handler": start_coolify_service
    },
    
    "coolify-stop-service": {
        "definition": types.Tool(
            name="coolify-stop-service",
            description="Stop a service in Coolify.",
            inputSchema={
                "type": "object",
                "required": ["service_uuid"],
                "properties": {
                    "service_uuid": {
                        "type": "string",
                        "description": "The UUID of the service to stop"
                    }
                },
                "additionalProperties": False
            }
        ),
        "handler": stop_coolify_service
    },
    
    "coolify-restart-service": {
        "definition": types.Tool(
            name="coolify-restart-service",
            description="Restart a service in Coolify.",
            inputSchema={
                "type": "object",
                "required": ["service_uuid"],
                "properties": {
                    "service_uuid": {
                        "type": "string",
                        "description": "The UUID of the service to restart"
                    }
                },
                "additionalProperties": False
            }
        ),
        "handler": restart_coolify_service
    },
    
    "coolify-delete-service": {
        "definition": types.Tool(
            name="coolify-delete-service",
            description="Delete a service in Coolify.",
            inputSchema={
                "type": "object",
                "required": ["service_uuid"],
                "properties": {
                    "service_uuid": {
                        "type": "string",
                        "description": "The UUID of the service to delete"
                    },
                    "confirm": {
                        "type": "boolean",
                        "default": False,
                        "description": "Confirmation that you want to delete the service"
                    }
                },
                "additionalProperties": False
            }
        ),
        "handler": delete_coolify_service
    },
    
    "coolify-manage-service-env": {
        "definition": types.Tool(
            name="coolify-manage-service-env",
            description="Manage environment variables for a service in Coolify.",
            inputSchema={
                "type": "object",
                "required": ["service_uuid", "action"],
                "properties": {
                    "service_uuid": {
                        "type": "string",
                        "description": "The UUID of the service"
                    },
                    "action": {
                        "type": "string",
                        "enum": ["list", "create", "update", "delete"],
                        "description": "Action to perform on environment variables"
                    },
                    "key": {
                        "type": "string",
                        "description": "Environment variable key (required for create/update/delete)"
                    },
                    "value": {
                        "type": "string",
                        "description": "Environment variable value (required for create/update)"
                    }
                },
                "additionalProperties": False
            }
        ),
        "handler": manage_coolify_service_env
    }
}