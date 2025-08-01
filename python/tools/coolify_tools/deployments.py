"""Deployment and monitoring tools for Coolify API."""

import requests
import mcp.types as types
from .base import get_coolify_headers, get_coolify_base_url, logger
from utils.error_handler import handle_requests_error, format_enhanced_error

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
        application_name = deployment_data.get('application_name', 'N/A')
        
        result = f"""📋 **Deployment Summary**
UUID: {deployment_uuid}
Application: {application_name}
Status: **{status.upper()}**
Started: {started_at}
Finished: {finished_at}

"""
        
        # Check logs size before processing
        logs_data = deployment_data.get('logs', [])
        
        # Debug: Check actual log data type and size
        logger.info(f"Logs data type: {type(logs_data)}, size: {len(str(logs_data))}")
        
        # Immediately truncate if response is too large
        if len(str(logs_data)) > 50000:  # Extremely aggressive limit
            result += f"⚠️ **Massive Log Response** ({len(str(logs_data)):,} chars)\n\n"
            result += "**🔴 Response too large to process safely**\n"
            result += "**Status:** Deployment completed but logs are extensive\n"
            result += "**Recommendation:** Check Coolify UI for full deployment logs\n"
            return [types.TextContent(type="text", text=result)]
        
        # If logs are a string, be extremely aggressive with truncation
        if isinstance(logs_data, str):
            if len(logs_data) > 1000:  # Very small threshold
                result += f"⚠️ **Large Log File** ({len(logs_data):,} chars) - Summary Only\n\n"
                
                # Find the main error quickly
                lines = logs_data.split('\n')
                error_found = False
                
                for line in lines:
                    if 'npm error' in line.lower() or 'eresolve' in line.lower():
                        result += f"**🔴 Main Error:** {line[:200]}...\n"
                        error_found = True
                        break
                
                if not error_found:
                    for line in lines:
                        if any(keyword in line.lower() for keyword in ['error', 'failed', 'exit code']):
                            result += f"**🔴 Error:** {line[:150]}...\n"
                            break
                
                # Show last line only
                last_line = [line for line in lines[-3:] if line.strip()][-1] if lines else ""
                if last_line:
                    result += f"**📄 Final:** {last_line[:100]}...\n"
                        
                result += f"\n💡 Use Coolify UI for full logs"
                return [types.TextContent(type="text", text=result)]
        
        # Process normally sized logs
        if isinstance(logs_data, str):
            import json
            try:
                logs_data = json.loads(logs_data)
            except:
                result += f"**Raw Logs:**\n{logs_data[:3000]}{'...' if len(logs_data) > 3000 else ''}"
                return [types.TextContent(type="text", text=result)]
        
        if isinstance(logs_data, list):
            result += f"**📋 Deployment Logs** (Last {min(lines, len(logs_data))} entries):\n\n"
            
            # Get the last N lines
            recent_logs = logs_data[-lines:] if lines > 0 else logs_data[-20:]
            
            for log_entry in recent_logs:
                if isinstance(log_entry, dict):
                    output = log_entry.get('output', '')
                    log_type = log_entry.get('type', 'INFO')
                    hidden = log_entry.get('hidden', False)
                    
                    # Skip hidden logs unless they contain important error info
                    if hidden and not any(keyword in output.lower() for keyword in ['error', 'fail', 'exception', 'unhealthy']):
                        continue
                    
                    if output.strip():
                        truncated_output = output[:400] + "..." if len(output) > 400 else output
                        result += f"**{log_type.upper()}:** {truncated_output}\n\n"
                else:
                    truncated_entry = str(log_entry)[:400] + "..." if len(str(log_entry)) > 400 else str(log_entry)
                    result += f"**LOG:** {truncated_entry}\n\n"
        else:
            result += f"**Logs Data:** {str(logs_data)[:1000]}{'...' if len(str(logs_data)) > 1000 else ''}"
        
        return [types.TextContent(type="text", text=result)]
        
    except requests.exceptions.HTTPError as e:
        error_msg = f"HTTP Error {e.response.status_code}: {e.response.text}"
        logger.error(f"Failed to get deployment logs for {deployment_uuid}: {error_msg}")
        return [types.TextContent(type="text", text=f"Failed to get deployment logs: {error_msg}")]
    except Exception as e:
        logger.error(f"Failed to get deployment logs for {deployment_uuid}: {e}")
        return [types.TextContent(type="text", text=f"Error getting deployment logs: {e}")]

