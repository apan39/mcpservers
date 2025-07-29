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
        
        response = requests.get(f"{base_url}/applications/{app_uuid}/deployments", headers=headers, timeout=30)
        response.raise_for_status()
        
        deployments = response.json()
        logger.info(f"Successfully retrieved deployments for application {app_uuid}")
        
        if not deployments or len(deployments) == 0:
            return [types.TextContent(type="text", text=f"No deployments found for application {app_uuid}")]
        
        # Sort by created date and limit results
        if isinstance(deployments, list):
            sorted_deployments = sorted(deployments, key=lambda x: x.get('created_at', ''), reverse=True)
            recent_deployments = sorted_deployments[:limit]
        else:
            recent_deployments = [deployments]
        
        result = f"📋 **Recent Deployments for Application {app_uuid}**\n\n"
        
        for i, deployment in enumerate(recent_deployments, 1):
            uuid = deployment.get('uuid', 'N/A')
            status = deployment.get('status', 'N/A')
            created_at = deployment.get('created_at', 'N/A')
            finished_at = deployment.get('finished_at', 'In progress...')
            
            # Add status emoji
            status_emoji = {
                'success': '✅',
                'failed': '❌',
                'error': '❌',
                'running': '⏳',
                'in_progress': '⏳',
                'cancelled': '⏹️'
            }.get(status.lower(), 'ℹ️')
            
            result += f"""{i}. {status_emoji} **Deployment {uuid[:8]}...**
   Status: {status}
   Started: {created_at}
   Finished: {finished_at}
   
"""
        
        result += f"""
💡 **Commands:**
• View logs: `coolify-get-deployment-logs --deployment_uuid DEPLOYMENT_UUID`
• Watch deployment: `coolify-watch-deployment --deployment_uuid DEPLOYMENT_UUID`
"""
        
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
        
        response = requests.get(f"{base_url}/applications/{app_uuid}/deployments", headers=headers, timeout=30)
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
    }
}