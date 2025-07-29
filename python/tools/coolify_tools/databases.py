"""Database management tools for Coolify API."""

import os
import mcp.types as types
import requests
from utils.logger import setup_logger
from utils.error_handler import handle_requests_error, format_enhanced_error, get_resource_not_found_message
from .base import get_coolify_headers, get_coolify_base_url

# Set up logging
logger = setup_logger("coolify_tools.databases")

# Database Management Functions

async def list_coolify_databases() -> list[types.TextContent]:
    """List all databases in Coolify."""
    try:
        base_url = get_coolify_base_url()
        headers = get_coolify_headers()
        
        response = requests.get(f"{base_url}/databases", headers=headers, timeout=30)
        response.raise_for_status()
        
        databases = response.json()
        
        if not databases:
            return [types.TextContent(type="text", text="✅ No databases found in Coolify.")]
        
        result = f"🗄️ **Coolify Databases** ({len(databases)} found)\n\n"
        
        for db in databases:
            name = db.get('name', 'N/A')
            uuid = db.get('uuid', 'N/A')
            type_name = db.get('type', 'N/A')
            status = db.get('status', 'N/A')
            
            # Status emoji
            status_emoji = "✅" if status == "running" else "❌" if status == "stopped" else "⚠️"
            
            result += f"**{status_emoji} {name}** ({type_name})\n"
            result += f"   • UUID: `{uuid}`\n"
            result += f"   • Status: {status}\n"
            result += f"   • Actions: `coolify-get-database-by-uuid --database_uuid {uuid}`\n\n"
        
        result += f"💡 **Available Actions:**\n"
        result += f"• Get details: `coolify-get-database-by-uuid --database_uuid UUID`\n"
        result += f"• Create database: `coolify-create-database --database_type TYPE --name NAME`\n"
        result += f"• Start/Stop: `coolify-start-database` / `coolify-stop-database`\n"
        
        logger.info(f"Successfully listed {len(databases)} databases")
        return [types.TextContent(type="text", text=result)]
        
    except Exception as e:
        logger.error(f"Failed to list databases: {e}")
        error_msg = handle_requests_error(e, "Unable to list databases", "coolify-list-databases")
        return [types.TextContent(type="text", text=error_msg)]

def _validate_uuid_parameter(uuid_value: str, param_name: str, resource_type: str) -> types.TextContent | None:
    """Validate UUID parameter and return helpful error message if invalid."""
    if not uuid_value:
        return types.TextContent(type="text", text=f"""❌ **Missing Required Parameter: {param_name}**

🔧 **Usage:**
```bash
coolify-get-{resource_type}-by-uuid --{param_name} UUID_HERE
```

💡 **Examples:**
```bash
# Get {resource_type} details
coolify-get-{resource_type}-by-uuid --{param_name} eoks0kg48ksg0k0scsssocok

# List all {resource_type}s to find UUIDs
coolify-list-{resource_type}s
```

🚀 **Get {resource_type.title()} UUIDs:**
• List all: `coolify-list-{resource_type}s`
""")
    
    if len(uuid_value) < 20:  # Basic UUID length check
        return types.TextContent(type="text", text=f"""❌ **Invalid {param_name}: {uuid_value}**

The {param_name} appears to be invalid. UUIDs should be long alphanumeric strings like: `eoks0kg48ksg0k0scsssocok`

💡 **Get valid {resource_type} UUIDs:**
```bash
coolify-list-{resource_type}s
```
""")
    
    return None