async def watch_deployment(deployment_uuid: str, show_progress: bool = True) -> list[types.TextContent]:
    """Get real-time deployment progress and status."""
    try:
        base_url = get_coolify_base_url()
        headers = get_coolify_headers()
        
        response = requests.get(f"{base_url}/deployments/{deployment_uuid}", headers=headers, timeout=30)
        response.raise_for_status()
        
        deployment_data = response.json()
        logger.info(f"Successfully retrieved deployment status for {deployment_uuid}")
        
        # Extract deployment information
        status = deployment_data.get('status', 'unknown')
        started_at = deployment_data.get('started_at', 'N/A')
        finished_at = deployment_data.get('finished_at', 'In progress...')
        application_name = deployment_data.get('application_name', 'N/A')
        
        result = f"""🚀 **Deployment Status Monitor**

Deployment UUID: {deployment_uuid}
Application: {application_name}
Status: **{status.upper()}**
Started: {started_at}
Finished: {finished_at}

"""
        
        if show_progress:
            # Add progress indicators based on status
            if status in ['running', 'in_progress']:
                result += "⏳ **Current Progress:**\n"
                result += "• Build phase in progress...\n"
                result += "• Check logs for detailed progress\n"
            elif status == 'success':
                result += "✅ **Deployment Completed Successfully!**\n"
                result += "• Application is ready\n"
                result += "• Check application status for health info\n"
            elif status in ['failed', 'error']:
                result += "❌ **Deployment Failed**\n"
                result += "• Check deployment logs for error details\n"
                result += "• Review application configuration\n"
            else:
                result += f"ℹ️ **Status:** {status}\n"
        
        # Add useful next steps
        result += f"""
💡 **Next Steps:**
• View detailed logs: `coolify-get-deployment-logs --deployment_uuid {deployment_uuid}`
• Check application status: Check application info after deployment
• Monitor application: Use application monitoring tools
"""
        
        return [types.TextContent(type="text", text=result)]
        
    except requests.exceptions.HTTPError as e:
        logger.error(f"Failed to watch deployment {deployment_uuid}: {e}")
        error_msg = handle_requests_error(e, f"Unable to get deployment status for {deployment_uuid}", "coolify-watch-deployment")
        return [types.TextContent(type="text", text=error_msg)]
    except Exception as e:
        logger.error(f"Failed to watch deployment {deployment_uuid}: {e}")
        error_msg = format_enhanced_error(e, f"Unexpected error while watching deployment {deployment_uuid}", "coolify-watch-deployment")
        return [types.TextContent(type="text", text=error_msg)]

