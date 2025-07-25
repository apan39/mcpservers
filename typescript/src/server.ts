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

// Authentication middleware
app.use((req, res, next) => {
  // Allow health check without auth
  if (req.path === "/health") return next();
  
  // Check Authorization header
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
        // Basic implementation - you can enhance this
        res.json({
          jsonrpc: "2.0",
          id,
          result: {
            content: [
              {
                type: "text",
                text: `Would scrape URL: ${args.url} (Playwright tool not implemented in simplified mode)`
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

// SSE endpoints for MCP Inspector compatibility
app.get("/sse", async (req: Request, res: Response) => {
  try {
    const transport = new SSEServerTransport("/messages", res);
    sseTransports[transport.sessionId] = transport;

    res.on("close", () => {
      delete sseTransports[transport.sessionId];
    });

    const server = createMCPServer();
    await server.connect(transport);
  } catch (error) {
    console.error("Error handling SSE connection:", error);
  }
});

app.post("/messages", async (req: Request, res: Response) => {
  try {
    const sessionId = req.query.sessionId as string | undefined;
    if (!sessionId || !sseTransports[sessionId]) {
      res.status(400).json({ error: "Invalid or missing sessionId" });
      return;
    }
    const transport = sseTransports[sessionId];
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