import express, { Request, Response } from "express";
import { McpServer, ResourceTemplate  } from "@modelcontextprotocol/sdk/server/mcp.js";
import { SSEServerTransport} from "@modelcontextprotocol/sdk/server/sse.js";
import { z } from "zod";
// import { ResourceTemplate } from "@modelcontextprotocol/sdk/server/resource.js";


const server = new McpServer({
  name: "example-server",
  version: "1.0.0"
});

// Example tool for adding numbers
server.tool(
  "add-numbers",
  {
    a: z.number(),
    b: z.number()
  },
  async ({ a, b }) => ({
    content: [{
      type: "text",
      text: String(a + b)
    }]
  })
);

// Example resource for fetching greetings
server.resource(
  "greeting",
  new ResourceTemplate("greeting://{name}", { list: undefined }),
  async (uri, { name }) => ({
    contents: [{
      uri: uri.href,
      text: `Hello, ${name}! Welcome to the TypeScript MCP server.`
    }]
  })
);

// Example tool for string operations
server.tool(
  "string-operations",
  {
    text: z.string(),
    operation: z.enum(["uppercase", "lowercase", "reverse"])
  },
  async ({ text, operation }) => {
    let result: string;
    
    switch (operation) {
      case "uppercase":
        result = text.toUpperCase();
        break;
      case "lowercase":
        result = text.toLowerCase();
        break;
      case "reverse":
        result = text.split('').reverse().join('');
        break;
      default:
        throw new Error(`Unknown operation: ${operation}`);
    }

    return {
      content: [{
        type: "text",
        text: result
      }]
    };
  }
);

const app = express();

// to support multiple simultaneous connections we have a lookup object from
// sessionId to transport
const transports: {[sessionId: string]: SSEServerTransport} = {};

app.get("/sse", async (_: Request, res: Response) => {
  const transport = new SSEServerTransport('/messages', res);
  transports[transport.sessionId] = transport;
  res.on("close", () => {
    delete transports[transport.sessionId];
  });
  await server.connect(transport);
});

app.post("/messages", async (req: Request, res: Response) => {
  const sessionId = req.query.sessionId as string;
  const transport = transports[sessionId];
  if (transport) {
    await transport.handlePostMessage(req, res);
  } else {
    res.status(400).send('No transport found for sessionId');
  }
});

app.listen(3001);

// import express from 'express';
// import cors from 'cors';
// import { McpServer, ResourceTemplate } from "@modelcontextprotocol/sdk/server/mcp.js";
// import { SSEServerTransport } from "@modelcontextprotocol/sdk/server/sse.js";
// import { z } from 'zod';

// // Create Express app
// const app = express();
// app.use(cors());
// app.use(express.json());

// // Create MCP server
// const server = new McpServer({
//   name: "TypeScript Demo Server",
//   version: "1.0.0",
//   description: "Demo MCP server with example tools and resources"
// });

// // Example tool for adding numbers
// server.tool(
//   "add-numbers",
//   {
//     a: z.number(),
//     b: z.number()
//   },
//   async ({ a, b }) => ({
//     content: [{
//       type: "text",
//       text: String(a + b)
//     }]
//   })
// );

// // Example resource for fetching greetings
// server.resource(
//   "greeting",
//   new ResourceTemplate("greeting://{name}", { list: undefined }),
//   async (uri, { name }) => ({
//     contents: [{
//       uri: uri.href,
//       text: `Hello, ${name}! Welcome to the TypeScript MCP server.`
//     }]
//   })
// );

// // Example tool for string operations
// server.tool(
//   "string-operations",
//   {
//     text: z.string(),
//     operation: z.enum(["uppercase", "lowercase", "reverse"])
//   },
//   async ({ text, operation }) => {
//     let result: string;
    
//     switch (operation) {
//       case "uppercase":
//         result = text.toUpperCase();
//         break;
//       case "lowercase":
//         result = text.toLowerCase();
//         break;
//       case "reverse":
//         result = text.split('').reverse().join('');
//         break;
//       default:
//         throw new Error(`Unknown operation: ${operation}`);
//     }

//     return {
//       content: [{
//         type: "text",
//         text: result
//       }]
//     };
//   }
// );

// // Map to store active transports
// const transports: Record<string, SSEServerTransport> = {};

// // Set up SSE endpoint
// app.get("/sse", async (req, res) => {
//   try {
//     res.writeHead(200, {
//       'Content-Type': 'text/event-stream',
//       'Cache-Control': 'no-cache',
//       'Connection': 'keep-alive',
//       'Access-Control-Allow-Origin': '*'
//     });

//     const transport = new SSEServerTransport('/messages', res);
//     transports[transport.sessionId] = transport;

//     req.on("close", () => {
//       delete transports[transport.sessionId];
//     });

//     await server.connect(transport);
//   } catch (error) {
//     console.error("Error connecting transport:", error);
//     if (!res.writableEnded) {
//       res.end();
//     }
//   }
// });

// // Set up message endpoint
// app.post("/messages", async (req, res) => {
//   try {
//     const sessionId = req.query.sessionId as string;
//     const transport = transports[sessionId];

//     if (!transport) {
//       res.status(400).json({ error: 'No transport found for sessionId' });
//       return;
//     }

//     res.writeHead(200, {
//       'Content-Type': 'application/json',
//       'Access-Control-Allow-Origin': '*'
//     });

//     await transport.handlePostMessage(req, res);
//   } catch (error) {
//     console.error("Error handling message:", error);
//     if (!res.writableEnded) {
//       res.end(JSON.stringify({ error: 'Internal server error' }));
//     }
//   }
// });

// // Start the server
// const PORT = 3002;
// app.listen(PORT, () => {
//   console.log(`TypeScript MCP Server running on port ${PORT}`);
// });