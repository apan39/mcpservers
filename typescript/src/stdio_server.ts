#!/usr/bin/env node

import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import {
  CallToolResult,
  GetPromptResult,
} from "@modelcontextprotocol/sdk/types.js";
import * as githubTools from "./githubTools.js";
import { config } from "dotenv";

// Load environment variables
config();

// Create MCP server using the same pattern as the HTTP server
const server = new McpServer(
  {
    name: "typescript-mcp-stdio",
    version: "1.0.0",
  },
  { capabilities: { logging: {} } }
);

// Initialize GitHub client with token from environment
githubTools.initializeGitHub(process.env.GITHUB_TOKEN);

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

// GitHub Tools

// GitHub authentication and user info
server.tool(
  "github-get-user",
  "Get information about the authenticated GitHub user",
  {},
  async (): Promise<CallToolResult> => {
    return await githubTools.getCurrentUser();
  }
);

// List repositories
server.tool(
  "github-list-repos",
  "List repositories for a user (or authenticated user if no username provided)",
  {
    username: z.string().optional().describe("Username to list repositories for (optional)"),
  },
  async ({ username }): Promise<CallToolResult> => {
    return await githubTools.listRepositories(username);
  }
);

// Get repository details
server.tool(
  "github-get-repo",
  "Get detailed information about a specific repository",
  {
    owner: z.string().describe("Repository owner/organization"),
    repo: z.string().describe("Repository name"),
  },
  async ({ owner, repo }): Promise<CallToolResult> => {
    return await githubTools.getRepository(owner, repo);
  }
);

// List issues
server.tool(
  "github-list-issues",
  "List issues for a repository",
  {
    owner: z.string().describe("Repository owner/organization"),
    repo: z.string().describe("Repository name"),
    state: z.enum(["open", "closed", "all"]).optional().describe("Issue state filter"),
  },
  async ({ owner, repo, state }): Promise<CallToolResult> => {
    return await githubTools.listIssues(owner, repo, state);
  }
);

// Create issue
server.tool(
  "github-create-issue",
  "Create a new issue in a repository",
  {
    owner: z.string().describe("Repository owner/organization"),
    repo: z.string().describe("Repository name"),
    title: z.string().describe("Issue title"),
    body: z.string().optional().describe("Issue description/body"),
    labels: z.array(z.string()).optional().describe("Issue labels"),
  },
  async ({ owner, repo, title, body, labels }): Promise<CallToolResult> => {
    return await githubTools.createIssue(owner, repo, title, body, labels);
  }
);

// List pull requests
server.tool(
  "github-list-prs",
  "List pull requests for a repository",
  {
    owner: z.string().describe("Repository owner/organization"),
    repo: z.string().describe("Repository name"),
    state: z.enum(["open", "closed", "all"]).optional().describe("PR state filter"),
  },
  async ({ owner, repo, state }): Promise<CallToolResult> => {
    return await githubTools.listPullRequests(owner, repo, state);
  }
);

// Get repository contents
server.tool(
  "github-get-contents",
  "Get contents of a repository directory or file",
  {
    owner: z.string().describe("Repository owner/organization"),
    repo: z.string().describe("Repository name"),
    path: z.string().optional().describe("Path to directory or file (empty for root)"),
  },
  async ({ owner, repo, path }): Promise<CallToolResult> => {
    return await githubTools.getContents(owner, repo, path || "");
  }
);

// Search repositories
server.tool(
  "github-search-repos",
  "Search for repositories on GitHub",
  {
    query: z.string().describe("Search query"),
    sort: z.enum(["stars", "forks", "updated"]).optional().describe("Sort order"),
  },
  async ({ query, sort }): Promise<CallToolResult> => {
    return await githubTools.searchRepositories(query, sort);
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