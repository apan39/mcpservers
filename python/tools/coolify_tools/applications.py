"""Application management tools for Coolify API."""

import os
import requests
import mcp.types as types
from .base import get_coolify_headers, get_coolify_base_url, logger
from utils.error_handler import handle_requests_error, format_enhanced_error, get_resource_not_found_message


# Helper function for enhanced error handling with retry logic
async def make_request_with_retry(method: str, url: str, headers: dict, max_retries: int = 3, **kwargs) -> requests.Response:
    """Make HTTP request with retry logic and enhanced error handling."""
    import time
    
    for attempt in range(max_retries):
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, timeout=30, **kwargs)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=headers, timeout=30, **kwargs)
            elif method.upper() == 'PUT':
                response = requests.put(url, headers=headers, timeout=30, **kwargs)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=30, **kwargs)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response
            
        except requests.exceptions.ConnectionError as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                logger.warning(f"Connection error on attempt {attempt + 1}, retrying in {wait_time}s: {e}")
                time.sleep(wait_time)
                continue
            raise
        except requests.exceptions.Timeout as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                logger.warning(f"Timeout on attempt {attempt + 1}, retrying in {wait_time}s: {e}")
                time.sleep(wait_time)
                continue
            raise
        except requests.exceptions.HTTPError as e:
            # Don't retry HTTP errors (4xx, 5xx)
            raise
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                logger.warning(f"Request failed on attempt {attempt + 1}, retrying in {wait_time}s: {e}")
                time.sleep(wait_time)
                continue
            raise


# Core Application Management Functions
async def list_coolify_applications(**kwargs) -> list[types.TextContent]:
    """List all applications or filter by project UUID."""
    try:
        base_url = get_coolify_base_url()
        headers = get_coolify_headers()
        
        # Extract project_uuid from kwargs
        project_uuid = kwargs.get('project_uuid', None)
        
        # Treat empty string as None
        if project_uuid == "":
            project_uuid = None
        
        # Use the correct endpoint that gets all applications
        response = requests.get(f"{base_url}/applications", headers=headers, timeout=30)
        response.raise_for_status()
        
        applications = response.json()
        logger.info(f"Successfully retrieved applications")
        
        if isinstance(applications, list):
            # Filter by project if project_uuid is provided
            if project_uuid:
                # Get project details to find environment IDs
                try:
                    project_response = requests.get(f"{base_url}/projects/{project_uuid}", headers=headers, timeout=30)
                    if project_response.status_code == 200:
                        project_data = project_response.json()
                        environment_ids = [env.get('id') for env in project_data.get('environments', [])]
                        
                        filtered_apps = []
                        for app in applications:
                            app_env_id = app.get('environment_id')
                            if app_env_id in environment_ids:
                                filtered_apps.append(app)
                        applications = filtered_apps
                    else:
                        logger.warning(f"Could not fetch project {project_uuid} for filtering")
                except Exception as filter_error:
                    logger.error(f"Error filtering by project {project_uuid}: {filter_error}")
            
            app_info = []
            for app in applications:
                name = app.get('name', 'N/A')
                uuid = app.get('uuid', 'N/A')
                status = app.get('status', 'N/A')
                git_repo = app.get('git_repository', 'N/A')
                build_pack = app.get('build_pack', 'N/A')
                last_online = app.get('last_online_at', 'Never')
                
                app_line = f"• **{name}** (UUID: `{uuid}`): {status}"
                if git_repo != 'N/A':
                    app_line += f"\n  └─ Repository: {git_repo}"
                if build_pack != 'N/A':
                    app_line += f" | Build: {build_pack}"
                if last_online != 'Never':
                    app_line += f" | Last online: {last_online}"
                    
                app_info.append(app_line)
            
            title = f"Applications in project {project_uuid}" if project_uuid else "All Applications"
            result = f"{title}:\n" + "\n".join(app_info)
        else:
            result = f"Applications: {applications}"
            
        return [types.TextContent(type="text", text=result)]
        
    except Exception as e:
        logger.error(f"Failed to list applications: {e}")
        return [types.TextContent(type="text", text=f"Error listing applications: {e}")]


