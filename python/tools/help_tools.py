"""Help and categorization tools for the MCP server."""

import mcp.types as types
from utils.logger import setup_logger

# Set up logging
logger = setup_logger("help_tools")

# Tool categories with descriptions and metadata
TOOL_CATEGORIES = {
    "math": {
        "name": "Math & Calculations",
        "description": "Tools for mathematical operations and calculations",
        "icon": "🧮",
        "color": "#4CAF50"
    },
    "text": {
        "name": "Text Processing",
        "description": "Tools for text manipulation and analysis",
        "icon": "📝",
        "color": "#2196F3"
    },
    "web": {
        "name": "Web Scraping",
        "description": "Tools for web content extraction and crawling",
        "icon": "🌐",
        "color": "#FF9800"
    },
    "coolify": {
        "name": "Coolify API",
        "description": "Tools for Coolify deployment and management",
        "icon": "🚀",
        "color": "#9C27B0"
    },
    "deployment": {
        "name": "Deployment Operations",
        "description": "Tools for application deployment and monitoring",
        "icon": "⚙️",
        "color": "#607D8B"
    },
    "config": {
        "name": "Configuration Management",
        "description": "Tools for managing application configuration",
        "icon": "🔧",
        "color": "#795548"
    },
    "monitoring": {
        "name": "Monitoring & Health",
        "description": "Tools for application monitoring and health checks",
        "icon": "📊",
        "color": "#E91E63"
    }
}

# Tool metadata with categories and complexity levels
TOOL_METADATA = {
    # Math tools
    "add-numbers": {"category": "math", "complexity": "basic", "tags": ["arithmetic", "addition"]},
    "multiply-numbers": {"category": "math", "complexity": "basic", "tags": ["arithmetic", "multiplication"]},
    "calculate-percentage": {"category": "math", "complexity": "basic", "tags": ["percentage", "calculation"]},
    
    # Text tools
    "string-operations": {"category": "text", "complexity": "basic", "tags": ["strings", "formatting"]},
    "word-count": {"category": "text", "complexity": "basic", "tags": ["analysis", "counting"]},
    "format-text": {"category": "text", "complexity": "intermediate", "tags": ["formatting", "case-conversion"]},
    
    # Web tools
    "crawl-url": {"category": "web", "complexity": "advanced", "tags": ["scraping", "extraction", "content"]},
    
    # Coolify core tools
    "coolify-get-version": {"category": "coolify", "complexity": "basic", "tags": ["info", "version"]},
    "coolify-list-projects": {"category": "coolify", "complexity": "basic", "tags": ["listing", "projects"]},
    "coolify-list-servers": {"category": "coolify", "complexity": "basic", "tags": ["listing", "servers"]},
    "coolify-list-applications": {"category": "coolify", "complexity": "basic", "tags": ["listing", "apps"]},
    "coolify-create-github-app": {"category": "deployment", "complexity": "advanced", "tags": ["github", "deployment", "creation"]},
    
    # Application management
    "coolify-get-application-info": {"category": "coolify", "complexity": "basic", "tags": ["info", "applications"]},
    "coolify-restart-application": {"category": "deployment", "complexity": "intermediate", "tags": ["restart", "control"]},
    "coolify-stop-application": {"category": "deployment", "complexity": "intermediate", "tags": ["stop", "control"]},
    "coolify-start-application": {"category": "deployment", "complexity": "intermediate", "tags": ["start", "control"]},
    "coolify-delete-application": {"category": "deployment", "complexity": "advanced", "tags": ["delete", "destructive"]},
    
    # Deployment operations
    "coolify-deploy-application": {"category": "deployment", "complexity": "intermediate", "tags": ["deploy", "build"]},
    "coolify-get-deployment-logs": {"category": "monitoring", "complexity": "intermediate", "tags": ["logs", "debugging"]},
    "coolify-get-deployment-info": {"category": "deployment", "complexity": "basic", "tags": ["info", "deployment"]},
    "coolify-watch-deployment": {"category": "monitoring", "complexity": "advanced", "tags": ["monitoring", "real-time"]},
    "coolify-get-recent-deployments": {"category": "deployment", "complexity": "basic", "tags": ["history", "deployments"]},
    "coolify-deployment-metrics": {"category": "monitoring", "complexity": "intermediate", "tags": ["metrics", "analytics"]},
    
    # Configuration management
    "coolify-set-env-variable": {"category": "config", "complexity": "intermediate", "tags": ["environment", "variables"]},
    "coolify-delete-env-variable": {"category": "config", "complexity": "intermediate", "tags": ["environment", "cleanup"]},
    "coolify-bulk-update-env": {"category": "config", "complexity": "advanced", "tags": ["bulk", "environment", "efficiency"]},
    "coolify-update-build-settings": {"category": "config", "complexity": "advanced", "tags": ["build", "configuration"]},
    "coolify-manage-domains": {"category": "config", "complexity": "advanced", "tags": ["domains", "networking"]},
    "coolify-update-resource-limits": {"category": "config", "complexity": "advanced", "tags": ["resources", "limits"]},
    
    # Health and monitoring
    "coolify-update-health-check": {"category": "monitoring", "complexity": "intermediate", "tags": ["health", "configuration"]},
    "coolify-test-health-endpoint": {"category": "monitoring", "complexity": "intermediate", "tags": ["health", "testing"]},
    "coolify-get-application-logs": {"category": "monitoring", "complexity": "basic", "tags": ["logs", "debugging"]},
    
    # Bulk operations
    "coolify-bulk-restart": {"category": "deployment", "complexity": "advanced", "tags": ["bulk", "restart", "efficiency"]},
    "coolify-bulk-deploy": {"category": "deployment", "complexity": "advanced", "tags": ["bulk", "deploy", "efficiency"]},
    "coolify-project-status": {"category": "monitoring", "complexity": "intermediate", "tags": ["status", "overview"]},
}

