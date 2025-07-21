#!/usr/bin/env node

import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import {
  CallToolResult,
  GetPromptResult,
} from "@modelcontextprotocol/sdk/types.js";

// Create MCP server using the same pattern as the HTTP server
const server = new McpServer(
  {
    name: "typescript-mcp-stdio",
    version: "1.0.0",
  },
  { capabilities: { logging: {} } }
);

// Simple greeting tool
server.tool(
  "greet",
  "A simple greeting tool",
  {
    name: z.string().describe("Name to greet"),
  },
  async ({ name }): Promise<CallToolResult> => {
    return {
      content: [
        {
          type: "text",
          text: `Hello, ${name}!`,
        },
      ],
    };
  }
);

// Multi-greeting tool (simplified for stdio)
server.tool(
  "multi-greet",
  "A tool that sends a friendly greeting",
  {
    name: z.string().describe("Name to greet"),
  },
  async ({ name }): Promise<CallToolResult> => {
    return {
      content: [
        {
          type: "text", 
          text: `Good morning, ${name}! (Multi-greet completed via stdio)`,
        },
      ],
    };
  }
);

// Simple prompt
server.prompt(
  "greeting-template",
  "A simple greeting prompt template",
  {
    name: z.string().describe("Name to include in greeting"),
  },
  async ({ name }): Promise<GetPromptResult> => {
    return {
      messages: [
        {
          role: "user",
          content: {
            type: "text",
            text: `Please greet ${name} in a friendly manner.`,
          },
        },
      ],
    };
  }
);

// Main function
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main().catch((error) => {
  console.error("TypeScript stdio server error:", error);
  process.exit(1);
});