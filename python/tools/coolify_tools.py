"""Coolify API tools for the MCP server."""

import os
import mcp.types as types
import requests
from utils.logger import setup_logger

# Set up logging
logger = setup_logger("coolify_tools")

def register_coolify_tools(tool_registry):
    """Register Coolify API tools with the tool registry."""
    
    tool_registry["coolify-get-version"] = {
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
    }
    
    tool_registry["coolify-list-projects"] = {
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
    }
    
    tool_registry["coolify-list-servers"] = {
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
    }
    
    tool_registry["coolify-list-applications"] = {
        "definition": types.Tool(
            name="coolify-list-applications",
            description="List applications for a specific project.",
            inputSchema={
                "type": "object",
                "required": ["project_uuid"],
                "properties": {
                    "project_uuid": {
                        "type": "string",
                        "description": "The UUID of the project"
                    }
                }
            }
        ),
        "handler": list_coolify_applications
    }
    
    tool_registry["coolify-create-github-app"] = {
        "definition": types.Tool(
            name="coolify-create-github-app",
            description="Create a new application from a GitHub repository in Coolify.",
            inputSchema={
                "type": "object",
                "required": ["project_uuid", "server_uuid", "git_repository", "name"],
                "properties": {
                    "project_uuid": {
                        "type": "string",
                        "description": "The UUID of the project to deploy to"
                    },
                    "server_uuid": {
                        "type": "string",
                        "description": "The UUID of the server to deploy on"
                    },
                    "git_repository": {
                        "type": "string",
                        "description": "GitHub repository URL (e.g., https://github.com/user/repo)"
                    },
                    "git_branch": {
                        "type": "string",
                        "description": "Git branch to deploy",
                        "default": "main"
                    },
                    "name": {
                        "type": "string",
                        "description": "Application name"
                    },
                    "build_pack": {
                        "type": "string",
                        "description": "Build method (static, nixpacks, dockerfile, etc.)",
                        "default": "nixpacks"
                    },
                    "domains": {
                        "type": "string",
                        "description": "Custom domains (comma-separated)"
                    },
                    "environment_name": {
                        "type": "string",
                        "description": "Environment name",
                        "default": "production"
                    },
                    "instant_deploy": {
                        "type": "boolean",
                        "description": "Deploy immediately after creation",
                        "default": True
                    },
                    "base_directory": {
                        "type": "string",
                        "description": "Source code subdirectory"
                    },
                    "publish_directory": {
                        "type": "string",
                        "description": "Output directory for static builds"
                    },
                    "install_command": {
                        "type": "string",
                        "description": "Custom install command"
                    },
                    "build_command": {
                        "type": "string",
                        "description": "Custom build command"
                    },
                    "start_command": {
                        "type": "string",
                        "description": "Custom start command"
                    },
                    "ports_exposes": {
                        "type": "string",
                        "description": "Port to expose (e.g., '3000')"
                    }
                }
            }
        ),
        "handler": create_github_application
    }
    
    tool_registry["coolify-get-deployment-logs"] = {
        "definition": types.Tool(
            name="coolify-get-deployment-logs",
            description="Get deployment logs and status for a specific deployment UUID.",
            inputSchema={
                "type": "object",
                "required": ["deployment_uuid"],
                "properties": {
                    "deployment_uuid": {
                        "type": "string",
                        "description": "The UUID of the deployment to get logs for"
                    },
                    "lines": {
                        "type": "integer",
                        "description": "Number of recent log lines to show (default: 50)",
                        "default": 50
                    }
                }
            }
        ),
        "handler": get_deployment_logs
    }
    
    tool_registry["coolify-get-application-info"] = {
        "definition": types.Tool(
            name="coolify-get-application-info",
            description="Get detailed application information and status by application UUID.",
            inputSchema={
                "type": "object",
                "required": ["app_uuid"],
                "properties": {
                    "app_uuid": {
                        "type": "string",
                        "description": "The UUID of the application to get information for"
                    }
                }
            }
        ),
        "handler": get_application_info
    }
    
    tool_registry["coolify-restart-application"] = {
        "definition": types.Tool(
            name="coolify-restart-application",
            description="Restart an application in Coolify.",
            inputSchema={
                "type": "object",
                "required": ["app_uuid"],
                "properties": {
                    "app_uuid": {
                        "type": "string",
                        "description": "The UUID of the application to restart"
                    }
                }
            }
        ),
        "handler": restart_application
    }
    
    tool_registry["coolify-stop-application"] = {
        "definition": types.Tool(
            name="coolify-stop-application",
            description="Stop an application in Coolify.",
            inputSchema={
                "type": "object",
                "required": ["app_uuid"],
                "properties": {
                    "app_uuid": {
                        "type": "string",
                        "description": "The UUID of the application to stop"
                    }
                }
            }
        ),
        "handler": stop_application
    }
    
    tool_registry["coolify-start-application"] = {
        "definition": types.Tool(
            name="coolify-start-application",
            description="Start an application in Coolify.",
            inputSchema={
                "type": "object",
                "required": ["app_uuid"],
                "properties": {
                    "app_uuid": {
                        "type": "string",
                        "description": "The UUID of the application to start"
                    }
                }
            }
        ),
        "handler": start_application
    }
    
    tool_registry["coolify-delete-application"] = {
        "definition": types.Tool(
            name="coolify-delete-application",
            description="Delete an application in Coolify.",
            inputSchema={
                "type": "object",
                "required": ["app_uuid"],
                "properties": {
                    "app_uuid": {
                        "type": "string",
                        "description": "The UUID of the application to delete"
                    },
                    "confirm": {
                        "type": "boolean",
                        "description": "Confirmation that you want to delete the application",
                        "default": False
                    }
                }
            }
        ),
        "handler": delete_application
    }
    
    tool_registry["coolify-get-application-logs"] = {
        "definition": types.Tool(
            name="coolify-get-application-logs",
            description="Get runtime logs for an application.",
            inputSchema={
                "type": "object",
                "required": ["app_uuid"],
                "properties": {
                    "app_uuid": {
                        "type": "string",
                        "description": "The UUID of the application to get logs for"
                    },
                    "lines": {
                        "type": "integer",
                        "description": "Number of recent log lines to show",
                        "default": 100
                    }
                }
            }
        ),
        "handler": get_application_logs
    }
    
    tool_registry["coolify-deploy-application"] = {
        "definition": types.Tool(
            name="coolify-deploy-application",
            description="Trigger a deployment for an existing application.",
            inputSchema={
                "type": "object",
                "required": ["app_uuid"],
                "properties": {
                    "app_uuid": {
                        "type": "string",
                        "description": "The UUID of the application to deploy"
                    },
                    "force": {
                        "type": "boolean",
                        "description": "Force deployment even if no changes detected",
                        "default": False
                    }
                }
            }
        ),
        "handler": deploy_application
    }
    
    tool_registry["coolify-get-deployment-info"] = {
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
        
    except Exception as e:
        logger.error(f"Failed to get Coolify version: {e}")
        return [types.TextContent(type="text", text=f"Error getting Coolify version: {e}")]

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
        
    except Exception as e:
        logger.error(f"Failed to list Coolify projects: {e}")
        return [types.TextContent(type="text", text=f"Error listing projects: {e}")]

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

async def list_coolify_applications(project_uuid: str) -> list[types.TextContent]:
    """List applications for a specific project."""
    try:
        base_url = get_coolify_base_url()
        headers = get_coolify_headers()
        
        response = requests.get(f"{base_url}/projects/{project_uuid}/applications", headers=headers, timeout=30)
        response.raise_for_status()
        
        applications = response.json()
        logger.info(f"Successfully retrieved applications for project {project_uuid}")
        
        if isinstance(applications, list):
            app_info = []
            for app in applications:
                name = app.get('name', 'N/A')
                uuid = app.get('uuid', 'N/A')
                status = app.get('status', 'N/A')
                app_info.append(f"• {name} (UUID: {uuid}): {status}")
            
            result = f"Applications in project {project_uuid}:\n" + "\n".join(app_info)
        else:
            result = f"Applications: {applications}"
            
        return [types.TextContent(type="text", text=result)]
        
    except Exception as e:
        logger.error(f"Failed to list applications for project {project_uuid}: {e}")
        return [types.TextContent(type="text", text=f"Error listing applications: {e}")]

async def create_github_application(
    project_uuid: str,
    server_uuid: str,
    git_repository: str,
    name: str,
    git_branch: str = "main",
    build_pack: str = "nixpacks",
    domains: str = None,
    environment_name: str = "production",
    instant_deploy: bool = True,
    base_directory: str = None,
    publish_directory: str = None,
    install_command: str = None,
    build_command: str = None,
    start_command: str = None,
    ports_exposes: str = None,
    **kwargs
) -> list[types.TextContent]:
    """Create a new application from a GitHub repository."""
    try:
        base_url = get_coolify_base_url()
        headers = get_coolify_headers()
        
        # Prepare the request payload
        payload = {
            "project_uuid": project_uuid,
            "server_uuid": server_uuid,
            "git_repository": git_repository,
            "git_branch": git_branch,
            "name": name,
            "build_pack": build_pack,
            "environment_name": environment_name,
            "instant_deploy": instant_deploy
        }
        
        # Add optional fields if provided
        if domains:
            payload["domains"] = domains
        if base_directory:
            payload["base_directory"] = base_directory
        if publish_directory:
            payload["publish_directory"] = publish_directory
        if install_command:
            payload["install_command"] = install_command
        if build_command:
            payload["build_command"] = build_command
        if start_command:
            payload["start_command"] = start_command
        if ports_exposes:
            payload["ports_exposes"] = ports_exposes
        
        logger.info(f"Creating application {name} from {git_repository}")
        
        response = requests.post(f"{base_url}/applications/public", headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        app_uuid = result.get('uuid', 'N/A')
        
        success_msg = f"""✅ Application created successfully!
        
Application Details:
• Name: {name}
• UUID: {app_uuid}
• Repository: {git_repository}
• Branch: {git_branch}
• Build Pack: {build_pack}
• Environment: {environment_name}
• Project: {project_uuid}
• Server: {server_uuid}

The application will be deployed automatically if instant_deploy is enabled."""
        
        logger.info(f"Successfully created application {name} with UUID {app_uuid}")
        return [types.TextContent(type="text", text=success_msg)]
        
    except requests.exceptions.HTTPError as e:
        error_msg = f"HTTP Error {e.response.status_code}: {e.response.text}"
        logger.error(f"Failed to create application {name}: {error_msg}")
        return [types.TextContent(type="text", text=f"Failed to create application: {error_msg}")]
    except Exception as e:
        logger.error(f"Failed to create application {name}: {e}")
        return [types.TextContent(type="text", text=f"Error creating application: {e}")]

async def get_deployment_logs(deployment_uuid: str, lines: int = 50) -> list[types.TextContent]:
    """Get deployment logs and status for a specific deployment UUID."""
    try:
        base_url = get_coolify_base_url()
        headers = get_coolify_headers()
        
        response = requests.get(f"{base_url}/deployments/{deployment_uuid}", headers=headers, timeout=30)
        response.raise_for_status()
        
        deployment_data = response.json()
        logger.info(f"Successfully retrieved deployment data for {deployment_uuid}")
        
        # Extract basic deployment info
        status = deployment_data.get('status', 'N/A')
        started_at = deployment_data.get('started_at', 'N/A')
        finished_at = deployment_data.get('finished_at', 'N/A')
        
        result = f"""Deployment UUID: {deployment_uuid}
Status: {status}
Started At: {started_at}
Finished At: {finished_at}

=== DEPLOYMENT LOGS ===
"""
        
        # Process logs
        logs_data = deployment_data.get('logs', [])
        if isinstance(logs_data, str):
            # If logs are stored as JSON string, parse them
            import json
            try:
                logs_data = json.loads(logs_data)
            except:
                result += f"Raw logs: {logs_data}"
                return [types.TextContent(type="text", text=result)]
        
        if isinstance(logs_data, list):
            # Get the last N lines
            recent_logs = logs_data[-lines:] if lines > 0 else logs_data
            
            for log_entry in recent_logs:
                if isinstance(log_entry, dict):
                    output = log_entry.get('output', '')
                    log_type = log_entry.get('type', 'INFO')
                    hidden = log_entry.get('hidden', False)
                    
                    # Skip hidden logs unless they contain important error info
                    if hidden and not any(keyword in output.lower() for keyword in ['error', 'fail', 'exception', 'unhealthy']):
                        continue
                    
                    if output.strip():
                        result += f"{log_type.upper()}: {output}\n"
                else:
                    result += f"LOG: {log_entry}\n"
        else:
            result += f"Logs data: {logs_data}"
        
        return [types.TextContent(type="text", text=result)]
        
    except requests.exceptions.HTTPError as e:
        error_msg = f"HTTP Error {e.response.status_code}: {e.response.text}"
        logger.error(f"Failed to get deployment logs for {deployment_uuid}: {error_msg}")
        return [types.TextContent(type="text", text=f"Failed to get deployment logs: {error_msg}")]
    except Exception as e:
        logger.error(f"Failed to get deployment logs for {deployment_uuid}: {e}")
        return [types.TextContent(type="text", text=f"Error getting deployment logs: {e}")]

async def get_application_info(app_uuid: str) -> list[types.TextContent]:
    """Get detailed application information and status by application UUID."""
    try:
        base_url = get_coolify_base_url()
        headers = get_coolify_headers()
        
        response = requests.get(f"{base_url}/applications/{app_uuid}", headers=headers, timeout=30)
        response.raise_for_status()
        
        app_data = response.json()
        logger.info(f"Successfully retrieved application data for {app_uuid}")
        
        # Extract key application information
        name = app_data.get('name', 'N/A')
        status = app_data.get('status', 'N/A')
        build_pack = app_data.get('build_pack', 'N/A')
        last_online_at = app_data.get('last_online_at', 'N/A')
        git_repository = app_data.get('git_repository', 'N/A')
        git_branch = app_data.get('git_branch', 'N/A')
        start_command = app_data.get('start_command', 'N/A')
        dockerfile_location = app_data.get('dockerfile_location', 'N/A')
        
        result = f"""Application Information:
Name: {name}
UUID: {app_uuid}
Status: {status}
Build Pack: {build_pack}
Last Online At: {last_online_at}

Repository Information:
Git Repository: {git_repository}
Git Branch: {git_branch}

Configuration:
Start Command: {start_command}
Dockerfile Location: {dockerfile_location}
"""
        
        # Try to get environment variables
        try:
            env_response = requests.get(f"{base_url}/applications/{app_uuid}/envs", headers=headers, timeout=30)
            if env_response.status_code == 200:
                env_vars = env_response.json()
                result += f"\nEnvironment Variables:\n"
                if env_vars and isinstance(env_vars, list):
                    for env_var in env_vars:
                        key = env_var.get('key', 'N/A')
                        value = env_var.get('value', 'N/A')
                        # Mask sensitive values
                        if any(sensitive in key.lower() for sensitive in ['token', 'key', 'secret', 'password']):
                            value = '***MASKED***'
                        result += f"  {key}: {value}\n"
                else:
                    result += "  No environment variables set\n"
        except Exception as env_error:
            result += f"\nEnvironment Variables: Error retrieving ({env_error})\n"
        
        return [types.TextContent(type="text", text=result)]
        
    except requests.exceptions.HTTPError as e:
        error_msg = f"HTTP Error {e.response.status_code}: {e.response.text}"
        logger.error(f"Failed to get application info for {app_uuid}: {error_msg}")
        return [types.TextContent(type="text", text=f"Failed to get application info: {error_msg}")]
    except Exception as e:
        logger.error(f"Failed to get application info for {app_uuid}: {e}")
        return [types.TextContent(type="text", text=f"Error getting application info: {e}")]

async def restart_application(app_uuid: str) -> list[types.TextContent]:
    """Restart an application in Coolify."""
    try:
        base_url = get_coolify_base_url()
        headers = get_coolify_headers()
        
        response = requests.post(f"{base_url}/applications/{app_uuid}/restart", headers=headers, timeout=30)
        response.raise_for_status()
        
        result_data = response.json()
        message = result_data.get('message', 'Application restart initiated')
        
        logger.info(f"Successfully restarted application {app_uuid}")
        return [types.TextContent(type="text", text=f"✅ {message}")]
        
    except requests.exceptions.HTTPError as e:
        error_msg = f"HTTP Error {e.response.status_code}: {e.response.text}"
        logger.error(f"Failed to restart application {app_uuid}: {error_msg}")
        return [types.TextContent(type="text", text=f"❌ Failed to restart application: {error_msg}")]
    except Exception as e:
        logger.error(f"Failed to restart application {app_uuid}: {e}")
        return [types.TextContent(type="text", text=f"❌ Error restarting application: {e}")]

async def stop_application(app_uuid: str) -> list[types.TextContent]:
    """Stop an application in Coolify."""
    try:
        base_url = get_coolify_base_url()
        headers = get_coolify_headers()
        
        response = requests.post(f"{base_url}/applications/{app_uuid}/stop", headers=headers, timeout=30)
        response.raise_for_status()
        
        result_data = response.json()
        message = result_data.get('message', 'Application stop initiated')
        
        logger.info(f"Successfully stopped application {app_uuid}")
        return [types.TextContent(type="text", text=f"⏹️ {message}")]
        
    except requests.exceptions.HTTPError as e:
        error_msg = f"HTTP Error {e.response.status_code}: {e.response.text}"
        logger.error(f"Failed to stop application {app_uuid}: {error_msg}")
        return [types.TextContent(type="text", text=f"❌ Failed to stop application: {error_msg}")]
    except Exception as e:
        logger.error(f"Failed to stop application {app_uuid}: {e}")
        return [types.TextContent(type="text", text=f"❌ Error stopping application: {e}")]

async def start_application(app_uuid: str) -> list[types.TextContent]:
    """Start an application in Coolify."""
    try:
        base_url = get_coolify_base_url()
        headers = get_coolify_headers()
        
        response = requests.post(f"{base_url}/applications/{app_uuid}/start", headers=headers, timeout=30)
        response.raise_for_status()
        
        result_data = response.json()
        message = result_data.get('message', 'Application start initiated')
        
        logger.info(f"Successfully started application {app_uuid}")
        return [types.TextContent(type="text", text=f"▶️ {message}")]
        
    except requests.exceptions.HTTPError as e:
        error_msg = f"HTTP Error {e.response.status_code}: {e.response.text}"
        logger.error(f"Failed to start application {app_uuid}: {error_msg}")
        return [types.TextContent(type="text", text=f"❌ Failed to start application: {error_msg}")]
    except Exception as e:
        logger.error(f"Failed to start application {app_uuid}: {e}")
        return [types.TextContent(type="text", text=f"❌ Error starting application: {e}")]

async def delete_application(app_uuid: str, confirm: bool = False) -> list[types.TextContent]:
    """Delete an application in Coolify."""
    if not confirm:
        return [types.TextContent(type="text", text="⚠️ Application deletion requires confirmation. Set 'confirm' parameter to true to proceed.")]
    
    try:
        base_url = get_coolify_base_url()
        headers = get_coolify_headers()
        
        response = requests.delete(f"{base_url}/applications/{app_uuid}", headers=headers, timeout=30)
        response.raise_for_status()
        
        logger.info(f"Successfully deleted application {app_uuid}")
        return [types.TextContent(type="text", text=f"🗑️ Application {app_uuid} has been deleted successfully")]
        
    except requests.exceptions.HTTPError as e:
        error_msg = f"HTTP Error {e.response.status_code}: {e.response.text}"
        logger.error(f"Failed to delete application {app_uuid}: {error_msg}")
        return [types.TextContent(type="text", text=f"❌ Failed to delete application: {error_msg}")]
    except Exception as e:
        logger.error(f"Failed to delete application {app_uuid}: {e}")
        return [types.TextContent(type="text", text=f"❌ Error deleting application: {e}")]

async def get_application_logs(app_uuid: str, lines: int = 100) -> list[types.TextContent]:
    """Get runtime logs for an application."""
    try:
        base_url = get_coolify_base_url()
        headers = get_coolify_headers()
        
        # Try to get application logs - this endpoint may vary depending on Coolify version
        response = requests.get(f"{base_url}/applications/{app_uuid}/logs", headers=headers, timeout=30)
        
        if response.status_code == 404:
            # Try alternative endpoint structure
            response = requests.get(f"{base_url}/applications/{app_uuid}/containers/logs", headers=headers, timeout=30)
        
        response.raise_for_status()
        
        # Handle different response formats
        if response.headers.get('content-type', '').startswith('application/json'):
            logs_data = response.json()
            if isinstance(logs_data, list):
                recent_logs = logs_data[-lines:] if lines > 0 else logs_data
                result = "\n".join([log.get('message', str(log)) for log in recent_logs])
            else:
                result = str(logs_data)
        else:
            # Plain text logs
            log_lines = response.text.split('\n')
            recent_logs = log_lines[-lines:] if lines > 0 else log_lines
            result = '\n'.join(recent_logs)
        
        logger.info(f"Successfully retrieved logs for application {app_uuid}")
        return [types.TextContent(type="text", text=f"📋 Application Logs ({lines} lines):\n\n{result}")]
        
    except requests.exceptions.HTTPError as e:
        error_msg = f"HTTP Error {e.response.status_code}: {e.response.text}"
        logger.error(f"Failed to get logs for application {app_uuid}: {error_msg}")
        return [types.TextContent(type="text", text=f"❌ Failed to get application logs: {error_msg}")]
    except Exception as e:
        logger.error(f"Failed to get logs for application {app_uuid}: {e}")
        return [types.TextContent(type="text", text=f"❌ Error getting application logs: {e}")]

async def deploy_application(app_uuid: str, force: bool = False) -> list[types.TextContent]:
    """Trigger a deployment for an existing application."""
    try:
        base_url = get_coolify_base_url()
        headers = get_coolify_headers()
        
        payload = {"uuid": app_uuid}
        if force:
            payload["force"] = True
        
        response = requests.post(f"{base_url}/deploy", headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        result_data = response.json()
        deployment_uuid = None
        
        if 'deployments' in result_data and result_data['deployments']:
            deployment_info = result_data['deployments'][0]
            deployment_uuid = deployment_info.get('deployment_uuid')
            message = deployment_info.get('message', 'Deployment queued')
            
            result = f"🚀 {message}"
            if deployment_uuid:
                result += f"\nDeployment UUID: {deployment_uuid}"
                result += f"\n\nUse 'coolify-get-deployment-logs' with UUID '{deployment_uuid}' to monitor progress."
        else:
            result = f"🚀 Deployment initiated for application {app_uuid}"
        
        logger.info(f"Successfully triggered deployment for application {app_uuid}")
        return [types.TextContent(type="text", text=result)]
        
    except requests.exceptions.HTTPError as e:
        error_msg = f"HTTP Error {e.response.status_code}: {e.response.text}"
        logger.error(f"Failed to deploy application {app_uuid}: {error_msg}")
        return [types.TextContent(type="text", text=f"❌ Failed to deploy application: {error_msg}")]
    except Exception as e:
        logger.error(f"Failed to deploy application {app_uuid}: {e}")
        return [types.TextContent(type="text", text=f"❌ Error deploying application: {e}")]

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
                result += f"• **{name}**: `{uuid}`\n"
                if description and description != 'No description':
                    result += f"  └─ {description}\n"
            result += "\n"
        
        # Deployment template
        result += "🛠️ **Deployment Template**:\n"
        result += "```bash\n"
        result += "coolify-create-github-app \\\n"
        result += "  --project_uuid \"PROJECT_UUID_FROM_ABOVE\" \\\n"
        result += f"  --server_uuid \"{server_uuid}\" \\\n"
        result += "  --git_repository \"https://github.com/username/repo\" \\\n"
        result += "  --name \"your-app-name\" \\\n"
        result += "  --git_branch \"main\" \\\n"
        result += "  --build_pack \"dockerfile\"\n"
        result += "```\n\n"
        
        result += "💡 **Quick Tips**:\n"
        result += f"• Always use server UUID: `{server_uuid}`\n"
        result += "• Choose project UUID from the list above\n"
        result += "• Use `coolify-get-application-info` to monitor deployment\n"
        
        logger.info("Successfully retrieved deployment information")
        return [types.TextContent(type="text", text=result)]
        
    except Exception as e:
        logger.error(f"Failed to get deployment info: {e}")
        return [types.TextContent(type="text", text=f"❌ Error getting deployment info: {e}")]