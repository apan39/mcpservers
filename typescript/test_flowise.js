import fetch from 'node-fetch';
import * as dotenv from 'dotenv';
import * as path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
dotenv.config({ path: path.resolve(__dirname, '../.env') });

const API_KEY = process.env.MCP_API_KEY;
const BASE_URL = 'http://localhost:3010';

async function testFlowise() {
  console.log('🧪 Testing Flowise MCP Integration...\n');

  try {
    // Test 1: Initialize session
    console.log('1. Initializing MCP session...');
    const initResponse = await fetch(`${BASE_URL}/mcp-advanced`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/event-stream',
        'Authorization': `Bearer ${API_KEY}`
      },
      body: JSON.stringify({
        jsonrpc: '2.0',
        id: 1,
        method: 'initialize',
        params: {
          protocolVersion: '2024-11-05',
          capabilities: { tools: {} },
          clientInfo: { name: 'test-client', version: '1.0.0' }
        }
      })
    });

    if (!initResponse.ok) {
      throw new Error(`Init failed: ${initResponse.status} ${initResponse.statusText}`);
    }

    const initText = await initResponse.text();
    console.log('✅ Session initialized');
    
    // Extract session ID from response
    const sessionIdMatch = initText.match(/mcp-session-id:\s*([^\s]+)/);
    let sessionId = null;
    
    // Try to get session ID from headers or generate one
    if (initResponse.headers.get('mcp-session-id')) {
      sessionId = initResponse.headers.get('mcp-session-id');
    } else {
      sessionId = 'test-session-' + Date.now();
    }
    
    console.log(`Session ID: ${sessionId}\n`);

    // Test 2: List tools
    console.log('2. Listing available tools...');
    const toolsResponse = await fetch(`${BASE_URL}/mcp-advanced`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/event-stream',
        'Authorization': `Bearer ${API_KEY}`,
        'mcp-session-id': sessionId
      },
      body: JSON.stringify({
        jsonrpc: '2.0',
        id: 2,
        method: 'tools/list'
      })
    });

    if (toolsResponse.ok) {
      const toolsText = await toolsResponse.text();
      console.log('✅ Tools listed successfully');
      
      // Check if Flowise tools are present
      if (toolsText.includes('flowise-test-connection')) {
        console.log('✅ Flowise tools detected\n');
      } else {
        console.log('⚠️  Flowise tools not found in tools list\n');
      }
    } else {
      console.log('❌ Failed to list tools\n');
    }

    // Test 3: Test Flowise connection
    console.log('3. Testing Flowise connection...');
    const connectionResponse = await fetch(`${BASE_URL}/mcp-advanced`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/event-stream',
        'Authorization': `Bearer ${API_KEY}`,
        'mcp-session-id': sessionId
      },
      body: JSON.stringify({
        jsonrpc: '2.0',
        id: 3,
        method: 'tools/call',
        params: {
          name: 'flowise-test-connection',
          arguments: {}
        }
      })
    });

    if (connectionResponse.ok) {
      const connectionText = await connectionResponse.text();
      console.log('✅ Flowise connection test executed');
      console.log('Response:', connectionText.replace(/^[^{]*/, '').trim());
    } else {
      const errorText = await connectionResponse.text();
      console.log('❌ Flowise connection test failed');
      console.log('Error:', errorText);
    }

    console.log('\n🎉 Test completed!');

  } catch (error) {
    console.error('❌ Test failed:', error.message);
  }
}

// Run the test
testFlowise();