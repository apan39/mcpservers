import express, { Request, Response } from "express";
import { randomUUID } from "node:crypto";
import { z } from "zod";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import {
  CallToolResult,
  GetPromptResult,
  isInitializeRequest,
  ReadResourceResult,
} from "@modelcontextprotocol/sdk/types.js";

import { registerPlaywrightTools } from "./playwrightTools.js";
// If you want resumability, you can implement an event store (optional)
// For demo, we'll use a simple in-memory event store
class InMemoryEventStore {
  private events: Record<string, any[]> = {};
  async storeEvent(streamId: string, message: any): Promise<string> {
    if (!this.events[streamId]) this.events[streamId] = [];
    this.events[streamId].push(message);
    // Use array length as event ID for simplicity
    return String(this.events[streamId].length - 1);
  }
  async replayEventsAfter(
    lastEventId: string,
    { send }: { send: (eventId: string, message: any) => Promise<void> }
  ): Promise<string> {
    // For demo, just replay all events after lastEventId
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
  async append(sessionId: string, event: any) {
    // Deprecated, for compatibility
    return this.storeEvent(sessionId, event);
  }
  async getEvents(sessionId: string) {
    return this.events[sessionId] || [];
  }
  async clear(sessionId: string) {
    delete this.events[sessionId];
  }
}

// Create an MCP server with implementation details
function getServer(): McpServer {
  const server = new McpServer(
    {
      name: "simple-streamable-http-server",
      version: "1.0.0",
    },
    { capabilities: { logging: {} } }
  );

  // Register a simple tool that returns a greeting
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

  // Register a tool that sends multiple greetings with notifications
  server.tool(
    "multi-greet",
    "A tool that sends different greetings with delays between them",
    {
      name: z.string().describe("Name to greet"),
    },
    // Remove extra options object to match expected signature
    async (
      { name }: { name: string },
      { sendNotification }: { sendNotification: (msg: any) => Promise<void> }
    ): Promise<CallToolResult> => {
      const sleep = (ms: number) =>
        new Promise((resolve) => setTimeout(resolve, ms));

      await sendNotification({
        method: "notifications/message",
        params: { level: "debug", data: `Starting multi-greet for ${name}` },
      });

      await sleep(1000);

      await sendNotification({
        method: "notifications/message",
        params: { level: "info", data: `Sending first greeting to ${name}` },
      });

      await sleep(1000);

      await sendNotification({
        method: "notifications/message",
        params: { level: "info", data: `Sending second greeting to ${name}` },
      });

      return {
        content: [
          {
            type: "text",
            text: `Good morning, ${name}!`,
          },
        ],
      };
    }
  );

  // Register a simple prompt
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

  // Register a tool for testing resumability
  server.tool(
    "start-notification-stream",
    "Starts sending periodic notifications for testing resumability",
    {
      interval: z
        .number()
        .describe("Interval in milliseconds between notifications")
        .default(100),
      count: z
        .number()
        .describe("Number of notifications to send (0 for 100)")
        .default(50),
    },
    async (
      { interval, count },
      { sendNotification }
    ): Promise<CallToolResult> => {
      const sleep = (ms: number) =>
        new Promise((resolve) => setTimeout(resolve, ms));
      let counter = 0;

      while (count === 0 || counter < count) {
        counter++;
        try {
          await sendNotification({
            method: "notifications/message",
            params: {
              level: "info",
              data: `Periodic notification #${counter} at ${new Date().toISOString()}`,
            },
          });
        } catch (error) {
          console.error("Error sending notification:", error);
        }
        await sleep(interval);
      }

      return {
        content: [
          {
            type: "text",
            text: `Started sending periodic notifications every ${interval}ms`,
          },
        ],
      };
    }
  );

  // Register Playwright tools
  registerPlaywrightTools(server);
  return server;

  // Create a simple resource at a fixed URI
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
  return server;
}

const app = express();
app.use(express.json());

// Map to store transports by session ID
const transports: { [sessionId: string]: StreamableHTTPServerTransport } = {};

app.post("/mcp", async (req: Request, res: Response) => {
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

      const server = getServer();
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

app.get("/mcp", async (req: Request, res: Response) => {
  const sessionId = req.headers["mcp-session-id"] as string | undefined;
  const acceptHeader = req.headers["accept"] || "";
  const isSSE =
    typeof acceptHeader === "string" &&
    acceptHeader.includes("text/event-stream");

  if (!sessionId || !transports[sessionId]) {
    if (isSSE) {
      // SSE client: respond with SSE error message instead of 400
      res.set({
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        Connection: "keep-alive",
      });
      res.flushHeaders();
      res.write(
        `data: ${JSON.stringify({
          message: "SSE transport is deprecated. Use streamable-http instead.",
          code: 400,
          type: "error",
        })}\n\n`
      );
      res.end();
    } else {
      res.status(400).send("Invalid or missing session ID");
    }
    return;
  }

  const lastEventId = req.headers["last-event-id"] as string | undefined;
  const transport = transports[sessionId];
  // --- SSE support using /connect and /messages endpoints ---

  import { SSEServerTransport } from "@modelcontextprotocol/sdk/server/sse.js";

  // Map to store SSE transports by session ID
  const sseTransports: { [sessionId: string]: SSEServerTransport } = {};

  // SSE connection endpoint
  app.get("/connect", async (req: Request, res: Response) => {
    // Create a new SSE transport and connect to the MCP server
    const transport = new SSEServerTransport("/messages", res);
    sseTransports[transport.sessionId] = transport;

    res.on("close", () => {
      delete sseTransports[transport.sessionId];
    });

    const server = getServer();
    await server.connect(transport);

    // Optionally send a welcome message or start streaming
    // await transport.send({ jsonrpc: "2.0", method: "sse/connection", params: { message: "SSE Connection established" } });
  });

  // SSE message POST endpoint
  app.post("/messages", async (req: Request, res: Response) => {
    const sessionId = req.query.sessionId as string | undefined;
    if (!sessionId || !sseTransports[sessionId]) {
      res.status(400).send({ message: "Invalid or missing sessionId" });
      return;
    }
    const transport = sseTransports[sessionId];
    await transport.handlePostMessage(req, res, req.body);
  });

  if (isSSE) {
    // SSE streaming logic (same as /mcp-sse)
    const eventStore = (transport as any).eventStore as any;
    if (!eventStore) {
      res.status(500).send("No event store found for session");
      return;
    }

    res.set({
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache",
      Connection: "keep-alive",
    });
    res.flushHeaders();

    const events = await eventStore.getEvents(sessionId);
    let lastId = 0;
    for (let i = 0; i < events.length; i++) {
      res.write(`id: ${i}\ndata: ${JSON.stringify(events[i])}\n\n`);
      lastId = i;
    }

    const interval = setInterval(async () => {
      const newEvents = await eventStore.getEvents(sessionId);
      for (let i = lastId + 1; i < newEvents.length; i++) {
        res.write(`id: ${i}\ndata: ${JSON.stringify(newEvents[i])}\n\n`);
        lastId = i;
      }
    }, 1000);

    req.on("close", () => {
      clearInterval(interval);
      res.end();
    });
  } else {
    await transport.handleRequest(req, res);
  }
});
// SSE endpoint for streaming events in parallel to HTTP streaming
app.get("/mcp-sse", async (req: Request, res: Response) => {
  const sessionId = req.headers["mcp-session-id"] as string | undefined;
  if (!sessionId || !transports[sessionId]) {
    res.status(400).send("Invalid or missing session ID");
    return;
  }

  // Set SSE headers
  res.set({
    "Content-Type": "text/event-stream",
    "Cache-Control": "no-cache",
    Connection: "keep-alive",
  });
  res.flushHeaders();

  // Access the event store from the transport
  const transport = transports[sessionId];
  const eventStore = (transport as any).eventStore as any;
  if (!eventStore) {
    res.status(500).send("No event store found for session");
    return;
  }

  // Get all events for the session and stream them
  const events = await eventStore.getEvents(sessionId);
  let lastId = 0;
  for (let i = 0; i < events.length; i++) {
    res.write(`id: ${i}\ndata: ${JSON.stringify(events[i])}\n\n`);
    lastId = i;
  }

  // Listen for new events and stream them as they arrive
  const interval = setInterval(async () => {
    const newEvents = await eventStore.getEvents(sessionId);
    for (let i = lastId + 1; i < newEvents.length; i++) {
      res.write(`id: ${i}\ndata: ${JSON.stringify(newEvents[i])}\n\n`);
      lastId = i;
    }
  }, 1000);

  req.on("close", () => {
    clearInterval(interval);
    res.end();
  });
});

app.delete("/mcp", async (req: Request, res: Response) => {
  const sessionId = req.headers["mcp-session-id"] as string | undefined;
  if (!sessionId || !transports[sessionId]) {
    res.status(400).send("Invalid or missing session ID");
    return;
  }

  try {
    const transport = transports[sessionId];
    await transport.handleRequest(req, res);
  } catch (error) {
    if (!res.headersSent) {
      res.status(500).send("Error processing session termination");
    }
  }
});

const PORT = 3000;
app.listen(PORT, () => {
  console.log(`MCP Streamable HTTP Server listening on port ${PORT}`);
});

process.on("SIGINT", async () => {
  for (const sessionId in transports) {
    try {
      await transports[sessionId].close();
      delete transports[sessionId];
    } catch (error) {
      // Ignore errors on shutdown
    }
  }
  process.exit(0);
});