def register_help_tools(tool_registry):
    """Register help and categorization tools with the tool registry."""
    
    tool_registry["list-tool-categories"] = {
        "definition": types.Tool(
            name="list-tool-categories",
            description="List all available tool categories with descriptions and counts.",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        ),
        "handler": list_tool_categories
    }
    
    tool_registry["get-tools-by-category"] = {
        "definition": types.Tool(
            name="get-tools-by-category",
            description="Get all tools in a specific category with detailed information.",
            inputSchema={
                "type": "object",
                "required": ["category"],
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "Category name (math, text, web, coolify, deployment, config, monitoring)",
                        "enum": list(TOOL_CATEGORIES.keys())
                    }
                },
                "additionalProperties": False
            }
        ),
        "handler": get_tools_by_category
    }
    
    tool_registry["search-tools"] = {
        "definition": types.Tool(
            name="search-tools",
            description="Search for tools by name, description, or tags.",
            inputSchema={
                "type": "object",
                "required": ["query"],
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (tool name, description keywords, or tags)"
                    },
                    "category": {
                        "type": "string",
                        "description": "Optional category filter",
                        "enum": list(TOOL_CATEGORIES.keys())
                    },
                    "complexity": {
                        "type": "string",
                        "description": "Optional complexity filter",
                        "enum": ["basic", "intermediate", "advanced"]
                    }
                },
                "additionalProperties": False
            }
        ),
        "handler": search_tools
    }
    
    tool_registry["get-tool-info"] = {
        "definition": types.Tool(
            name="get-tool-info",
            description="Get detailed information about a specific tool including usage examples.",
            inputSchema={
                "type": "object",
                "required": ["tool_name"],
                "properties": {
                    "tool_name": {
                        "type": "string",
                        "description": "Name of the tool to get information about"
                    }
                },
                "additionalProperties": False
            }
        ),
        "handler": get_tool_info
    }
    
    tool_registry["get-learning-path"] = {
        "definition": types.Tool(
            name="get-learning-path",
            description="Get a recommended learning path for tools based on complexity and category.",
            inputSchema={
                "type": "object",
                "properties": {
                    "focus": {
                        "type": "string",
                        "description": "Focus area for learning path",
                        "enum": ["beginner", "deployment", "monitoring", "configuration", "automation"]
                    }
                },
                "additionalProperties": False
            }
        ),
        "handler": get_learning_path
    }

