"""
LangChain integration example for Browser-Use MCP Server
"""

import asyncio
import json
from typing import Any, Dict, List, Optional

from langchain.tools import BaseTool
from langchain.agents import initialize_agent, AgentType
from langchain.llms import OpenAI
from langchain.schema import AgentAction, AgentFinish
from pydantic import BaseModel, Field

import httpx
from mcp.client.session import ClientSession
from mcp.client.sse import sse_client


class BrowserUseMCPTool(BaseTool):
    """LangChain tool for Browser-Use MCP Server."""
    
    name: str = Field(...)
    description: str = Field(...)
    mcp_server_url: str = Field(default="http://localhost:3000")
    api_key: str = Field(...)
    
    def _run(self, **kwargs) -> str:
        """Run the tool synchronously."""
        return asyncio.run(self._arun(**kwargs))
    
    async def _arun(self, **kwargs) -> str:
        """Run the tool asynchronously."""
        try:
            transport = sse_client(f"{self.mcp_server_url}/sse")
            
            async with ClientSession(transport) as session:
                await session.initialize()
                
                result = await session.call_tool(self.name, kwargs)
                return result.content[0].text
                
        except Exception as e:
            return f"Error: {str(e)}"


class BrowserUseMCPToolkit:
    """Toolkit for creating LangChain tools from Browser-Use MCP Server."""
    
    def __init__(self, server_url: str = "http://localhost:3000", api_key: str = None):
        self.server_url = server_url
        self.api_key = api_key
    
    async def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get available tools from the MCP server."""
        try:
            transport = sse_client(f"{self.server_url}/sse")
            
            async with ClientSession(transport) as session:
                await session.initialize()
                tools = await session.list_tools()
                
                return [
                    {
                        "name": tool.name,
                        "description": tool.description,
                        "input_schema": tool.inputSchema
                    }
                    for tool in tools.tools
                ]
                
        except Exception as e:
            print(f"Error getting tools: {e}")
            return []
    
    async def create_langchain_tools(self) -> List[BrowserUseMCPTool]:
        """Create LangChain tools from MCP server tools."""
        mcp_tools = await self.get_available_tools()
        
        langchain_tools = []
        
        for tool_info in mcp_tools:
            tool = BrowserUseMCPTool(
                name=tool_info["name"],
                description=tool_info["description"],
                mcp_server_url=self.server_url,
                api_key=self.api_key
            )
            langchain_tools.append(tool)
        
        return langchain_tools


class BrowserUseAgent:
    """High-level agent for browser automation using LangChain."""
    
    def __init__(self, 
                 llm,
                 mcp_server_url: str = "http://localhost:3000",
                 api_key: str = None):
        self.llm = llm
        self.mcp_server_url = mcp_server_url
        self.api_key = api_key
        self.tools = []
        self.agent = None
    
    async def setup(self):
        """Set up the agent with tools from MCP server."""
        toolkit = BrowserUseMCPToolkit(self.mcp_server_url, self.api_key)
        self.tools = await toolkit.create_langchain_tools()
        
        # Create LangChain agent
        self.agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True
        )
    
    async def execute_task(self, task: str) -> str:
        """Execute a browser automation task."""
        if not self.agent:
            await self.setup()
        
        try:
            result = await self.agent.arun(task)
            return result
        except Exception as e:
            return f"Error executing task: {str(e)}"


# Example usage
async def main():
    """Example usage of Browser-Use MCP with LangChain."""
    
    # Initialize LLM
    llm = OpenAI(temperature=0.1)
    
    # Create browser agent
    agent = BrowserUseAgent(
        llm=llm,
        mcp_server_url="http://localhost:3000",
        api_key="your-api-key"
    )
    
    # Set up the agent
    await agent.setup()
    
    # Execute tasks
    tasks = [
        "Create a browser session and navigate to https://example.com",
        "Get the page content and summarize what you see",
        "Close the browser session when done"
    ]
    
    for task in tasks:
        print(f"\n🔧 Executing task: {task}")
        result = await agent.execute_task(task)
        print(f"✅ Result: {result}")


if __name__ == "__main__":
    asyncio.run(main())