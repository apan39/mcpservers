import express, { Request, Response } from "express";
import { randomUUID } from "node:crypto";
import { z } from "zod";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import { SSEServerTransport } from "@modelcontextprotocol/sdk/server/sse.js";
import rateLimit from "express-rate-limit";
import {
  CallToolResult,
  GetPromptResult,
  isInitializeRequest,
  ReadResourceResult,
} from "@modelcontextprotocol/sdk/types.js";

import { registerPlaywrightTools } from "./playwrightTools.js";
import { registerFlowiseTools } from "./flowiseTools.js";
import { registerContext7Tools } from "./context7Tools.js";
import { registerPayloadCMSTools } from "./payloadcmsTools.js";
import { 
  githubGetUser, githubListRepos, githubGetRepo, githubListIssues, 
  githubCreateIssue, githubListPRs, githubGetContents, githubSearchRepos,
  githubCreateOrUpdateFile, githubGetFileSha, githubAddSubmodule
} from "./githubRemoteTools.js";
import { coolifyInvestigateApp, coolifyAnalyzeRepo } from "./coolifyGithubTools.js";
import * as path from "path";
import * as dotenv from "dotenv";
import { fileURLToPath } from "url";
import dayjs from "dayjs";
import cors from "cors";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
dotenv.config({ path: path.resolve(__dirname, "../../.env") });

// Configuration
const API_KEY = process.env.MCP_API_KEY || (() => {
  console.error('MCP_API_KEY environment variable is not set!');
  process.exit(1);
})();

const PORT = parseInt(process.env.TYPESCRIPT_MCP_PORT || "3010");

// Simple in-memory event store for resumability
class InMemoryEventStore {
  private events: Record<string, any[]> = {};

  async storeEvent(streamId: string, message: any): Promise<string> {
    if (!this.events[streamId]) this.events[streamId] = [];
    this.events[streamId].push(message);
    return String(this.events[streamId].length - 1);
  }

  async replayEventsAfter(
    lastEventId: string,
    { send }: { send: (eventId: string, message: any) => Promise<void> }
  ): Promise<string> {
    for (const streamId in this.events) {
      const events = this.events[streamId];
      const start = lastEventId ? parseInt(lastEventId, 10) + 1 : 0;
      for (let i = start; i < events.length; i++) {
        await send(String(i), events[i]);
      }
      return streamId;
    }
    return "";
  }

  async getEvents(sessionId: string) {
    return this.events[sessionId] || [];
  }

  async clear(sessionId: string) {
    delete this.events[sessionId];
  }
}