async def list_tool_categories() -> list[types.TextContent]:
    """List all available tool categories with descriptions and tool counts."""
    try:
        result = "📚 **Available Tool Categories**\n\n"
        
        # Count tools in each category
        category_counts = {}
        for tool_name, metadata in TOOL_METADATA.items():
            category = metadata["category"]
            category_counts[category] = category_counts.get(category, 0) + 1
        
        # Display categories
        for category_id, category_info in TOOL_CATEGORIES.items():
            count = category_counts.get(category_id, 0)
            result += f"{category_info['icon']} **{category_info['name']}** ({count} tools)\n"
            result += f"   {category_info['description']}\n\n"
        
        result += "💡 **Usage:**\n"
        result += "• Use `get-tools-by-category` to see tools in a specific category\n"
        result += "• Use `search-tools` to find tools by keywords\n"
        result += "• Use `get-tool-info` to get detailed information about a specific tool\n"
        
        logger.info("Successfully listed tool categories")
        return [types.TextContent(type="text", text=result)]
        
    except Exception as e:
        logger.error(f"Error listing tool categories: {str(e)}")
        return [types.TextContent(type="text", text=f"❌ Error listing categories: {str(e)}")]

async def get_tools_by_category(category: str) -> list[types.TextContent]:
    """Get all tools in a specific category with detailed information."""
    try:
        if category not in TOOL_CATEGORIES:
            return [types.TextContent(type="text", text=f"❌ Unknown category: {category}")]
        
        category_info = TOOL_CATEGORIES[category]
        result = f"{category_info['icon']} **{category_info['name']} Tools**\n\n"
        result += f"{category_info['description']}\n\n"
        
        # Find tools in this category
        tools_in_category = []
        for tool_name, metadata in TOOL_METADATA.items():
            if metadata["category"] == category:
                tools_in_category.append((tool_name, metadata))
        
        if not tools_in_category:
            result += "No tools found in this category.\n"
            return [types.TextContent(type="text", text=result)]
        
        # Group by complexity
        complexity_groups = {"basic": [], "intermediate": [], "advanced": []}
        for tool_name, metadata in tools_in_category:
            complexity = metadata.get("complexity", "basic")
            complexity_groups[complexity].append((tool_name, metadata))
        
        # Display tools by complexity
        complexity_icons = {"basic": "🟢", "intermediate": "🟡", "advanced": "🔴"}
        
        for complexity in ["basic", "intermediate", "advanced"]:
            tools = complexity_groups[complexity]
            if tools:
                result += f"### {complexity_icons[complexity]} {complexity.title()} Tools\n\n"
                for tool_name, metadata in tools:
                    tags = ", ".join(metadata.get("tags", []))
                    result += f"• **{tool_name}**"
                    if tags:
                        result += f" | Tags: {tags}"
                    result += "\n"
                result += "\n"
        
        result += "💡 Use `get-tool-info <tool-name>` for detailed information and examples.\n"
        
        logger.info(f"Successfully listed tools for category: {category}")
        return [types.TextContent(type="text", text=result)]
        
    except Exception as e:
        logger.error(f"Error getting tools by category: {str(e)}")
        return [types.TextContent(type="text", text=f"❌ Error getting tools for category {category}: {str(e)}")]