async def get_recent_deployments(app_uuid: str, limit: int = 5) -> list[types.TextContent]:
    """Get the last N deployments for an application with status."""
    try:
        base_url = get_coolify_base_url()
        headers = get_coolify_headers()
        
        # Use the specific endpoint for application deployments
        response = requests.get(f"{base_url}/deployments/list-by-app-uuid?uuid={app_uuid}", headers=headers, timeout=30)
        response.raise_for_status()
        
        app_deployments = response.json()
        logger.info(f"Successfully retrieved deployments for application {app_uuid}")
        
        # Ensure we have a list
        if not isinstance(app_deployments, list):
            app_deployments = [app_deployments] if app_deployments else []
        
        if not app_deployments:
            return [types.TextContent(type="text", text=f"No deployments found for application {app_uuid}")]
        
        # Sort by created date and limit results
        sorted_deployments = sorted(app_deployments, key=lambda x: x.get('created_at', ''), reverse=True)
        recent_deployments = sorted_deployments[:limit]
        
        result = f"📋 **Recent Deployments for Application {app_uuid}**\n\n"
        
        for i, deployment in enumerate(recent_deployments, 1):
            # Try different possible UUID field names
            deployment_uuid = (deployment.get('deployment_uuid') or 
                             deployment.get('uuid') or 
                             deployment.get('id') or 
                             'N/A')
            
            status = deployment.get('status', 'N/A')
            created_at = deployment.get('created_at', 'N/A')
            finished_at = deployment.get('finished_at', deployment.get('updated_at', 'In progress...'))
            
            # Add status emoji
            status_emoji = {
                'success': '✅',
                'failed': '❌',
                'error': '❌',
                'running': '⏳',
                'in_progress': '⏳',
                'cancelled': '⏹️'
            }.get(status.lower(), 'ℹ️')
            
            uuid_display = deployment_uuid[:8] + "..." if len(str(deployment_uuid)) > 8 else str(deployment_uuid)
            
            result += f"""{i}. {status_emoji} **Deployment {uuid_display}**
   UUID: {deployment_uuid}
   Status: {status}
   Started: {created_at}
   Finished: {finished_at}
   
"""
        
        result += f"""
💡 **Commands:**
• View logs: `coolify-get-deployment-logs --deployment_uuid DEPLOYMENT_UUID`
• Watch deployment: `coolify-watch-deployment --deployment_uuid DEPLOYMENT_UUID`

🔍 **Available Deployment UUIDs:**"""

        for deployment in recent_deployments:
            deployment_uuid = (deployment.get('deployment_uuid') or 
                             deployment.get('uuid') or 
                             deployment.get('id') or 
                             'N/A')
            result += f"\n• {deployment_uuid}"
        
        return [types.TextContent(type="text", text=result)]
        
    except requests.exceptions.HTTPError as e:
        logger.error(f"Failed to get recent deployments for {app_uuid}: {e}")
        error_msg = handle_requests_error(e, f"Unable to get deployments for application {app_uuid}", "coolify-get-recent-deployments")
        return [types.TextContent(type="text", text=error_msg)]
    except Exception as e:
        logger.error(f"Failed to get recent deployments for {app_uuid}: {e}")
        error_msg = format_enhanced_error(e, f"Unexpected error while getting deployments for {app_uuid}", "coolify-get-recent-deployments")
        return [types.TextContent(type="text", text=error_msg)]

