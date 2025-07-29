import { z } from "zod";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { CallToolResult } from "@modelcontextprotocol/sdk/types.js";

// Flowise configuration
const FLOWISE_API_KEY = "spAm3bDe2NkIPOs_mVJsKRxh04DJlWZU5ePm-GkOmeE";
const FLOWISE_BASE_URL = "http://w0cwck80owcgkw4s4kkos4ko.135.181.149.150.sslip.io";

interface FlowiseChatflow {
  id: string;
  name: string;
  flowData: string;
  deployed: boolean;
  isPublic: boolean;
  apikeyid: string;
  chatbotConfig: any;
  createdDate: string;
  updatedDate: string;
}

interface FlowisePredictionRequest {
  question: string;
  streaming?: boolean;
  overrideConfig?: Record<string, any>;
  history?: any[];
  uploads?: any[];
  form?: Record<string, any>;
}

interface FlowisePredictionResponse {
  text: string;
  sourceDocuments?: any[];
  followUpPrompts?: string[];
  sessionId?: string;
}

async function makeFlowiseRequest(endpoint: string, options: RequestInit = {}, requiresAuth = true): Promise<any> {
  const url = `${FLOWISE_BASE_URL}${endpoint}`;
  
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> || {}),
  };

  // Only add authorization for endpoints that require it
  if (requiresAuth) {
    headers['Authorization'] = `Bearer ${FLOWISE_API_KEY}`;
  }
  
  const response = await fetch(url, {
    headers,
    ...options,
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Flowise API error: ${response.status} ${response.statusText} - ${errorText}`);
  }

  return response.json();
}

export function registerFlowiseTools(server: McpServer): void {
  // List all chatflows
  server.tool(
    "flowise-list-chatflows",
    "List all available Flowise chatflows",
    {},
    async (): Promise<CallToolResult> => {
      try {
        const chatflows: FlowiseChatflow[] = await makeFlowiseRequest('/api/v1/chatflows');
        
        const chatflowList = chatflows.map(flow => ({
          id: flow.id,
          name: flow.name,
          deployed: flow.deployed,
          isPublic: flow.isPublic,
          createdDate: flow.createdDate,
          updatedDate: flow.updatedDate
        }));

        return {
          content: [
            {
              type: "text",
              text: `Found ${chatflows.length} chatflows:\n\n${chatflowList.map(flow => 
                `• **${flow.name}** (ID: ${flow.id})\n  - Deployed: ${flow.deployed}\n  - Public: ${flow.isPublic}\n  - Created: ${flow.createdDate}`
              ).join('\n\n')}`
            }
          ]
        };
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        return {
          content: [
            {
              type: "text",
              text: `Error listing chatflows: ${errorMessage}`
            }
          ]
        };
      }
    }
  );

  // Get specific chatflow details
  server.tool(
    "flowise-get-chatflow",
    "Get details of a specific Flowise chatflow",
    {
      chatflowId: z.string().describe("The ID of the chatflow to retrieve")
    },
    async ({ chatflowId }): Promise<CallToolResult> => {
      try {
        const chatflow: FlowiseChatflow = await makeFlowiseRequest(`/api/v1/chatflows/${chatflowId}`);
        
        return {
          content: [
            {
              type: "text",
              text: `**Chatflow Details:**\n\n` +
                   `• **Name:** ${chatflow.name}\n` +
                   `• **ID:** ${chatflow.id}\n` +
                   `• **Deployed:** ${chatflow.deployed}\n` +
                   `• **Public:** ${chatflow.isPublic}\n` +
                   `• **API Key ID:** ${chatflow.apikeyid || 'None'}\n` +
                   `• **Created:** ${chatflow.createdDate}\n` +
                   `• **Updated:** ${chatflow.updatedDate}\n` +
                   `• **Has Chatbot Config:** ${chatflow.chatbotConfig ? 'Yes' : 'No'}`
            }
          ]
        };
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        return {
          content: [
            {
              type: "text",
              text: `Error retrieving chatflow: ${errorMessage}`
            }
          ]
        };
      }
    }
  );

  // Make a prediction (chat with a chatflow) - tries without auth first
  server.tool(
    "flowise-predict",
    "Send a message to a Flowise chatflow and get a response",
    {
      chatflowId: z.string().describe("The ID of the chatflow to use"),
      question: z.string().describe("The message/question to send"),
      streaming: z.boolean().optional().describe("Enable streaming response (default: false)"),
      sessionId: z.string().optional().describe("Session ID for conversation continuity"),
      overrideConfig: z.record(z.any()).optional().describe("Override chatflow configuration"),
      history: z.array(z.any()).optional().describe("Previous conversation history")
    },
    async ({ chatflowId, question, streaming = false, sessionId, overrideConfig, history }): Promise<CallToolResult> => {
      const requestBody: FlowisePredictionRequest = {
        question,
        streaming,
        overrideConfig: overrideConfig || {},
        history: history || []
      };

      // Add sessionId to URL if provided
      const endpoint = `/api/v1/prediction/${chatflowId}${sessionId ? `?sessionId=${sessionId}` : ''}`;
      
      try {
        // First try without authentication (for public chatflows)
        const response: FlowisePredictionResponse = await makeFlowiseRequest(endpoint, {
          method: 'POST',
          body: JSON.stringify(requestBody)
        }, false);

        let responseText = `**Flowise Response:**\n\n${response.text}`;
        
        if (response.sessionId) {
          responseText += `\n\n**Session ID:** ${response.sessionId}`;
        }
        
        if (response.sourceDocuments && response.sourceDocuments.length > 0) {
          responseText += `\n\n**Source Documents:** ${response.sourceDocuments.length} documents referenced`;
        }
        
        if (response.followUpPrompts && response.followUpPrompts.length > 0) {
          responseText += `\n\n**Follow-up Prompts:**\n${response.followUpPrompts.map(prompt => `• ${prompt}`).join('\n')}`;
        }

        return {
          content: [
            {
              type: "text",
              text: responseText
            }
          ]
        };
      } catch (error) {
        // If public access fails, try with authentication
        try {
          const response: FlowisePredictionResponse = await makeFlowiseRequest(endpoint, {
            method: 'POST',
            body: JSON.stringify(requestBody)
          }, true);

          let responseText = `**Flowise Response (Authenticated):**\n\n${response.text}`;
          
          if (response.sessionId) {
            responseText += `\n\n**Session ID:** ${response.sessionId}`;
          }
          
          if (response.sourceDocuments && response.sourceDocuments.length > 0) {
            responseText += `\n\n**Source Documents:** ${response.sourceDocuments.length} documents referenced`;
          }
          
          if (response.followUpPrompts && response.followUpPrompts.length > 0) {
            responseText += `\n\n**Follow-up Prompts:**\n${response.followUpPrompts.map(prompt => `• ${prompt}`).join('\n')}`;
          }

          return {
            content: [
              {
                type: "text",
                text: responseText
              }
            ]
          };
        } catch (authError) {
          const errorMessage = authError instanceof Error ? authError.message : 'Unknown error';
          return {
            content: [
              {
                type: "text",
                text: `Error making prediction (both public and authenticated access failed): ${errorMessage}`
              }
            ]
          };
        }
      }
    }
  );

  // Create a new chatflow
  server.tool(
    "flowise-create-chatflow",
    "Create a new Flowise chatflow",
    {
      name: z.string().describe("Name for the new chatflow"),
      flowData: z.string().optional().describe("JSON string of flow configuration"),
      deployed: z.boolean().optional().describe("Whether to deploy the chatflow immediately (default: false)")
    },
    async ({ name, flowData, deployed = false }): Promise<CallToolResult> => {
      try {
        const requestBody = {
          name,
          flowData: flowData || '{"nodes":[],"edges":[]}',
          deployed
        };

        const newChatflow: FlowiseChatflow = await makeFlowiseRequest('/api/v1/chatflows', {
          method: 'POST',
          body: JSON.stringify(requestBody)
        });

        return {
          content: [
            {
              type: "text",
              text: `**Chatflow Created Successfully!**\n\n` +
                   `• **Name:** ${newChatflow.name}\n` +
                   `• **ID:** ${newChatflow.id}\n` +
                   `• **Deployed:** ${newChatflow.deployed}\n` +
                   `• **Created:** ${newChatflow.createdDate}`
            }
          ]
        };
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        return {
          content: [
            {
              type: "text",
              text: `Error creating chatflow: ${errorMessage}`
            }
          ]
        };
      }
    }
  );

  // Update a chatflow
  server.tool(
    "flowise-update-chatflow",
    "Update an existing Flowise chatflow",
    {
      chatflowId: z.string().describe("The ID of the chatflow to update"),
      name: z.string().optional().describe("New name for the chatflow"),
      flowData: z.string().optional().describe("Updated JSON string of flow configuration"),
      deployed: z.boolean().optional().describe("Whether the chatflow should be deployed")
    },
    async ({ chatflowId, name, flowData, deployed }): Promise<CallToolResult> => {
      try {
        const requestBody: any = {};
        if (name) requestBody.name = name;
        if (flowData) requestBody.flowData = flowData;
        if (deployed !== undefined) requestBody.deployed = deployed;

        const updatedChatflow: FlowiseChatflow = await makeFlowiseRequest(`/api/v1/chatflows/${chatflowId}`, {
          method: 'PUT',
          body: JSON.stringify(requestBody)
        });

        return {
          content: [
            {
              type: "text",
              text: `**Chatflow Updated Successfully!**\n\n` +
                   `• **Name:** ${updatedChatflow.name}\n` +
                   `• **ID:** ${updatedChatflow.id}\n` +
                   `• **Deployed:** ${updatedChatflow.deployed}\n` +
                   `• **Updated:** ${updatedChatflow.updatedDate}`
            }
          ]
        };
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        return {
          content: [
            {
              type: "text",
              text: `Error updating chatflow: ${errorMessage}`
            }
          ]
        };
      }
    }
  );

  // Delete a chatflow
  server.tool(
    "flowise-delete-chatflow",
    "Delete a Flowise chatflow",
    {
      chatflowId: z.string().describe("The ID of the chatflow to delete"),
      confirm: z.boolean().describe("Confirmation that you want to delete the chatflow")
    },
    async ({ chatflowId, confirm }): Promise<CallToolResult> => {
      try {
        if (!confirm) {
          return {
            content: [
              {
                type: "text",
                text: "Deletion cancelled. Set confirm to true to proceed with deletion."
              }
            ]
          };
        }

        await makeFlowiseRequest(`/api/v1/chatflows/${chatflowId}`, {
          method: 'DELETE'
        });

        return {
          content: [
            {
              type: "text",
              text: `**Chatflow Deleted Successfully!**\n\nChatflow ID: ${chatflowId} has been permanently removed.`
            }
          ]
        };
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        return {
          content: [
            {
              type: "text",
              text: `Error deleting chatflow: ${errorMessage}`
            }
          ]
        };
      }
    }
  );

  // Test Flowise connection
  server.tool(
    "flowise-test-connection",
    "Test connection to Flowise instance",
    {},
    async (): Promise<CallToolResult> => {
      try {
        // Test basic connectivity first
        const healthResponse = await fetch(`${FLOWISE_BASE_URL}/health`);
        
        if (healthResponse.ok) {
          let statusText = `**✅ Flowise Server Online!**\n\n` +
                         `• **URL:** ${FLOWISE_BASE_URL}\n` +
                         `• **Health Status:** ${healthResponse.status} ${healthResponse.statusText}\n`;

          // Try to access API endpoints
          try {
            // Try authenticated access to chatflows
            const authResponse = await fetch(`${FLOWISE_BASE_URL}/api/v1/chatflows`, {
              headers: {
                'Authorization': `Bearer ${FLOWISE_API_KEY}`,
              },
            });

            if (authResponse.ok) {
              const chatflows = await authResponse.json();
              statusText += `• **Authenticated API Access:** ✅ Working\n`;
              statusText += `• **Available Chatflows:** ${Array.isArray(chatflows) ? chatflows.length : 'Unknown'}`;
            } else {
              statusText += `• **Authenticated API Access:** ❌ Failed (${authResponse.status})\n`;
              statusText += `• **Note:** Management endpoints require JWT authentication`;
            }
          } catch (apiError) {
            statusText += `• **API Access:** ❌ Error accessing management endpoints\n`;
            statusText += `• **Note:** Prediction endpoints may still work for public chatflows`;
          }

          return {
            content: [
              {
                type: "text",
                text: statusText
              }
            ]
          };
        } else {
          return {
            content: [
              {
                type: "text",
                text: `**❌ Flowise Server Unreachable!**\n\n` +
                     `• **URL:** ${FLOWISE_BASE_URL}\n` +
                     `• **Status:** ${healthResponse.status} ${healthResponse.statusText}`
              }
            ]
          };
        }
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        return {
          content: [
            {
              type: "text",
              text: `**❌ Flowise Connection Error!**\n\n` +
                   `• **URL:** ${FLOWISE_BASE_URL}\n` +
                   `• **Error:** ${errorMessage}`
            }
          ]
        };
      }
    }
  );
}