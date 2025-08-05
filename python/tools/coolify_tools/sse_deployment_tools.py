"""SSE-enabled deployment monitoring tools."""

import mcp.types as types
from .sse_deployment_monitor import deployment_monitor
from .base import logger

async def start_deployment_with_sse_monitoring(app_uuid: str, force: bool = False) -> list[types.TextContent]:
    """Start deployment and begin real-time SSE monitoring."""
    try:
        result = await deployment_monitor.start_deployment_with_monitoring(app_uuid, force)
        
        response = f"""🚀 **Deployment Started with Real-time Monitoring**

Application UUID: {app_uuid}
Deployment UUID: {result['deployment_uuid']}
Status: {result['status']}

**Real-time Monitoring Active ✅**
• Deployment progress will be tracked automatically
• SSE stream available at: `/sse/deployment/{result['deployment_uuid']}`
• Monitoring will continue until deployment completion

**Next Steps:**
1. Use `coolify-get-sse-deployment-status` to check current status
2. Access SSE stream for real-time updates
3. Wait for completion notification

⚠️ **Important:** This prevents command overlap by providing real-time status updates!
"""
        
        return [types.TextContent(type="text", text=response)]
        
    except Exception as e:
        logger.error(f"Failed to start SSE deployment monitoring: {e}")
        return [types.TextContent(type="text", text=f"Error starting deployment monitoring: {e}")]

async def get_sse_deployment_status(deployment_uuid: str) -> list[types.TextContent]:
    """Get current status of SSE-monitored deployment."""
    try:
        status = deployment_monitor.get_deployment_status(deployment_uuid)
        
        if not status:
            return [types.TextContent(type="text", text=f"❌ Deployment {deployment_uuid} not found in monitoring system")]
        
        # Format status response
        completion_status = "✅ Completed" if status['completed'] else "⏳ In Progress"
        success_indicator = ""
        
        if status['completed']:
            if status.get('success'):
                success_indicator = "✅ **SUCCESS**"
            else:
                success_indicator = "❌ **FAILED**"
        
        response = f"""📊 **SSE Deployment Status**

Deployment UUID: {deployment_uuid}
Application UUID: {status['app_uuid']}
Status: {status['status'].upper()}
Completion: {completion_status}
{success_indicator}

**Timeline:**
• Started: {status['started_at']}
• Last Check: {status.get('last_check', 'N/A')}
"""
        
        if status['completed']:
            response += f"• Finished: {status.get('finished_at', 'N/A')}\n"
        
        # Show recent progress events
        events = status.get('progress_events', [])
        if events:
            response += f"\n**Recent Progress Events:**\n"
            for event in events[-3:]:  # Show last 3 events
                response += f"• {event['timestamp']}: {event['status']}\n"
        
        # Add streaming info for active deployments
        if not status['completed']:
            response += f"\n**Real-time Stream:** Available at `/sse/deployment/{deployment_uuid}`"
            response += f"\n**Monitoring:** Active - no command overlap risk"
        
        return [types.TextContent(type="text", text=response)]
        
    except Exception as e:
        logger.error(f"Failed to get SSE deployment status: {e}")
        return [types.TextContent(type="text", text=f"Error getting deployment status: {e}")]

async def list_active_sse_deployments() -> list[types.TextContent]:
    """List all currently monitored deployments."""
    try:
        deployments = deployment_monitor.list_active_deployments()
        
        if not deployments:
            return [types.TextContent(type="text", text="📊 **No Active SSE Deployments**\n\nNo deployments are currently being monitored in real-time.")]
        
        response = f"📊 **Active SSE Deployment Monitoring** ({len(deployments)} deployments)\n\n"
        
        for deployment_uuid, data in deployments.items():
            status_icon = "⏳" if not data['completed'] else ("✅" if data.get('success') else "❌")
            
            response += f"{status_icon} **{deployment_uuid[:8]}...{deployment_uuid[-8:]}**\n"
            response += f"  • App: {data['app_uuid']}\n"
            response += f"  • Status: {data['status']}\n"
            response += f"  • Started: {data['started_at']}\n"
            
            if data['completed']:
                response += f"  • Completed: {data.get('finished_at', 'N/A')}\n"
            else:
                response += f"  • Real-time monitoring active ✅\n"
            
            response += "\n"
        
        response += "**Benefits:**\n"
        response += "• Real-time status updates\n"
        response += "• No command overlap issues\n"
        response += "• Automatic completion detection\n"
        
        return [types.TextContent(type="text", text=response)]
        
    except Exception as e:
        logger.error(f"Failed to list active deployments: {e}")
        return [types.TextContent(type="text", text=f"Error listing active deployments: {e}")]

async def stop_sse_deployment_monitoring(deployment_uuid: str) -> list[types.TextContent]:
    """Stop monitoring a specific deployment."""
    try:
        success = deployment_monitor.stop_monitoring(deployment_uuid)
        
        if success:
            response = f"""🛑 **SSE Deployment Monitoring Stopped**

Deployment UUID: {deployment_uuid}
Status: Monitoring stopped
Action: Manual stop requested

The real-time monitoring for this deployment has been terminated.
You can still use regular Coolify tools to check deployment status.
"""
        else:
            response = f"❌ **Failed to Stop Monitoring**\n\nDeployment {deployment_uuid} was not found in the monitoring system."
        
        return [types.TextContent(type="text", text=response)]
        
    except Exception as e:
        logger.error(f"Failed to stop deployment monitoring: {e}")
        return [types.TextContent(type="text", text=f"Error stopping deployment monitoring: {e}")]

# Tool definitions for registry  
SSE_DEPLOYMENT_TOOLS = {
    "coolify-deploy-with-sse-monitoring": {
        "definition": types.Tool(
            name="coolify-deploy-with-sse-monitoring",
            description="Start deployment with real-time SSE monitoring to prevent command overlap.",
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
                },
                "additionalProperties": False
            }
        ),
        "handler": start_deployment_with_sse_monitoring
    },
    
    "coolify-get-sse-deployment-status": {
        "definition": types.Tool(
            name="coolify-get-sse-deployment-status",
            description="Get current status of SSE-monitored deployment with real-time progress.",
            inputSchema={
                "type": "object",
                "required": ["deployment_uuid"],
                "properties": {
                    "deployment_uuid": {
                        "type": "string",
                        "description": "The UUID of the deployment to check"
                    }
                },
                "additionalProperties": False
            }
        ),
        "handler": get_sse_deployment_status
    },
    
    "coolify-list-active-sse-deployments": {
        "definition": types.Tool(
            name="coolify-list-active-sse-deployments", 
            description="List all currently monitored deployments with real-time status.",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        ),
        "handler": list_active_sse_deployments
    },
    
    "coolify-stop-sse-deployment-monitoring": {
        "definition": types.Tool(
            name="coolify-stop-sse-deployment-monitoring",
            description="Stop real-time monitoring for a specific deployment.",
            inputSchema={
                "type": "object",
                "required": ["deployment_uuid"],
                "properties": {
                    "deployment_uuid": {
                        "type": "string",
                        "description": "The UUID of the deployment to stop monitoring"
                    }
                },
                "additionalProperties": False
            }
        ),
        "handler": stop_sse_deployment_monitoring
    }
}