# VS Code Integration Guide - Browser-Use MCP Server

## ✅ Successfully Added to VS Code!

The Browser-Use MCP Server has been successfully added to your VS Code MCP configuration.

## 📋 Configuration Details

**Server Name:** Browser-Use MCP Server  
**URL:** http://localhost:3005/sse  
**Protocol:** SSE (Server-Sent Events)  
**Status:** Enabled  
**API Key:** demo-api-key-123  

## 🔧 Available Tools in VS Code

Your VS Code extension now has access to these browser automation tools:

1. **`create_browser_session`** - Create a new browser session
   - Parameters: `session_id` (required), `headless` (optional)

2. **`navigate_to_url`** - Navigate to any URL
   - Parameters: `session_id` (required), `url` (required)

3. **`get_page_content`** - Extract page content (title, URL, text)
   - Parameters: `session_id` (required)

4. **`execute_task`** - Run AI-powered browser automation tasks
   - Parameters: `session_id` (required), `task` (required), `provider` (optional: "openai" or "anthropic")

5. **`close_session`** - Clean up browser sessions
   - Parameters: `session_id` (required)

6. **`list_sessions`** - View all active browser sessions
   - Parameters: none

## 🚀 Usage Examples in VS Code

### Basic Web Scraping
```
Please create a browser session called "scraper", navigate to https://example.com, and get the page content.
```

### AI-Powered Task Automation
```
Create a browser session and use an AI agent to search for "Model Context Protocol" on Google, then summarize the first 3 results.
```

### Data Extraction
```
Go to https://news.ycombinator.com and extract the titles of the top 10 stories.
```

## 🔄 Workflow Tips

1. **Always create a session first**: Use `create_browser_session` before other operations
2. **Clean up sessions**: Use `close_session` when done to free resources
3. **Monitor sessions**: Use `list_sessions` to see active sessions
4. **Use AI tasks**: The `execute_task` tool can handle complex workflows automatically

## 🛠️ Configuration File Location

The configuration is stored in:
```
/Users/imac_2/Library/Application Support/Code/User/globalStorage/rooveterinaryinc.roo-cline/settings/mcp_settings.json
```

## 🔧 Server Management

**Start Server:**
```bash
cd /Users/imac_2/utveckling/mcpservers/browser-use-mcp
python3 server_simple.py
```

**Check Server Health:**
```bash
curl http://localhost:3005/health
```

**Server Log Output:**
The server runs on port 3005 and logs all operations for debugging.

## 🎯 Pre-configured Settings

- **Protocol**: SSE for real-time communication
- **Authentication**: API key authentication enabled
- **Auto-allow**: All tools are pre-approved for seamless usage
- **Error Handling**: Comprehensive error reporting and logging

## 🔄 Restart Instructions

If you need to restart the VS Code extension or server:

1. **Restart VS Code Extension**: Use Command Palette → "Developer: Reload Window"
2. **Restart Server**: Kill the Python process and run `python3 server_simple.py` again
3. **Check Connection**: Verify with health check endpoint

## 🎉 Ready to Use!

Your VS Code is now equipped with powerful browser automation capabilities through the Browser-Use MCP Server. Start by asking your AI assistant to perform web-based tasks, and it will automatically use these tools to help you!