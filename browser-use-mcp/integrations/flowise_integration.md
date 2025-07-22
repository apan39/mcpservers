# Flowise Integration for Browser-Use MCP Server

This document explains how to integrate the Browser-Use MCP Server with Flowise.

## Prerequisites

- Running Browser-Use MCP Server
- Flowise installed and running
- API keys configured

## Integration Steps

### 1. Create Custom MCP Node

In Flowise, create a custom MCP node with the following configuration:

```json
{
  "command": "python",
  "args": ["/path/to/browser-use-mcp/server.py"],
  "env": {
    "API_KEY": "your-secure-api-key",
    "ANTHROPIC_API_KEY": "your-anthropic-api-key",
    "PORT": "3000"
  }
}
```

### 2. Available Actions

The Browser-Use MCP Server provides these actions for Flowise:

- `create_browser_session`: Create a new browser session
- `close_browser_session`: Close a browser session
- `navigate_to_url`: Navigate to a URL
- `get_page_content`: Get page content
- `create_agent`: Create an AI agent
- `execute_agent_task`: Execute a task with AI agent
- `get_agent_history`: Get agent execution history
- `list_active_sessions`: List active sessions
- `get_session_info`: Get session details

### 3. Example Workflow

Create a Flowise workflow with these nodes:

1. **Chat Input**: User provides task description
2. **Browser-Use MCP**: Execute browser automation
3. **Chat Output**: Return results to user

### 4. Configuration Example

```json
{
  "nodes": [
    {
      "id": "chatInput",
      "type": "ChatInput",
      "position": { "x": 100, "y": 100 }
    },
    {
      "id": "browserUseMCP",
      "type": "CustomMCP",
      "position": { "x": 300, "y": 100 },
      "data": {
        "mcpServerConfig": {
          "command": "python",
          "args": ["/path/to/browser-use-mcp/server.py"],
          "env": {
            "API_KEY": "your-api-key",
            "ANTHROPIC_API_KEY": "your-anthropic-key"
          }
        },
        "selectedActions": [
          "create_browser_session",
          "execute_agent_task",
          "close_browser_session"
        ]
      }
    },
    {
      "id": "chatOutput",
      "type": "ChatOutput",
      "position": { "x": 500, "y": 100 }
    }
  ],
  "edges": [
    {
      "source": "chatInput",
      "target": "browserUseMCP",
      "sourceHandle": "output",
      "targetHandle": "input"
    },
    {
      "source": "browserUseMCP",
      "target": "chatOutput",
      "sourceHandle": "output",
      "targetHandle": "input"
    }
  ]
}
```

### 5. Usage Examples

#### Simple Web Scraping

```
User: "Go to https://example.com and get the page title"

Workflow:
1. Create browser session
2. Navigate to URL
3. Get page content
4. Extract title
5. Close session
```

#### Complex Task Automation

```
User: "Search for 'AI automation tools' on Google and summarize the first 3 results"

Workflow:
1. Create browser session
2. Create AI agent
3. Execute task: "Search for 'AI automation tools' on Google"
4. Execute task: "Summarize the first 3 results"
5. Get agent history
6. Close session
```

### 6. Error Handling

The integration includes comprehensive error handling:

- Connection errors
- Authentication failures
- Browser automation errors
- API rate limits

### 7. Security Considerations

- Use secure API keys
- Restrict network access
- Monitor resource usage
- Implement request rate limiting

### 8. Monitoring

Monitor the integration through:

- Flowise execution logs
- MCP server health checks
- Browser session metrics
- Agent execution history

### 9. Troubleshooting

Common issues and solutions:

1. **Connection Failed**: Check server URL and API key
2. **Browser Not Starting**: Verify Playwright installation
3. **Task Timeout**: Increase max_steps or max_actions
4. **Memory Issues**: Limit concurrent sessions

### 10. Best Practices

- Always close browser sessions after use
- Use appropriate timeouts
- Monitor resource usage
- Implement proper error handling
- Use headless mode for production