/**
 * PayloadCMS 3.x MCP Tools
 * Comprehensive API integration for PayloadCMS backend management
 */

import { z } from "zod";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { CallToolResult } from "@modelcontextprotocol/sdk/types.js";
import fetch from "node-fetch";

// PayloadCMS Configuration
interface PayloadConfig {
  baseUrl: string;
  apiKey?: string;
  token?: string;
  timeout?: number;
}

// Authentication state management
class PayloadAuthManager {
  private static tokens = new Map<string, { token: string; expires: Date }>();
  
  static setToken(instanceUrl: string, token: string, expiresIn?: number) {
    const expires = new Date();
    expires.setHours(expires.getHours() + (expiresIn || 24)); // Default 24 hours
    this.tokens.set(instanceUrl, { token, expires });
  }
  
  static getToken(instanceUrl: string): string | null {
    const auth = this.tokens.get(instanceUrl);
    if (!auth || auth.expires < new Date()) {
      this.tokens.delete(instanceUrl);
      return null;
    }
    return auth.token;
  }
  
  static clearToken(instanceUrl: string) {
    this.tokens.delete(instanceUrl);
  }
}

// Utility function to make PayloadCMS API calls
async function makePayloadRequest(
  config: PayloadConfig,
  endpoint: string,
  options: RequestInit = {}
): Promise<any> {
  const url = `${config.baseUrl}/api${endpoint}`;
  
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    ...((options.headers as Record<string, string>) || {})
  };

  // Add authentication
  if (config.token) {
    headers['Authorization'] = `JWT ${config.token}`;
  } else if (config.apiKey) {
    headers['Authorization'] = `users API-Key ${config.apiKey}`;
  }

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), config.timeout || 30000);
  
  try {
    const response = await fetch(url, {
      ...options,
      headers,
      signal: controller.signal
    } as any);
    clearTimeout(timeoutId);

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`PayloadCMS API Error ${response.status}: ${errorText}`);
    }

    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      return await response.json();
    }
    
    return await response.text();
  } catch (error) {
    clearTimeout(timeoutId);
    throw error;
  }
}

// Configuration schema
const payloadConfigSchema = z.object({
  baseUrl: z.string().url().describe("PayloadCMS instance URL (e.g., 'https://cms.example.com')"),
  apiKey: z.string().optional().describe("PayloadCMS API key (optional if using token)"),
  token: z.string().optional().describe("JWT token (optional if using API key)"),
  timeout: z.number().optional().default(30000).describe("Request timeout in milliseconds")
});

// Collection operations schemas
const findDocumentsSchema = z.object({
  config: payloadConfigSchema,
  collection: z.string().describe("Collection slug (e.g., 'posts', 'users')"),
  where: z.record(z.any()).optional().describe("Query filters (JSON object)"),
  limit: z.number().optional().describe("Number of documents to return"),
  page: z.number().optional().describe("Page number for pagination"),
  sort: z.string().optional().describe("Sort field (e.g., '-createdAt')"),
  depth: z.number().optional().describe("Relationship depth to populate"),
  locale: z.string().optional().describe("Locale for localized content")
});

const getDocumentSchema = z.object({
  config: payloadConfigSchema,
  collection: z.string().describe("Collection slug"),
  id: z.string().describe("Document ID"),
  depth: z.number().optional().describe("Relationship depth to populate"),
  locale: z.string().optional().describe("Locale for localized content")
});

const createDocumentSchema = z.object({
  config: payloadConfigSchema,
  collection: z.string().describe("Collection slug"),
  data: z.record(z.any()).describe("Document data (JSON object)"),
  locale: z.string().optional().describe("Locale for localized content"),
  draft: z.boolean().optional().describe("Save as draft")
});

const updateDocumentSchema = z.object({
  config: payloadConfigSchema,
  collection: z.string().describe("Collection slug"),
  id: z.string().describe("Document ID"),
  data: z.record(z.any()).describe("Updated document data (JSON object)"),
  locale: z.string().optional().describe("Locale for localized content"),
  draft: z.boolean().optional().describe("Save as draft")
});

const deleteDocumentSchema = z.object({
  config: payloadConfigSchema,
  collection: z.string().describe("Collection slug"),
  id: z.string().describe("Document ID")
});

const countDocumentsSchema = z.object({
  config: payloadConfigSchema,
  collection: z.string().describe("Collection slug"),
  where: z.record(z.any()).optional().describe("Query filters (JSON object)")
});

