"""Environment variable management tools for Coolify API."""

import requests
import mcp.types as types
from .base import get_coolify_headers, get_coolify_base_url, logger
from utils.error_handler import handle_requests_error, format_enhanced_error

async def make_request_with_retry(method, url, headers, json=None, retries=2):
    """Make HTTP request with retry logic."""
    for attempt in range(retries + 1):
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=headers, json=json, timeout=30)
            elif method.upper() == 'PUT':
                response = requests.put(url, headers=headers, json=json, timeout=30)
            elif method.upper() == 'PATCH':
                response = requests.patch(url, headers=headers, json=json, timeout=30)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            if attempt == retries:
                raise e
            logger.warning(f"Request attempt {attempt + 1} failed, retrying...")
    
async def set_env_variable(app_uuid: str, key: str, value: str, is_preview: bool = False) -> list[types.TextContent]:
    """Add or update an environment variable for an application."""
    try:
        base_url = get_coolify_base_url()
        headers = get_coolify_headers()
        
        # First, check if the variable already exists
        try:
            env_response = await make_request_with_retry('GET', f"{base_url}/applications/{app_uuid}/envs", headers)
            existing_vars = env_response.json()
            
            # Find existing variable
            existing_var = None
            if isinstance(existing_vars, list):
                for env_var in existing_vars:
                    if env_var.get('key') == key and env_var.get('is_preview', False) == is_preview:
                        existing_var = env_var
                        break
            
            if existing_var:
                # Update existing variable using PATCH
                env_data = {
                    "key": key,
                    "value": value,
                    "is_preview": is_preview,
                    "is_build_time": existing_var.get('is_build_time', False),
                    "is_literal": existing_var.get('is_literal', False)
                }
                
                response = await make_request_with_retry(
                    'PATCH', f"{base_url}/applications/{app_uuid}/envs", headers, json=env_data
                )
            else:
                # Create new variable using POST
                env_data = {
                    "key": key,
                    "value": value,
                    "is_preview": is_preview,
                    "is_build_time": False,  # Default to runtime variable
                    "is_literal": False
                }
                
                response = await make_request_with_retry(
                    'POST', f"{base_url}/applications/{app_uuid}/envs", headers, json=env_data
                )
                
        except Exception as check_error:
            # If we can't check existing variables, try to create new one
            logger.warning(f"Could not check existing variables, attempting to create: {check_error}")
            env_data = {
                "key": key,
                "value": value,
                "is_preview": is_preview,  
                "is_build_time": False,
                "is_literal": False
            }
            
            response = await make_request_with_retry(
                'POST', f"{base_url}/applications/{app_uuid}/envs", headers, json=env_data
            )
        
        env_type = "Preview" if is_preview else "Production"
        # Mask sensitive values in output
        display_value = "***MASKED***" if any(sensitive in key.lower() for sensitive in ['token', 'key', 'secret', 'password', 'api']) else value[:50] + ("..." if len(value) > 50 else "")
        
        result = f"✅ Environment variable **{key}** set successfully!\n\n"
        result += f"**Variable Details:**\n"
        result += f"• Key: {key}\n"
        result += f"• Value: {display_value}\n"
        result += f"• Environment: {env_type}\n"
        result += f"• Type: Runtime variable\n\n"
        result += f"💡 **Next Steps:**\n"
        result += f"• Restart application to apply changes: `coolify-restart-application`\n"
        result += f"• Verify with: `coolify-get-application-info`\n"
        
        logger.info(f"Successfully set environment variable {key} for application {app_uuid}")
        return [types.TextContent(type="text", text=result)]
        
    except Exception as e:
        logger.error(f"Failed to set environment variable {key} for {app_uuid}: {e}")
        return [types.TextContent(type="text", text=f"❌ Failed to set environment variable: {str(e)}\n\n💡 **Troubleshooting:**\n• Verify application UUID is correct\n• Check if variable name is valid\n• Ensure sufficient permissions")]

