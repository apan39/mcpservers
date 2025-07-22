# Browser-Use MCP Server

A comprehensive Model Context Protocol (MCP) server that integrates with the [browser-use](https://github.com/browser-use/browser-use) library to provide AI agents with powerful browser automation capabilities.

## Features

- **Browser Session Management**: Create and manage multiple browser sessions
- **AI Agent Integration**: Create AI agents with various LLM providers
- **Task Execution**: Execute natural language tasks using AI agents
- **Content Extraction**: Get page content as HTML, text, or screenshots
- **Multi-Provider Support**: Support for Anthropic, OpenAI, Google, Groq, and Ollama
- **Session Persistence**: Maintain browser sessions across multiple operations
- **Real-time Communication**: SSE-based communication for real-time updates

## Requirements

- Python 3.11+
- Browser-use library
- Playwright (for browser automation)
- At least one LLM provider API key

## Installation

1. Clone or copy the server files
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install Playwright browsers:
   ```bash
   playwright install chromium
   ```

4. Configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

## Configuration

### Environment Variables

- `PORT`: Server port (default: 3000)
- `API_KEY`: Server authentication key
- `ANTHROPIC_API_KEY`: Anthropic API key
- `OPENAI_API_KEY`: OpenAI API key
- `GOOGLE_API_KEY`: Google API key
- `GROQ_API_KEY`: Groq API key

### LLM Provider Configuration

The server supports multiple LLM providers. Configure at least one:

- **Anthropic**: Claude models (recommended)
- **OpenAI**: GPT models
- **Google**: Gemini models
- **Groq**: Fast inference models
- **Ollama**: Local models

## Usage

### Starting the Server

```bash
python server.py
```

The server will start on `http://localhost:3000` by default.

### MCP Tools

The server provides the following tools:

#### Browser Session Management

1. **create_browser_session**
   - Creates a new browser session
   - Parameters: `session_id`, `headless`, `browser_type`, `viewport_width`, `viewport_height`

2. **close_browser_session**
   - Closes a browser session
   - Parameters: `session_id`

3. **navigate_to_url**
   - Navigates to a URL
   - Parameters: `session_id`, `url`, `wait_for_load`

4. **get_page_content**
   - Gets page content (HTML, text, or screenshot)
   - Parameters: `session_id`, `content_type`, `full_page`

#### AI Agent Management

5. **create_agent**
   - Creates an AI agent
   - Parameters: `agent_id`, `session_id`, `llm_provider`, `model_name`, `max_actions`, `temperature`

6. **execute_agent_task**
   - Executes a task using an AI agent
   - Parameters: `agent_id`, `task`, `max_steps`

7. **get_agent_history**
   - Gets agent execution history
   - Parameters: `agent_id`, `limit`

#### Session Management

8. **list_active_sessions**
   - Lists all active browser sessions and agents

9. **get_session_info**
   - Gets detailed information about a session
   - Parameters: `session_id`

### Example Usage

#### 1. Create a Browser Session

```json
{
  "name": "create_browser_session",
  "arguments": {
    "session_id": "my-browser-1",
    "headless": false,
    "browser_type": "chromium",
    "viewport_width": 1920,
    "viewport_height": 1080
  }
}
```

#### 2. Create an AI Agent

```json
{
  "name": "create_agent",
  "arguments": {
    "agent_id": "my-agent-1",
    "session_id": "my-browser-1",
    "llm_provider": "anthropic",
    "model_name": "claude-3-5-sonnet-20241022",
    "max_actions": 100,
    "temperature": 0.1
  }
}
```

#### 3. Execute a Task

```json
{
  "name": "execute_agent_task",
  "arguments": {
    "agent_id": "my-agent-1",
    "task": "Go to Google and search for 'Model Context Protocol'",
    "max_steps": 20
  }
}
```

#### 4. Get Page Content

```json
{
  "name": "get_page_content",
  "arguments": {
    "session_id": "my-browser-1",
    "content_type": "text"
  }
}
```

## Integration with Development Tools

### Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "browser-use": {
      "command": "python",
      "args": ["/path/to/browser-use-mcp/server.py"],
      "env": {
        "API_KEY": "your-api-key",
        "ANTHROPIC_API_KEY": "your-anthropic-key"
      }
    }
  }
}
```

### Continue.dev

Add to your `config.json`:

```json
{
  "mcpServers": [
    {
      "name": "browser-use",
      "url": "http://localhost:3000",
      "apiKey": "your-api-key"
    }
  ]
}
```

### LangChain Integration

```python
from langchain.tools import Tool
from langchain.agents import initialize_agent

# Create MCP client
mcp_client = MCPClient("http://localhost:3000", api_key="your-api-key")

# Create tools
tools = [
    Tool(
        name="create_browser_session",
        description="Create a new browser session",
        func=mcp_client.call_tool
    ),
    # Add more tools...
]

# Initialize agent
agent = initialize_agent(tools, llm, agent="zero-shot-react-description")
```

## Error Handling

The server provides comprehensive error handling:

- **Authentication Errors**: Invalid API keys
- **Session Errors**: Session not found or already exists
- **Browser Errors**: Browser automation failures
- **LLM Errors**: API rate limits or model errors
- **Network Errors**: Connection issues

## Security

- **API Key Authentication**: All requests require a valid API key
- **CORS Support**: Configurable CORS for web applications
- **Environment Variables**: Secure storage of API keys
- **Session Isolation**: Each session is isolated from others

## Monitoring

The server provides:

- **Health Check**: `/health` endpoint
- **Logging**: Comprehensive logging with configurable levels
- **Session Tracking**: Monitor active sessions and agents
- **Error Reporting**: Detailed error messages and stack traces

## Development

### Running in Development Mode

```bash
# Install development dependencies
pip install -r requirements.txt

# Run with auto-reload
uvicorn server:starlette_app --reload --host 0.0.0.0 --port 3000
```

### Testing

```bash
# Run basic health check
curl http://localhost:3000/health

# Test authentication
curl -H "Authorization: Bearer your-api-key" http://localhost:3000/health
```

## Troubleshooting

### Common Issues

1. **Browser Not Starting**: Ensure Playwright is installed: `playwright install chromium`
2. **API Key Errors**: Check that environment variables are set correctly
3. **Port Conflicts**: Change the PORT environment variable
4. **Memory Issues**: Limit concurrent sessions and agents

### Debug Mode

Enable debug mode by setting `LOG_LEVEL=DEBUG` in your environment.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and support:
- Check the [browser-use documentation](https://docs.browser-use.com/)
- Review the [MCP specification](https://modelcontextprotocol.io/)
- Open an issue in the repository