// Authentication schemas
const loginSchema = z.object({
  config: payloadConfigSchema,
  collection: z.string().default("users").describe("Auth collection slug"),
  email: z.string().email().describe("User email"),
  password: z.string().describe("User password")
});

const getCurrentUserSchema = z.object({
  config: payloadConfigSchema,
  collection: z.string().default("users").describe("Auth collection slug")
});

const logoutSchema = z.object({
  config: payloadConfigSchema,
  collection: z.string().default("users").describe("Auth collection slug")
});

const refreshTokenSchema = z.object({
  config: payloadConfigSchema,
  collection: z.string().default("users").describe("Auth collection slug")
});

const resetPasswordSchema = z.object({
  config: payloadConfigSchema,
  collection: z.string().default("users").describe("Auth collection slug"),
  email: z.string().email().describe("User email")
});

// Global operations schemas
const getGlobalSchema = z.object({
  config: payloadConfigSchema,
  slug: z.string().describe("Global slug (e.g., 'header', 'footer')"),
  locale: z.string().optional().describe("Locale for localized content")
});

const updateGlobalSchema = z.object({
  config: payloadConfigSchema,
  slug: z.string().describe("Global slug"),
  data: z.record(z.any()).describe("Global data (JSON object)"),
  locale: z.string().optional().describe("Locale for localized content")
});

// File upload schemas
const uploadFileSchema = z.object({
  config: payloadConfigSchema,
  collection: z.string().describe("Upload collection slug (e.g., 'media')"),
  fileData: z.string().describe("Base64 encoded file data or file URL"),
  fileName: z.string().describe("File name with extension"),
  mimeType: z.string().optional().describe("MIME type of the file"),
  data: z.record(z.any()).optional().describe("Additional file metadata (JSON object)")
});

const getFileSchema = z.object({
  config: payloadConfigSchema,
  collection: z.string().describe("Upload collection slug"),
  id: z.string().describe("File document ID")
});

const updateFileSchema = z.object({
  config: payloadConfigSchema,
  collection: z.string().describe("Upload collection slug"),
  id: z.string().describe("File document ID"),
  data: z.record(z.any()).describe("Updated file metadata (JSON object)")
});

const deleteFileSchema = z.object({
  config: payloadConfigSchema,
  collection: z.string().describe("Upload collection slug"),
  id: z.string().describe("File document ID")
});

// GraphQL schemas
const graphqlQuerySchema = z.object({
  config: payloadConfigSchema,
  query: z.string().describe("GraphQL query string"),
  variables: z.record(z.any()).optional().describe("GraphQL variables (JSON object)")
});

const graphqlMutationSchema = z.object({
  config: payloadConfigSchema,
  mutation: z.string().describe("GraphQL mutation string"),
  variables: z.record(z.any()).optional().describe("GraphQL variables (JSON object)")
});

// Health check schema
const healthCheckSchema = z.object({
  config: payloadConfigSchema
});

/**
 * Register all PayloadCMS tools with the MCP server
 */