async def create_github_application(
    project_uuid: str = None,
    server_uuid: str = None,
    git_repository: str = None,
    name: str = None,
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
    
    # Usage guidance and parameter validation
    if not project_uuid or not server_uuid or not git_repository or not name:
        missing_params = []
        if not project_uuid: missing_params.append("project_uuid")
        if not server_uuid: missing_params.append("server_uuid")
        if not git_repository: missing_params.append("git_repository")
        if not name: missing_params.append("name")
        
        return [types.TextContent(type="text", text=f"""❌ **Missing Required Parameters: {', '.join(missing_params)}**

🔧 **Usage:**
```bash
coolify-create-github-app \\
  --project_uuid l8cog4c48w48kckkcgos8cwg \\
  --server_uuid csgkk88okkgkwg8w0g8og8c8 \\
  --git_repository https://github.com/username/repo \\
  --name my-app
```

📋 **Required Parameters:**
• **project_uuid**: Project UUID (get with `coolify-list-projects`)
• **server_uuid**: Server UUID (get with `coolify-get-deployment-info`)
• **git_repository**: GitHub repository URL (e.g., https://github.com/user/repo)
• **name**: Application name (e.g., 'my-app', 'frontend')

🔧 **Optional Parameters:**
• **git_branch**: Git branch to deploy (default: main)
• **build_pack**: Build method - nixpacks, dockerfile, static (default: nixpacks)
• **environment_name**: Environment (default: production)
• **instant_deploy**: Deploy immediately after creation (default: true)
• **domains**: Custom domains (comma-separated)
• **base_directory**: Source code subdirectory
• **publish_directory**: Output directory for static builds
• **install_command**: Custom install command
• **build_command**: Custom build command  
• **start_command**: Custom start command
• **ports_exposes**: Port to expose (e.g., '3000')

💡 **Examples:**
```bash
# Simple Node.js app
coolify-create-github-app --project_uuid PROJECT_UUID --server_uuid SERVER_UUID --git_repository https://github.com/user/my-app --name my-app

# Static site with custom build
coolify-create-github-app --project_uuid PROJECT_UUID --server_uuid SERVER_UUID --git_repository https://github.com/user/docs --name docs-site --build_pack static --publish_directory dist

# Docker app with custom domain
coolify-create-github-app --project_uuid PROJECT_UUID --server_uuid SERVER_UUID --git_repository https://github.com/user/api --name api --build_pack dockerfile --domains api.example.com --ports_exposes 8080
```

🚀 **Get Required UUIDs:**
• Server UUID: `coolify-get-deployment-info`
• Project UUID: `coolify-list-projects`

💡 **Build Pack Options:**
• **nixpacks**: Auto-detect and build (recommended)
• **dockerfile**: Use Dockerfile in repository
• **static**: Static files (HTML, CSS, JS)
""")]
    
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


async def get_application_info(app_uuid: str = None) -> list[types.TextContent]:
    """Get detailed application information and status by application UUID."""
    
    # Usage guidance and parameter validation
    if not app_uuid:
        return [types.TextContent(type="text", text="""❌ **Missing Required Parameter: app_uuid**

🔧 **Usage:**
```bash
coolify-get-application-info --app_uuid APPLICATION_UUID_HERE
```

📋 **Required Parameters:**
• **app_uuid**: Application UUID (long alphanumeric string)

💡 **Examples:**
```bash
# Get application details
coolify-get-application-info --app_uuid zs8sk0cgs4s8gsgwswsg88ko

# Check application status and configuration
coolify-get-application-info --app_uuid r4kss4gcs4oosg0o444s4c4s
```

🚀 **Get Application UUIDs:**
• List all applications: `coolify-list-applications`
• Filter by project: `coolify-list-applications --project_uuid PROJECT_UUID`

💡 **What you'll get:**
• Application name, status, and health
• Repository and branch information  
• Build configuration and commands
• Environment variables (masked)
• Deployment settings
""")]
    
    if len(app_uuid) < 20:  # Basic UUID length check
        return [types.TextContent(type="text", text=f"""❌ **Invalid app_uuid: {app_uuid}**

The app_uuid appears to be invalid. Application UUIDs should be long alphanumeric strings like: `zs8sk0cgs4s8gsgwswsg88ko`

💡 **Get valid application UUIDs:**
```bash
coolify-list-applications
```
""")]
    
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
        if e.response.status_code == 404:
            logger.error(f"Application {app_uuid} not found")
            error_msg = get_resource_not_found_message("application", app_uuid, "coolify-get-application-info")
            return [types.TextContent(type="text", text=error_msg)]
        else:
            logger.error(f"Failed to get application info for {app_uuid}: {e}")
            error_msg = handle_requests_error(e, f"Unable to retrieve application {app_uuid}", "coolify-get-application-info")
            return [types.TextContent(type="text", text=error_msg)]
    except requests.RequestException as e:
        logger.error(f"Failed to get application info for {app_uuid}: {e}")
        error_msg = handle_requests_error(e, f"Connection error while retrieving application {app_uuid}", "coolify-get-application-info")
        return [types.TextContent(type="text", text=error_msg)]
    except Exception as e:
        logger.error(f"Failed to get application info for {app_uuid}: {e}")
        error_msg = format_enhanced_error(e, f"Unexpected error while getting application info for {app_uuid}", "coolify-get-application-info")
        return [types.TextContent(type="text", text=error_msg)]


# Application Lifecycle Management
async def restart_application(app_uuid: str = None) -> list[types.TextContent]:
    """Restart an application in Coolify."""
    
    # Usage guidance and parameter validation
    if not app_uuid:
        return [types.TextContent(type="text", text="""❌ **Missing Required Parameter: app_uuid**

🔧 **Usage:**
```bash
coolify-restart-application --app_uuid APPLICATION_UUID_HERE
```

📋 **Required Parameters:**
• **app_uuid**: Application UUID to restart

💡 **Examples:**
```bash
# Restart application
coolify-restart-application --app_uuid zs8sk0cgs4s8gsgwswsg88ko

# Restart after configuration changes
coolify-restart-application --app_uuid r4kss4gcs4oosg0o444s4c4s
```

🚀 **Get Application UUIDs:**
• List all applications: `coolify-list-applications`

💡 **What happens:**
• Stops the application containers
• Starts them again with current configuration
• Maintains the same deployment/version
• Does NOT rebuild from source (use deploy for that)

⚠️ **Note:** This restarts the current deployment. To deploy new code changes, use `coolify-deploy-application` instead.

🔍 **Check Status After Restart:**
• Get application info: `coolify-get-application-info --app_uuid APP_UUID`
""")]
    
    if len(app_uuid) < 20:  # Basic UUID length check
        return [types.TextContent(type="text", text=f"""❌ **Invalid app_uuid: {app_uuid}**

The app_uuid appears to be invalid. Application UUIDs should be long alphanumeric strings like: `zs8sk0cgs4s8gsgwswsg88ko`

💡 **Get valid application UUIDs:**
```bash
coolify-list-applications
```
""")]
    
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


# Deployment Management
async def deploy_application(app_uuid: str = None, force: bool = False) -> list[types.TextContent]:
    """Trigger a deployment for an existing application."""
    
    # Usage guidance and parameter validation
    if not app_uuid:
        return [types.TextContent(type="text", text="""❌ **Missing Required Parameter: app_uuid**

🔧 **Usage:**
```bash
coolify-deploy-application --app_uuid APPLICATION_UUID_HERE
```

📋 **Required Parameters:**
• **app_uuid**: Application UUID to deploy

🔧 **Optional Parameters:**
• **force**: Force deployment even if no changes detected (default: false)

💡 **Examples:**
```bash
# Normal deployment
coolify-deploy-application --app_uuid zs8sk0cgs4s8gsgwswsg88ko

# Force deployment (rebuild even without changes) 
coolify-deploy-application --app_uuid zs8sk0cgs4s8gsgwswsg88ko --force true
```

🚀 **Get Application UUIDs:**
• List all applications: `coolify-list-applications`

💡 **What happens:**
• Triggers a new deployment from the latest Git commit
• Creates a deployment UUID for monitoring progress
• Returns deployment status and monitoring instructions

🔍 **Monitor Deployment:**
• Check deployment logs: `coolify-get-deployment-logs --deployment_uuid DEPLOYMENT_UUID`
• Watch progress: `coolify-watch-deployment --deployment_uuid DEPLOYMENT_UUID`
""")]
    
    if len(app_uuid) < 20:  # Basic UUID length check
        return [types.TextContent(type="text", text=f"""❌ **Invalid app_uuid: {app_uuid}**

The app_uuid appears to be invalid. Application UUIDs should be long alphanumeric strings like: `zs8sk0cgs4s8gsgwswsg88ko`

💡 **Get valid application UUIDs:**
```bash
coolify-list-applications
```
""")]
    
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


# Health Check Management
async def update_health_check(app_uuid: str, enabled: bool = True, health_check_path: str = "/health", 
                            health_check_port: int = 3000, health_check_method: str = "GET",
                            health_check_return_code: int = 200, health_check_interval: int = 30,
                            health_check_timeout: int = 10, health_check_retries: int = 3,
                            health_check_start_period: int = 10) -> list[types.TextContent]:
    """Update health check configuration for an application."""
    try:
        base_url = get_coolify_base_url()
        headers = get_coolify_headers()
        
        # Prepare health check configuration
        health_config = {
            "health_check_enabled": enabled,
            "health_check_path": health_check_path,
            "health_check_port": str(health_check_port),
            "health_check_method": health_check_method,
            "health_check_return_code": health_check_return_code,
            "health_check_interval": health_check_interval,
            "health_check_timeout": health_check_timeout,
            "health_check_retries": health_check_retries,
            "health_check_start_period": health_check_start_period
        }
        
        response = await make_request_with_retry(
            'PUT', f"{base_url}/applications/{app_uuid}", headers, json=health_config
        )
        
        status_emoji = "✅" if enabled else "⏸️"
        result = f"{status_emoji} Health check configuration updated successfully!\n\n"
        result += f"**Configuration Applied:**\n"
        result += f"• Status: {'Enabled' if enabled else 'Disabled'}\n"
        if enabled:
            result += f"• Path: {health_check_path}\n"
            result += f"• Port: {health_check_port}\n"
            result += f"• Method: {health_check_method}\n"
            result += f"• Expected Status Code: {health_check_return_code}\n"
            result += f"• Interval: {health_check_interval}s\n"
            result += f"• Timeout: {health_check_timeout}s\n"
            result += f"• Retries: {health_check_retries}\n"
            result += f"• Start Period: {health_check_start_period}s\n"
        
        result += f"\n💡 **Next Steps:**\n"
        result += f"• Use `coolify-restart-application` to apply changes\n"
        result += f"• Use `coolify-test-health-endpoint` to verify endpoint\n"
        
        logger.info(f"Successfully updated health check for application {app_uuid}")
        return [types.TextContent(type="text", text=result)]
        
    except Exception as e:
        logger.error(f"Failed to update health check for {app_uuid}: {e}")
        return [types.TextContent(type="text", text=f"❌ Failed to update health check: {str(e)}\n\n💡 **Troubleshooting:**\n• Verify application UUID is correct\n• Check if application supports health checks\n• Ensure Coolify API permissions are sufficient")]


async def test_health_endpoint(app_uuid: str) -> list[types.TextContent]:
    """Test health endpoint manually for an application."""
    try:
        base_url = get_coolify_base_url()
        headers = get_coolify_headers()
        
        # Get application info first
        app_response = await make_request_with_retry('GET', f"{base_url}/applications/{app_uuid}", headers)
        app_data = app_response.json()
        
        app_name = app_data.get('name', 'N/A')
        health_check_enabled = app_data.get('health_check_enabled', False)
        health_check_path = app_data.get('health_check_path', '/health')
        
        # Try to determine the application URL - check multiple fields
        fqdn = app_data.get('fqdn', '')
        custom_domain = app_data.get('custom_domain', '')
        domains = app_data.get('domains', '')
        ports_mappings = app_data.get('ports_mappings', '')
        
        # Use the best available domain information
        best_domain = fqdn or custom_domain or domains
        
        result = f"🏥 Health Check Test for **{app_name}**\n\n"
        result += f"**Application Configuration:**\n"
        result += f"• UUID: {app_uuid}\n"
        result += f"• Health Checks: {'✅ Enabled' if health_check_enabled else '❌ Disabled'}\n"
        result += f"• Health Path: {health_check_path}\n"
        result += f"• FQDN: {fqdn or 'Not configured'}\n"
        if custom_domain:
            result += f"• Custom Domain: {custom_domain}\n"
        if domains and domains != fqdn:
            result += f"• Additional Domains: {domains}\n"
        result += f"• Port Mappings: {ports_mappings or 'Not configured'}\n\n"
        
        if not health_check_enabled:
            result += "⚠️ **Health checks are disabled** for this application.\n"
            result += "Use `coolify-update-health-check` to enable them.\n\n"
        
        # Try to test the health endpoint if we have enough info
        if best_domain and health_check_path:
            try:
                # Smart URL construction - handle different FQDN formats
                if best_domain.startswith('http://') or best_domain.startswith('https://'):
                    # Domain already includes protocol
                    health_url = f"{best_domain}{health_check_path}"
                elif '.' in best_domain and not best_domain.startswith('localhost'):
                    # Looks like a proper domain, try HTTPS first for security
                    health_url = f"https://{best_domain}{health_check_path}"
                else:
                    # Local or development URL, use HTTP
                    health_url = f"http://{best_domain}{health_check_path}"
                
                result += f"**Testing Health Endpoint:** `{health_url}`\n"
                
                # Test without auth first
                test_response = None
                try:
                    test_response = requests.get(health_url, timeout=10)
                except requests.exceptions.SSLError as ssl_error:
                    # If HTTPS fails due to SSL issues, try HTTP as fallback
                    if health_url.startswith('https://'):
                        http_url = health_url.replace('https://', 'http://')
                        result += f"• ⚠️ HTTPS failed (SSL issue), trying HTTP: `{http_url}`\n"
                        try:
                            test_response = requests.get(http_url, timeout=10)
                            health_url = http_url  # Update for reporting
                        except Exception as http_error:
                            result += f"• Result: ❌ **Both HTTPS and HTTP failed**\n"
                            result += f"• HTTPS Error: {str(ssl_error)[:100]}...\n"
                            result += f"• HTTP Error: {str(http_error)[:100]}...\n"
                            test_response = None
                    else:
                        result += f"• Result: ❌ **SSL Error**: {str(ssl_error)[:100]}...\n"
                        test_response = None
                except Exception as e:
                    result += f"• Result: ❌ **Connection Error**: {str(e)[:100]}...\n"
                    test_response = None
                
                if test_response:
                    result += f"• Status Code: {test_response.status_code}\n"
                    result += f"• Response Time: {test_response.elapsed.total_seconds():.2f}s\n"
                    
                    if test_response.status_code == 200:
                        result += f"• Result: ✅ **Healthy**\n"
                        try:
                            health_data = test_response.json()
                            result += f"• Response: {health_data}\n"
                        except:
                            result += f"• Response: {test_response.text[:200]}...\n"
                    else:
                        result += f"• Result: ❌ **Unhealthy** (Status: {test_response.status_code})\n"
                        result += f"• Response: {test_response.text[:200]}...\n"
                
            except requests.exceptions.ConnectionError:
                result += f"• Result: ❌ **Connection Failed** - Application may be down\n"
            except requests.exceptions.Timeout:
                result += f"• Result: ⏱️ **Timeout** - Application is slow to respond\n"
            except Exception as test_error:
                result += f"• Result: ❌ **Test Failed**: {str(test_error)}\n"
        else:
            result += "⚠️ **Cannot test endpoint** - Missing domain information or health path configuration\n"
        
        result += f"\n💡 **Recommendations:**\n"
        if not health_check_enabled:
            result += f"• Enable health checks with `coolify-update-health-check`\n"
        if not best_domain:
            result += f"• Configure custom domain or FQDN in Coolify application settings\n"
            result += f"• Check port mappings configuration\n"
        if best_domain and not health_check_path.startswith('/'):
            result += f"• Ensure health check path starts with '/' (currently: {health_check_path})\n"
        result += f"• Check application logs with `coolify-get-application-logs`\n"
        result += f"• Verify application is running with `coolify-get-application-info`\n"
        
        logger.info(f"Successfully tested health endpoint for application {app_uuid}")
        return [types.TextContent(type="text", text=result)]
        
    except Exception as e:
        logger.error(f"Failed to test health endpoint for {app_uuid}: {e}")
        return [types.TextContent(type="text", text=f"❌ Failed to test health endpoint: {str(e)}\n\n💡 **Troubleshooting:**\n• Verify application UUID is correct\n• Check if application is running\n• Ensure health endpoint exists")]


# Configuration Management
async def update_build_settings(app_uuid: str, **kwargs) -> list[types.TextContent]:
    """Update application build settings (build pack, commands, etc.)."""
    try:
        base_url = get_coolify_base_url()
        headers = get_coolify_headers()
        
        # Filter out None values and prepare update data
        update_data = {}
        settings_map = {
            'build_pack': 'Build Pack',
            'install_command': 'Install Command',
            'build_command': 'Build Command', 
            'start_command': 'Start Command',
            'base_directory': 'Base Directory',
            'publish_directory': 'Publish Directory'
        }
        
        for key, value in kwargs.items():
            if value is not None and key in settings_map:
                update_data[key] = value
        
        if not update_data:
            return [types.TextContent(type="text", text="❌ No build settings provided to update")]
        
        response = await make_request_with_retry(
            'PUT', f"{base_url}/applications/{app_uuid}", headers, json=update_data
        )
        
        result = f"⚙️ **Build settings updated successfully!**\n\n"
        result += f"**Updated Settings:**\n"
        
        for key, value in update_data.items():
            display_name = settings_map.get(key, key)
            result += f"• {display_name}: {value}\n"
        
        result += f"\n💡 **Next Steps:**\n"
        result += f"• Redeploy application to apply changes: `coolify-deploy-application`\n"
        result += f"• Monitor deployment: `coolify-watch-deployment`\n"
        result += f"• Verify settings: `coolify-get-application-info`\n"
        
        logger.info(f"Successfully updated build settings for application {app_uuid}")
        return [types.TextContent(type="text", text=result)]
        
    except Exception as e:
        logger.error(f"Failed to update build settings for {app_uuid}: {e}")
        return [types.TextContent(type="text", text=f"❌ Failed to update build settings: {str(e)}\n\n💡 **Troubleshooting:**\n• Verify application UUID is correct\n• Check if build settings are valid\n• Ensure sufficient permissions")]


async def manage_domains(app_uuid: str, action: str, domain: str = None) -> list[types.TextContent]:
    """Add or remove custom domains for an application."""
    try:
        base_url = get_coolify_base_url()
        headers = get_coolify_headers()
        
        if action == "list":
            # Get current application info to list domains
            app_response = await make_request_with_retry('GET', f"{base_url}/applications/{app_uuid}", headers)
            app_data = app_response.json()
            
            app_name = app_data.get('name', 'N/A')
            fqdn = app_data.get('fqdn', '')
            domains = app_data.get('domains', '')
            
            result = f"🌐 **Domains for {app_name}**\n\n"
            result += f"**Current Configuration:**\n"
            result += f"• Primary FQDN: {fqdn or 'Not set'}\n"
            result += f"• Custom Domains: {domains or 'None configured'}\n\n"
            
            result += f"💡 **Domain Management:**\n"
            result += f"• Set Primary FQDN: `coolify-set-fqdn --app_uuid {app_uuid} --fqdn your-domain.com`\n"
            result += f"• Add domain: `coolify-manage-domains --action add --domain example.com`\n"
            result += f"• Remove domain: `coolify-manage-domains --action remove --domain example.com`\n"
            
            return [types.TextContent(type="text", text=result)]
        
        elif action in ["add", "remove"]:
            if not domain:
                return [types.TextContent(type="text", text=f"❌ Domain is required for {action} action")]
            
            # Get current domains
            app_response = await make_request_with_retry('GET', f"{base_url}/applications/{app_uuid}", headers)
            app_data = app_response.json()
            
            current_domains = app_data.get('domains', '')
            domains_list = [d.strip() for d in current_domains.split(',') if d.strip()] if current_domains else []
            
            if action == "add":
                if domain in domains_list:
                    return [types.TextContent(type="text", text=f"⚠️ Domain **{domain}** is already configured")]
                
                domains_list.append(domain)
                action_emoji = "➕"
                action_text = "added"
                
            else:  # remove
                if domain not in domains_list:
                    return [types.TextContent(type="text", text=f"⚠️ Domain **{domain}** is not currently configured")]
                
                domains_list.remove(domain)
                action_emoji = "➖"
                action_text = "removed"
            
            # Update domains
            new_domains = ','.join(domains_list)
            update_data = {"domains": new_domains}
            
            await make_request_with_retry(
                'PUT', f"{base_url}/applications/{app_uuid}", headers, json=update_data
            )
            
            result = f"{action_emoji} **Domain {action_text} successfully!**\n\n"
            result += f"**Domain Configuration:**\n"
            result += f"• {action_text.title()} Domain: {domain}\n"
            result += f"• All Domains: {new_domains or 'None'}\n\n"
            
            result += f"💡 **Next Steps:**\n"
            result += f"• Configure DNS to point {domain} to your server\n"
            result += f"• Redeploy application: `coolify-deploy-application`\n"
            result += f"• Test domain accessibility after deployment\n"
            
            logger.info(f"Successfully {action_text} domain {domain} for application {app_uuid}")
            return [types.TextContent(type="text", text=result)]
        
        else:
            return [types.TextContent(type="text", text=f"❌ Invalid action: {action}. Use 'add', 'remove', or 'list'")]
        
    except Exception as e:
        logger.error(f"Failed to manage domains for {app_uuid}: {e}")
        return [types.TextContent(type="text", text=f"❌ Failed to manage domains: {str(e)}\n\n💡 **Troubleshooting:**\n• Verify application UUID is correct\n• Check if domain format is valid\n• Ensure sufficient permissions")]


async def set_fqdn(app_uuid: str, fqdn: str = None) -> list[types.TextContent]:
    """Set the Primary FQDN for an application."""
    
    # Usage guidance and parameter validation
    if not app_uuid:
        return [types.TextContent(type="text", text="""❌ **Missing Required Parameter: app_uuid**

🔧 **Usage:**
```bash
coolify-set-fqdn --app_uuid APPLICATION_UUID_HERE --fqdn your-domain.com
```

📋 **Required Parameters:**
• **app_uuid**: Application UUID
• **fqdn**: Fully Qualified Domain Name (e.g., 'api.example.com', 'myapp.domain.com')

💡 **Examples:**
```bash
# Set Primary FQDN for an application
coolify-set-fqdn --app_uuid wcs4kc88cow4wc0gs0g404co --fqdn myapp.example.com

# Set subdomain FQDN
coolify-set-fqdn --app_uuid abc123 --fqdn api.mydomain.com
```

🚀 **Get Application UUIDs:**
• List all applications: `coolify-list-applications`

💡 **What this does:**
• Sets the Primary FQDN field in Coolify
• Enables external domain routing
• Fixes 404 errors for new applications
• Required for proper domain configuration
""")]
    
    if not fqdn:
        return [types.TextContent(type="text", text="""❌ **Missing Required Parameter: fqdn**

🔧 **Usage:**
```bash
coolify-set-fqdn --app_uuid APPLICATION_UUID_HERE --fqdn your-domain.com
```

📋 **FQDN Requirements:**
• Must be a valid domain name (e.g., 'api.example.com')
• Should point to your server's IP address via DNS
• Can be a subdomain or root domain
• Must not include http:// or https:// prefix

💡 **Valid FQDN Examples:**
• myapp.example.com
• api.mydomain.org  
• service.company.net
• app.localhost (for local development)
""")]
    
    if len(app_uuid) < 20:  # Basic UUID length check
        return [types.TextContent(type="text", text=f"""❌ **Invalid app_uuid: {app_uuid}**

The app_uuid appears to be invalid. Application UUIDs should be long alphanumeric strings like: `wcs4kc88cow4wc0gs0g404co`

💡 **Get valid application UUIDs:**
```bash
coolify-list-applications
```
""")]
    
    try:
        base_url = get_coolify_base_url()
        headers = get_coolify_headers()
        
        # Get current application info first
        app_response = await make_request_with_retry('GET', f"{base_url}/applications/{app_uuid}", headers)
        app_data = app_response.json()
        
        app_name = app_data.get('name', 'N/A')
        current_fqdn = app_data.get('fqdn', '')
        
        # Update the FQDN
        update_data = {"fqdn": fqdn}
        
        await make_request_with_retry(
            'PUT', f"{base_url}/applications/{app_uuid}", headers, json=update_data
        )
        
        result = f"🌐 **Primary FQDN set successfully!**\n\n"
        result += f"**Application:** {app_name}\n"
        result += f"**Previous FQDN:** {current_fqdn or 'Not set'}\n"
        result += f"**New FQDN:** {fqdn}\n\n"
        
        result += f"💡 **Next Steps:**\n"
        result += f"1. **Configure DNS:** Point {fqdn} to your server IP\n"
        result += f"2. **Restart Application:** `coolify-restart-application --app_uuid {app_uuid}`\n"
        result += f"3. **Test Domain:** Visit http://{fqdn} or https://{fqdn}\n"
        result += f"4. **Verify SSL:** Coolify will automatically provision SSL certificates\n\n"
        
        result += f"🔍 **Verification:**\n"
        result += f"• Check domain status: `coolify-manage-domains --app_uuid {app_uuid} --action list`\n"
        result += f"• Test health endpoint: `coolify-test-health-endpoint --app_uuid {app_uuid}`\n"
        result += f"• View application info: `coolify-get-application-info --app_uuid {app_uuid}`\n"
        
        logger.info(f"Successfully set FQDN {fqdn} for application {app_uuid}")
        return [types.TextContent(type="text", text=result)]
        
    except Exception as e:
        logger.error(f"Failed to set FQDN for {app_uuid}: {e}")
        return [types.TextContent(type="text", text=f"❌ Failed to set FQDN: {str(e)}\n\n💡 **Troubleshooting:**\n• Verify application UUID is correct\n• Check if FQDN format is valid (no http/https prefix)\n• Ensure sufficient API permissions\n• Try setting a simple domain first")]


async def update_resource_limits(app_uuid: str, **kwargs) -> list[types.TextContent]:
    """Set CPU and memory limits for an application.""" 
    try:
        base_url = get_coolify_base_url()
        headers = get_coolify_headers()
        
        # Prepare resource limit updates
        update_data = {}
        resource_map = {
            'cpu_limit': 'CPU Limit',
            'memory_limit': 'Memory Limit', 
            'cpu_reservation': 'CPU Reservation',
            'memory_reservation': 'Memory Reservation'
        }
        
        for key, value in kwargs.items():
            if value is not None and key in resource_map:
                update_data[key] = value
        
        if not update_data:
            return [types.TextContent(type="text", text="❌ No resource limits provided to update")]
        
        response = await make_request_with_retry(
            'PUT', f"{base_url}/applications/{app_uuid}", headers, json=update_data
        )
        
        result = f"💾 **Resource limits updated successfully!**\n\n"
        result += f"**Updated Limits:**\n"
        
        for key, value in update_data.items():
            display_name = resource_map.get(key, key)
            result += f"• {display_name}: {value}\n"
        
        result += f"\n💡 **Next Steps:**\n"
        result += f"• Restart application to apply limits: `coolify-restart-application`\n"
        result += f"• Monitor resource usage after restart\n"
        result += f"• Verify limits: `coolify-get-application-info`\n"
        
        result += f"\n📋 **Resource Limit Examples:**\n"
        result += f"• CPU: '0.5' (half CPU), '1.0' (one CPU), '2' (two CPUs)\n"
        result += f"• Memory: '512m', '1g', '2g' (megabytes/gigabytes)\n"
        
        logger.info(f"Successfully updated resource limits for application {app_uuid}")
        return [types.TextContent(type="text", text=result)]
        
    except Exception as e:
        logger.error(f"Failed to update resource limits for {app_uuid}: {e}")
        return [types.TextContent(type="text", text=f"❌ Failed to update resource limits: {str(e)}\n\n💡 **Troubleshooting:**\n• Verify application UUID is correct\n• Check resource limit format (e.g., '1g', '0.5')\n• Ensure sufficient permissions")]


# Batch Operations
async def bulk_restart(app_uuids: str, parallel: bool = False) -> list[types.TextContent]:
    """Restart multiple applications at once."""
    try:
        base_url = get_coolify_base_url()
        headers = get_coolify_headers()
        
        # Parse UUIDs
        uuid_list = [uuid.strip() for uuid in app_uuids.split(',') if uuid.strip()]
        
        if not uuid_list:
            return [types.TextContent(type="text", text="❌ No valid application UUIDs provided")]
        
        result = f"🔄 **Bulk Restart Operation** ({'Parallel' if parallel else 'Sequential'})\n\n"
        result += f"**Applications to restart:** {len(uuid_list)}\n\n"
        
        successful_restarts = []
        failed_restarts = []
        
        if parallel:
            # Parallel execution using asyncio
            import asyncio
            
            async def restart_single_app(app_uuid):
                try:
                    response = await make_request_with_retry(
                        'POST', f"{base_url}/applications/{app_uuid}/restart", headers
                    )
                    return app_uuid, "success", response.json().get('message', 'Restart initiated')
                except Exception as e:
                    return app_uuid, "failed", str(e)
            
            # Execute all restarts concurrently
            restart_tasks = [restart_single_app(uuid) for uuid in uuid_list]
            results = await asyncio.gather(*restart_tasks, return_exceptions=True)
            
            for app_result in results:
                if isinstance(app_result, Exception):
                    failed_restarts.append(f"Unknown: {str(app_result)}")
                else:
                    app_uuid, status, message = app_result
                    if status == "success":
                        successful_restarts.append(f"✅ {app_uuid}: {message}")
                    else:
                        failed_restarts.append(f"❌ {app_uuid}: {message}")
        
        else:
            # Sequential execution
            for app_uuid in uuid_list:
                try:
                    response = await make_request_with_retry(
                        'POST', f"{base_url}/applications/{app_uuid}/restart", headers
                    )
                    message = response.json().get('message', 'Restart initiated')
                    successful_restarts.append(f"✅ {app_uuid}: {message}")
                    
                except Exception as e:
                    failed_restarts.append(f"❌ {app_uuid}: {str(e)}")
        
        # Build results
        result += f"**📊 Results:**\n"
        result += f"• ✅ Successful: {len(successful_restarts)}\n"
        result += f"• ❌ Failed: {len(failed_restarts)}\n\n"
        
        if successful_restarts:
            result += f"**✅ Successful Restarts:**\n"
            for success in successful_restarts:
                result += f"{success}\n"
            result += "\n"
        
        if failed_restarts:
            result += f"**❌ Failed Restarts:**\n"
            for failure in failed_restarts[:5]:  # Show first 5 failures
                result += f"{failure}\n"
            if len(failed_restarts) > 5:
                result += f"... and {len(failed_restarts) - 5} more failures\n"
            result += "\n"
        
        result += f"💡 **Next Steps:**\n"
        result += f"• Monitor application status with `coolify-project-status`\n"
        result += f"• Check individual app status with `coolify-get-application-info`\n"
        if failed_restarts:
            result += f"• Investigate failed restarts individually\n"
        
        logger.info(f"Bulk restart completed: {len(successful_restarts)} successful, {len(failed_restarts)} failed")
        return [types.TextContent(type="text", text=result)]
        
    except Exception as e:
        logger.error(f"Failed to perform bulk restart: {e}")
        return [types.TextContent(type="text", text=f"❌ Failed to perform bulk restart: {str(e)}\n\n💡 **Troubleshooting:**\n• Verify all application UUIDs are correct\n• Check API permissions\n• Try sequential mode if parallel fails")]


async def project_status(project_uuid: str, include_details: bool = False) -> list[types.TextContent]:
    """Get status overview of all applications in a project."""
    try:
        base_url = get_coolify_base_url()
        headers = get_coolify_headers()
        
        # Get project info
        project_response = await make_request_with_retry('GET', f"{base_url}/projects/{project_uuid}", headers)
        project_data = project_response.json()
        
        project_name = project_data.get('name', 'N/A')
        
        # Get all applications and filter by project
        apps_response = await make_request_with_retry('GET', f"{base_url}/applications", headers)
        all_applications = apps_response.json()
        
        # Filter applications by project environment IDs
        environment_ids = [env.get('id') for env in project_data.get('environments', [])]
        project_applications = []
        
        if isinstance(all_applications, list):
            for app in all_applications:
                app_env_id = app.get('environment_id')
                if app_env_id in environment_ids:
                    project_applications.append(app)
        
        if not project_applications:
            return [types.TextContent(type="text", text=f"📋 No applications found in project **{project_name}**")]
        
        # Count statuses
        status_counts = {}
        healthy_count = 0
        unhealthy_count = 0
        
        result = f"📊 **Project Status: {project_name}**\n\n"
        result += f"**Overview:**\n"
        result += f"• Total Applications: {len(project_applications)}\n"
        
        for app in project_applications:
            status = app.get('status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
            
            if 'healthy' in status.lower():
                healthy_count += 1
            elif 'unhealthy' in status.lower() or 'failed' in status.lower() or 'error' in status.lower():
                unhealthy_count += 1
        
        result += f"• 🟢 Healthy: {healthy_count}\n"
        result += f"• 🔴 Unhealthy: {unhealthy_count}\n"
        result += f"• ⚪ Other: {len(project_applications) - healthy_count - unhealthy_count}\n\n"
        
        # Status breakdown
        result += f"**📈 Status Breakdown:**\n"
        for status, count in sorted(status_counts.items()):
            status_emoji = "🟢" if "healthy" in status.lower() else "🔴" if any(x in status.lower() for x in ["unhealthy", "failed", "error"]) else "⚪"
            result += f"• {status_emoji} {status}: {count}\n"
        result += "\n"
        
        # Application details
        if include_details:
            result += f"**📋 Application Details:**\n"
            for app in project_applications:
                name = app.get('name', 'N/A')
                uuid = app.get('uuid', 'N/A')
                status = app.get('status', 'N/A')
                last_online = app.get('last_online_at', 'Never')
                
                status_emoji = "🟢" if "healthy" in status.lower() else "🔴" if any(x in status.lower() for x in ["unhealthy", "failed", "error"]) else "⚪"
                
                result += f"**{status_emoji} {name}**\n"
                result += f"   • UUID: `{uuid}`\n"
                result += f"   • Status: {status}\n"
                result += f"   • Last Online: {last_online}\n"
                result += f"   • Commands: `coolify-get-application-info --app_uuid {uuid}`\n\n"
        else:
            result += f"**🎯 Quick Actions:**\n"
            result += f"• Detailed view: `coolify-project-status --include_details true`\n"
            result += f"• Restart all: `coolify-bulk-restart --app_uuids \"{','.join([app.get('uuid', '') for app in project_applications])}\"`\n"
            result += f"• Deploy all: `coolify-bulk-deploy --app_uuids \"{','.join([app.get('uuid', '') for app in project_applications])}\"`\n"
        
        # Health recommendations
        result += f"\n💡 **Recommendations:**\n"
        if unhealthy_count > 0:
            result += f"• ⚠️ {unhealthy_count} applications need attention\n"
            result += f"• Use detailed view to identify problematic apps\n"
        if healthy_count == len(project_applications):
            result += f"• ✅ All applications are healthy!\n"
        
        result += f"• Monitor regularly with this command\n"
        result += f"• Use `coolify-deployment-metrics` for deployment insights\n"
        
        logger.info(f"Successfully retrieved project status for {project_uuid}")
        return [types.TextContent(type="text", text=result)]
        
    except Exception as e:
        logger.error(f"Failed to get project status for {project_uuid}: {e}")
        return [types.TextContent(type="text", text=f"❌ Failed to get project status: {str(e)}\n\n💡 **Troubleshooting:**\n• Verify project UUID is correct\n• Check if project exists\n• Ensure API permissions are sufficient")]


async def bulk_deploy(app_uuids: str, force: bool = False, parallel: bool = False) -> list[types.TextContent]:
    """Deploy multiple applications at once."""
    try:
        base_url = get_coolify_base_url()
        headers = get_coolify_headers()
        
        # Parse UUIDs
        uuid_list = [uuid.strip() for uuid in app_uuids.split(',') if uuid.strip()]
        
        if not uuid_list:
            return [types.TextContent(type="text", text="❌ No valid application UUIDs provided")]
        
        result = f"🚀 **Bulk Deploy Operation** ({'Parallel' if parallel else 'Sequential'})\n\n"
        result += f"**Applications to deploy:** {len(uuid_list)}\n"
        result += f"**Force deployment:** {'Yes' if force else 'No'}\n\n"
        
        successful_deploys = []
        failed_deploys = []
        deployment_uuids = []
        
        if parallel:
            # Parallel execution using asyncio
            import asyncio
            
            async def deploy_single_app(app_uuid):
                try:
                    payload = {"uuid": app_uuid}
                    if force:
                        payload["force"] = True
                    
                    response = await make_request_with_retry(
                        'POST', f"{base_url}/deploy", headers, json=payload
                    )
                    result_data = response.json()
                    
                    deployment_uuid = None
                    if 'deployments' in result_data and result_data['deployments']:
                        deployment_info = result_data['deployments'][0]
                        deployment_uuid = deployment_info.get('deployment_uuid')
                    
                    return app_uuid, "success", deployment_uuid, "Deployment initiated"
                except Exception as e:
                    return app_uuid, "failed", None, str(e)
            
            # Execute all deployments concurrently
            deploy_tasks = [deploy_single_app(uuid) for uuid in uuid_list]
            results = await asyncio.gather(*deploy_tasks, return_exceptions=True)
            
            for app_result in results:
                if isinstance(app_result, Exception):
                    failed_deploys.append(f"Unknown: {str(app_result)}")
                else:
                    app_uuid, status, deployment_uuid, message = app_result
                    if status == "success":
                        successful_deploys.append(f"✅ {app_uuid}: {message}")
                        if deployment_uuid:
                            deployment_uuids.append(deployment_uuid)
                    else:
                        failed_deploys.append(f"❌ {app_uuid}: {message}")
        
        else:
            # Sequential execution
            for app_uuid in uuid_list:
                try:
                    payload = {"uuid": app_uuid}
                    if force:
                        payload["force"] = True
                    
                    response = await make_request_with_retry(
                        'POST', f"{base_url}/deploy", headers, json=payload
                    )
                    result_data = response.json()
                    
                    deployment_uuid = None
                    if 'deployments' in result_data and result_data['deployments']:
                        deployment_info = result_data['deployments'][0]
                        deployment_uuid = deployment_info.get('deployment_uuid')
                        deployment_uuids.append(deployment_uuid)
                    
                    successful_deploys.append(f"✅ {app_uuid}: Deployment initiated")
                    
                except Exception as e:
                    failed_deploys.append(f"❌ {app_uuid}: {str(e)}")
        
        # Build results
        result += f"**📊 Results:**\n"
        result += f"• ✅ Successful: {len(successful_deploys)}\n"
        result += f"• ❌ Failed: {len(failed_deploys)}\n"
        result += f"• 🔄 Deployments Started: {len(deployment_uuids)}\n\n"
        
        if successful_deploys:
            result += f"**✅ Successful Deployments:**\n"
            for success in successful_deploys:
                result += f"{success}\n"
            result += "\n"
        
        if failed_deploys:
            result += f"**❌ Failed Deployments:**\n"
            for failure in failed_deploys[:5]:  # Show first 5 failures
                result += f"{failure}\n"
            if len(failed_deploys) > 5:
                result += f"... and {len(failed_deploys) - 5} more failures\n"
            result += "\n"
        
        if deployment_uuids:
            result += f"**🔄 Deployment Monitoring:**\n"
            for i, dep_uuid in enumerate(deployment_uuids[:3], 1):  # Show first 3
                result += f"{i}. `coolify-watch-deployment --deployment_uuid {dep_uuid}`\n"
            if len(deployment_uuids) > 3:
                result += f"... and {len(deployment_uuids) - 3} more deployments\n"
            result += "\n"
        
        result += f"💡 **Next Steps:**\n"
        result += f"• Monitor deployment progress with commands above\n"
        result += f"• Check project status: `coolify-project-status`\n"
        result += f"• Use `coolify-get-recent-deployments` for deployment history\n"
        if failed_deploys:
            result += f"• Investigate failed deployments individually\n"
        
        logger.info(f"Bulk deploy completed: {len(successful_deploys)} successful, {len(failed_deploys)} failed")
        return [types.TextContent(type="text", text=result)]
        
    except Exception as e:
        logger.error(f"Failed to perform bulk deploy: {e}")
        return [types.TextContent(type="text", text=f"❌ Failed to perform bulk deploy: {str(e)}\n\n💡 **Troubleshooting:**\n• Verify all application UUIDs are correct\n• Check API permissions\n• Try sequential mode if parallel fails\n• Ensure applications are ready for deployment")]


# Tool Registration Dictionaries
APPLICATION_TOOLS = {
    "coolify-list-applications": {
        "definition": types.Tool(
            name="coolify-list-applications",
            description="List all applications or filter by project UUID.",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_uuid": {
                        "type": "string",
                        "description": "Optional UUID of the project to filter applications"
                    }
                },
                "additionalProperties": False
            }
        ),
        "handler": list_coolify_applications
    },
    
    "coolify-create-github-app": {
        "definition": types.Tool(
            name="coolify-create-github-app",
            description="Create a new application from a GitHub repository in Coolify.",
            inputSchema={
                "type": "object",
                "required": [],  # Made optional so we can provide helpful guidance
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
                },
                "additionalProperties": False
            }
        ),
        "handler": create_github_application
    },
    
    "coolify-get-application-info": {
        "definition": types.Tool(
            name="coolify-get-application-info",
            description="Get detailed application information and status by application UUID.",
            inputSchema={
                "type": "object",
                "required": [],  # Made optional so we can provide helpful guidance
                "properties": {
                    "app_uuid": {
                        "type": "string",
                        "description": "The UUID of the application to get information for"
                    }
                },
                "additionalProperties": False
            }
        ),
        "handler": get_application_info
    },
    
    "coolify-restart-application": {
        "definition": types.Tool(
            name="coolify-restart-application",
            description="Restart an application in Coolify.",
            inputSchema={
                "type": "object",
                "required": [],  # Made optional so we can provide helpful guidance
                "properties": {
                    "app_uuid": {
                        "type": "string",
                        "description": "The UUID of the application to restart"
                    }
                },
                "additionalProperties": False
            }
        ),
        "handler": restart_application
    },
    
    "coolify-stop-application": {
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
                },
                "additionalProperties": False
            }
        ),
        "handler": stop_application
    },
    
    "coolify-start-application": {
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
                },
                "additionalProperties": False
            }
        ),
        "handler": start_application
    },
    
    "coolify-delete-application": {
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
                },
                "additionalProperties": False
            }
        ),
        "handler": delete_application
    },
    
    "coolify-get-application-logs": {
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
                },
                "additionalProperties": False
            }
        ),
        "handler": get_application_logs
    },
    
    "coolify-deploy-application": {
        "definition": types.Tool(
            name="coolify-deploy-application",
            description="Trigger a deployment for an existing application.",
            inputSchema={
                "type": "object",
                "required": [],  # Made optional so we can provide helpful guidance
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
                },
                "additionalProperties": False
            }
        ),
        "handler": deploy_application
    },
    
    "coolify-update-health-check": {
        "definition": types.Tool(
            name="coolify-update-health-check",
            description="Enable/disable and configure health checks for an application.",
            inputSchema={
                "type": "object",
                "required": ["app_uuid"],
                "properties": {
                    "app_uuid": {
                        "type": "string",
                        "description": "The UUID of the application to configure"
                    },
                    "enabled": {
                        "type": "boolean",
                        "description": "Enable or disable health checks",
                        "default": True
                    },
                    "health_check_path": {
                        "type": "string",
                        "description": "Health check endpoint path (e.g., '/health')",
                        "default": "/health"
                    },
                    "health_check_port": {
                        "type": "integer",
                        "description": "Port for health checks",
                        "default": 3000
                    },
                    "health_check_method": {
                        "type": "string",
                        "description": "HTTP method for health checks",
                        "default": "GET"
                    },
                    "health_check_return_code": {
                        "type": "integer",
                        "description": "Expected HTTP return code",
                        "default": 200
                    },
                    "health_check_interval": {
                        "type": "integer",
                        "description": "Health check interval in seconds",
                        "default": 30
                    },
                    "health_check_timeout": {
                        "type": "integer",
                        "description": "Health check timeout in seconds",
                        "default": 10
                    },
                    "health_check_retries": {
                        "type": "integer",
                        "description": "Number of retries",
                        "default": 3
                    },
                    "health_check_start_period": {
                        "type": "integer",
                        "description": "Start period in seconds",
                        "default": 10
                    }
                },
                "additionalProperties": False
            }
        ),
        "handler": update_health_check
    },
    
    "coolify-test-health-endpoint": {
        "definition": types.Tool(
            name="coolify-test-health-endpoint",
            description="Test health endpoint manually for an application.",
            inputSchema={
                "type": "object",
                "required": ["app_uuid"],
                "properties": {
                    "app_uuid": {
                        "type": "string",
                        "description": "The UUID of the application to test"
                    }
                },
                "additionalProperties": False
            }
        ),
        "handler": test_health_endpoint
    },
    
    "coolify-update-build-settings": {
        "definition": types.Tool(
            name="coolify-update-build-settings",
            description="Update application build settings (build pack, commands, etc.).",
            inputSchema={
                "type": "object",
                "required": ["app_uuid"],
                "properties": {
                    "app_uuid": {
                        "type": "string",
                        "description": "The UUID of the application"
                    },
                    "build_pack": {
                        "type": "string",
                        "description": "Build method (static, nixpacks, dockerfile, etc.)"
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
                    "base_directory": {
                        "type": "string",
                        "description": "Source code subdirectory"
                    },
                    "publish_directory": {
                        "type": "string",
                        "description": "Output directory for static builds"
                    }
                },
                "additionalProperties": False
            }
        ),
        "handler": update_build_settings
    },
    
    "coolify-manage-domains": {
        "definition": types.Tool(
            name="coolify-manage-domains",
            description="Add or remove custom domains for an application.",
            inputSchema={
                "type": "object",
                "required": ["app_uuid", "action"],
                "properties": {
                    "app_uuid": {
                        "type": "string",
                        "description": "The UUID of the application"
                    },
                    "action": {
                        "type": "string",
                        "enum": ["add", "remove", "list"],
                        "description": "Action to perform on domains"
                    },
                    "domain": {
                        "type": "string",
                        "description": "Domain to add or remove (required for add/remove actions)"
                    }
                },
                "additionalProperties": False
            }
        ),
        "handler": manage_domains
    },
    
    "coolify-update-resource-limits": {
        "definition": types.Tool(
            name="coolify-update-resource-limits",
            description="Set CPU and memory limits for an application.",
            inputSchema={
                "type": "object",
                "required": ["app_uuid"],
                "properties": {
                    "app_uuid": {
                        "type": "string",
                        "description": "The UUID of the application"
                    },
                    "cpu_limit": {
                        "type": "string",
                        "description": "CPU limit (e.g., '0.5', '1.0', '2')"
                    },
                    "memory_limit": {
                        "type": "string",
                        "description": "Memory limit (e.g., '512m', '1g', '2g')"
                    },
                    "cpu_reservation": {
                        "type": "string",
                        "description": "CPU reservation (e.g., '0.1', '0.5')"
                    },
                    "memory_reservation": {
                        "type": "string",
                        "description": "Memory reservation (e.g., '256m', '512m')"
                    }
                },
                "additionalProperties": False
            }
        ),
        "handler": update_resource_limits
    },
    
    "coolify-bulk-restart": {
        "definition": types.Tool(
            name="coolify-bulk-restart",
            description="Restart multiple applications at once.",
            inputSchema={
                "type": "object",
                "required": ["app_uuids"],
                "properties": {
                    "app_uuids": {
                        "type": "string",
                        "description": "Comma-separated list of application UUIDs to restart"
                    },
                    "parallel": {
                        "type": "boolean",
                        "description": "Whether to restart in parallel (faster) or sequentially (safer)",
                        "default": False
                    }
                },
                "additionalProperties": False
            }
        ),
        "handler": bulk_restart
    },
    
    "coolify-project-status": {
        "definition": types.Tool(
            name="coolify-project-status",
            description="Get status overview of all applications in a project.",
            inputSchema={
                "type": "object",
                "required": ["project_uuid"],
                "properties": {
                    "project_uuid": {
                        "type": "string",
                        "description": "The UUID of the project"
                    },
                    "include_details": {
                        "type": "boolean",
                        "description": "Include detailed information for each app",
                        "default": False
                    }
                },
                "additionalProperties": False
            }
        ),
        "handler": project_status
    },
    
    "coolify-bulk-deploy": {
        "definition": types.Tool(
            name="coolify-bulk-deploy",
            description="Deploy multiple applications at once.",
            inputSchema={
                "type": "object",
                "required": ["app_uuids"],
                "properties": {
                    "app_uuids": {
                        "type": "string",
                        "description": "Comma-separated list of application UUIDs to deploy"
                    },
                    "force": {
                        "type": "boolean",
                        "description": "Force deployment even if no changes detected",
                        "default": False
                    },
                    "parallel": {
                        "type": "boolean",
                        "description": "Whether to deploy in parallel (faster) or sequentially (safer)",
                        "default": False
                    }
                },
                "additionalProperties": False
            }
        ),
        "handler": bulk_deploy
    },
    
    "coolify-set-fqdn": {
        "definition": types.Tool(
            name="coolify-set-fqdn",
            description="Set the Primary FQDN for an application to enable external domain routing.",
            inputSchema={
                "type": "object",
                "required": [],  # Made optional so we can provide helpful guidance
                "properties": {
                    "app_uuid": {
                        "type": "string",
                        "description": "The UUID of the application"
                    },
                    "fqdn": {
                        "type": "string",
                        "description": "Fully Qualified Domain Name (e.g., 'api.example.com', 'myapp.domain.com')"
                    }
                },
                "additionalProperties": False
            }
        ),
        "handler": set_fqdn
    }
}