async def search_tools(query: str, category: str = None, complexity: str = None) -> list[types.TextContent]:
    """Search for tools by name, description, or tags."""
    try:
        query_lower = query.lower()
        results = []
        
        for tool_name, metadata in TOOL_METADATA.items():
            # Apply filters
            if category and metadata["category"] != category:
                continue
            if complexity and metadata.get("complexity") != complexity:
                continue
            
            # Search in tool name, tags
            tags = metadata.get("tags", [])
            tags_str = " ".join(tags).lower()
            
            if (query_lower in tool_name.lower() or 
                query_lower in tags_str or
                any(query_lower in tag.lower() for tag in tags)):
                
                category_info = TOOL_CATEGORIES[metadata["category"]]
                results.append({
                    "name": tool_name,
                    "category": category_info["name"],
                    "category_icon": category_info["icon"],
                    "complexity": metadata.get("complexity", "basic"),
                    "tags": tags
                })
        
        if not results:
            result = f"🔍 **Search Results for '{query}'**\n\n"
            result += "No tools found matching your search criteria.\n\n"
            result += "💡 **Tips:**\n"
            result += "• Try broader search terms\n"
            result += "• Use `list-tool-categories` to see all available categories\n"
            result += "• Remove category or complexity filters\n"
            return [types.TextContent(type="text", text=result)]
        
        result = f"🔍 **Search Results for '{query}'** ({len(results)} found)\n\n"
        
        if category:
            result += f"**Filtered by category:** {TOOL_CATEGORIES[category]['name']}\n"
        if complexity:
            result += f"**Filtered by complexity:** {complexity.title()}\n"
        
        result += "\n"
        
        complexity_icons = {"basic": "🟢", "intermediate": "🟡", "advanced": "🔴"}
        
        for tool in results:
            icon = complexity_icons.get(tool["complexity"], "⚪")
            result += f"{icon} **{tool['name']}** {tool['category_icon']} {tool['category']}\n"
            if tool["tags"]:
                result += f"   Tags: {', '.join(tool['tags'])}\n"
            result += "\n"
        
        result += "💡 Use `get-tool-info <tool-name>` for detailed information and examples.\n"
        
        logger.info(f"Successfully searched tools with query: {query}")
        return [types.TextContent(type="text", text=result)]
        
    except Exception as e:
        logger.error(f"Error searching tools: {str(e)}")
        return [types.TextContent(type="text", text=f"❌ Error searching tools: {str(e)}")]