// Create MCP server with tools
function createMCPServer(): McpServer {
  const server = new McpServer(
    {
      name: "typescript-mcp-server",
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

  // Multi-greeting with notifications
  server.tool(
    "multi-greet",
    "A tool that sends different greetings with delays between them",
    {
      name: z.string().describe("Name to greet"),
    },
    async (
      { name }: { name: string },
      { sendNotification }: { sendNotification: (msg: any) => Promise<void> }
    ): Promise<CallToolResult> => {
      const sleep = (ms: number) =>
        new Promise((resolve) => setTimeout(resolve, ms));

      try {
        await sendNotification({
          method: "notifications/message",
          params: { level: "debug", data: `Starting multi-greet for ${name}` },
        });

        await sleep(1000);

        await sendNotification({
          method: "notifications/message",
          params: { level: "info", data: `Sending greeting to ${name}` },
        });

        return {
          content: [
            {
              type: "text",
              text: `Good morning, ${name}!`,
            },
          ],
        };
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        return {
          content: [
            {
              type: "text",
              text: `Error in multi-greet: ${errorMessage}`,
            },
          ],
        };
      }
    }
  );

  // Notification stream tool
  server.tool(
    "start-notification-stream",
    "Starts sending periodic notifications for testing resumability",
    {
      interval: z
        .number()
        .min(100)
        .max(10000)
        .describe("Interval in milliseconds between notifications")
        .default(1000),
      count: z
        .number()
        .min(1)
        .max(20)
        .describe("Number of notifications to send")
        .default(5),
    },
    async (
      { interval, count },
      { sendNotification }
    ): Promise<CallToolResult> => {
      const sleep = (ms: number) =>
        new Promise((resolve) => setTimeout(resolve, ms));
      
      try {
        for (let counter = 1; counter <= count; counter++) {
          await sendNotification({
            method: "notifications/message",
            params: {
              level: "info",
              data: `Notification ${counter}/${count} at ${new Date().toISOString()}`,
            },
          });
          
          if (counter < count) {
            await sleep(interval);
          }
        }

        return {
          content: [
            {
              type: "text",
              text: `Successfully sent ${count} notifications with ${interval}ms interval`,
            },
          ],
        };
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        return {
          content: [
            {
              type: "text",
              text: `Error sending notifications: ${errorMessage}`,
            },
          ],
        };
      }
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

  // Simple resource
  server.resource(
    "greeting-resource",
    "https://example.com/greetings/default",
    { mimeType: "text/plain" },
    async (): Promise<ReadResourceResult> => {
      return {
        contents: [
          {
            uri: "https://example.com/greetings/default",
            text: "Hello, world!",
          },
        ],
      };
    }
  );

  // Register Playwright tools
  registerPlaywrightTools(server);
  
  // Register Flowise tools
  registerFlowiseTools(server);
  
  // Register Context7 tools
  registerContext7Tools(server);
  
  // Register PayloadCMS tools
  registerPayloadCMSTools(server);
  
  return server;
}

// Express app setup
const app = express();

// Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // limit each IP to 100 requests per windowMs
  message: 'Too many requests from this IP, please try again later.',
  standardHeaders: true,
  legacyHeaders: false,
});
app.use(limiter);

// CORS
app.use(cors({
  origin: process.env.ALLOWED_ORIGINS?.split(',') || ['http://localhost:3009', 'http://localhost:3010'],
  methods: ["GET", "POST", "OPTIONS", "DELETE"],
  allowedHeaders: ["Authorization", "Content-Type", "mcp-session-id", "last-event-id"],
  credentials: true
}));

app.use(express.json({ limit: '10mb' }));

// Health check endpoint (no auth required)
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Remove OAuth endpoints - they're not needed for local SSE servers

// Authentication middleware - only for HTTP endpoints, not SSE
app.use((req, res, next) => {
  // Allow health check, SSE endpoint, and messages endpoint without auth
  if (req.path === "/health" || req.path === "/sse" || req.path === "/messages") {
    return next();
  }
  
  // Check Authorization header for other endpoints
  const auth = req.header("authorization");
  if (!auth || !auth.startsWith('Bearer ')) {
    return res.status(401).json({ 
      error: "Missing or invalid Authorization header. Use Bearer token." 
    });
  }
  
  const token = auth.substring(7); // Remove 'Bearer ' prefix
  if (token !== API_KEY) {
    return res.status(401).json({ error: "Invalid API key" });
  }
  
  next();
});

// Session management
const transports: { [sessionId: string]: StreamableHTTPServerTransport } = {};
const sseTransports: { [sessionId: string]: SSEServerTransport } = {};

// Simple MCP endpoint (no session management for basic operations)
app.post("/mcp", async (req: Request, res: Response) => {
  try {
    const { method, params, id } = req.body;
    
    console.log(`MCP Request: ${method}`, params);

    if (method === "initialize") {
      res.json({
        jsonrpc: "2.0",
        id,
        result: {
          protocolVersion: "2024-11-05",
          capabilities: {
            tools: {},
            logging: {}
          },
          serverInfo: {
            name: "typescript-mcp-server",
            version: "1.0.0"
          }
        }
      });
      return;
    }

    if (method === "notifications/initialized") {
      res.json({
        jsonrpc: "2.0",
        id,
        result: {}
      });
      return;
    }

    if (method === "tools/list") {
      res.json({
        jsonrpc: "2.0",
        id,
        result: {
          tools: [
            {
              name: "greet",
              description: "A simple greeting tool",
              inputSchema: {
                type: "object",
                required: ["name"],
                properties: {
                  name: {
                    type: "string",
                    description: "Name to greet"
                  }
                }
              }
            },
            {
              name: "multi-greet", 
              description: "A tool that sends different greetings with delays between them",
              inputSchema: {
                type: "object",
                required: ["name"],
                properties: {
                  name: {
                    type: "string",
                    description: "Name to greet"
                  }
                }
              }
            },
            {
              name: "scrape-dynamic-url",
              description: "Scrape text content from a dynamic webpage using Playwright",
              inputSchema: {
                type: "object",
                required: ["url"],
                properties: {
                  url: {
                    type: "string",
                    format: "uri",
                    description: "The URL to scrape"
                  },
                  waitFor: {
                    type: "string",
                    description: "CSS selector to wait for before scraping"
                  },
                  timeout: {
                    type: "number",
                    minimum: 1000,
                    maximum: 30000,
                    default: 10000,
                    description: "Timeout in milliseconds"
                  }
                }
              }
            },
            {
              name: "flowise-list-chatflows",
              description: "List all available Flowise chatflows",
              inputSchema: {
                type: "object",
                properties: {}
              }
            },
            {
              name: "flowise-get-chatflow",
              description: "Get details of a specific Flowise chatflow",
              inputSchema: {
                type: "object",
                required: ["chatflowId"],
                properties: {
                  chatflowId: {
                    type: "string",
                    description: "The ID of the chatflow to retrieve"
                  }
                }
              }
            },
            {
              name: "flowise-predict",
              description: "Send a message to a Flowise chatflow and get a response",
              inputSchema: {
                type: "object",
                required: ["chatflowId", "question"],
                properties: {
                  chatflowId: {
                    type: "string",
                    description: "The ID of the chatflow to use"
                  },
                  question: {
                    type: "string",
                    description: "The message/question to send"
                  },
                  streaming: {
                    type: "boolean",
                    description: "Enable streaming response (default: false)"
                  },
                  sessionId: {
                    type: "string",
                    description: "Session ID for conversation continuity"
                  },
                  overrideConfig: {
                    type: "object",
                    description: "Override chatflow configuration"
                  },
                  history: {
                    type: "array",
                    description: "Previous conversation history"
                  }
                }
              }
            },
            {
              name: "flowise-test-connection",
              description: "Test connection to Flowise instance",
              inputSchema: {
                type: "object",
                properties: {}
              }
            },
            {
              name: "context7-get-docs",
              description: "Get up-to-date documentation and code examples for a library using context7",
              inputSchema: {
                type: "object",
                required: ["library"],
                properties: {
                  library: {
                    type: "string",
                    description: "Library name or identifier (e.g., 'react', 'next.js', 'typescript')"
                  },
                  version: {
                    type: "string",
                    description: "Specific version to get docs for (optional, uses latest if not specified)"
                  },
                  query: {
                    type: "string",
                    description: "Specific query or topic within the library documentation"
                  }
                }
              }
            },
            {
              name: "context7-search-examples",
              description: "Search for code examples and usage patterns for a specific library or framework",
              inputSchema: {
                type: "object",
                required: ["library", "pattern"],
                properties: {
                  library: {
                    type: "string",
                    description: "Library name to search examples for"
                  },
                  pattern: {
                    type: "string",
                    description: "Specific pattern, function, or use case to find examples for"
                  },
                  language: {
                    type: "string",
                    description: "Programming language preference (e.g., 'typescript', 'javascript')"
                  }
                }
              }
            },
            {
              name: "context7-library-info",
              description: "Get general information and latest version details for a library",
              inputSchema: {
                type: "object",
                required: ["library"],
                properties: {
                  library: {
                    type: "string",
                    description: "Library name to get information for"
                  }
                }
              }
            },
            {
              name: "context7-ai-context",
              description: "Get comprehensive context for AI coding assistance with up-to-date library information",
              inputSchema: {
                type: "object",
                required: ["libraries", "task"],
                properties: {
                  libraries: {
                    type: "array",
                    items: {
                      type: "string"
                    },
                    description: "Array of library names to get context for"
                  },
                  task: {
                    type: "string",
                    description: "Description of the coding task or what you're trying to build"
                  },
                  preferences: {
                    type: "object",
                    properties: {
                      typescript: {
                        type: "boolean",
                        description: "Prefer TypeScript examples"
                      },
                      react: {
                        type: "boolean",
                        description: "Focus on React-related examples"
                      },
                      latest: {
                        type: "boolean",
                        description: "Only use latest versions"
                      }
                    },
                    description: "Preferences for the context gathering"
                  }
                }
              }
            },
            {
              name: "context7-server-status",
              description: "Check if context7 MCP server is running and get connection info",
              inputSchema: {
                type: "object",
                properties: {}
              }
            },
            {
              name: "github-get-user",
              description: "Get information about the authenticated GitHub user",
              inputSchema: {
                type: "object",
                properties: {}
              }
            },
            {
              name: "github-list-repos",
              description: "List repositories for a user (or authenticated user if no username provided)",
              inputSchema: {
                type: "object",
                properties: {
                  username: {
                    type: "string",
                    description: "Username to list repositories for (optional)"
                  }
                }
              }
            },
            {
              name: "github-get-repo",
              description: "Get detailed information about a specific repository",
              inputSchema: {
                type: "object",
                required: ["owner", "repo"],
                properties: {
                  owner: {
                    type: "string",
                    description: "Repository owner/organization"
                  },
                  repo: {
                    type: "string",
                    description: "Repository name"
                  }
                }
              }
            },
            {
              name: "github-list-issues",
              description: "List issues for a repository",
              inputSchema: {
                type: "object",
                required: ["owner", "repo"],
                properties: {
                  owner: {
                    type: "string",
                    description: "Repository owner/organization"
                  },
                  repo: {
                    type: "string",
                    description: "Repository name"
                  },
                  state: {
                    type: "string",
                    enum: ["open", "closed", "all"],
                    description: "Issue state filter"
                  }
                }
              }
            },
            {
              name: "github-create-issue",
              description: "Create a new issue in a repository",
              inputSchema: {
                type: "object",
                required: ["owner", "repo", "title"],
                properties: {
                  owner: {
                    type: "string",
                    description: "Repository owner/organization"
                  },
                  repo: {
                    type: "string",
                    description: "Repository name"
                  },
                  title: {
                    type: "string",
                    description: "Issue title"
                  },
                  body: {
                    type: "string",
                    description: "Issue description/body"
                  },
                  labels: {
                    type: "array",
                    items: {
                      type: "string"
                    },
                    description: "Issue labels"
                  }
                }
              }
            },
            {
              name: "github-list-prs",
              description: "List pull requests for a repository",
              inputSchema: {
                type: "object",
                required: ["owner", "repo"],
                properties: {
                  owner: {
                    type: "string",
                    description: "Repository owner/organization"
                  },
                  repo: {
                    type: "string",
                    description: "Repository name"
                  },
                  state: {
                    type: "string",
                    enum: ["open", "closed", "all"],
                    description: "PR state filter"
                  }
                }
              }
            },
            {
              name: "github-get-contents",
              description: "Get contents of a repository directory or file",
              inputSchema: {
                type: "object",
                required: ["owner", "repo"],
                properties: {
                  owner: {
                    type: "string",
                    description: "Repository owner/organization"
                  },
                  repo: {
                    type: "string",
                    description: "Repository name"
                  },
                  path: {
                    type: "string",
                    description: "Path to directory or file (empty for root)"
                  }
                }
              }
            },
            {
              name: "github-search-repos",
              description: "Search for repositories on GitHub",
              inputSchema: {
                type: "object",
                required: ["query"],
                properties: {
                  query: {
                    type: "string",
                    description: "Search query"
                  },
                  sort: {
                    type: "string",
                    enum: ["stars", "forks", "updated"],
                    description: "Sort order"
                  }
                }
              }
            },
            {
              name: "coolify-investigate-app",
              description: "Investigate a Coolify application's GitHub repository, analyzing structure and key files",
              inputSchema: {
                type: "object",
                required: ["coolifyAppInfo"],
                properties: {
                  coolifyAppInfo: {
                    type: "object",
                    description: "Coolify application information object (from coolify-get-application-info)"
                  }
                }
              }
            },
            {
              name: "coolify-analyze-repo",
              description: "Analyze a GitHub repository by URL, with optional specific path analysis",
              inputSchema: {
                type: "object",
                required: ["repoUrl"],
                properties: {
                  repoUrl: {
                    type: "string",
                    description: "GitHub repository URL or owner/repo format"
                  },
                  specificPath: {
                    type: "string",
                    description: "Optional specific file or directory path to analyze"
                  }
                }
              }
            },
            {
              name: "github-create-or-update-file",
              description: "Create or update a file in a GitHub repository",
              inputSchema: {
                type: "object",
                required: ["owner", "repo", "path", "content", "message"],
                properties: {
                  owner: {
                    type: "string",
                    description: "Repository owner/organization"
                  },
                  repo: {
                    type: "string",
                    description: "Repository name"
                  },
                  path: {
                    type: "string",
                    description: "File path in the repository"
                  },
                  content: {
                    type: "string",
                    description: "File content"
                  },
                  message: {
                    type: "string",
                    description: "Commit message"
                  },
                  branch: {
                    type: "string",
                    default: "main",
                    description: "Branch name (default: main)"
                  },
                  sha: {
                    type: "string",
                    description: "File SHA (required for updates, get with github-get-file-sha)"
                  }
                }
              }
            },
            {
              name: "github-get-file-sha",
              description: "Get the SHA of a file (needed for updates/deletes)",
              inputSchema: {
                type: "object",
                required: ["owner", "repo", "path"],
                properties: {
                  owner: {
                    type: "string",
                    description: "Repository owner/organization"
                  },
                  repo: {
                    type: "string",
                    description: "Repository name"
                  },
                  path: {
                    type: "string",
                    description: "File path in the repository"
                  },
                  branch: {
                    type: "string",
                    default: "main",
                    description: "Branch name (default: main)"
                  }
                }
              }
            },
            {
              name: "github-add-submodule",
              description: "Add a git submodule to a repository (creates/updates .gitmodules)",
              inputSchema: {
                type: "object",
                required: ["owner", "repo", "submodulePath", "submoduleUrl"],
                properties: {
                  owner: {
                    type: "string",
                    description: "Repository owner/organization"
                  },
                  repo: {
                    type: "string",
                    description: "Repository name"
                  },
                  submodulePath: {
                    type: "string",
                    description: "Path where submodule should be added (e.g., 'docs')"
                  },
                  submoduleUrl: {
                    type: "string",
                    description: "URL of the submodule repository"
                  },
                  branch: {
                    type: "string",
                    default: "main",
                    description: "Branch name (default: main)"
                  },
                  commitMessage: {
                    type: "string",
                    description: "Custom commit message (optional)"
                  }
                }
              }
            },
            // PayloadCMS Tools
            {
              name: "payload-find-documents",
              description: "Query and find documents in a PayloadCMS collection with filtering, pagination, and sorting",
              inputSchema: {
                type: "object",
                required: ["config", "collection"],
                properties: {
                  config: { type: "object" },
                  collection: { type: "string" },
                  where: { type: "object" },
                  limit: { type: "number" },
                  page: { type: "number" },
                  sort: { type: "string" },
                  depth: { type: "number" },
                  locale: { type: "string" }
                }
              }
            },
            {
              name: "payload-get-document",
              description: "Get a specific document by ID from a PayloadCMS collection",
              inputSchema: {
                type: "object",
                required: ["config", "collection", "id"],
                properties: {
                  config: { type: "object" },
                  collection: { type: "string" },
                  id: { type: "string" },
                  depth: { type: "number" },
                  locale: { type: "string" }
                }
              }
            },
            {
              name: "payload-create-document",
              description: "Create a new document in a PayloadCMS collection",
              inputSchema: {
                type: "object",
                required: ["config", "collection", "data"],
                properties: {
                  config: { type: "object" },
                  collection: { type: "string" },
                  data: { type: "object" },
                  locale: { type: "string" },
                  draft: { type: "boolean" }
                }
              }
            },
            {
              name: "payload-update-document",
              description: "Update an existing document in a PayloadCMS collection",
              inputSchema: {
                type: "object",
                required: ["config", "collection", "id", "data"],
                properties: {
                  config: { type: "object" },
                  collection: { type: "string" },
                  id: { type: "string" },
                  data: { type: "object" },
                  locale: { type: "string" },
                  draft: { type: "boolean" }
                }
              }
            },
            {
              name: "payload-delete-document",
              description: "Delete a document from a PayloadCMS collection",
              inputSchema: {
                type: "object",
                required: ["config", "collection", "id"],
                properties: {
                  config: { type: "object" },
                  collection: { type: "string" },
                  id: { type: "string" }
                }
              }
            },
            {
              name: "payload-login",
              description: "Authenticate with PayloadCMS and obtain JWT token",
              inputSchema: {
                type: "object",
                required: ["config", "email", "password"],
                properties: {
                  config: { type: "object" },
                  collection: { type: "string", default: "users" },
                  email: { type: "string", format: "email" },
                  password: { type: "string" }
                }
              }
            },
            {
              name: "payload-get-current-user",
              description: "Get information about the currently authenticated user",
              inputSchema: {
                type: "object",
                required: ["config"],
                properties: {
                  config: { type: "object" },
                  collection: { type: "string", default: "users" }
                }
              }
            },
            {
              name: "payload-get-global",
              description: "Get a PayloadCMS global configuration",
              inputSchema: {
                type: "object",
                required: ["config", "slug"],
                properties: {
                  config: { type: "object" },
                  slug: { type: "string" },
                  locale: { type: "string" }
                }
              }
            },
            {
              name: "payload-update-global",
              description: "Update a PayloadCMS global configuration",
              inputSchema: {
                type: "object",
                required: ["config", "slug", "data"],
                properties: {
                  config: { type: "object" },
                  slug: { type: "string" },
                  data: { type: "object" },
                  locale: { type: "string" }
                }
              }
            },
            {
              name: "payload-upload-file",
              description: "Upload a file to a PayloadCMS upload collection",
              inputSchema: {
                type: "object",
                required: ["config", "collection", "fileData", "fileName"],
                properties: {
                  config: { type: "object" },
                  collection: { type: "string" },
                  fileData: { type: "string" },
                  fileName: { type: "string" },
                  mimeType: { type: "string" },
                  data: { type: "object" }
                }
              }
            },
            {
              name: "payload-graphql-query",
              description: "Execute a GraphQL query against PayloadCMS",
              inputSchema: {
                type: "object",
                required: ["config", "query"],
                properties: {
                  config: { type: "object" },
                  query: { type: "string" },
                  variables: { type: "object" }
                }
              }
            },
            {
              name: "payload-health-check",
              description: "Check PayloadCMS API connectivity and get version information",
              inputSchema: {
                type: "object",
                required: ["config"],
                properties: {
                  config: { type: "object" }
                }
              }
            }
          ]
        }
      });
      return;
    }

    if (method === "tools/call") {
      const { name, arguments: args } = params;
      
      if (name === "greet") {
        res.json({
          jsonrpc: "2.0",
          id,
          result: {
            content: [
              {
                type: "text",
                text: `Hello, ${args.name}!`
              }
            ]
          }
        });
        return;
      }

      if (name === "multi-greet") {
        res.json({
          jsonrpc: "2.0", 
          id,
          result: {
            content: [
              {
                type: "text",
                text: `Good morning, ${args.name}!`
              }
            ]
          }
        });
        return;
      }

      if (name === "scrape-dynamic-url") {
        // Direct implementation using Playwright
        try {
          const { chromium } = await import("playwright");
          let browser = null;
          
          try {
            // Validate URL and provide helpful error for localhost
            const parsedUrl = new URL(args.url);
            if (parsedUrl.hostname === 'localhost' || parsedUrl.hostname === '127.0.0.1') {
              res.json({
                jsonrpc: "2.0",
                id,
                result: {
                  content: [
                    {
                      type: "text",
                      text: `⚠️  Cannot access localhost from external server. 
Solutions:
1. Use ngrok: 'ngrok http ${parsedUrl.port || '3000'}' then use the ngrok URL
2. Use your local IP instead of localhost (e.g., http://192.168.1.100:${parsedUrl.port || '3000'})
3. Deploy your app to a public URL
4. Run this MCP server locally instead`,
                    },
                  ],
                }
              });
              return;
            }
            
            browser = await chromium.launch({ 
              headless: true,
              timeout: args.timeout || 10000
            });
            const context = await browser.newContext({
              userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
              ignoreHTTPSErrors: args.ignoreHTTPSErrors || false
            });
            const page = await context.newPage();
            
            await page.goto(args.url, { 
              waitUntil: "domcontentloaded",
              timeout: args.timeout || 10000
            });
            
            // Wait for specific selector if provided
            if (args.waitFor) {
              await page.waitForSelector(args.waitFor, { timeout: args.timeout || 10000 });
            }
            
            const text = await page.evaluate(() => document.body.innerText);
            
            res.json({
              jsonrpc: "2.0",
              id,
              result: {
                content: [
                  {
                    type: "text",
                    text: text.trim(),
                  },
                ],
              }
            });
            
          } finally {
            if (browser) {
              await browser.close();
            }
          }
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
          res.json({
            jsonrpc: "2.0",
            id,
            error: {
              code: -32603,
              message: `Error scraping URL: ${errorMessage}`
            }
          });
        }
        return;
      }

      // Handle Flowise tools
      if (name.startsWith("flowise-")) {
        // For the simple endpoint, just pass through to advanced endpoint
        res.json({
          jsonrpc: "2.0",
          id,
          result: {
            content: [
              {
                type: "text",
                text: `Flowise tool "${name}" requires the advanced MCP endpoint. Use /mcp-advanced instead.`
              }
            ]
          }
        });
        return;
      }

      // Handle Context7 tools
      if (name.startsWith("context7-")) {
        // For the simple endpoint, just pass through to advanced endpoint
        res.json({
          jsonrpc: "2.0",
          id,
          result: {
            content: [
              {
                type: "text",
                text: `Context7 tool "${name}" requires the advanced MCP endpoint. Use /mcp-advanced instead.`
              }
            ]
          }
        });
        return;
      }

      // Handle GitHub tools
      if (name === "github-get-user") {
        try {
          const result = await githubGetUser();
          res.json({
            jsonrpc: "2.0",
            id,
            result
          });
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : 'Unknown error';
          res.json({
            jsonrpc: "2.0",
            id,
            error: {
              code: -32603,
              message: `Error calling github-get-user: ${errorMessage}`
            }
          });
        }
        return;
      }

      if (name === "github-list-repos") {
        try {
          const result = await githubListRepos(args.username);
          res.json({
            jsonrpc: "2.0",
            id,
            result
          });
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : 'Unknown error';
          res.json({
            jsonrpc: "2.0",
            id,
            error: {
              code: -32603,
              message: `Error calling github-list-repos: ${errorMessage}`
            }
          });
        }
        return;
      }

      if (name === "github-get-repo") {
        try {
          const result = await githubGetRepo(args.owner, args.repo);
          res.json({
            jsonrpc: "2.0",
            id,
            result
          });
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : 'Unknown error';
          res.json({
            jsonrpc: "2.0",
            id,
            error: {
              code: -32603,
              message: `Error calling github-get-repo: ${errorMessage}`
            }
          });
        }
        return;
      }

      if (name === "github-list-issues") {
        try {
          const result = await githubListIssues(args.owner, args.repo, args.state);
          res.json({
            jsonrpc: "2.0",
            id,
            result
          });
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : 'Unknown error';
          res.json({
            jsonrpc: "2.0",
            id,
            error: {
              code: -32603,
              message: `Error calling github-list-issues: ${errorMessage}`
            }
          });
        }
        return;
      }

      if (name === "github-create-issue") {
        try {
          const result = await githubCreateIssue(args.owner, args.repo, args.title, args.body, args.labels);
          res.json({
            jsonrpc: "2.0",
            id,
            result
          });
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : 'Unknown error';
          res.json({
            jsonrpc: "2.0",
            id,
            error: {
              code: -32603,
              message: `Error calling github-create-issue: ${errorMessage}`
            }
          });
        }
        return;
      }

      if (name === "github-list-prs") {
        try {
          const result = await githubListPRs(args.owner, args.repo, args.state);
          res.json({
            jsonrpc: "2.0",
            id,
            result
          });
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : 'Unknown error';
          res.json({
            jsonrpc: "2.0",
            id,
            error: {
              code: -32603,
              message: `Error calling github-list-prs: ${errorMessage}`
            }
          });
        }
        return;
      }

      if (name === "github-get-contents") {
        try {
          const result = await githubGetContents(args.owner, args.repo, args.path);
          res.json({
            jsonrpc: "2.0",
            id,
            result
          });
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : 'Unknown error';
          res.json({
            jsonrpc: "2.0",
            id,
            error: {
              code: -32603,
              message: `Error calling github-get-contents: ${errorMessage}`
            }
          });
        }
        return;
      }

      if (name === "github-search-repos") {
        try {
          const result = await githubSearchRepos(args.query, args.sort);
          res.json({
            jsonrpc: "2.0",
            id,
            result
          });
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : 'Unknown error';
          res.json({
            jsonrpc: "2.0",
            id,
            error: {
              code: -32603,
              message: `Error calling github-search-repos: ${errorMessage}`
            }
          });
        }
        return;
      }

      if (name === "coolify-investigate-app") {
        try {
          const result = await coolifyInvestigateApp(args.coolifyAppInfo);
          res.json({
            jsonrpc: "2.0",
            id,
            result
          });
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : 'Unknown error';
          res.json({
            jsonrpc: "2.0",
            id,
            error: {
              code: -32603,
              message: `Error calling coolify-investigate-app: ${errorMessage}`
            }
          });
        }
        return;
      }

      if (name === "coolify-analyze-repo") {
        try {
          const result = await coolifyAnalyzeRepo(args.repoUrl, args.specificPath);
          res.json({
            jsonrpc: "2.0",
            id,
            result
          });
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : 'Unknown error';
          res.json({
            jsonrpc: "2.0",
            id,
            error: {
              code: -32603,
              message: `Error calling coolify-analyze-repo: ${errorMessage}`
            }
          });
        }
        return;
      }

      if (name === "github-create-or-update-file") {
        try {
          const result = await githubCreateOrUpdateFile(
            args.owner, 
            args.repo, 
            args.path, 
            args.content, 
            args.message, 
            args.branch, 
            args.sha
          );
          res.json({
            jsonrpc: "2.0",
            id,
            result
          });
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : 'Unknown error';
          res.json({
            jsonrpc: "2.0",
            id,
            error: {
              code: -32603,
              message: `Error calling github-create-or-update-file: ${errorMessage}`
            }
          });
        }
        return;
      }

      if (name === "github-get-file-sha") {
        try {
          const result = await githubGetFileSha(args.owner, args.repo, args.path, args.branch);
          res.json({
            jsonrpc: "2.0",
            id,
            result
          });
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : 'Unknown error';
          res.json({
            jsonrpc: "2.0",
            id,
            error: {
              code: -32603,
              message: `Error calling github-get-file-sha: ${errorMessage}`
            }
          });
        }
        return;
      }

      if (name === "github-add-submodule") {
        try {
          const result = await githubAddSubmodule(
            args.owner,
            args.repo,
            args.submodulePath,
            args.submoduleUrl,
            args.branch,
            args.commitMessage
          );
          res.json({
            jsonrpc: "2.0",
            id,
            result
          });
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : 'Unknown error';
          res.json({
            jsonrpc: "2.0",
            id,
            error: {
              code: -32603,
              message: `Error calling github-add-submodule: ${errorMessage}`
            }
          });
        }
        return;
      }

      // Handle PayloadCMS tools
      if (name.startsWith("payload-")) {
        // For the simple endpoint, just pass through to advanced endpoint
        res.json({
          jsonrpc: "2.0",
          id,
          result: {
            content: [
              {
                type: "text",
                text: `PayloadCMS tool "${name}" requires the advanced MCP endpoint. Use /mcp-advanced instead.`
              }
            ]
          }
        });
        return;
      }

      res.status(400).json({
        jsonrpc: "2.0",
        id,
        error: {
          code: -32601,
          message: `Unknown tool: ${name}`
        }
      });
      return;
    }

    res.status(400).json({
      jsonrpc: "2.0",
      id,
      error: {
        code: -32601,
        message: `Unknown method: ${method}`
      }
    });

  } catch (error) {
    console.error("Error handling MCP request:", error);
    if (!res.headersSent) {
      res.status(500).json({
        jsonrpc: "2.0",
        error: {
          code: -32603,
          message: "Internal server error",
        },
        id: null,
      });
    }
  }
});

// Complex MCP endpoint with session management (for advanced features)
app.post("/mcp-advanced", async (req: Request, res: Response) => {
  try {
    const sessionId = req.headers["mcp-session-id"] as string | undefined;
    let transport: StreamableHTTPServerTransport;

    if (sessionId && transports[sessionId]) {
      transport = transports[sessionId];
    } else if (!sessionId && isInitializeRequest(req.body)) {
      const eventStore = new InMemoryEventStore();
      transport = new StreamableHTTPServerTransport({
        sessionIdGenerator: () => randomUUID(),
        eventStore,
        onsessioninitialized: (sessionId) => {
          transports[sessionId] = transport;
        },
      });

      transport.onclose = () => {
        const sid = transport.sessionId;
        if (sid && transports[sid]) {
          delete transports[sid];
        }
      };

      const server = createMCPServer();
      await server.connect(transport);
      await transport.handleRequest(req, res, req.body);
      return;
    } else {
      res.status(400).json({
        jsonrpc: "2.0",
        error: {
          code: -32000,
          message: "Bad Request: No valid session ID provided",
        },
        id: null,
      });
      return;
    }

    await transport.handleRequest(req, res, req.body);
  } catch (error) {
    console.error("Error handling MCP advanced request:", error);
    if (!res.headersSent) {
      res.status(500).json({
        jsonrpc: "2.0",
        error: {
          code: -32603,
          message: "Internal server error",
        },
        id: null,
      });
    }
  }
});

// SSE endpoint following official MCP patterns
app.get("/sse", async (req: Request, res: Response) => {
  try {
    console.log(`SSE connection attempt from ${req.ip}`);
    
    // Validate Origin header for DNS rebinding protection (recommended by MCP spec)
    const origin = req.headers.origin;
    if (origin && !origin.startsWith('http://localhost') && !origin.startsWith('https://localhost')) {
      console.warn(`Potentially unsafe origin: ${origin}`);
    }
    
    // Create SSE transport with DNS rebinding protection options
    const transport = new SSEServerTransport("/messages", res, {
      enableDnsRebindingProtection: false, // Disable for local development
      allowedHosts: ['localhost', '127.0.0.1'],
      allowedOrigins: ['http://localhost:3010', 'https://localhost:3010']
    });
    
    sseTransports[transport.sessionId] = transport;

    res.on("close", () => {
      delete sseTransports[transport.sessionId];
      console.log(`SSE connection closed for session: ${transport.sessionId}`);
    });

    const server = createMCPServer();
    await server.connect(transport);
    console.log(`SSE connection established for session: ${transport.sessionId}`);
  } catch (error) {
    console.error("Error handling SSE connection:", error);
    if (!res.headersSent) {
      res.status(500).json({ error: "Internal server error" });
    }
  }
});

// Messages endpoint for SSE transport (following MCP spec)
app.post("/messages", async (req: Request, res: Response) => {
  try {
    const sessionId = req.query.sessionId as string | undefined;
    
    console.log(`Message received for session: ${sessionId}`);
    
    if (!sessionId || !sseTransports[sessionId]) {
      console.error(`Invalid or missing sessionId: ${sessionId}`);
      res.status(400).json({ error: "Invalid or missing sessionId" });
      return;
    }
    
    const transport = sseTransports[sessionId];
    
    // Use the transport's built-in message handling
    await transport.handlePostMessage(req, res, req.body);
  } catch (error) {
    console.error("Error handling SSE message:", error);
    if (!res.headersSent) {
      res.status(500).json({ error: "Internal server error" });
    }
  }
});

// Session cleanup endpoint
app.delete("/mcp", async (req: Request, res: Response) => {
  try {
    const sessionId = req.headers["mcp-session-id"] as string | undefined;
    if (!sessionId || !transports[sessionId]) {
      res.status(400).json({ error: "Invalid or missing session ID" });
      return;
    }

    const transport = transports[sessionId];
    await transport.handleRequest(req, res);
  } catch (error) {
    console.error("Error handling session cleanup:", error);
    if (!res.headersSent) {
      res.status(500).json({ error: "Error processing session termination" });
    }
  }
});

// Start server
app.listen(PORT, () => {
  console.log(`TypeScript MCP Server listening on port ${PORT}`);
});

// Graceful shutdown
process.on("SIGINT", async () => {
  console.log("Shutting down gracefully...");
  
  // Close all transports
  for (const sessionId in transports) {
    try {
      await transports[sessionId].close();
      delete transports[sessionId];
    } catch (error) {
      console.error(`Error closing transport ${sessionId}:`, error);
    }
  }
  
  for (const sessionId in sseTransports) {
    try {
      delete sseTransports[sessionId];
    } catch (error) {
      console.error(`Error cleaning up SSE transport ${sessionId}:`, error);
    }
  }
  
  process.exit(0);
});