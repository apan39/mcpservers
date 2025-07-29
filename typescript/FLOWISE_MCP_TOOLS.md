# Flowise MCP Tools

This TypeScript MCP server provides comprehensive Flowise AI integration tools for building, managing, and interacting with AI chatflows and agents.

## Setup

1. **Configure Flowise Instance:**
   - Deploy or access your Flowise instance
   - Note the base URL (e.g., `http://your-flowise-instance.com`)
   - Obtain API key if required for protected chatflows

2. **Configure Environment:**
   ```bash
   # Edit src/flowiseTools.ts with your Flowise details
   const FLOWISE_API_KEY = "your-api-key";
   const FLOWISE_BASE_URL = "http://your-flowise-instance.com";
   ```

3. **Install Dependencies:**
   ```bash
   npm install
   npm run build
   npm start
   ```

## Available Tools

### Connection & Testing
- **`flowise-test-connection`** - Test connectivity to Flowise instance
  - Tests server health and API access
  - Shows authentication status
  - Verifies endpoint availability

### AI Conversation Tools
- **`flowise-predict`** - Send messages to AI chatflows and get responses
  - `chatflowId` (required): The ID of the chatflow to use
  - `question` (required): The message/question to send
  - `streaming` (optional): Enable streaming response (default: false)
  - `sessionId` (optional): Session ID for conversation continuity
  - `overrideConfig` (optional): Override chatflow configuration
  - `history` (optional): Previous conversation history

### Chatflow Management
- **`flowise-list-chatflows`** - List all available AI workflows
  - Returns chatflow names, IDs, deployment status, and metadata
  - Requires JWT authentication for management endpoints

- **`flowise-get-chatflow`** - Get detailed chatflow information
  - `chatflowId` (required): The ID of the chatflow to retrieve
  - Returns complete chatflow configuration and settings

- **`flowise-create-chatflow`** - Create new AI agent workflows
  - `name` (required): Name for the new chatflow
  - `flowData` (optional): JSON string of flow configuration
  - `deployed` (optional): Whether to deploy immediately (default: false)

- **`flowise-update-chatflow`** - Update existing chatflows
  - `chatflowId` (required): The ID of the chatflow to update
  - `name` (optional): New name for the chatflow
  - `flowData` (optional): Updated JSON flow configuration
  - `deployed` (optional): Whether the chatflow should be deployed

- **`flowise-delete-chatflow`** - Delete chatflows
  - `chatflowId` (required): The ID of the chatflow to delete
  - `confirm` (required): Confirmation that you want to delete

## Usage Examples

### Testing Connection
```bash
# Test Flowise connectivity
flowise-test-connection
```

### AI Conversations
```bash
# Simple chat with a chatflow
flowise-predict --chatflowId "abc123" --question "What is artificial intelligence?"

# Chat with session continuity
flowise-predict --chatflowId "abc123" --question "Tell me more" --sessionId "session-456"

# Override model temperature
flowise-predict --chatflowId "abc123" --question "Be creative" --overrideConfig '{"temperature": 0.9}'
```

### Chatflow Management
```bash
# List all chatflows
flowise-list-chatflows

# Get specific chatflow details
flowise-get-chatflow --chatflowId "abc123"

# Create new chatflow
flowise-create-chatflow --name "Customer Support Bot" --deployed true

# Update chatflow name
flowise-update-chatflow --chatflowId "abc123" --name "Updated Bot Name"

# Delete chatflow (with confirmation)
flowise-delete-chatflow --chatflowId "test123" --confirm true
```

## Authentication Methods

The tools support multiple authentication approaches:

1. **Public Chatflows**: No authentication required for prediction endpoints
2. **API Key Authentication**: Bearer token for protected chatflows
3. **JWT Authentication**: Required for management endpoints (list, create, update, delete)

The `flowise-predict` tool automatically tries public access first, then falls back to authenticated access if needed.

## Configuration Options

### Prediction Parameters
- **Streaming**: Enable real-time response streaming
- **Session Management**: Maintain conversation context across requests
- **Configuration Overrides**: Modify model parameters at runtime
- **History**: Include previous conversation context
- **File Uploads**: Support for document and image analysis (planned)

### Advanced Features
- **Source Document Tracking**: See which documents were referenced
- **Follow-up Prompts**: Get suggested next questions
- **Multi-turn Conversations**: Maintain context across interactions
- **Variable Injection**: Pass dynamic variables to chatflows

## Error Handling

The tools include comprehensive error handling:
- Network connectivity issues
- Authentication failures
- Invalid chatflow IDs
- API rate limiting
- Server unavailability

Errors are returned with detailed messages to help troubleshoot issues.

## Security Notes

- Store API keys securely in environment variables
- Use HTTPS in production environments
- Implement proper access controls for management endpoints
- Monitor API usage for unexpected activity
- Regularly rotate API keys

## Rate Limiting

- Prediction endpoints: Depends on Flowise instance configuration
- Management endpoints: Typically more restrictive
- Authentication attempts: May be rate limited

## Integration Examples

### Customer Support Bot
```javascript
// Create a customer support chatflow
await flowise_create_chatflow({
  name: "Customer Support Bot",
  deployed: true
});

// Chat with customers
const response = await flowise_predict({
  chatflowId: "support-bot-id",
  question: "I need help with my order",
  sessionId: user_session_id
});
```

### Document Analysis
```javascript
// Use chatflow for document analysis
const analysis = await flowise_predict({
  chatflowId: "document-analyzer",
  question: "Summarize the key points from this document",
  overrideConfig: {
    max_tokens: 500,
    temperature: 0.1
  }
});
```

### Multi-step Workflow
```javascript
// Step 1: Create chatflow
const chatflow = await flowise_create_chatflow({
  name: "Code Review Assistant"
});

// Step 2: Configure and deploy
await flowise_update_chatflow({
  chatflowId: chatflow.id,
  deployed: true
});

// Step 3: Use for code review
const review = await flowise_predict({
  chatflowId: chatflow.id,
  question: "Review this Python function for bugs and improvements: " + code
});
```

## Troubleshooting

### Common Issues

1. **Connection Failed (401 Unauthorized)**
   - Check API key configuration
   - Verify Flowise instance requires authentication
   - Ensure JWT token is valid if using management endpoints

2. **Chatflow Not Found**
   - Verify chatflow ID is correct
   - Check if chatflow is deployed
   - Ensure you have access permissions

3. **Server Unreachable**
   - Verify Flowise instance URL
   - Check network connectivity
   - Confirm Flowise service is running

4. **Rate Limited**
   - Reduce request frequency
   - Check Flowise instance rate limiting settings
   - Consider implementing backoff strategies

### Debug Mode

Enable detailed logging by setting debug flags in the server configuration to troubleshoot issues.

## Performance Tips

- Reuse session IDs for conversation continuity
- Cache chatflow listings to reduce API calls
- Use streaming for better user experience with long responses
- Implement connection pooling for high-volume applications

## Running the Server

```bash
# Development mode with auto-reload
npm run dev

# Production mode
npm run build
npm start

# Test the integration
node test_flowise.js
```

## API Compatibility

This integration is compatible with:
- Flowise v1.4.0+
- MCP Protocol 2024-11-05
- Node.js 18+
- TypeScript 5.0+