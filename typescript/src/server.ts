import express, { Request, Response } from "express";
import {
  McpServer,
  ResourceTemplate,
} from "@modelcontextprotocol/sdk/server/mcp.js";
import { SSEServerTransport } from "@modelcontextprotocol/sdk/server/sse.js";
import { z } from "zod";
// import { ResourceTemplate } from "@modelcontextprotocol/sdk/server/resource.js";

import { registerPlaywrightTools } from "./playwrightTools.js";

const server = new McpServer({
  name: "example-server",
  version: "1.0.0",
});

// Example tool for adding numbers
server.tool(
  "add-numbers",
  {
    a: z.number(),
    b: z.number(),
  },
  async ({ a, b }) => ({
    content: [
      {
        type: "text",
        text: String(a + b),
      },
    ],
  })
);

// Example resource for fetching greetings
server.resource(
  "greeting",
  new ResourceTemplate("greeting://{name}", { list: undefined }),
  async (uri, { name }) => ({
    contents: [
      {
        uri: uri.href,
        text: `Hello, ${name}! Welcome to the TypeScript MCP server.`,
      },
    ],
  })
);

// Example tool for string operations
server.tool(
  "string-operations",
  {
    text: z.string(),
    operation: z.enum(["uppercase", "lowercase", "reverse"]),
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
        result = text.split("").reverse().join("");
        break;
      default:
        throw new Error(`Unknown operation: ${operation}`);
    }

    return {
      content: [
        {
          type: "text",
          text: result,
        },
      ],
    };
  }
);

import Tesseract from "tesseract.js";
// pdfjsLib will be dynamically imported in the tool handler for ES module compatibility

// OCR tool using tesseract.js
server.tool(
  "ocr-tesseract",
  {
    imageBase64: z.string().describe("Image file as base64-encoded string"),
    lang: z.string().optional().default("eng"),
  },
  async ({ imageBase64, lang }) => {
    const imageBuffer = Buffer.from(imageBase64, "base64");
    const { data } = await Tesseract.recognize(imageBuffer, lang);
    return {
      content: [
        {
          type: "text",
          text: data.text,
        },
      ],
    };
  }
);

// PDF text extraction tool using pdfjs-dist
server.tool(
  "extract-pdf-text",
  {
    pdfBase64: z.string().describe("PDF file as base64-encoded string"),
  },
  async ({ pdfBase64 }) => {
    const pdfjsLib = await import("pdfjs-dist/legacy/build/pdf.mjs");
    const pdfBuffer = Buffer.from(pdfBase64, "base64");
    const loadingTask = pdfjsLib.getDocument({ data: pdfBuffer });
    const pdf = await loadingTask.promise;
    let text = "";
    for (let i = 1; i <= pdf.numPages; i++) {
      const page = await pdf.getPage(i);
      const content = await page.getTextContent();
      text += content.items.map((item: any) => item.str).join(" ") + "\n";
    }
    return {
      content: [
        {
          type: "text",
          text,
        },
      ],
    };
  }
);

registerPlaywrightTools(server);

const app = express();

// Enable CORS for all routes
// Rate limiting for failed API key attempts
import cors from "cors";
app.use(cors());

import rateLimit from "express-rate-limit";

// Track failed attempts per IP
const failedAuthLimiter = rateLimit({
  windowMs: 1 * 60 * 1000, // 15 minutes
  max: 5, // limit each IP to 5 failed attempts per windowMs
  message: { detail: "Too many failed API key attempts, please try again later." },
  keyGenerator: (req) => req.ip || "unknown",
  skipSuccessfulRequests: false,
});

// Load .env from parent directory if present
import path from "path";
import dotenv from "dotenv";
// __dirname is not available in ES modules, use import.meta.url
import { fileURLToPath } from "url";
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
dotenv.config({ path: path.resolve(__dirname, "../../.env") });
// API key authentication middleware
const API_KEY = process.env.MCP_API_KEY || "changeme";
const failedAuthAttempts: Record<string, { count: number; lockUntil: number }> = {};
const MAX_FAILED_ATTEMPTS = 5;
const LOCK_TIME_MS = 15 * 60 * 1000; // 15 minutes

app.use((req, res, next) => {
  // Allow health check without auth
  if (req.path === "/health") return next();
  const ip = req.ip || "unknown";
  const now = Date.now();

  // Check if IP is locked out
  if (failedAuthAttempts[ip] && failedAuthAttempts[ip].lockUntil > now) {
    return res.status(429).json({ detail: "Too many failed API key attempts, please try again later." });
  }

  const auth = req.header("authorization");
  if (!auth || auth !== `Bearer ${API_KEY}`) {
    // Increment failed attempts
    if (!failedAuthAttempts[ip]) {
      failedAuthAttempts[ip] = { count: 1, lockUntil: 0 };
    } else {
      failedAuthAttempts[ip].count += 1;
    }
    console.log("Failed API key attempt from IP:", ip, "Header:", auth, "Count:", failedAuthAttempts[ip].count);

    // Lock out if max attempts reached
    if (failedAuthAttempts[ip].count >= MAX_FAILED_ATTEMPTS) {
      failedAuthAttempts[ip].lockUntil = now + LOCK_TIME_MS;
      failedAuthAttempts[ip].count = 0; // reset count after lock
      return res.status(429).json({ detail: "Too many failed API key attempts, please try again later." });
    }
    return res.status(401).json({ detail: "Unauthorized" });
  }

  // On successful auth, reset failed attempts
  if (failedAuthAttempts[ip]) {
    delete failedAuthAttempts[ip];
  }
  next();
});
// to support multiple simultaneous connections we have a lookup object from
// sessionId to transport
const transports: { [sessionId: string]: SSEServerTransport } = {};

app.get("/sse", async (_: Request, res: Response) => {
  const transport = new SSEServerTransport("/messages", res);
  transports[transport.sessionId] = transport;
  res.on("close", () => {
    delete transports[transport.sessionId];
  });
  await server.connect(transport);
});

app.post("/messages", async (req: Request, res: Response) => {
  // Disable API key check for /messages endpoint (SSE POST)
  const sessionId = req.query.sessionId as string;
  const transport = transports[sessionId];
  if (transport) {
    await transport.handlePostMessage(req, res);
  } else {
    res.status(400).send("No transport found for sessionId");
  }
});

app.listen(3001, () => {
  console.log("MCP TypeScript server running at http://localhost:3001");
});

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
