"""Registry for all Coolify tools."""

from .core import CORE_TOOLS
from .applications import APPLICATION_TOOLS
from .databases import DATABASE_TOOLS
from .services import SERVICE_TOOLS
from .deployments import DEPLOYMENT_TOOLS
from .environments import ENVIRONMENT_TOOLS
from .sse_deployment_tools import SSE_DEPLOYMENT_TOOLS

def register_coolify_tools(tool_registry):
    """Register all Coolify API tools with the tool registry."""
    
    # Register core tools (version, projects, servers, deployment info)
    tool_registry.update(CORE_TOOLS)
    
    # Register application tools
    tool_registry.update(APPLICATION_TOOLS)
    
    # Register database tools
    tool_registry.update(DATABASE_TOOLS)
    
    # Register service tools
    tool_registry.update(SERVICE_TOOLS)
    
    # Register deployment tools
    tool_registry.update(DEPLOYMENT_TOOLS)
    
    # Register environment variable tools
    tool_registry.update(ENVIRONMENT_TOOLS)
    
    # Register SSE deployment monitoring tools
    tool_registry.update(SSE_DEPLOYMENT_TOOLS)