async def delete_env_variable(app_uuid: str, key: str, is_preview: bool = False) -> list[types.TextContent]:
    """Remove an environment variable from an application."""
    try:
        base_url = get_coolify_base_url()
        headers = get_coolify_headers()
        
        # First, get all environment variables to find the one to delete
        env_response = await make_request_with_retry('GET', f"{base_url}/applications/{app_uuid}/envs", headers)
        env_vars = env_response.json()
        
        # Find the environment variable to delete
        env_to_delete = None
        if isinstance(env_vars, list):
            for env_var in env_vars:
                if env_var.get('key') == key and env_var.get('is_preview', False) == is_preview:
                    env_to_delete = env_var
                    break
        
        if not env_to_delete:
            env_type = "preview" if is_preview else "production"
            return [types.TextContent(type="text", text=f"❌ Environment variable **{key}** not found in {env_type} environment")]
        
        # Delete the environment variable  
        env_uuid = env_to_delete.get('uuid', env_to_delete.get('id'))
        await make_request_with_retry('DELETE', f"{base_url}/applications/{app_uuid}/envs/{env_uuid}", headers)
        
        env_type = "Preview" if is_preview else "Production"
        result = f"🗑️ Environment variable **{key}** deleted successfully!\n\n"
        result += f"**Details:**\n"
        result += f"• Variable: {key}\n"
        result += f"• Environment: {env_type}\n\n"
        result += f"💡 **Next Steps:**\n"
        result += f"• Restart application to apply changes: `coolify-restart-application`\n"
        result += f"• Verify removal with: `coolify-get-application-info`\n"
        
        logger.info(f"Successfully deleted environment variable {key} for application {app_uuid}")
        return [types.TextContent(type="text", text=result)]
        
    except Exception as e:
        logger.error(f"Failed to delete environment variable {key} for {app_uuid}: {e}")
        return [types.TextContent(type="text", text=f"❌ Failed to delete environment variable: {str(e)}\n\n💡 **Troubleshooting:**\n• Verify application UUID and variable name\n• Check if variable exists\n• Ensure sufficient permissions")]

