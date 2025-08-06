import { z } from "zod";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { CallToolResult } from "@modelcontextprotocol/sdk/types.js";

// Environment variables
const PORKBUN_API_KEY = process.env.PORKBUN_API_KEY;
const PORKBUN_SECRET_API_KEY = process.env.PORKBUN_SECRET_API_KEY;
const PORKBUN_API_BASE_URL = "https://api.porkbun.com/api/json/v3";

// Common Porkbun API auth payload
interface PorkbunAuthPayload {
  apikey: string;
  secretapikey: string;
}

// Create auth payload for all requests
function createAuthPayload(): PorkbunAuthPayload {
  if (!PORKBUN_API_KEY || !PORKBUN_SECRET_API_KEY) {
    throw new Error("Porkbun API credentials not configured. Please set PORKBUN_API_KEY and PORKBUN_SECRET_API_KEY environment variables.");
  }
  
  return {
    apikey: PORKBUN_API_KEY,
    secretapikey: PORKBUN_SECRET_API_KEY
  };
}

// Generic API call function
async function porkbunApiCall(endpoint: string, payload: any = {}): Promise<any> {
  const authPayload = createAuthPayload();
  const requestBody = { ...authPayload, ...payload };
  
  try {
    const response = await fetch(`${PORKBUN_API_BASE_URL}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(requestBody)
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const result = await response.json();
    
    if (result.status === 'ERROR') {
      throw new Error(`Porkbun API error: ${result.message || 'Unknown error'}`);
    }
    
    return result;
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`Porkbun API call failed: ${error.message}`);
    }
    throw new Error('Unknown error occurred during Porkbun API call');
  }
}

// Domain Management Functions
async function listDomains(): Promise<CallToolResult> {
  try {
    const result = await porkbunApiCall('/domain/listAll');
    
    return {
      content: [{
        type: "text",
        text: JSON.stringify({
          status: "success",
          domains: result.domains || [],
          count: result.domains?.length || 0
        }, null, 2)
      }]
    };
  } catch (error) {
    return {
      content: [{
        type: "text", 
        text: `Error listing domains: ${error instanceof Error ? error.message : 'Unknown error'}`
      }]
    };
  }
}

async function checkDomainAvailability(domain: string): Promise<CallToolResult> {
  try {
    const result = await porkbunApiCall('/domain/availabilitycheck', { domain });
    
    return {
      content: [{
        type: "text",
        text: JSON.stringify({
          domain,
          available: result.status === 'AVAILABLE',
          status: result.status,
          message: result.message || 'Domain availability checked'
        }, null, 2)
      }]
    };
  } catch (error) {
    return {
      content: [{
        type: "text",
        text: `Error checking domain availability: ${error instanceof Error ? error.message : 'Unknown error'}`
      }]
    };
  }
}

async function getDomainNameservers(domain: string): Promise<CallToolResult> {
  try {
    const result = await porkbunApiCall(`/domain/getNs/${domain}`);
    
    return {
      content: [{
        type: "text",
        text: JSON.stringify({
          domain,
          nameservers: result.ns || [],
          status: "success"
        }, null, 2)
      }]
    };
  } catch (error) {
    return {
      content: [{
        type: "text",
        text: `Error getting domain nameservers: ${error instanceof Error ? error.message : 'Unknown error'}`
      }]
    };
  }
}

async function updateDomainNameservers(domain: string, ns: string[]): Promise<CallToolResult> {
  try {
    const result = await porkbunApiCall(`/domain/updateNs/${domain}`, { ns });
    
    return {
      content: [{
        type: "text",
        text: JSON.stringify({
          domain,
          message: result.message || 'Nameservers updated successfully',
          status: "success"
        }, null, 2)
      }]
    };
  } catch (error) {
    return {
      content: [{
        type: "text",
        text: `Error updating domain nameservers: ${error instanceof Error ? error.message : 'Unknown error'}`
      }]
    };
  }
}

// DNS Record Management Functions
async function createDnsRecord(domain: string, name: string, type: string, content: string, ttl?: number, prio?: number): Promise<CallToolResult> {
  try {
    const payload: any = { name, type, content };
    if (ttl) payload.ttl = ttl;
    if (prio) payload.prio = prio;
    
    const result = await porkbunApiCall(`/dns/create/${domain}`, payload);
    
    return {
      content: [{
        type: "text",
        text: JSON.stringify({
          domain,
          record: payload,
          id: result.id,
          message: result.message || 'DNS record created successfully',
          status: "success"
        }, null, 2)
      }]
    };
  } catch (error) {
    return {
      content: [{
        type: "text",
        text: `Error creating DNS record: ${error instanceof Error ? error.message : 'Unknown error'}`
      }]
    };
  }
}

async function editDnsRecord(domain: string, id: string, name?: string, type?: string, content?: string, ttl?: number, prio?: number): Promise<CallToolResult> {
  try {
    const payload: any = {};
    if (name) payload.name = name;
    if (type) payload.type = type;
    if (content) payload.content = content;
    if (ttl) payload.ttl = ttl;
    if (prio) payload.prio = prio;
    
    const result = await porkbunApiCall(`/dns/edit/${domain}/${id}`, payload);
    
    return {
      content: [{
        type: "text",
        text: JSON.stringify({
          domain,
          recordId: id,
          updates: payload,
          message: result.message || 'DNS record updated successfully',
          status: "success"
        }, null, 2)
      }]
    };
  } catch (error) {
    return {
      content: [{
        type: "text",
        text: `Error editing DNS record: ${error instanceof Error ? error.message : 'Unknown error'}`
      }]
    };
  }
}

async function deleteDnsRecord(domain: string, id: string): Promise<CallToolResult> {
  try {
    const result = await porkbunApiCall(`/dns/delete/${domain}/${id}`);
    
    return {
      content: [{
        type: "text",
        text: JSON.stringify({
          domain,
          recordId: id,
          message: result.message || 'DNS record deleted successfully',
          status: "success"
        }, null, 2)
      }]
    };
  } catch (error) {
    return {
      content: [{
        type: "text",
        text: `Error deleting DNS record: ${error instanceof Error ? error.message : 'Unknown error'}`
      }]
    };
  }
}

async function retrieveDnsRecords(domain: string): Promise<CallToolResult> {
  try {
    const result = await porkbunApiCall(`/dns/retrieve/${domain}`);
    
    return {
      content: [{
        type: "text",
        text: JSON.stringify({
          domain,
          records: result.records || [],
          count: result.records?.length || 0,
          status: "success"
        }, null, 2)
      }]
    };
  } catch (error) {
    return {
      content: [{
        type: "text",
        text: `Error retrieving DNS records: ${error instanceof Error ? error.message : 'Unknown error'}`
      }]
    };
  }
}

// URL Forwarding Functions
async function addUrlForward(domain: string, subdomain: string, location: string, type: string, wildcard?: string, includeExclude?: string): Promise<CallToolResult> {
  try {
    const payload: any = { subdomain, location, type };
    if (wildcard) payload.wildcard = wildcard;
    if (includeExclude) payload.includeExclude = includeExclude;
    
    const result = await porkbunApiCall(`/domain/addUrlForward/${domain}`, payload);
    
    return {
      content: [{
        type: "text",
        text: JSON.stringify({
          domain,
          forward: payload,
          message: result.message || 'URL forward added successfully',
          status: "success"
        }, null, 2)
      }]
    };
  } catch (error) {
    return {
      content: [{
        type: "text",
        text: `Error adding URL forward: ${error instanceof Error ? error.message : 'Unknown error'}`
      }]
    };
  }
}

async function getUrlForwards(domain: string): Promise<CallToolResult> {
  try {
    const result = await porkbunApiCall(`/domain/getUrlForwards/${domain}`);
    
    return {
      content: [{
        type: "text",
        text: JSON.stringify({
          domain,
          forwards: result.forwards || [],
          count: result.forwards?.length || 0,
          status: "success"
        }, null, 2)
      }]
    };
  } catch (error) {
    return {
      content: [{
        type: "text",
        text: `Error getting URL forwards: ${error instanceof Error ? error.message : 'Unknown error'}`
      }]
    };
  }
}

async function deleteUrlForward(domain: string, id: string): Promise<CallToolResult> {
  try {
    const result = await porkbunApiCall(`/domain/deleteUrlForward/${domain}/${id}`);
    
    return {
      content: [{
        type: "text",
        text: JSON.stringify({
          domain,
          forwardId: id,
          message: result.message || 'URL forward deleted successfully',
          status: "success"
        }, null, 2)
      }]
    };
  } catch (error) {
    return {
      content: [{
        type: "text",
        text: `Error deleting URL forward: ${error instanceof Error ? error.message : 'Unknown error'}`
      }]
    };
  }
}

// SSL Certificate Function
async function getSslBundle(domain: string): Promise<CallToolResult> {
  try {
    const result = await porkbunApiCall(`/ssl/retrieve/${domain}`);
    
    return {
      content: [{
        type: "text",
        text: JSON.stringify({
          domain,
          ssl: {
            certificatechain: result.certificatechain,
            privatekey: result.privatekey,
            publickey: result.publickey
          },
          status: "success"
        }, null, 2)
      }]
    };
  } catch (error) {
    return {
      content: [{
        type: "text",
        text: `Error retrieving SSL bundle: ${error instanceof Error ? error.message : 'Unknown error'}`
      }]
    };
  }
}

// Test API connection
async function testPorkbunConnection(): Promise<CallToolResult> {
  try {
    // Test with ping endpoint or domain list
    const result = await porkbunApiCall('/ping');
    
    return {
      content: [{
        type: "text",
        text: JSON.stringify({
          status: "success",
          message: "Porkbun API connection successful",
          response: result
        }, null, 2)
      }]
    };
  } catch (error) {
    return {
      content: [{
        type: "text",
        text: `Porkbun API connection failed: ${error instanceof Error ? error.message : 'Unknown error'}`
      }]
    };
  }
}

// Register all Porkbun tools with the MCP server
export function registerPorkbunTools(server: McpServer) {
  // Domain Management Tools
  server.tool(
    "porkbun-list-domains",
    "List all domains in your Porkbun account",
    {},
    async (): Promise<CallToolResult> => {
      return await listDomains();
    }
  );

  server.tool(
    "porkbun-check-domain-availability",
    "Check if a domain is available for registration",
    {
      domain: z.string().describe("Domain name to check availability for")
    },
    async ({ domain }): Promise<CallToolResult> => {
      return await checkDomainAvailability(domain);
    }
  );

  server.tool(
    "porkbun-get-domain-nameservers",
    "Get nameservers for a domain",
    {
      domain: z.string().describe("Domain name")
    },
    async ({ domain }): Promise<CallToolResult> => {
      return await getDomainNameservers(domain);
    }
  );

  server.tool(
    "porkbun-update-domain-nameservers",
    "Update nameservers for a domain",
    {
      domain: z.string().describe("Domain name"),
      nameservers: z.array(z.string()).describe("Array of nameserver hostnames")
    },
    async ({ domain, nameservers }): Promise<CallToolResult> => {
      return await updateDomainNameservers(domain, nameservers);
    }
  );

  // DNS Record Management Tools
  server.tool(
    "porkbun-create-dns-record",
    "Create a new DNS record for a domain",
    {
      domain: z.string().describe("Domain name"),
      name: z.string().describe("Record name (subdomain or @ for root)"),
      type: z.string().describe("DNS record type (A, AAAA, CNAME, MX, TXT, NS, SRV, etc.)"),
      content: z.string().describe("Record content/value"),
      ttl: z.number().optional().describe("Time to live in seconds (optional, default: 600)"),
      prio: z.number().optional().describe("Priority for MX/SRV records (optional)")
    },
    async ({ domain, name, type, content, ttl, prio }): Promise<CallToolResult> => {
      return await createDnsRecord(domain, name, type, content, ttl, prio);
    }
  );

  server.tool(
    "porkbun-edit-dns-record",
    "Edit an existing DNS record",
    {
      domain: z.string().describe("Domain name"),
      recordId: z.string().describe("DNS record ID to edit"),
      name: z.string().optional().describe("New record name (optional)"),
      type: z.string().optional().describe("New DNS record type (optional)"),
      content: z.string().optional().describe("New record content/value (optional)"),
      ttl: z.number().optional().describe("New time to live in seconds (optional)"),
      prio: z.number().optional().describe("New priority for MX/SRV records (optional)")
    },
    async ({ domain, recordId, name, type, content, ttl, prio }): Promise<CallToolResult> => {
      return await editDnsRecord(domain, recordId, name, type, content, ttl, prio);
    }
  );

  server.tool(
    "porkbun-delete-dns-record",
    "Delete a DNS record",
    {
      domain: z.string().describe("Domain name"),
      recordId: z.string().describe("DNS record ID to delete")
    },
    async ({ domain, recordId }): Promise<CallToolResult> => {
      return await deleteDnsRecord(domain, recordId);
    }
  );

  server.tool(
    "porkbun-retrieve-dns-records",
    "Retrieve all DNS records for a domain",
    {
      domain: z.string().describe("Domain name")
    },
    async ({ domain }): Promise<CallToolResult> => {
      return await retrieveDnsRecords(domain);
    }
  );

  // URL Forwarding Tools
  server.tool(
    "porkbun-add-url-forward",
    "Add URL forwarding for a domain/subdomain",
    {
      domain: z.string().describe("Domain name"),
      subdomain: z.string().describe("Subdomain to forward (@ for root domain)"),
      location: z.string().describe("Destination URL"),
      type: z.string().describe("Forward type: temporary_redirect (302) or permanent_redirect (301)"),
      wildcard: z.string().optional().describe("Wildcard forwarding (yes/no) - optional"),
      includeExclude: z.string().optional().describe("Include path in redirect (include/exclude) - optional")
    },
    async ({ domain, subdomain, location, type, wildcard, includeExclude }): Promise<CallToolResult> => {
      return await addUrlForward(domain, subdomain, location, type, wildcard, includeExclude);
    }
  );

  server.tool(
    "porkbun-get-url-forwards",
    "Get all URL forwards for a domain",
    {
      domain: z.string().describe("Domain name")
    },
    async ({ domain }): Promise<CallToolResult> => {
      return await getUrlForwards(domain);
    }
  );

  server.tool(
    "porkbun-delete-url-forward",
    "Delete a URL forward",
    {
      domain: z.string().describe("Domain name"),
      forwardId: z.string().describe("URL forward ID to delete")
    },
    async ({ domain, forwardId }): Promise<CallToolResult> => {
      return await deleteUrlForward(domain, forwardId);
    }
  );

  // SSL Certificate Tool
  server.tool(
    "porkbun-get-ssl-bundle",
    "Retrieve SSL certificate bundle for a domain",
    {
      domain: z.string().describe("Domain name")
    },
    async ({ domain }): Promise<CallToolResult> => {
      return await getSslBundle(domain);
    }
  );

  // Connection Test Tool
  server.tool(
    "porkbun-test-connection",
    "Test connection to Porkbun API",
    {},
    async (): Promise<CallToolResult> => {
      return await testPorkbunConnection();
    }
  );
}