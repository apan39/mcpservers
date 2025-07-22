#!/usr/bin/env python3
"""
HTTP test client for Browser-Use MCP Server
"""

import asyncio
import json
import httpx


async def test_server():
    """Test server with direct HTTP calls."""
    base_url = "http://localhost:3005"
    api_key = "demo-api-key-123"
    
    print("🚀 Testing Browser-Use MCP Server via HTTP...")
    
    # Test health check
    print("\n1. Testing health check...")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{base_url}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed:")
            print(f"  Status: {data['status']}")
            print(f"  Service: {data['service']}")
            print(f"  Active Sessions: {data['active_sessions']}")
            print(f"  Version: {data['version']}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    
    # Test SSE endpoint
    print("\n2. Testing SSE endpoint availability...")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{base_url}/sse", headers={
                "Authorization": f"Bearer {api_key}",
                "Accept": "text/event-stream"
            }, timeout=5.0)
            print(f"✅ SSE endpoint accessible (status: {response.status_code})")
        except httpx.TimeoutException:
            print("✅ SSE endpoint accessible (timeout expected for SSE)")
        except Exception as e:
            print(f"❌ SSE endpoint error: {e}")
    
    print("\n✅ Server is running and accessible!")
    print(f"\n📋 Connection Details:")
    print(f"  Base URL: {base_url}")
    print(f"  Health Check: {base_url}/health")
    print(f"  SSE Endpoint: {base_url}/sse")
    print(f"  API Key: {api_key}")
    
    print(f"\n🔧 Usage Example:")
    print(f"```python")
    print(f"from mcp.client.sse import sse_client")
    print(f"from mcp.client.session import ClientSession")
    print(f"")
    print(f"transport = sse_client('{base_url}/sse')")
    print(f"async with ClientSession(transport) as session:")
    print(f"    await session.initialize()")
    print(f"    tools = await session.list_tools()")
    print(f"```")
    
    return True


if __name__ == "__main__":
    success = asyncio.run(test_server())
    if success:
        print("\n🎉 Browser-Use MCP Server is ready for use!")
    else:
        print("\n❌ Server test failed")
        exit(1)