async def deployment_metrics(app_uuid: str, days: int = 30) -> list[types.TextContent]:
    """Get deployment success/failure rates and timing metrics."""
    try:
        base_url = get_coolify_base_url()
        headers = get_coolify_headers()
        
        response = requests.get(f"{base_url}/deployments/by-app-uuid?uuid={app_uuid}", headers=headers, timeout=30)
        response.raise_for_status()
        
        deployments = response.json()
        logger.info(f"Successfully retrieved deployment metrics for application {app_uuid}")
        
        if not deployments or len(deployments) == 0:
            return [types.TextContent(type="text", text=f"No deployment data available for application {app_uuid}")]
        
        # Filter deployments by date range if needed
        from datetime import datetime, timedelta
        cutoff_date = datetime.now() - timedelta(days=days)
        
        if isinstance(deployments, list):
            recent_deployments = []
            for deployment in deployments:
                created_at = deployment.get('created_at', '')
                if created_at:
                    try:
                        deployment_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        if deployment_date >= cutoff_date:
                            recent_deployments.append(deployment)
                    except:
                        # Include if we can't parse date
                        recent_deployments.append(deployment)
                else:
                    recent_deployments.append(deployment)
        else:
            recent_deployments = [deployments]
        
        if not recent_deployments:
            return [types.TextContent(type="text", text=f"No deployments found in the last {days} days for application {app_uuid}")]
        
        # Calculate metrics
        total_deployments = len(recent_deployments)
        successful = len([d for d in recent_deployments if d.get('status', '').lower() == 'success'])
        failed = len([d for d in recent_deployments if d.get('status', '').lower() in ['failed', 'error']])
        in_progress = len([d for d in recent_deployments if d.get('status', '').lower() in ['running', 'in_progress']])
        
        success_rate = (successful / total_deployments * 100) if total_deployments > 0 else 0
        failure_rate = (failed / total_deployments * 100) if total_deployments > 0 else 0
        
        result = f"""📊 **Deployment Metrics for Application {app_uuid}**
*Analysis Period: Last {days} days*

📈 **Overall Statistics:**
• Total Deployments: {total_deployments}
• Successful: {successful} ({success_rate:.1f}%)
• Failed: {failed} ({failure_rate:.1f}%)
• In Progress: {in_progress}

📊 **Success Rate Analysis:**
"""
        
        if success_rate >= 90:
            result += "🟢 Excellent success rate (≥90%)\n"
        elif success_rate >= 70:
            result += "🟡 Good success rate (70-89%)\n"
        elif success_rate >= 50:
            result += "🟠 Fair success rate (50-69%)\n"
        else:
            result += "🔴 Poor success rate (<50%)\n"
        
        # Calculate timing metrics if we have finish times
        durations = []
        for deployment in recent_deployments:
            started_at = deployment.get('started_at', '')
            finished_at = deployment.get('finished_at', '')
            if started_at and finished_at and finished_at != 'In progress...':
                try:
                    start = datetime.fromisoformat(started_at.replace('Z', '+00:00'))
                    finish = datetime.fromisoformat(finished_at.replace('Z', '+00:00'))
                    duration = (finish - start).total_seconds()
                    durations.append(duration)
                except:
                    continue
        
        if durations:
            avg_duration = sum(durations) / len(durations)
            min_duration = min(durations)
            max_duration = max(durations)
            
            result += f"""
⏱️ **Timing Metrics:**
• Average Duration: {avg_duration/60:.1f} minutes
• Fastest Deployment: {min_duration/60:.1f} minutes
• Slowest Deployment: {max_duration/60:.1f} minutes
"""
        
        result += f"""
💡 **Recommendations:**
• Monitor failed deployments for patterns
• Consider optimizing build times if durations are high
• Review recent successful deployments for best practices
"""
        
        return [types.TextContent(type="text", text=result)]
        
    except requests.exceptions.HTTPError as e:
        logger.error(f"Failed to get deployment metrics for {app_uuid}: {e}")
        error_msg = handle_requests_error(e, f"Unable to get deployment metrics for application {app_uuid}", "coolify-deployment-metrics")
        return [types.TextContent(type="text", text=error_msg)]
    except Exception as e:
        logger.error(f"Failed to get deployment metrics for {app_uuid}: {e}")
        error_msg = format_enhanced_error(e, f"Unexpected error while getting deployment metrics for {app_uuid}", "coolify-deployment-metrics")
        return [types.TextContent(type="text", text=error_msg)]

async def get_application_logs(app_uuid: str, lines: int = 100) -> list[types.TextContent]:
    """Get runtime logs for an application."""
    try:
        base_url = get_coolify_base_url()
        headers = get_coolify_headers()
        
        response = requests.get(f"{base_url}/applications/{app_uuid}/logs?lines={lines}", headers=headers, timeout=30)
        response.raise_for_status()
        
        logs_data = response.json()
        logger.info(f"Successfully retrieved application logs for {app_uuid}")
        
        result = f"📋 **Application Logs for {app_uuid}**\n\n"
        
        # Process logs based on response format
        if isinstance(logs_data, dict):
            logs = logs_data.get('logs', logs_data.get('data', []))
        else:
            logs = logs_data
        
        if isinstance(logs, list):
            for log_entry in logs[-lines:]:
                if isinstance(log_entry, dict):
                    timestamp = log_entry.get('timestamp', '')
                    message = log_entry.get('message', log_entry.get('output', ''))
                    level = log_entry.get('level', log_entry.get('type', 'INFO'))
                    
                    if timestamp:
                        result += f"[{timestamp}] {level}: {message}\n"
                    else:
                        result += f"{level}: {message}\n"
                else:
                    result += f"LOG: {log_entry}\n"
        elif isinstance(logs, str):
            # If logs are returned as a single string
            result += logs
        else:
            result += f"Logs data: {logs}"
        
        return [types.TextContent(type="text", text=result)]
        
    except requests.exceptions.HTTPError as e:
        logger.error(f"Failed to get application logs for {app_uuid}: {e}")
        error_msg = handle_requests_error(e, f"Unable to get application logs for {app_uuid}", "coolify-get-application-logs")
        return [types.TextContent(type="text", text=error_msg)]
    except Exception as e:
        logger.error(f"Failed to get application logs for {app_uuid}: {e}")
        error_msg = format_enhanced_error(e, f"Unexpected error while getting application logs for {app_uuid}", "coolify-get-application-logs")
        return [types.TextContent(type="text", text=error_msg)]

