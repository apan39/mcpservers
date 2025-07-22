#!/usr/bin/env python3
"""
Simple test client for Browser-Use MCP Server
"""

import asyncio
import json
import httpx


async def test_mcp_server():
    """Test the MCP server functionality."""
    base_url = "http://localhost:3005"
    api_key = "demo-api-key-123"
    
    print("🚀 Testing Browser-Use MCP Server...")
    
    # Test 1: Health check
    print("\n1. Testing health check...")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{base_url}/health")
        if response.status_code == 200:
            print(f"✅ Health check passed: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return
    
    # Test 2: MCP SSE connection (simplified test)
    print("\n2. Testing MCP tools availability...")
    try:
        from mcp.client.session import ClientSession
        from mcp.client.sse import sse_client
        
        transport = sse_client(f"{base_url}/sse")
        
        async with ClientSession(transport) as session:
            # Initialize
            await session.initialize()
            print("✅ MCP connection established")
            
            # List tools
            tools = await session.list_tools()
            print(f"✅ Available tools: {len(tools.tools)}")
            for tool in tools.tools:
                print(f"  - {tool.name}: {tool.description}")
            
            # Test create session
            print("\n3. Testing browser session creation...")
            result = await session.call_tool(
                "create_browser_session",
                {"session_id": "test-session", "headless": True}
            )
            print(f"✅ Session creation: {result.content[0].text}")
            
            # Test navigation
            print("\n4. Testing navigation...")
            result = await session.call_tool(
                "navigate_to_url",
                {"session_id": "test-session", "url": "https://example.com"}
            )
            print(f"✅ Navigation: {result.content[0].text}")
            
            # Test getting content
            print("\n5. Testing content extraction...")
            result = await session.call_tool(
                "get_page_content",
                {"session_id": "test-session"}
            )
            content = result.content[0].text
            print(f"✅ Content extracted ({len(content)} characters)")
            print(f"Preview: {content[:100]}...")
            
            # Test listing sessions
            print("\n6. Testing session listing...")
            result = await session.call_tool("list_sessions", {})
            sessions = json.loads(result.content[0].text)
            print(f"✅ Active sessions: {len(sessions)}")
            
            # Test close session
            print("\n7. Testing session cleanup...")
            result = await session.call_tool(
                "close_session",
                {"session_id": "test-session"}
            )
            print(f"✅ Session cleanup: {result.content[0].text}")
    
    except Exception as e:
        print(f"❌ MCP test error: {e}")
        return
    
    print("\n🎉 All tests passed! Browser-Use MCP Server is working correctly.")
    print(f"\n📋 Server Details:")
    print(f"  URL: {base_url}")
    print(f"  API Key: {api_key}")
    print(f"  Health: {base_url}/health")
    print(f"  SSE Endpoint: {base_url}/sse")


async def main():
    await test_mcp_server()


if __name__ == "__main__":
    asyncio.run(main())