async def get_tool_info(tool_name: str) -> list[types.TextContent]:
    """Get detailed information about a specific tool including usage examples."""
    try:
        if tool_name not in TOOL_METADATA:
            # Suggest similar tools
            similar = []
            for existing_tool in TOOL_METADATA.keys():
                if tool_name.lower() in existing_tool.lower() or existing_tool.lower() in tool_name.lower():
                    similar.append(existing_tool)
            
            result = f"❌ **Tool '{tool_name}' not found**\n\n"
            if similar:
                result += f"**Did you mean?**\n"
                for s in similar[:3]:
                    result += f"• {s}\n"
                result += "\n"
            result += "💡 Use `search-tools` to find tools or `list-tool-categories` to browse categories.\n"
            return [types.TextContent(type="text", text=result)]
        
        metadata = TOOL_METADATA[tool_name]
        category_info = TOOL_CATEGORIES[metadata["category"]]
        complexity_icons = {"basic": "🟢", "intermediate": "🟡", "advanced": "🔴"}
        
        result = f"📖 **Tool Information: {tool_name}**\n\n"
        result += f"**Category:** {category_info['icon']} {category_info['name']}\n"
        result += f"**Complexity:** {complexity_icons.get(metadata.get('complexity', 'basic'), '⚪')} {metadata.get('complexity', 'basic').title()}\n"
        
        tags = metadata.get("tags", [])
        if tags:
            result += f"**Tags:** {', '.join(tags)}\n"
        
        result += "\n**Description:** "
        
        # Add tool-specific descriptions and examples
        tool_descriptions = {
            "add-numbers": "Add two numbers together. Supports integers and floating-point numbers.",
            "multiply-numbers": "Multiply two numbers together. Supports integers and floating-point numbers.",
            "calculate-percentage": "Calculate percentage of a value. Useful for financial calculations and statistics.",
            "string-operations": "Perform string operations like uppercase, lowercase, reverse, and title case.",
            "word-count": "Count words, characters, and lines in text. Useful for content analysis.",
            "format-text": "Format text using different case styles (camel, snake, kebab, title, sentence).",
            "crawl-url": "Advanced web scraping with content filtering, extraction modes, and selector-based targeting.",
            "coolify-get-version": "Get Coolify instance version and system information.",
            "coolify-list-projects": "List all projects in your Coolify instance.",
            "coolify-list-servers": "List all available servers for deployment.",
            "coolify-list-applications": "List applications, optionally filtered by project UUID.",
            "coolify-create-github-app": "Deploy a GitHub repository to Coolify with configurable build settings.",
            "coolify-get-application-info": "Get detailed information about an application including status and configuration.",
            "coolify-restart-application": "Restart an application. Useful when the app is unresponsive.",
            "coolify-stop-application": "Stop an application. Use for maintenance or resource management.",
            "coolify-start-application": "Start a stopped application.",
            "coolify-delete-application": "Permanently delete an application. Use with caution!",
            "coolify-deploy-application": "Trigger a new deployment for an application.",
            "coolify-get-deployment-logs": "Get logs for a specific deployment to debug issues.",
            "coolify-get-deployment-info": "Get information about a specific deployment.",
            "coolify-watch-deployment": "Monitor deployment progress in real-time.",
            "coolify-get-recent-deployments": "Get recent deployment history for an application.",
            "coolify-deployment-metrics": "Get deployment metrics and statistics.",
            "coolify-set-env-variable": "Set or update an environment variable for an application.",
            "coolify-delete-env-variable": "Delete an environment variable from an application.",
            "coolify-bulk-update-env": "Update multiple environment variables at once for efficiency.",
            "coolify-update-build-settings": "Update build configuration like build pack and commands.",
            "coolify-manage-domains": "Manage custom domains for an application.",
            "coolify-update-resource-limits": "Update CPU and memory limits for an application.",
            "coolify-update-health-check": "Configure health check settings for an application.",
            "coolify-test-health-endpoint": "Test an application's health endpoint manually.",
            "coolify-get-application-logs": "Get runtime logs from an application.",
            "coolify-bulk-restart": "Restart multiple applications simultaneously.",
            "coolify-bulk-deploy": "Deploy multiple applications simultaneously.",
            "coolify-project-status": "Get comprehensive status for all applications in a project."
        }
        
        description = tool_descriptions.get(tool_name, "No detailed description available.")
        result += f"{description}\n\n"
        
        # Add usage examples
        result += "**Usage Examples:**\n"
        
        tool_examples = {
            "add-numbers": [
                "Please add 25 and 37 using add-numbers",
                "Use add-numbers to calculate 15.5 + 23.8"
            ],
            "coolify-create-github-app": [
                "Please deploy https://github.com/user/app to project abc-123 on server xyz-789",
                "Deploy my Next.js app from GitHub with name 'my-nextjs-app'"
            ],
            "coolify-watch-deployment": [
                "Please watch the deployment progress for deployment xyz-789",
                "Monitor my latest deployment in real-time"
            ],
            "crawl-url": [
                "Please crawl https://example.com and extract only the main content",
                "Get headings from https://docs.example.com",
                "Crawl this page but exclude ads: https://news.site.com"
            ]
        }
        
        examples = tool_examples.get(tool_name, [f"Please use {tool_name} to perform its function"])
        for i, example in enumerate(examples, 1):
            result += f"{i}. {example}\n"
        
        result += "\n"
        
        # Add related tools
        related_tools = []
        current_category = metadata["category"]
        for other_tool, other_metadata in TOOL_METADATA.items():
            if (other_tool != tool_name and 
                other_metadata["category"] == current_category and 
                len(related_tools) < 3):
                related_tools.append(other_tool)
        
        if related_tools:
            result += f"**Related Tools:**\n"
            for related in related_tools:
                result += f"• {related}\n"
        
        logger.info(f"Successfully got tool info for: {tool_name}")
        return [types.TextContent(type="text", text=result)]
        
    except Exception as e:
        logger.error(f"Error getting tool info: {str(e)}")
        return [types.TextContent(type="text", text=f"❌ Error getting tool info: {str(e)}")]