async def debug_deployments_api() -> list[types.TextContent]:
    """Debug function to see raw deployment API response structure."""
    try:
        base_url = get_coolify_base_url()
        headers = get_coolify_headers()
        
        response = requests.get(f"{base_url}/deployments", headers=headers, timeout=30)
        response.raise_for_status()
        
        deployments = response.json()
        
        # Show first few deployments with full structure
        import json
        result = f"🔧 **Coolify Deployments API Debug**\n\n"
        result += f"**Total deployments found:** {len(deployments) if isinstance(deployments, list) else 1}\n\n"
        
        if isinstance(deployments, list) and len(deployments) > 0:
            result += "**First deployment structure:**\n"
            result += f"```json\n{json.dumps(deployments[0], indent=2)}\n```\n\n"
            
            if len(deployments) > 1:
                result += "**Available deployment keys:**\n"
                for i, deployment in enumerate(deployments[:3]):  # Show first 3
                    result += f"Deployment {i+1}: {list(deployment.keys())}\n"
        else:
            result += f"**Response:**\n```json\n{json.dumps(deployments, indent=2)}\n```"
        
        return [types.TextContent(type="text", text=result)]
        
    except requests.exceptions.HTTPError as e:
        logger.error(f"Failed to debug deployments API: {e}")
        error_msg = handle_requests_error(e, "Unable to access deployments API", "debug-deployments-api")
        return [types.TextContent(type="text", text=error_msg)]
    except Exception as e:
        logger.error(f"Failed to debug deployments API: {e}")
        error_msg = format_enhanced_error(e, "Unexpected error while debugging deployments API", "debug-deployments-api")
        return [types.TextContent(type="text", text=error_msg)]

# Tool registration dictionary
DEPLOYMENT_TOOLS = {
    "coolify-get-deployment-logs": {
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
    },
    
    "coolify-watch-deployment": {
        "definition": types.Tool(
            name="coolify-watch-deployment",
            description="Get real-time deployment progress and status.",
            inputSchema={
                "type": "object",
                "required": ["deployment_uuid"],
                "properties": {
                    "deployment_uuid": {
                        "type": "string",
                        "description": "The UUID of the deployment to watch"
                    },
                    "show_progress": {
                        "type": "boolean",
                        "description": "Show detailed progress information",
                        "default": True
                    }
                }
            }
        ),
        "handler": watch_deployment
    },
    
    "coolify-get-recent-deployments": {
        "definition": types.Tool(
            name="coolify-get-recent-deployments",
            description="Get the last N deployments for an application with status.",
            inputSchema={
                "type": "object",
                "required": ["app_uuid"],
                "properties": {
                    "app_uuid": {
                        "type": "string",
                        "description": "The UUID of the application"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of recent deployments to show",
                        "default": 5
                    }
                }
            }
        ),
        "handler": get_recent_deployments
    },
    
    "coolify-deployment-metrics": {
        "definition": types.Tool(
            name="coolify-deployment-metrics",
            description="Get deployment success/failure rates and timing metrics.",
            inputSchema={
                "type": "object",
                "required": ["app_uuid"],
                "properties": {
                    "app_uuid": {
                        "type": "string",
                        "description": "The UUID of the application"
                    },
                    "days": {
                        "type": "integer",
                        "description": "Number of days to analyze",
                        "default": 30
                    }
                }
            }
        ),
        "handler": deployment_metrics
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
                }
            }
        ),
        "handler": get_application_logs
    },
    
    "coolify-debug-deployments-api": {
        "definition": types.Tool(
            name="coolify-debug-deployments-api",
            description="Debug function to see raw deployment API response structure.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        "handler": debug_deployments_api
    }
}