async def get_coolify_database_by_uuid(database_uuid: str = None) -> list[types.TextContent]:
    """Get detailed information about a specific database by UUID."""
    
    # Validate UUID parameter
    if validation_error := _validate_uuid_parameter(database_uuid, "database_uuid", "database"):
        return [validation_error]
    
    try:
        base_url = get_coolify_base_url()
        headers = get_coolify_headers()
        
        response = requests.get(f"{base_url}/databases/{database_uuid}", headers=headers, timeout=30)
        response.raise_for_status()
        
        db_data = response.json()
        
        name = db_data.get('name', 'N/A')
        db_type = db_data.get('type', 'N/A')
        status = db_data.get('status', 'N/A')
        environment = db_data.get('environment', {}).get('name', 'N/A')
        server_name = db_data.get('destination', {}).get('name', 'N/A')
        
        # Connection info
        internal_url = db_data.get('internal_db_url', 'N/A')
        external_url = db_data.get('external_db_url', 'N/A')
        
        result = f"""🗄️ **Database Information:**
Name: {name}
UUID: {database_uuid}
Type: {db_type}
Status: {status}
Environment: {environment}
Server: {server_name}

🔗 **Connection Information:**
Internal URL: {internal_url}
External URL: {external_url}

🛠️ **Available Actions:**
• Start: `coolify-start-database --database_uuid {database_uuid}`
• Stop: `coolify-stop-database --database_uuid {database_uuid}`
• Restart: `coolify-restart-database --database_uuid {database_uuid}`
• Delete: `coolify-delete-database --database_uuid {database_uuid} --confirm true`
"""
        
        logger.info(f"Successfully retrieved database info for {database_uuid}")
        return [types.TextContent(type="text", text=result)]
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            logger.error(f"Database {database_uuid} not found")
            error_msg = get_resource_not_found_message("database", database_uuid, "coolify-get-database-by-uuid")
            return [types.TextContent(type="text", text=error_msg)]
        else:
            logger.error(f"Failed to get database info for {database_uuid}: {e}")
            error_msg = handle_requests_error(e, f"Unable to retrieve database {database_uuid}", "coolify-get-database-by-uuid")
            return [types.TextContent(type="text", text=error_msg)]
    except Exception as e:
        logger.error(f"Failed to get database info for {database_uuid}: {e}")
        return [types.TextContent(type="text", text=f"❌ Failed to get database info: {str(e)}")]