export function registerPayloadCMSTools(server: McpServer) {
  
  // === Collection CRUD Operations ===
  
  server.tool(
    "payload-find-documents",
    "Query and find documents in a PayloadCMS collection with filtering, pagination, and sorting",
    findDocumentsSchema.shape,
    async ({ config, collection, where, limit, page, sort, depth, locale }: any): Promise<CallToolResult> => {
      try {
        const params = new URLSearchParams();
        if (where) params.append('where', JSON.stringify(where));
        if (limit) params.append('limit', limit.toString());
        if (page) params.append('page', page.toString());
        if (sort) params.append('sort', sort);
        if (depth) params.append('depth', depth.toString());
        if (locale) params.append('locale', locale);

        const endpoint = `/${collection}${params.toString() ? '?' + params.toString() : ''}`;
        const result = await makePayloadRequest(config as PayloadConfig, endpoint, { method: 'GET' });

        return {
          content: [
            {
              type: "text",
              text: `✅ Found ${result.totalDocs || result.docs?.length || 0} documents in '${collection}' collection\n\n${JSON.stringify(result, null, 2)}`
            }
          ]
        };
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        return {
          content: [
            {
              type: "text",
              text: `❌ Error finding documents in '${collection}': ${errorMessage}`
            }
          ]
        };
      }
    }
  );

  server.tool(
    "payload-get-document",
    "Get a specific document by ID from a PayloadCMS collection",
    getDocumentSchema.shape,
    async ({ config, collection, id, depth, locale }: any): Promise<CallToolResult> => {
      try {
        const params = new URLSearchParams();
        if (depth) params.append('depth', depth.toString());
        if (locale) params.append('locale', locale);

        const endpoint = `/${collection}/${id}${params.toString() ? '?' + params.toString() : ''}`;
        const result = await makePayloadRequest(config as PayloadConfig, endpoint, { method: 'GET' });

        return {
          content: [
            {
              type: "text",
              text: `✅ Retrieved document '${id}' from '${collection}' collection\n\n${JSON.stringify(result, null, 2)}`
            }
          ]
        };
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        return {
          content: [
            {
              type: "text",
              text: `❌ Error getting document '${id}' from '${collection}': ${errorMessage}`
            }
          ]
        };
      }
    }
  );

  server.tool(
    "payload-create-document",
    "Create a new document in a PayloadCMS collection",
    createDocumentSchema.shape,
    async ({ config, collection, data, locale, draft }: any): Promise<CallToolResult> => {
      try {
        const params = new URLSearchParams();
        if (locale) params.append('locale', locale);
        if (draft) params.append('draft', 'true');

        const endpoint = `/${collection}${params.toString() ? '?' + params.toString() : ''}`;
        const result = await makePayloadRequest(config as PayloadConfig, endpoint, {
          method: 'POST',
          body: JSON.stringify(data)
        });

        return {
          content: [
            {
              type: "text",
              text: `✅ Created new document in '${collection}' collection\nID: ${result.id}\n\n${JSON.stringify(result, null, 2)}`
            }
          ]
        };
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        return {
          content: [
            {
              type: "text",
              text: `❌ Error creating document in '${collection}': ${errorMessage}`
            }
          ]
        };
      }
    }
  );

  server.tool(
    "payload-update-document",
    "Update an existing document in a PayloadCMS collection",
    updateDocumentSchema.shape,
    async ({ config, collection, id, data, locale, draft }: any): Promise<CallToolResult> => {
      try {
        const params = new URLSearchParams();
        if (locale) params.append('locale', locale);
        if (draft) params.append('draft', 'true');

        const endpoint = `/${collection}/${id}${params.toString() ? '?' + params.toString() : ''}`;
        const result = await makePayloadRequest(config as PayloadConfig, endpoint, {
          method: 'PATCH',
          body: JSON.stringify(data)
        });

        return {
          content: [
            {
              type: "text",
              text: `✅ Updated document '${id}' in '${collection}' collection\n\n${JSON.stringify(result, null, 2)}`
            }
          ]
        };
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        return {
          content: [
            {
              type: "text",
              text: `❌ Error updating document '${id}' in '${collection}': ${errorMessage}`
            }
          ]
        };
      }
    }
  );

  server.tool(
    "payload-delete-document",
    "Delete a document from a PayloadCMS collection",
    deleteDocumentSchema.shape,
    async ({ config, collection, id }: any): Promise<CallToolResult> => {
      try {
        const endpoint = `/${collection}/${id}`;
        const result = await makePayloadRequest(config as PayloadConfig, endpoint, { method: 'DELETE' });

        return {
          content: [
            {
              type: "text",
              text: `✅ Deleted document '${id}' from '${collection}' collection\n\n${JSON.stringify(result, null, 2)}`
            }
          ]
        };
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        return {
          content: [
            {
              type: "text",
              text: `❌ Error deleting document '${id}' from '${collection}': ${errorMessage}`
            }
          ]
        };
      }
    }
  );

  server.tool(
    "payload-count-documents",
    "Count documents in a PayloadCMS collection with optional filtering",
    countDocumentsSchema.shape,
    async ({ config, collection, where }: any): Promise<CallToolResult> => {
      try {
        const params = new URLSearchParams();
        if (where) params.append('where', JSON.stringify(where));

        const endpoint = `/${collection}/count${params.toString() ? '?' + params.toString() : ''}`;
        const result = await makePayloadRequest(config as PayloadConfig, endpoint, { method: 'GET' });

        return {
          content: [
            {
              type: "text",
              text: `✅ Document count for '${collection}' collection: ${result.totalDocs || result.count || 0}`
            }
          ]
        };
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        return {
          content: [
            {
              type: "text",
              text: `❌ Error counting documents in '${collection}': ${errorMessage}`
            }
          ]
        };
      }
    }
  );

  // === Authentication Operations ===

  server.tool(
    "payload-login",
    "Authenticate with PayloadCMS and obtain JWT token",
    loginSchema.shape,
    async ({ config, collection, email, password }: any): Promise<CallToolResult> => {
      try {
        const endpoint = `/${collection}/login`;
        const result = await makePayloadRequest(config as PayloadConfig, endpoint, {
          method: 'POST',
          body: JSON.stringify({ email, password })
        });

        if (result.token) {
          PayloadAuthManager.setToken(config.baseUrl, result.token, 24); // 24 hours
        }

        return {
          content: [
            {
              type: "text",
              text: `✅ Successfully logged in as ${email}\nToken stored for future requests\n\nUser: ${JSON.stringify(result.user, null, 2)}`
            }
          ]
        };
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        return {
          content: [
            {
              type: "text",
              text: `❌ Login failed for ${email}: ${errorMessage}`
            }
          ]
        };
      }
    }
  );

  server.tool(
    "payload-get-current-user",
    "Get information about the currently authenticated user",
    getCurrentUserSchema.shape,
    async ({ config, collection }: any): Promise<CallToolResult> => {
      try {
        // Use stored token if available
        const storedToken = PayloadAuthManager.getToken(config.baseUrl);
        if (storedToken && !config.token) {
          config.token = storedToken;
        }

        const endpoint = `/${collection}/me`;
        const result = await makePayloadRequest(config as PayloadConfig, endpoint, { method: 'GET' });

        return {
          content: [
            {
              type: "text",
              text: `✅ Current user information:\n\n${JSON.stringify(result, null, 2)}`
            }
          ]
        };
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        return {
          content: [
            {
              type: "text",
              text: `❌ Error getting current user: ${errorMessage}`
            }
          ]
        };
      }
    }
  );

  server.tool(
    "payload-logout",
    "Logout from PayloadCMS and invalidate token",
    logoutSchema.shape,
    async ({ config, collection }: any): Promise<CallToolResult> => {
      try {
        const storedToken = PayloadAuthManager.getToken(config.baseUrl);
        if (storedToken && !config.token) {
          config.token = storedToken;
        }

        const endpoint = `/${collection}/logout`;
        const result = await makePayloadRequest(config as PayloadConfig, endpoint, { method: 'POST' });

        PayloadAuthManager.clearToken(config.baseUrl);

        return {
          content: [
            {
              type: "text",
              text: `✅ Successfully logged out\nToken cleared from storage`
            }
          ]
        };
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        return {
          content: [
            {
              type: "text",
              text: `❌ Logout error: ${errorMessage}`
            }
          ]
        };
      }
    }
  );

  server.tool(
    "payload-refresh-token",
    "Refresh the JWT authentication token",
    refreshTokenSchema.shape,
    async ({ config, collection }: any): Promise<CallToolResult> => {
      try {
        const storedToken = PayloadAuthManager.getToken(config.baseUrl);
        if (storedToken && !config.token) {
          config.token = storedToken;
        }

        const endpoint = `/${collection}/refresh-token`;
        const result = await makePayloadRequest(config as PayloadConfig, endpoint, { method: 'POST' });

        if (result.token) {
          PayloadAuthManager.setToken(config.baseUrl, result.token, 24);
        }

        return {
          content: [
            {
              type: "text",
              text: `✅ Token refreshed successfully\nNew token stored for future requests`
            }
          ]
        };
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        return {
          content: [
            {
              type: "text",
              text: `❌ Token refresh failed: ${errorMessage}`
            }
          ]
        };
      }
    }
  );

  server.tool(
    "payload-reset-password",
    "Send password reset email for a user",
    resetPasswordSchema.shape,
    async ({ config, collection, email }: any): Promise<CallToolResult> => {
      try {
        const endpoint = `/${collection}/forgot-password`;
        const result = await makePayloadRequest(config as PayloadConfig, endpoint, {
          method: 'POST',
          body: JSON.stringify({ email })
        });

        return {
          content: [
            {
              type: "text",
              text: `✅ Password reset email sent to ${email}`
            }
          ]
        };
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        return {
          content: [
            {
              type: "text",
              text: `❌ Password reset failed for ${email}: ${errorMessage}`
            }
          ]
        };
      }
    }
  );

  // === Global Operations ===

  server.tool(
    "payload-get-global",
    "Get a PayloadCMS global configuration",
    getGlobalSchema.shape,
    async ({ config, slug, locale }: any): Promise<CallToolResult> => {
      try {
        const params = new URLSearchParams();
        if (locale) params.append('locale', locale);

        const endpoint = `/globals/${slug}${params.toString() ? '?' + params.toString() : ''}`;
        const result = await makePayloadRequest(config as PayloadConfig, endpoint, { method: 'GET' });

        return {
          content: [
            {
              type: "text",
              text: `✅ Retrieved global '${slug}'\n\n${JSON.stringify(result, null, 2)}`
            }
          ]
        };
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        return {
          content: [
            {
              type: "text",
              text: `❌ Error getting global '${slug}': ${errorMessage}`
            }
          ]
        };
      }
    }
  );

  server.tool(
    "payload-update-global",
    "Update a PayloadCMS global configuration",
    updateGlobalSchema.shape,
    async ({ config, slug, data, locale }: any): Promise<CallToolResult> => {
      try {
        const params = new URLSearchParams();
        if (locale) params.append('locale', locale);

        const endpoint = `/globals/${slug}${params.toString() ? '?' + params.toString() : ''}`;
        const result = await makePayloadRequest(config as PayloadConfig, endpoint, {
          method: 'POST',
          body: JSON.stringify(data)
        });

        return {
          content: [
            {
              type: "text",
              text: `✅ Updated global '${slug}'\n\n${JSON.stringify(result, null, 2)}`
            }
          ]
        };
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        return {
          content: [
            {
              type: "text",
              text: `❌ Error updating global '${slug}': ${errorMessage}`
            }
          ]
        };
      }
    }
  );

  // === File Management Operations ===

  server.tool(
    "payload-upload-file",
    "Upload a file to a PayloadCMS upload collection",
    uploadFileSchema.shape,
    async ({ config, collection, fileData, fileName, mimeType, data }: any): Promise<CallToolResult> => {
      try {
        const formData = new FormData();
        
        // Handle base64 encoded file data
        let fileBuffer: Buffer;
        if (fileData.startsWith('data:')) {
          // Data URL format: data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...
          const [header, base64Data] = fileData.split(',');
          if (!mimeType) {
            const mimeMatch = header.match(/data:([^;]+)/);
            if (mimeMatch) {
              mimeType = mimeMatch[1];
            }
          }
          fileBuffer = Buffer.from(base64Data, 'base64');
        } else if (fileData.startsWith('http')) {
          // URL format - fetch the file
          const response = await fetch(fileData);
          if (!response.ok) {
            throw new Error(`Failed to fetch file from URL: ${response.statusText}`);
          }
          fileBuffer = Buffer.from(await response.arrayBuffer());
          if (!mimeType) {
            mimeType = response.headers.get('content-type') || 'application/octet-stream';
          }
        } else {
          // Assume base64 encoded data without data URL prefix
          fileBuffer = Buffer.from(fileData, 'base64');
        }

        // Create form data
        formData.append('file', new Blob([fileBuffer as any], { type: mimeType }), fileName);
        
        // Add additional metadata
        if (data) {
          Object.entries(data).forEach(([key, value]) => {
            formData.append(key, JSON.stringify(value));
          });
        }

        const endpoint = `/${collection}`;
        const result = await makePayloadRequest(config as PayloadConfig, endpoint, {
          method: 'POST',
          body: formData,
          headers: {} // Let fetch set Content-Type for FormData
        });

        return {
          content: [
            {
              type: "text",
              text: `✅ File '${fileName}' uploaded successfully to '${collection}' collection\nID: ${result.id}\nURL: ${result.url || 'N/A'}\n\n${JSON.stringify(result, null, 2)}`
            }
          ]
        };
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        return {
          content: [
            {
              type: "text",
              text: `❌ Error uploading file '${fileName}' to '${collection}': ${errorMessage}`
            }
          ]
        };
      }
    }
  );

  server.tool(
    "payload-get-file",
    "Get file information from a PayloadCMS upload collection",
    getFileSchema.shape,
    async ({ config, collection, id }: any): Promise<CallToolResult> => {
      try {
        const endpoint = `/${collection}/${id}`;
        const result = await makePayloadRequest(config as PayloadConfig, endpoint, { method: 'GET' });

        return {
          content: [
            {
              type: "text",
              text: `✅ Retrieved file information for '${id}' from '${collection}' collection\nURL: ${result.url || 'N/A'}\nFilename: ${result.filename || 'N/A'}\nSize: ${result.filesize || 'N/A'} bytes\n\n${JSON.stringify(result, null, 2)}`
            }
          ]
        };
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        return {
          content: [
            {
              type: "text",
              text: `❌ Error getting file '${id}' from '${collection}': ${errorMessage}`
            }
          ]
        };
      }
    }
  );

  server.tool(
    "payload-update-file",
    "Update file metadata in a PayloadCMS upload collection",
    updateFileSchema.shape,
    async ({ config, collection, id, data }: any): Promise<CallToolResult> => {
      try {
        const endpoint = `/${collection}/${id}`;
        const result = await makePayloadRequest(config as PayloadConfig, endpoint, {
          method: 'PATCH',
          body: JSON.stringify(data)
        });

        return {
          content: [
            {
              type: "text",
              text: `✅ Updated file metadata for '${id}' in '${collection}' collection\n\n${JSON.stringify(result, null, 2)}`
            }
          ]
        };
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        return {
          content: [
            {
              type: "text",
              text: `❌ Error updating file '${id}' in '${collection}': ${errorMessage}`
            }
          ]
        };
      }
    }
  );

  server.tool(
    "payload-delete-file",
    "Delete a file from a PayloadCMS upload collection",
    deleteFileSchema.shape,
    async ({ config, collection, id }: any): Promise<CallToolResult> => {
      try {
        const endpoint = `/${collection}/${id}`;
        const result = await makePayloadRequest(config as PayloadConfig, endpoint, { method: 'DELETE' });

        return {
          content: [
            {
              type: "text",
              text: `✅ Deleted file '${id}' from '${collection}' collection\n\n${JSON.stringify(result, null, 2)}`
            }
          ]
        };
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        return {
          content: [
            {
              type: "text",
              text: `❌ Error deleting file '${id}' from '${collection}': ${errorMessage}`
            }
          ]
        };
      }
    }
  );

  // === GraphQL Operations ===

  server.tool(
    "payload-graphql-query",
    "Execute a GraphQL query against PayloadCMS",
    graphqlQuerySchema.shape,
    async ({ config, query, variables }: any): Promise<CallToolResult> => {
      try {
        const endpoint = '/graphql';
        const result = await makePayloadRequest(config as PayloadConfig, endpoint, {
          method: 'POST',
          body: JSON.stringify({ query, variables })
        });

        return {
          content: [
            {
              type: "text",
              text: `✅ GraphQL query executed successfully\n\n${JSON.stringify(result, null, 2)}`
            }
          ]
        };
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        return {
          content: [
            {
              type: "text",
              text: `❌ GraphQL query failed: ${errorMessage}`
            }
          ]
        };
      }
    }
  );

  server.tool(
    "payload-graphql-mutation",
    "Execute a GraphQL mutation against PayloadCMS",
    graphqlMutationSchema.shape,
    async ({ config, mutation, variables }: any): Promise<CallToolResult> => {
      try {
        const endpoint = '/graphql';
        const result = await makePayloadRequest(config as PayloadConfig, endpoint, {
          method: 'POST',
          body: JSON.stringify({ query: mutation, variables })
        });

        return {
          content: [
            {
              type: "text",
              text: `✅ GraphQL mutation executed successfully\n\n${JSON.stringify(result, null, 2)}`
            }
          ]
        };
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        return {
          content: [
            {
              type: "text",
              text: `❌ GraphQL mutation failed: ${errorMessage}`
            }
          ]
        };
      }
    }
  );

  // === Utility Operations ===

  server.tool(
    "payload-health-check",
    "Check PayloadCMS API connectivity and get version information",
    healthCheckSchema.shape,
    async ({ config }: any): Promise<CallToolResult> => {
      try {
        // Try to access the root API endpoint
        const result = await makePayloadRequest(config as PayloadConfig, '', { method: 'GET' });

        return {
          content: [
            {
              type: "text",
              text: `✅ PayloadCMS API is accessible at ${config.baseUrl}\n\n${JSON.stringify(result, null, 2)}`
            }
          ]
        };
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        return {
          content: [
            {
              type: "text",
              text: `❌ PayloadCMS API health check failed for ${config.baseUrl}: ${errorMessage}`
            }
          ]
        };
      }
    }
  );

  console.log("✅ PayloadCMS tools registered successfully");
}