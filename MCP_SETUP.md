# MCP Setup for Claude Code CLI

## ✅ Setup Complete!

Your MCP servers are now configured and ready to use with Claude Code CLI!

### Current Configuration

```bash
claude mcp list
```

Shows:
- `python-tools`: All math, text, and web crawling tools
- `typescript-tools`: Basic greeting and notification tools

### Quick Test

```bash
# Test math tool
claude mcp call python-tools add-numbers '{"a": 25, "b": 37}'

# Test text tool  
claude mcp call python-tools string-operations '{"text": "Hello World", "operation": "uppercase"}'

# Test web crawling
claude mcp call python-tools crawl-url '{"url": "https://sunet.se", "max_pages": 1}'

# Test greeting tool
claude mcp call typescript-tools greet '{"name": "Claude"}'
```

### If You Need to Reconfigure

```bash
# Add servers manually if needed
claude mcp add python-tools python /Users/johansimac/development/mcpservers/python/simple_stdio_server.py
claude mcp add typescript-tools node /Users/johansimac/development/mcpservers/typescript/dist/stdio_server.js
```

## Available Tools

### Python Tools (python-tools server):
- `add-numbers` - Add two numbers: `{"a": 5, "b": 3}`
- `multiply-numbers` - Multiply numbers: `{"a": 4, "b": 7}` 
- `calculate-percentage` - Calculate percentage: `{"value": 100, "percentage": 20}`
- `string-operations` - Text operations: `{"text": "Hello", "operation": "uppercase"}`
- `word-count` - Count words: `{"text": "Hello world"}`
- `format-text` - Format text: `{"text": "hello world", "format_type": "title_case"}`
- `crawl-url` - Web scraping: `{"url": "https://example.com", "max_pages": 1}`

### TypeScript Tools (typescript-tools server):
- `greet` - Simple greeting: `{"name": "Claude"}`
- `multi-greet` - Friendly greeting: `{"name": "Claude"}`

## Usage in Claude Code CLI

Once configured, you can use these in natural language:

```
Please use the add-numbers tool to calculate 25 + 37
Please use the string-operations tool to make "Hello World" uppercase  
Please use the greet tool to say hello to Claude
Please use the crawl-url tool to get content from https://example.com
```

## Troubleshooting

If tools don't work:

1. **Check paths**: Ensure the paths in the config are correct
2. **Check permissions**: Run `chmod +x` on the server files if needed
3. **Check dependencies**: Ensure Python and Node.js are in your PATH
4. **Check logs**: Run `claude mcp doctor` for diagnostics

## Files Created

- `/Users/johansimac/development/mcpservers/mcp_config.json` - MCP configuration
- `/Users/johansimac/development/mcpservers/python/mcp_stdio_server.py` - Python stdio server
- `/Users/johansimac/development/mcpservers/typescript/dist/stdio_server.js` - TypeScript stdio server