async def create_coolify_database(database_type: str = None, name: str = None, description: str = None, 
                                environment_name: str = "production", server_uuid: str = None, 
                                project_uuid: str = None, postgres_user: str = None, 
                                postgres_password: str = None, postgres_db: str = None,
                                instant_deploy: bool = True) -> list[types.TextContent]:
    """Create a new database in Coolify."""
    
    # Usage guidance and parameter validation
    if not database_type or not name or not server_uuid or not project_uuid:
        missing_params = []
        if not database_type: missing_params.append("database_type")
        if not name: missing_params.append("name") 
        if not server_uuid: missing_params.append("server_uuid")
        if not project_uuid: missing_params.append("project_uuid")
        
        return [types.TextContent(type="text", text=f"""❌ **Missing Required Parameters: {', '.join(missing_params)}**

🔧 **Usage:**
```bash
coolify-create-database \\
  --database_type postgresql \\
  --name myapp-db \\
  --server_uuid csgkk88okkgkwg8w0g8og8c8 \\
  --project_uuid l8cog4c48w48kckkcgos8cwg
```

📋 **Required Parameters:**
• **database_type**: postgresql, mysql, mariadb, mongodb, redis, dragonfly, keydb, clickhouse
• **name**: Database name (e.g., 'myapp-db', 'redis-cache')
• **server_uuid**: Server UUID (get with `coolify-get-deployment-info`)
• **project_uuid**: Project UUID (get with `coolify-list-projects`)

🔧 **Optional Parameters:**
• **description**: Database description
• **environment_name**: Environment (default: production)
• **postgres_user**: Database username (auto-generated if not provided)
• **postgres_password**: Database password (auto-generated if not provided)
• **postgres_db**: Database name (defaults to main database)

💡 **Examples:**
```bash
# PostgreSQL with custom credentials
coolify-create-database --database_type postgresql --name myapp-db --server_uuid SERVER_UUID --project_uuid PROJECT_UUID --postgres_user myuser --postgres_password mypass

# Redis cache
coolify-create-database --database_type redis --name app-cache --server_uuid SERVER_UUID --project_uuid PROJECT_UUID

# MongoDB with description
coolify-create-database --database_type mongodb --name user-data --description "User data storage" --server_uuid SERVER_UUID --project_uuid PROJECT_UUID
```

🚀 **Get Required UUIDs:**
• Server UUID: `coolify-get-deployment-info`
• Project UUID: `coolify-list-projects`
""")]
    
    try:
        base_url = get_coolify_base_url()
        headers = get_coolify_headers()
        
        # Map database types to their proper endpoint paths
        db_type_mapping = {
            "postgresql": "databases/postgresql",
            "mysql": "databases/mysql", 
            "mariadb": "databases/mariadb",
            "mongodb": "databases/mongodb",
            "redis": "databases/redis",
            "dragonfly": "databases/dragonfly",
            "keydb": "databases/keydb",
            "clickhouse": "databases/clickhouse"
        }
        
        if database_type not in db_type_mapping:
            return [types.TextContent(type="text", text=f"""❌ **Unsupported database type: {database_type}**

✅ **Supported database types:**
• postgresql - PostgreSQL database
• mysql - MySQL database  
• mariadb - MariaDB database
• mongodb - MongoDB document database
• redis - Redis key-value store
• dragonfly - Dragonfly in-memory database
• keydb - KeyDB (Redis alternative)
• clickhouse - ClickHouse analytics database

💡 **Example:**
```bash
coolify-create-database --database_type postgresql --name myapp-db --server_uuid {server_uuid or 'SERVER_UUID'} --project_uuid {project_uuid or 'PROJECT_UUID'}
```
""")]
        
        endpoint = db_type_mapping[database_type]
        
        # Build payload based on database type
        payload = {}
        
        # Common fields
        if name:
            payload["name"] = name
        if description:
            payload["description"] = description
        if environment_name:
            payload["environment_name"] = environment_name
        if server_uuid:
            payload["server_uuid"] = server_uuid
        if project_uuid:
            payload["project_uuid"] = project_uuid
        if instant_deploy is not None:
            payload["instant_deploy"] = instant_deploy
            
        # PostgreSQL specific fields
        if database_type == "postgresql":
            if postgres_user:
                payload["postgres_user"] = postgres_user
            if postgres_password:
                payload["postgres_password"] = postgres_password
            if postgres_db:
                payload["postgres_db"] = postgres_db
                
        # MySQL/MariaDB specific fields
        elif database_type in ["mysql", "mariadb"]:
            if postgres_user:  # Reuse for mysql_user
                payload["mysql_user"] = postgres_user
            if postgres_password:  # Reuse for mysql_password
                payload["mysql_password"] = postgres_password
            if postgres_db:  # Reuse for mysql_database
                payload["mysql_database"] = postgres_db
                
        # MongoDB specific fields
        elif database_type == "mongodb":
            if postgres_user:  # Reuse for mongo_initdb_root_username
                payload["mongo_initdb_root_username"] = postgres_user
            if postgres_password:  # Reuse for mongo_initdb_root_password
                payload["mongo_initdb_root_password"] = postgres_password
        
        response = requests.post(f"{base_url}/{endpoint}", headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        result_data = response.json()
        
        result = f"""✅ **Database Created Successfully!**

📋 **Database Details:**
Name: {name}
Type: {database_type}
Environment: {environment_name}
UUID: {result_data.get('uuid', 'N/A')}

💡 **Next Steps:**
• Get database info: `coolify-get-database-by-uuid --database_uuid {result_data.get('uuid', 'NEW_UUID')}`
• Start database: `coolify-start-database --database_uuid {result_data.get('uuid', 'NEW_UUID')}`
• List all databases: `coolify-list-databases`
"""
        
        logger.info(f"Successfully created {database_type} database: {name}")
        return [types.TextContent(type="text", text=result)]
        
    except Exception as e:
        logger.error(f"Failed to create database {name}: {e}")
        error_msg = handle_requests_error(e, f"Unable to create {database_type} database '{name}'", "coolify-create-database")
        return [types.TextContent(type="text", text=error_msg)]

async def start_coolify_database(database_uuid: str) -> list[types.TextContent]:
    """Start a database in Coolify."""
    try:
        base_url = get_coolify_base_url()
        headers = get_coolify_headers()
        
        response = requests.get(f"{base_url}/databases/{database_uuid}/start", headers=headers, timeout=30)
        response.raise_for_status()
        
        result = f"""✅ **Database Started Successfully!**

UUID: {database_uuid}

💡 **Next Steps:**
• Check status: `coolify-get-database-by-uuid --database_uuid {database_uuid}`
• View all databases: `coolify-list-databases`
"""
        
        logger.info(f"Successfully started database {database_uuid}")
        return [types.TextContent(type="text", text=result)]
        
    except Exception as e:
        logger.error(f"Failed to start database {database_uuid}: {e}")
        error_msg = handle_requests_error(e, f"Unable to start database {database_uuid}", "coolify-start-database")
        return [types.TextContent(type="text", text=error_msg)]

async def stop_coolify_database(database_uuid: str) -> list[types.TextContent]:
    """Stop a database in Coolify."""
    try:
        base_url = get_coolify_base_url()
        headers = get_coolify_headers()
        
        response = requests.get(f"{base_url}/databases/{database_uuid}/stop", headers=headers, timeout=30)
        response.raise_for_status()
        
        result = f"""✅ **Database Stopped Successfully!**

UUID: {database_uuid}

💡 **Next Steps:**
• Check status: `coolify-get-database-by-uuid --database_uuid {database_uuid}`
• Start database: `coolify-start-database --database_uuid {database_uuid}`
"""
        
        logger.info(f"Successfully stopped database {database_uuid}")
        return [types.TextContent(type="text", text=result)]
        
    except Exception as e:
        logger.error(f"Failed to stop database {database_uuid}: {e}")
        error_msg = handle_requests_error(e, f"Unable to stop database {database_uuid}", "coolify-stop-database")
        return [types.TextContent(type="text", text=error_msg)]

async def restart_coolify_database(database_uuid: str) -> list[types.TextContent]:
    """Restart a database in Coolify."""
    try:
        base_url = get_coolify_base_url()
        headers = get_coolify_headers()
        
        response = requests.get(f"{base_url}/databases/{database_uuid}/restart", headers=headers, timeout=30)
        response.raise_for_status()
        
        result = f"""✅ **Database Restarted Successfully!**

UUID: {database_uuid}

💡 **Next Steps:**
• Check status: `coolify-get-database-by-uuid --database_uuid {database_uuid}`
• View all databases: `coolify-list-databases`
"""
        
        logger.info(f"Successfully restarted database {database_uuid}")
        return [types.TextContent(type="text", text=result)]
        
    except Exception as e:
        logger.error(f"Failed to restart database {database_uuid}: {e}")
        error_msg = handle_requests_error(e, f"Unable to restart database {database_uuid}", "coolify-restart-database")
        return [types.TextContent(type="text", text=error_msg)]

async def delete_coolify_database(database_uuid: str, confirm: bool = False) -> list[types.TextContent]:
    """Delete a database in Coolify."""
    if not confirm:
        return [types.TextContent(type="text", text="⚠️ **Database deletion requires confirmation!**\n\nTo delete the database, use:\n`coolify-delete-database --database_uuid {database_uuid} --confirm true`\n\n❌ **Warning:** This action cannot be undone!")]
    
    try:
        base_url = get_coolify_base_url()
        headers = get_coolify_headers()
        
        response = requests.delete(f"{base_url}/databases/{database_uuid}", headers=headers, timeout=30)
        response.raise_for_status()
        
        result = f"""✅ **Database Deleted Successfully!**

UUID: {database_uuid}

💡 **Next Steps:**
• View remaining databases: `coolify-list-databases`
"""
        
        logger.info(f"Successfully deleted database {database_uuid}")
        return [types.TextContent(type="text", text=result)]
        
    except Exception as e:
        logger.error(f"Failed to delete database {database_uuid}: {e}")
        error_msg = handle_requests_error(e, f"Unable to delete database {database_uuid}", "coolify-delete-database")
        return [types.TextContent(type="text", text=error_msg)]

# Tool Registration Dictionaries

DATABASE_TOOLS = {
    "coolify-list-databases": {
        "definition": types.Tool(
            name="coolify-list-databases",
            description="List all databases in Coolify.",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        ),
        "handler": list_coolify_databases
    },
    
    "coolify-get-database-by-uuid": {
        "definition": types.Tool(
            name="coolify-get-database-by-uuid",
            description="Get detailed information about a specific database by UUID.",
            inputSchema={
                "type": "object",
                "required": [],  # Made optional so we can provide helpful guidance
                "properties": {
                    "database_uuid": {
                        "type": "string",
                        "description": "The UUID of the database to get information for"
                    }
                },
                "additionalProperties": False
            }
        ),
        "handler": get_coolify_database_by_uuid
    },
    
    "coolify-create-database": {
        "definition": types.Tool(
            name="coolify-create-database",
            description="Create a new database in Coolify. Supports PostgreSQL, MySQL, MariaDB, MongoDB, Redis, DragonFly, KeyDB, and Clickhouse.",
            inputSchema={
                "type": "object",
                "required": [],  # Made optional so we can provide helpful guidance
                "properties": {
                    "database_type": {
                        "type": "string",
                        "enum": ["postgresql", "mysql", "mariadb", "mongodb", "redis", "dragonfly", "keydb", "clickhouse"],
                        "description": "Type of database to create"
                    },
                    "name": {
                        "type": "string",
                        "description": "Name for the database"
                    },
                    "server_uuid": {
                        "type": "string",
                        "description": "UUID of the server to deploy the database on (required)"
                    },
                    "project_uuid": {
                        "type": "string",
                        "description": "UUID of the project to create the database in (required)"
                    },
                    "description": {
                        "type": "string",
                        "description": "Optional description for the database"
                    },
                    "environment_name": {
                        "type": "string",
                        "default": "production",
                        "description": "Environment name (default: production)"
                    },
                    "postgres_user": {
                        "type": "string",
                        "description": "Database username (postgres_user for PostgreSQL, mysql_user for MySQL/MariaDB, mongo_initdb_root_username for MongoDB)"
                    },
                    "postgres_password": {
                        "type": "string",
                        "description": "Database password (postgres_password for PostgreSQL, mysql_password for MySQL/MariaDB, mongo_initdb_root_password for MongoDB)"
                    },
                    "postgres_db": {
                        "type": "string",
                        "description": "Database name (postgres_db for PostgreSQL, mysql_database for MySQL/MariaDB)"
                    },
                    "instant_deploy": {
                        "type": "boolean",
                        "default": True,
                        "description": "Whether to deploy the database immediately after creation"
                    }
                },
                "additionalProperties": False
            }
        ),
        "handler": create_coolify_database
    },
    
    "coolify-start-database": {
        "definition": types.Tool(
            name="coolify-start-database",
            description="Start a database in Coolify.",
            inputSchema={
                "type": "object",
                "required": ["database_uuid"],
                "properties": {
                    "database_uuid": {
                        "type": "string",
                        "description": "The UUID of the database to start"
                    }
                },
                "additionalProperties": False
            }
        ),
        "handler": start_coolify_database
    },
    
    "coolify-stop-database": {
        "definition": types.Tool(
            name="coolify-stop-database",
            description="Stop a database in Coolify.",
            inputSchema={
                "type": "object",
                "required": ["database_uuid"],
                "properties": {
                    "database_uuid": {
                        "type": "string",
                        "description": "The UUID of the database to stop"
                    }
                },
                "additionalProperties": False
            }
        ),
        "handler": stop_coolify_database
    },
    
    "coolify-restart-database": {
        "definition": types.Tool(
            name="coolify-restart-database",
            description="Restart a database in Coolify.",
            inputSchema={
                "type": "object",
                "required": ["database_uuid"],
                "properties": {
                    "database_uuid": {
                        "type": "string",
                        "description": "The UUID of the database to restart"
                    }
                },
                "additionalProperties": False
            }
        ),
        "handler": restart_coolify_database
    },
    
    "coolify-delete-database": {
        "definition": types.Tool(
            name="coolify-delete-database",
            description="Delete a database in Coolify.",
            inputSchema={
                "type": "object",
                "required": ["database_uuid"],
                "properties": {
                    "database_uuid": {
                        "type": "string",
                        "description": "The UUID of the database to delete"
                    },
                    "confirm": {
                        "type": "boolean",
                        "default": False,
                        "description": "Confirmation that you want to delete the database"
                    }
                },
                "additionalProperties": False
            }
        ),
        "handler": delete_coolify_database
    }
}