async def bulk_update_env(app_uuid: str, env_vars: str, is_preview: bool = False) -> list[types.TextContent]:
    """Update multiple environment variables at once."""
    try:
        base_url = get_coolify_base_url()
        headers = get_coolify_headers()
        
        # Parse environment variables
        variables = []
        lines = env_vars.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            if '=' not in line:
                continue
                
            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip()
            variables.append((key, value))
        
        if not variables:
            return [types.TextContent(type="text", text="❌ No valid environment variables found. Use format: KEY=VALUE")]
        
        # Set each variable
        success_count = 0
        failed_vars = []
        
        # Get existing variables once for efficiency
        try:
            env_response = await make_request_with_retry('GET', f"{base_url}/applications/{app_uuid}/envs", headers)
            existing_vars = env_response.json() if env_response else []
        except Exception:
            existing_vars = []
        
        for key, value in variables:
            try:
                # Find existing variable
                existing_var = None
                if isinstance(existing_vars, list):
                    for env_var in existing_vars:
                        if env_var.get('key') == key and env_var.get('is_preview', False) == is_preview:
                            existing_var = env_var
                            break
                
                if existing_var:
                    # Update existing variable using PATCH
                    env_data = {
                        "key": key,
                        "value": value,
                        "is_preview": is_preview,
                        "is_build_time": existing_var.get('is_build_time', False),
                        "is_literal": existing_var.get('is_literal', False)
                    }
                    
                    await make_request_with_retry(
                        'PATCH', f"{base_url}/applications/{app_uuid}/envs", headers, json=env_data
                    )
                else:
                    # Create new variable
                    env_data = {
                        "key": key,
                        "value": value,
                        "is_preview": is_preview,
                        "is_build_time": False,
                        "is_literal": False
                    }
                    
                    await make_request_with_retry(
                        'POST', f"{base_url}/applications/{app_uuid}/envs", headers, json=env_data
                    )
                    
                success_count += 1
                
            except Exception as var_error:
                failed_vars.append(f"{key}: {str(var_error)}")
                logger.error(f"Failed to set {key}: {var_error}")
        
        env_type = "Preview" if is_preview else "Production"
        result = f"📦 Bulk environment variable update completed!\n\n"
        result += f"**Summary:**\n"
        result += f"• Environment: {env_type}\n"
        result += f"• Total Variables: {len(variables)}\n"
        result += f"• ✅ Successful: {success_count}\n"
        result += f"• ❌ Failed: {len(failed_vars)}\n\n"
        
        if failed_vars:
            result += f"**Failed Variables:**\n"
            for failure in failed_vars[:5]:  # Show first 5 failures
                result += f"• {failure}\n"
            if len(failed_vars) > 5:
                result += f"• ... and {len(failed_vars) - 5} more\n"
            result += "\n"
        
        result += f"💡 **Next Steps:**\n"
        result += f"• Restart application to apply changes: `coolify-restart-application`\n"
        result += f"• Verify variables with: `coolify-get-application-info`\n"
        
        logger.info(f"Successfully updated {success_count}/{len(variables)} environment variables for application {app_uuid}")
        return [types.TextContent(type="text", text=result)]
        
    except Exception as e:
        logger.error(f"Failed to bulk update environment variables for {app_uuid}: {e}")
        error_msg = format_enhanced_error(e, f"Unexpected error during bulk update for application {app_uuid}", "coolify-bulk-update-env")
        return [types.TextContent(type="text", text=error_msg)]

# Tool registration dictionary
ENVIRONMENT_TOOLS = {
    "coolify-set-env-variable": {
        "definition": types.Tool(
            name="coolify-set-env-variable",
            description="Add or update an environment variable for an application.",
            inputSchema={
                "type": "object",
                "required": ["app_uuid", "key", "value"],
                "properties": {
                    "app_uuid": {
                        "type": "string",
                        "description": "The UUID of the application"
                    },
                    "key": {
                        "type": "string",
                        "description": "Environment variable name"
                    },
                    "value": {
                        "type": "string",
                        "description": "Environment variable value"
                    },
                    "is_preview": {
                        "type": "boolean",
                        "description": "Whether this is for preview environment",
                        "default": False
                    }
                }
            }
        ),
        "handler": set_env_variable
    },
    
    "coolify-delete-env-variable": {
        "definition": types.Tool(
            name="coolify-delete-env-variable",
            description="Remove an environment variable from an application.",
            inputSchema={
                "type": "object",
                "required": ["app_uuid", "key"],
                "properties": {
                    "app_uuid": {
                        "type": "string",
                        "description": "The UUID of the application"
                    },
                    "key": {
                        "type": "string",
                        "description": "Environment variable name to remove"
                    },
                    "is_preview": {
                        "type": "boolean",
                        "description": "Whether this is for preview environment",
                        "default": False
                    }
                }
            }
        ),
        "handler": delete_env_variable
    },
    
    "coolify-bulk-update-env": {
        "definition": types.Tool(
            name="coolify-bulk-update-env",
            description="Update multiple environment variables at once.",
            inputSchema={
                "type": "object",
                "required": ["app_uuid", "env_vars"],
                "properties": {
                    "app_uuid": {
                        "type": "string",
                        "description": "The UUID of the application"
                    },
                    "env_vars": {
                        "type": "string",
                        "description": "Environment variables in KEY=VALUE format, separated by newlines"
                    },
                    "is_preview": {
                        "type": "boolean",
                        "description": "Whether this is for preview environment",
                        "default": False
                    }
                }
            }
        ),
        "handler": bulk_update_env
    }
}