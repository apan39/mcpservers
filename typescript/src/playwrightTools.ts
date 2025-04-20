import { chromium } from "playwright";
import { z } from "zod";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";

/**
 * Registers the "scrape-dynamic-url" tool on the provided MCP server.
 */
export function registerPlaywrightTools(server: McpServer) {
  server.tool(
    "scrape-dynamic-url",
    {
      url: z.string().describe("The URL to scrape"),
    },
    async ({ url }) => {
      const browser = await chromium.launch();
      const page = await browser.newPage();
      await page.goto(url, { waitUntil: "domcontentloaded" });
      const text = await page.evaluate(() => document.body.innerText);
      await browser.close();
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
}
