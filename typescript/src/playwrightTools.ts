import { chromium } from "playwright";
import { z } from "zod";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";

/**
 * Registers Playwright tools on the provided MCP server.
 */
export function registerPlaywrightTools(server: McpServer) {
  server.tool(
    "scrape-dynamic-url",
    "Scrape text content from a dynamic webpage using Playwright. Note: When deployed externally, localhost URLs won't work - use ngrok, your public IP, or deploy to the same network.",
    {
      url: z.string().url().describe("The URL to scrape (use ngrok URL for local dev servers when deployed externally)"),
      waitFor: z.string().optional().describe("CSS selector to wait for before scraping"),
      timeout: z.number().min(1000).max(30000).default(10000).describe("Timeout in milliseconds"),
      ignoreHTTPSErrors: z.boolean().default(false).describe("Ignore HTTPS certificate errors for development"),
    },
    async ({ url, waitFor, timeout, ignoreHTTPSErrors }) => {
      let browser = null;
      try {
        // Validate URL and provide helpful error for localhost
        const parsedUrl = new URL(url);
        if (parsedUrl.hostname === 'localhost' || parsedUrl.hostname === '127.0.0.1') {
          return {
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
          };
        }
        
        browser = await chromium.launch({ 
          headless: true,
          timeout: timeout
        });
        const context = await browser.newContext({
          userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
          ignoreHTTPSErrors: ignoreHTTPSErrors
        });
        const page = await context.newPage();
        
        await page.goto(url, { 
          waitUntil: "domcontentloaded",
          timeout: timeout
        });
        
        // Wait for specific selector if provided
        if (waitFor) {
          await page.waitForSelector(waitFor, { timeout: timeout });
        }
        
        const text = await page.evaluate(() => document.body.innerText);
        
        return {
          content: [
            {
              type: "text",
              text: text.trim(),
            },
          ],
        };
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
        return {
          content: [
            {
              type: "text",
              text: `Error scraping URL: ${errorMessage}`,
            },
          ],
        };
      } finally {
        if (browser) {
          await browser.close();
        }
      }
    }
  );
}