async def get_learning_path(focus: str = "beginner") -> list[types.TextContent]:
    """Get a recommended learning path for tools based on complexity and category."""
    try:
        result = f"🎯 **Learning Path: {focus.title()}**\n\n"
        
        if focus == "beginner":
            result += "**Recommended progression for new users:**\n\n"
            result += "**1. Start with Math Tools** 🧮\n"
            result += "• add-numbers → multiply-numbers → calculate-percentage\n"
            result += "• These tools help you understand basic MCP interactions\n\n"
            
            result += "**2. Try Text Processing** 📝\n"
            result += "• string-operations → word-count → format-text\n"
            result += "• Learn how tools handle different data types\n\n"
            
            result += "**3. Explore Coolify Basics** 🚀\n"
            result += "• coolify-get-version → coolify-list-projects → coolify-list-applications\n"
            result += "• Understand your Coolify environment\n\n"
            
            result += "**4. Basic Application Management** ⚙️\n"
            result += "• coolify-get-application-info → coolify-restart-application\n"
            result += "• Learn to check and control your applications\n"
            
        elif focus == "deployment":
            result += "**Master deployment workflows:**\n\n"
            result += "**Prerequisites:** Complete beginner path first\n\n"
            result += "**1. Repository Deployment** 🚀\n"
            result += "• coolify-create-github-app\n"
            result += "• Practice with test repositories\n\n"
            
            result += "**2. Deployment Monitoring** 📊\n"
            result += "• coolify-deploy-application → coolify-watch-deployment\n"
            result += "• coolify-get-deployment-logs → coolify-get-deployment-info\n\n"
            
            result += "**3. Bulk Operations** ⚡\n"
            result += "• coolify-bulk-deploy → coolify-bulk-restart\n"
            result += "• coolify-deployment-metrics\n"
            
        elif focus == "monitoring":
            result += "**Master application monitoring:**\n\n"
            result += "**1. Application Health** 🏥\n"
            result += "• coolify-get-application-info → coolify-test-health-endpoint\n"
            result += "• coolify-update-health-check\n\n"
            
            result += "**2. Logs and Debugging** 🔍\n"
            result += "• coolify-get-application-logs → coolify-get-deployment-logs\n"
            result += "• coolify-get-recent-deployments\n\n"
            
            result += "**3. Project Overview** 📈\n"
            result += "• coolify-project-status → coolify-deployment-metrics\n"
            
        elif focus == "configuration":
            result += "**Master application configuration:**\n\n"
            result += "**1. Environment Variables** 🔧\n"
            result += "• coolify-set-env-variable → coolify-delete-env-variable\n"
            result += "• coolify-bulk-update-env\n\n"
            
            result += "**2. Build Settings** ⚙️\n"
            result += "• coolify-update-build-settings\n"
            result += "• coolify-update-resource-limits\n\n"
            
            result += "**3. Domains and Networking** 🌐\n"
            result += "• coolify-manage-domains\n"
            
        elif focus == "automation":
            result += "**Build advanced automation workflows:**\n\n"
            result += "**Prerequisites:** Complete deployment and monitoring paths\n\n"
            result += "**1. Bulk Operations** ⚡\n"
            result += "• coolify-bulk-restart → coolify-bulk-deploy\n"
            result += "• coolify-bulk-update-env\n\n"
            
            result += "**2. Advanced Monitoring** 📊\n"
            result += "• coolify-watch-deployment → coolify-deployment-metrics\n"
            result += "• coolify-project-status\n\n"
            
            result += "**3. Web Scraping Integration** 🌐\n"
            result += "• crawl-url (advanced usage)\n"
            result += "• Combine with deployment tools for dynamic content\n"
        
        result += "\n💡 **Tips:**\n"
        result += "• Practice each tool individually before combining them\n"
        result += "• Use `get-tool-info <tool-name>` for detailed examples\n"
        result += "• Start with read-only operations before making changes\n"
        
        logger.info(f"Successfully generated learning path for: {focus}")
        return [types.TextContent(type="text", text=result)]
        
    except Exception as e:
        logger.error(f"Error generating learning path: {str(e)}")
        return [types.TextContent(type="text", text=f"❌ Error generating learning path: {str(e)}")]