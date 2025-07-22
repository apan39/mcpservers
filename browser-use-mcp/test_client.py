#!/usr/bin/env python3
"""
Test client for Browser-Use MCP Server
Tests compatibility with various agents and developer tools
"""

import asyncio
import json
import os
from datetime import datetime
from typing import Any, Dict, List

import httpx
from mcp.client.session import ClientSession
from mcp.client.sse import sse_client
from mcp.client.stdio import stdio_client


class BrowserUseMCPClient:
    """Test client for Browser-Use MCP Server."""
    
    def __init__(self, base_url: str = "http://localhost:3000", api_key: str = None):
        self.base_url = base_url
        self.api_key = api_key or os.getenv("API_KEY", "changeme")
        self.session_id = None
        self.agent_id = None
        
    async def test_health(self) -> bool:
        """Test server health."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/health")
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ Server is healthy: {data}")
                    return True
                else:
                    print(f"❌ Health check failed: {response.status_code}")
                    return False
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False
    
    async def test_sse_connection(self) -> bool:
        """Test SSE connection."""
        try:
            # Create SSE client
            transport = sse_client(f"{self.base_url}/sse")
            
            async with ClientSession(transport) as session:
                # Initialize the session
                await session.initialize()
                
                # List available tools
                tools = await session.list_tools()
                print(f"✅ SSE connection successful. Available tools: {len(tools.tools)}")
                
                # Print tool names
                for tool in tools.tools:
                    print(f"  - {tool.name}: {tool.description}")
                
                return True
                
        except Exception as e:
            print(f"❌ SSE connection error: {e}")
            return False
    
    async def test_browser_session_workflow(self) -> bool:
        """Test complete browser session workflow."""
        try:
            transport = sse_client(f"{self.base_url}/sse")
            
            async with ClientSession(transport) as session:
                await session.initialize()
                
                # 1. Create browser session
                print("🔧 Creating browser session...")
                self.session_id = f"test-session-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
                
                result = await session.call_tool(
                    "create_browser_session",
                    {
                        "session_id": self.session_id,
                        "headless": True,
                        "browser_type": "chromium"
                    }
                )
                print(f"✅ Browser session created: {result.content[0].text}")
                
                # 2. Navigate to a URL
                print("🔧 Navigating to URL...")
                result = await session.call_tool(
                    "navigate_to_url",
                    {
                        "session_id": self.session_id,
                        "url": "https://example.com",
                        "wait_for_load": True
                    }
                )
                print(f"✅ Navigation result: {result.content[0].text}")
                
                # 3. Get page content
                print("🔧 Getting page content...")
                result = await session.call_tool(
                    "get_page_content",
                    {
                        "session_id": self.session_id,
                        "content_type": "text"
                    }
                )
                content = result.content[0].text
                print(f"✅ Page content retrieved ({len(content)} characters)")
                
                # 4. List active sessions
                print("🔧 Listing active sessions...")
                result = await session.call_tool("list_active_sessions", {})
                sessions_info = json.loads(result.content[0].text)
                print(f"✅ Active sessions: {sessions_info}")
                
                # 5. Get session info
                print("🔧 Getting session info...")
                result = await session.call_tool(
                    "get_session_info",
                    {"session_id": self.session_id}
                )
                session_info = json.loads(result.content[0].text)
                print(f"✅ Session info: {session_info}")
                
                # 6. Close browser session
                print("🔧 Closing browser session...")
                result = await session.call_tool(
                    "close_browser_session",
                    {"session_id": self.session_id}
                )
                print(f"✅ Browser session closed: {result.content[0].text}")
                
                return True
                
        except Exception as e:
            print(f"❌ Browser session workflow error: {e}")
            return False
    
    async def test_agent_workflow(self) -> bool:
        """Test AI agent workflow."""
        try:
            transport = sse_client(f"{self.base_url}/sse")
            
            async with ClientSession(transport) as session:
                await session.initialize()
                
                # 1. Create browser session
                print("🔧 Creating browser session for agent...")
                self.session_id = f"agent-session-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
                
                result = await session.call_tool(
                    "create_browser_session",
                    {
                        "session_id": self.session_id,
                        "headless": True,
                        "browser_type": "chromium"
                    }
                )
                print(f"✅ Browser session created: {result.content[0].text}")
                
                # 2. Create AI agent
                print("🔧 Creating AI agent...")
                self.agent_id = f"test-agent-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
                
                result = await session.call_tool(
                    "create_agent",
                    {
                        "agent_id": self.agent_id,
                        "session_id": self.session_id,
                        "llm_provider": "anthropic",
                        "max_actions": 10,
                        "temperature": 0.1
                    }
                )
                print(f"✅ AI agent created: {result.content[0].text}")
                
                # 3. Execute a simple task
                print("🔧 Executing agent task...")
                result = await session.call_tool(
                    "execute_agent_task",
                    {
                        "agent_id": self.agent_id,
                        "task": "Navigate to https://example.com and describe what you see",
                        "max_steps": 5
                    }
                )
                task_result = result.content[0].text
                print(f"✅ Task executed: {task_result}")
                
                # 4. Get agent history
                print("🔧 Getting agent history...")
                result = await session.call_tool(
                    "get_agent_history",
                    {
                        "agent_id": self.agent_id,
                        "limit": 5
                    }
                )
                history = json.loads(result.content[0].text)
                print(f"✅ Agent history retrieved: {len(history)} entries")
                
                # 5. Clean up
                print("🔧 Cleaning up...")
                result = await session.call_tool(
                    "close_browser_session",
                    {"session_id": self.session_id}
                )
                print(f"✅ Cleanup completed: {result.content[0].text}")
                
                return True
                
        except Exception as e:
            print(f"❌ Agent workflow error: {e}")
            # Check if it's an API key issue
            if "API_KEY" in str(e) or "ANTHROPIC_API_KEY" in str(e):
                print("💡 This might be due to missing LLM provider API keys")
                print("   Set ANTHROPIC_API_KEY or other provider keys in your environment")
            return False
    
    async def test_compatibility(self) -> Dict[str, bool]:
        """Test compatibility with different scenarios."""
        results = {}
        
        print("🚀 Starting Browser-Use MCP Server compatibility tests...\n")
        
        # Test 1: Server health
        print("1. Testing server health...")
        results["health"] = await self.test_health()
        print()
        
        # Test 2: SSE connection
        print("2. Testing SSE connection...")
        results["sse_connection"] = await self.test_sse_connection()
        print()
        
        # Test 3: Browser session workflow
        print("3. Testing browser session workflow...")
        results["browser_workflow"] = await self.test_browser_session_workflow()
        print()
        
        # Test 4: AI agent workflow (may fail without API keys)
        print("4. Testing AI agent workflow...")
        results["agent_workflow"] = await self.test_agent_workflow()
        print()
        
        # Summary
        print("📊 Test Results Summary:")
        print("=" * 40)
        for test_name, success in results.items():
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{test_name.replace('_', ' ').title()}: {status}")
        
        total_tests = len(results)
        passed_tests = sum(results.values())
        print(f"\nTotal: {passed_tests}/{total_tests} tests passed")
        
        return results


async def main():
    """Main test function."""
    # Check if server is running
    client = BrowserUseMCPClient()
    
    if not await client.test_health():
        print("❌ Server is not running. Please start the server first:")
        print("   python server.py")
        return
    
    # Run compatibility tests
    results = await client.test_compatibility()
    
    # Exit with appropriate code
    if all(results.values()):
        print("\n🎉 All tests passed! The server is compatible with MCP standards.")
        exit(0)
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())