import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { CallToolResult } from "@modelcontextprotocol/sdk/types.js";
import { z } from "zod";
import fetch from "node-fetch";

// Context7 MCP client configuration
const CONTEXT7_BASE_URL = process.env.CONTEXT7_MCP_URL || 'https://mcp.context7.com';

// Helper function to make MCP calls to context7 server
async function callContext7Tool(toolName: string, params: any): Promise<any> {
  try {
    const response = await fetch(`${CONTEXT7_BASE_URL}/mcp`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/event-stream',
      },
      body: JSON.stringify({
        jsonrpc: '2.0',
        id: Date.now(),
        method: 'tools/call',
        params: {
          name: toolName,
          arguments: params
        }
      })
    });

    if (!response.ok) {
      throw new Error(`Context7 server error: ${response.status} ${response.statusText}`);
    }

    const result = await response.json();
    
    if (result.error) {
      throw new Error(`Context7 tool error: ${result.error.message}`);
    }

    return result.result;
  } catch (error) {
    throw new Error(`Failed to call context7 tool ${toolName}: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
}

export function registerContext7Tools(server: McpServer) {
  // Tool to resolve library documentation using context7
  server.tool(
    "context7-get-docs",
    "Get up-to-date documentation and code examples for a library using context7",
    {
      library: z.string().describe("Library name or identifier (e.g., 'react', 'next.js', 'typescript')"),
      version: z.string().optional().describe("Specific version to get docs for (optional, uses latest if not specified)"),
      query: z.string().optional().describe("Specific query or topic within the library documentation"),
    },
    async ({ library, version, query }): Promise<CallToolResult> => {
      try {
        // First, try to resolve the library ID
        const resolveResult = await callContext7Tool('resolve-library-id', { libraryName: library });
        
        let result = 'Context7 Integration Active\n\n';
        result += `Library: ${library}\n`;
        if (version) result += `Version: ${version}\n`;
        if (query) result += `Query: ${query}\n`;
        result += '\n--- Context7 Response ---\n';
        
        if (resolveResult && resolveResult.content) {
          if (Array.isArray(resolveResult.content)) {
            result += resolveResult.content.map((c: any) => c.text || c.content || JSON.stringify(c)).join('\n');
          } else {
            result += resolveResult.content.text || resolveResult.content || JSON.stringify(resolveResult);
          }
        } else {
          result += JSON.stringify(resolveResult, null, 2);
        }
        
        // Extract library ID from resolve result and get docs if query provided
        if (query && resolveResult && resolveResult.content) {
          try {
            // Try to extract library ID from the resolve result
            const resolveText = Array.isArray(resolveResult.content) 
              ? resolveResult.content.map((c: any) => c.text || c.content || '').join(' ')
              : (resolveResult.content.text || resolveResult.content || '');
            
            // Look for library ID pattern in the response
            const libraryIdMatch = resolveText.match(/\/[\w-]+\/[\w.-]+(?:\/[\w.-]+)?/);
            
            if (libraryIdMatch) {
              const libraryId = libraryIdMatch[0];
              const docsResult = await callContext7Tool('get-library-docs', { 
                context7CompatibleLibraryID: libraryId,
                topic: query 
              });
              
              if (docsResult && docsResult.content) {
                result += '\n\n--- Documentation Query Results ---\n';
                if (Array.isArray(docsResult.content)) {
                  result += docsResult.content.map((c: any) => c.text || c.content || JSON.stringify(c)).join('\n');
                } else {
                  result += docsResult.content.text || docsResult.content || JSON.stringify(docsResult);
                }
              }
            } else {
              result += `\n\nNote: Could not extract library ID from resolve result to fetch specific documentation.`;
            }
          } catch (docsError) {
            result += `\n\nNote: Could not fetch specific documentation query: ${docsError}`;
          }
        }

        return {
          content: [
            {
              type: "text",
              text: result,
            },
          ],
        };
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        return {
          content: [
            {
              type: "text",
              text: `Error connecting to context7 for ${library}: ${errorMessage}\n\nNote: Using public context7 server at ${CONTEXT7_BASE_URL}\nIf you prefer a local instance, set CONTEXT7_MCP_URL environment variable.`,
            },
          ],
        };
      }
    }
  );

  // Tool to search for code examples using context7
  server.tool(
    "context7-search-examples",
    "Search for code examples and usage patterns for a specific library or framework",
    {
      library: z.string().describe("Library name to search examples for"),
      pattern: z.string().describe("Specific pattern, function, or use case to find examples for"),
      language: z.string().optional().describe("Programming language preference (e.g., 'typescript', 'javascript')"),
    },
    async ({ library, pattern, language }): Promise<CallToolResult> => {
      try {
        let searchQuery = `${pattern}`;
        if (language) {
          searchQuery += ` ${language} examples`;
        }

        // First resolve the library to get the proper ID
        const resolveResult = await callContext7Tool('resolve-library-id', { libraryName: library });
        
        // Extract library ID from resolve result
        const resolveText = Array.isArray(resolveResult.content) 
          ? resolveResult.content.map((c: any) => c.text || c.content || '').join(' ')
          : (resolveResult.content.text || resolveResult.content || '');
        
        const libraryIdMatch = resolveText.match(/\/[\w-]+\/[\w.-]+(?:\/[\w.-]+)?/);
        
        if (!libraryIdMatch) {
          throw new Error('Could not resolve library ID');
        }
        
        const docsResult = await callContext7Tool('get-library-docs', { 
          context7CompatibleLibraryID: libraryIdMatch[0],
          topic: searchQuery 
        });
        
        let result = `Context7 Examples Search\n\n`;
        result += `Library: ${library}\n`;
        result += `Pattern: ${pattern}\n`;
        if (language) result += `Language: ${language}\n`;
        result += '\n--- Examples ---\n';
        
        if (docsResult && docsResult.content) {
          if (Array.isArray(docsResult.content)) {
            result += docsResult.content.map((c: any) => c.text || c.content || JSON.stringify(c)).join('\n');
          } else {
            result += docsResult.content.text || docsResult.content || JSON.stringify(docsResult);
          }
        } else {
          result += `No examples found for ${library} with pattern: ${pattern}`;
        }

        return {
          content: [
            {
              type: "text",
              text: result,
            },
          ],
        };
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        return {
          content: [
            {
              type: "text",
              text: `Error searching examples for ${library}: ${errorMessage}\n\nNote: Using public context7 server at ${CONTEXT7_BASE_URL}`,
            },
          ],
        };
      }
    }
  );

  // Tool to get the latest version info for a library
  server.tool(
    "context7-library-info",
    "Get general information and latest version details for a library",
    {
      library: z.string().describe("Library name to get information for"),
    },
    async ({ library }): Promise<CallToolResult> => {
      try {
        const resolveResult = await callContext7Tool('resolve-library-id', { libraryName: library });
        
        let result = `Context7 Library Information\n\n`;
        result += `Library: ${library}\n\n`;
        result += '--- Library Details ---\n';
        
        if (resolveResult && resolveResult.content) {
          if (Array.isArray(resolveResult.content)) {
            result += resolveResult.content.map((c: any) => c.text || c.content || JSON.stringify(c)).join('\n');
          } else {
            result += resolveResult.content.text || resolveResult.content || JSON.stringify(resolveResult);
          }
        } else {
          result += `No information found for library: ${library}`;
        }

        return {
          content: [
            {
              type: "text",
              text: result,
            },
          ],
        };
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        return {
          content: [
            {
              type: "text",
              text: `Error getting library info for ${library}: ${errorMessage}\n\nNote: Using public context7 server at ${CONTEXT7_BASE_URL}`,
            },
          ],
        };
      }
    }
  );

  // Tool to get context for AI coding assistance
  server.tool(
    "context7-ai-context",
    "Get comprehensive context for AI coding assistance with up-to-date library information",
    {
      libraries: z.array(z.string()).describe("Array of library names to get context for"),
      task: z.string().describe("Description of the coding task or what you're trying to build"),
      preferences: z.object({
        typescript: z.boolean().optional().describe("Prefer TypeScript examples"),
        react: z.boolean().optional().describe("Focus on React-related examples"),
        latest: z.boolean().optional().describe("Only use latest versions"),
      }).optional().describe("Preferences for the context gathering"),
    },
    async ({ libraries, task, preferences = {} }): Promise<CallToolResult> => {
      try {
        let contextResults: string[] = [];
        
        for (const library of libraries) {
          try {
            let query = task;
            if (preferences.typescript) query += " typescript";
            if (preferences.react) query += " react";
            if (preferences.latest) query += " latest version";
            
            // Extract library ID from previous resolve result
            const resolveText = Array.isArray(resolveResult.content) 
              ? resolveResult.content.map((c: any) => c.text || c.content || '').join(' ')
              : (resolveResult.content.text || resolveResult.content || '');
            
            const libraryIdMatch = resolveText.match(/\/[\w-]+\/[\w.-]+(?:\/[\w.-]+)?/);
            
            if (!libraryIdMatch) {
              throw new Error('Could not resolve library ID for ' + library);
            }
            
            const docsResult = await callContext7Tool('get-library-docs', { 
              context7CompatibleLibraryID: libraryIdMatch[0],
              topic: query 
            });
            
            let libraryContext = `=== ${library.toUpperCase()} ===\n`;
            
            if (docsResult && docsResult.content) {
              if (Array.isArray(docsResult.content)) {
                libraryContext += docsResult.content.map((c: any) => c.text || c.content || JSON.stringify(c)).join('\n');
              } else {
                libraryContext += docsResult.content.text || docsResult.content || JSON.stringify(docsResult);
              }
            } else {
              libraryContext += 'No context found for this library';
            }
            
            contextResults.push(libraryContext);
          } catch (libError) {
            contextResults.push(`=== ${library.toUpperCase()} ===\nError fetching context: ${libError}`);
          }
        }

        const finalContext = contextResults.length > 0 
          ? contextResults.join('\n\n')
          : 'No context found for the specified libraries';

        let result = `Context7 AI Coding Context\n\n`;
        result += `Task: ${task}\n`;
        result += `Libraries: ${libraries.join(', ')}\n`;
        if (preferences.typescript) result += '✓ TypeScript preferred\n';
        if (preferences.react) result += '✓ React focus\n';
        if (preferences.latest) result += '✓ Latest versions\n';
        result += '\n' + finalContext;

        return {
          content: [
            {
              type: "text",
              text: result,
            },
          ],
        };
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        return {
          content: [
            {
              type: "text",
              text: `Error gathering AI context: ${errorMessage}\n\nNote: Using public context7 server at ${CONTEXT7_BASE_URL}`,
            },
          ],
        };
      }
    }
  );

  // Tool to start/check context7 server
  server.tool(
    "context7-server-status",
    "Check if context7 MCP server is running and get connection info",
    {},
    async (): Promise<CallToolResult> => {
      try {
        const response = await fetch(`${CONTEXT7_BASE_URL}/mcp`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/event-stream',
          },
          body: JSON.stringify({
            jsonrpc: '2.0',
            id: 1,
            method: 'tools/list'
          })
        });
        
        if (response.ok) {
          return {
            content: [
              {
                type: "text",
                text: `✅ Context7 public server is running at ${CONTEXT7_BASE_URL}\n\nStatus: Connected and ready\nTools available: resolve-library-id, get-library-docs`,
              },
            ],
          };
        } else {
          throw new Error(`Server responded with status ${response.status}`);
        }
      } catch (error) {
        return {
          content: [
            {
              type: "text",
              text: `❌ Context7 server is not accessible at ${CONTEXT7_BASE_URL}\n\nUsing public context7 server. If connection fails, try setting CONTEXT7_MCP_URL to a local instance.\n\nError: ${error instanceof Error ? error.message : 'Unknown error'}`,
            },
          ],
        };
      }
    }
  );
}