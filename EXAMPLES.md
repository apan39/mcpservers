# MCP Tools - Comprehensive Usage Examples

This document provides detailed examples for using all 65 MCP tools across the Python, TypeScript, and Browser-Use servers.

## Table of Contents
- [Python Server Tools (32 tools)](#python-server-tools)
- [TypeScript Server Tools (3 tools)](#typescript-server-tools)  
- [Browser-Use MCP Server Tools (30 tools)](#browser-use-mcp-server-tools)

---

## Python Server Tools

### Math & Calculation Tools

#### add-numbers
Add two numbers together with validation.

**Claude Command:**
```
Please use the add-numbers tool to calculate 25 + 37
```

**Direct API Call:**
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "jsonrpc": "2.0",
       "method": "tools/call",
       "params": {
         "name": "add-numbers",
         "arguments": {"a": 25, "b": 37}
       },
       "id": 1
     }' \
     http://localhost:3009/mcp
```

#### multiply-numbers
Multiply two numbers with support for decimals.

**Claude Command:**
```
Please multiply 4.5 by 8.2 using the multiply-numbers tool
```

**Direct API Call:**
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "jsonrpc": "2.0",
       "method": "tools/call",
       "params": {
         "name": "multiply-numbers",
         "arguments": {"a": 4.5, "b": 8.2}
       },
       "id": 1
     }' \
     http://localhost:3009/mcp
```

#### calculate-percentage
Calculate percentage values with precision.

**Claude Command:**
```
Please calculate what 15% of 280 is using the calculate-percentage tool
```

**Direct API Call:**
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "jsonrpc": "2.0",
       "method": "tools/call",
       "params": {
         "name": "calculate-percentage",
         "arguments": {"value": 280, "percentage": 15}
       },
       "id": 1
     }' \
     http://localhost:3009/mcp
```

### Text Processing Tools

#### string-operations
Perform various string transformations.

**Available Operations:** `uppercase`, `lowercase`, `reverse`, `title_case`

**Claude Commands:**
```
Please use the string-operations tool to convert "Hello World" to uppercase
Please use the string-operations tool to reverse the text "MCP Server"
Please use the string-operations tool to make "hello world" title case
```

**Direct API Call:**
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "jsonrpc": "2.0",
       "method": "tools/call",
       "params": {
         "name": "string-operations",
         "arguments": {
           "text": "Hello World",
           "operation": "uppercase"
         }
       },
       "id": 1
     }' \
     http://localhost:3009/mcp
```

#### word-count
Count words, characters, and lines in text.

**Claude Command:**
```
Please count the words in this text: "The quick brown fox jumps over the lazy dog"
```

**Direct API Call:**
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "jsonrpc": "2.0",
       "method": "tools/call",
       "params": {
         "name": "word-count",
         "arguments": {
           "text": "The quick brown fox jumps over the lazy dog"
         }
       },
       "id": 1
     }' \
     http://localhost:3009/mcp
```

#### format-text
Format text using different formatting styles.

**Available Formats:** `title_case`, `sentence_case`, `camel_case`, `snake_case`, `kebab_case`

**Claude Commands:**
```
Please format "hello world example" as camel case
Please format "THIS IS A TITLE" as sentence case
Please format "convert-this-text" as snake case
```

**Direct API Call:**
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "jsonrpc": "2.0",
       "method": "tools/call",
       "params": {
         "name": "format-text",
         "arguments": {
           "text": "hello world example",
           "format_type": "camel_case"
         }
       },
       "id": 1
     }' \
     http://localhost:3009/mcp
```

### Web Scraping Tools

#### crawl-url
Advanced web scraping with multiple extraction modes and filtering options.

**Extraction Modes:** `full`, `main_content`, `headings`, `links`, `summary`

**Basic Usage:**
```
Please crawl https://example.com and extract all content
```

**Advanced Usage:**
```
Please crawl this news article but only extract the main content: https://news.example.com/article
Please get only the headings from this documentation: https://docs.example.com
Please extract a summary of this long blog post: https://blog.example.com/long-post
Please crawl this page but exclude ads and navigation: https://cluttered-site.com
```

**Direct API Call - Basic:**
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "jsonrpc": "2.0",
       "method": "tools/call",
       "params": {
         "name": "crawl-url",
         "arguments": {
           "url": "https://example.com",
           "max_pages": 1
         }
       },
       "id": 1
     }' \
     http://localhost:3009/mcp
```

**Direct API Call - Advanced:**
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "jsonrpc": "2.0",
       "method": "tools/call",
       "params": {
         "name": "crawl-url",
         "arguments": {
           "url": "https://news.example.com/article",
           "extract_mode": "main_content",
           "max_length": 5000,
           "exclude_selectors": [".ads", ".sidebar", "nav"]
         }
       },
       "id": 1
     }' \
     http://localhost:3009/mcp
```

### Coolify API Tools (25 tools)

#### Core Operations

##### coolify-get-version
Get Coolify instance version and system information.

**Claude Command:**
```
Please get the Coolify version using coolify-get-version
```

##### coolify-list-projects
List all projects in your Coolify instance.

**Claude Command:**
```
Please list all projects in Coolify
```

##### coolify-list-servers
List all available servers.

**Claude Command:**
```
Please show me all available servers in Coolify
```

##### coolify-list-applications
List applications, optionally filtered by project.

**Claude Commands:**
```
Please list all applications across all projects
Please show applications in project abc-123-def
```

**Direct API Call:**
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "jsonrpc": "2.0",
       "method": "tools/call",
       "params": {
         "name": "coolify-list-applications",
         "arguments": {
           "project_uuid": "abc-123-def"
         }
       },
       "id": 1
     }' \
     http://localhost:3009/mcp
```

##### coolify-create-github-app
Deploy a GitHub repository to Coolify.

**Claude Command:**
```
Please deploy https://github.com/user/awesome-app to project abc-123 on server xyz-789 with name "my-awesome-app"
```

**Direct API Call:**
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "jsonrpc": "2.0",
       "method": "tools/call",
       "params": {
         "name": "coolify-create-github-app",
         "arguments": {
           "project_uuid": "abc-123",
           "server_uuid": "xyz-789",
           "git_repository": "https://github.com/user/awesome-app",
           "name": "my-awesome-app",
           "git_branch": "main",
           "build_pack": "nixpacks"
         }
       },
       "id": 1
     }' \
     http://localhost:3009/mcp
```

#### Application Management

##### coolify-get-application-info
Get detailed information about an application.

**Claude Command:**
```
Please get detailed information about application abc-123-def
```

##### coolify-restart-application
Restart an application.

**Claude Command:**
```
Please restart application abc-123-def
```

##### coolify-stop-application / coolify-start-application
Stop or start an application.

**Claude Commands:**
```
Please stop application abc-123-def for maintenance
Please start application abc-123-def after maintenance
```

##### coolify-delete-application
Delete an application (use with caution).

**Claude Command:**
```
Please delete application abc-123-def that is no longer needed
```

#### Deployment Operations

##### coolify-deploy-application
Trigger a new deployment.

**Claude Command:**
```
Please deploy the latest changes to application abc-123-def
```

##### coolify-get-deployment-logs
Get logs for a specific deployment.

**Claude Command:**
```
Please get the deployment logs for deployment xyz-789-ghi
```

##### coolify-watch-deployment
Monitor deployment progress in real-time.

**Claude Command:**
```
Please watch the deployment progress for deployment xyz-789-ghi
```

##### coolify-get-recent-deployments
Get recent deployment history for an application.

**Claude Command:**
```
Please show the last 5 deployments for application abc-123-def
```

**Direct API Call:**
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "jsonrpc": "2.0",
       "method": "tools/call",
       "params": {
         "name": "coolify-get-recent-deployments",
         "arguments": {
           "app_uuid": "abc-123-def",
           "limit": 5
         }
       },
       "id": 1
     }' \
     http://localhost:3009/mcp
```

#### Configuration Management

##### coolify-set-env-variable / coolify-delete-env-variable
Manage individual environment variables.

**Claude Commands:**
```
Please set environment variable PORT=3000 for application abc-123-def
Please set NODE_ENV=production for application abc-123-def
Please delete the OLD_API_KEY environment variable from application abc-123-def
```

##### coolify-bulk-update-env
Update multiple environment variables at once.

**Claude Command:**
```
Please bulk update these environment variables for app abc-123-def: PORT=3000, NODE_ENV=production, API_URL=https://api.example.com
```

**Direct API Call:**
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "jsonrpc": "2.0",
       "method": "tools/call",
       "params": {
         "name": "coolify-bulk-update-env",
         "arguments": {
           "app_uuid": "abc-123-def",
           "env_vars": [
             {"key": "PORT", "value": "3000"},
             {"key": "NODE_ENV", "value": "production"},
             {"key": "API_URL", "value": "https://api.example.com"}
           ]
         }
       },
       "id": 1
     }' \
     http://localhost:3009/mcp
```

##### coolify-update-health-check
Configure application health checks.

**Claude Command:**
```
Please update the health check for app abc-123-def to use path /api/health with 30 second interval
```

**Direct API Call:**
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "jsonrpc": "2.0",
       "method": "tools/call",
       "params": {
         "name": "coolify-update-health-check",
         "arguments": {
           "app_uuid": "abc-123-def",
           "health_check_enabled": true,
           "health_check_path": "/api/health",
           "health_check_interval": 30
         }
       },
       "id": 1
     }' \
     http://localhost:3009/mcp
```

##### coolify-test-health-endpoint
Test an application's health endpoint.

**Claude Command:**
```
Please test the health endpoint for application abc-123-def
```

#### Bulk Operations

##### coolify-bulk-restart
Restart multiple applications simultaneously.

**Claude Command:**
```
Please restart these applications: abc-123, def-456, ghi-789
```

##### coolify-bulk-deploy
Deploy multiple applications simultaneously.

**Claude Command:**
```
Please deploy these applications: abc-123, def-456, ghi-789
```

##### coolify-project-status
Get comprehensive status for an entire project.

**Claude Command:**
```
Please show the complete status for project abc-123 including all applications
```

---

## TypeScript Server Tools

### greet
Simple greeting tool.

**Claude Command:**
```
Please greet me using the greet tool
```

### multi-greet
Friendly greeting with delays.

**Claude Command:**
```
Please use multi-greet to send me a friendly greeting
```

### scrape-dynamic-url
Playwright-powered dynamic web scraping for JavaScript-heavy sites.

**Claude Commands:**
```
Please use scrape-dynamic-url to get content from this SPA: https://app.example.com
Please scrape this JavaScript-heavy page with 15 second timeout: https://dynamic.example.com
```

**Direct API Call:**
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "jsonrpc": "2.0",
       "method": "tools/call",
       "params": {
         "name": "scrape-dynamic-url",
         "arguments": {
           "url": "https://app.example.com",
           "timeout": 15000
         }
       },
       "id": 1
     }' \
     http://localhost:3010/mcp
```

---

## Browser-Use MCP Server Tools

### Session Management

#### create_browser_session
Create a new browser session for automation.

**Claude Commands:**
```
Please create a browser session called "shopping" in headless mode
Please create a browser session called "testing" with visible browser window
```

**MCP Call:**
```
claude mcp call browser-use-mcp create_browser_session '{"session_id": "shopping", "headless": true}'
```

#### close_browser_session
Close and cleanup a browser session.

**Claude Command:**
```
Please close browser session "shopping"
```

#### list_browser_sessions
List all active browser sessions.

**Claude Command:**
```
Please list all active browser sessions
```

#### get_session_info
Get detailed information about a session.

**Claude Command:**
```
Please get detailed info about session "shopping"
```

### Navigation & Page Control

#### navigate_to_url
Navigate to a specific URL.

**Claude Commands:**
```
Please navigate to google.com in session "search"
Please go to https://example.com/login in session "auth"
```

#### go_back / go_forward
Navigate through browser history.

**Claude Commands:**
```
Please go back to the previous page in session "search"
Please go forward to the next page in session "search"
```

#### refresh_page
Refresh the current page.

**Claude Command:**
```
Please refresh the current page in session "search"
```

### Content Extraction

#### get_page_content
Extract text content or HTML from the current page.

**Claude Commands:**
```
Please get the text content from the current page in session "search"
Please get the HTML content from the current page in session "search"
```

#### extract_content
Extract specific content using CSS selectors.

**Claude Command:**
```
Please extract content from the main article section in session "reader"
```

#### get_page_html
Get raw HTML content of the page.

**Claude Command:**
```
Please get the HTML source of the current page in session "search"
```

### User Interactions

#### click_element
Click on elements using CSS selectors.

**Claude Commands:**
```
Please click the search button with class "search-btn" in session "search"
Please click the login link in session "auth"
Please click the submit button in session "form"
```

#### input_text
Type text into input fields.

**Claude Commands:**
```
Please type "MCP servers" into the search input in session "search"
Please enter "user@example.com" in the email field in session "auth"
```

#### scroll
Scroll the page in specified directions.

**Claude Commands:**
```
Please scroll down 500 pixels in session "search"
Please scroll to the top of the page in session "reader"
Please scroll to the bottom in session "content"
```

#### send_keys
Send keyboard keys like Tab, Enter, Escape.

**Claude Commands:**
```
Please press Tab then Enter in session "form"
Please press Escape to close any modals in session "app"
```

### Tab Management

#### create_tab
Create a new browser tab.

**Claude Command:**
```
Please create a new tab and navigate to example.com in session "multi"
```

#### list_tabs
List all open tabs in the session.

**Claude Command:**
```
Please list all open tabs in session "multi"
```

#### switch_tab
Switch to a specific tab.

**Claude Command:**
```
Please switch to tab 2 in session "multi"
```

#### close_tab
Close the current or specific tab.

**Claude Commands:**
```
Please close the current tab in session "multi"
Please close tab 3 in session "multi"
```

### File Operations

#### upload_file
Upload files using file input elements.

**Claude Command:**
```
Please upload file "/path/to/document.pdf" to the file input in session "upload"
```

#### download_file
Download files by clicking download links.

**Claude Command:**
```
Please download the file from this URL in session "download"
```

### Advanced Features

#### execute_javascript
Execute custom JavaScript code on the page.

**Claude Commands:**
```
Please execute JavaScript to get the page title in session "search"
Please run JavaScript to scroll to element with id "content" in session "reader"
```

#### wait_for_element
Wait for elements to appear on the page.

**Claude Commands:**
```
Please wait for element with class "results" to appear in session "search"
Please wait for the loading spinner to disappear in session "app"
```

#### wait_for_load
Wait for page loading to complete.

**Claude Command:**
```
Please wait for the page to finish loading in session "app"
```

#### take_screenshot
Capture screenshots of the page or specific elements.

**Claude Commands:**
```
Please take a screenshot of the current page in session "search"
Please take a screenshot of the results section in session "search"
```

#### get_browser_state
Get comprehensive browser state information.

**Claude Command:**
```
Please get the complete browser state for session "search"
```

#### get_dom_elements
Get clickable and interactive DOM elements.

**Claude Command:**
```
Please get all clickable elements on the current page in session "search"
```

### AI Agent Features

#### create_agent
Create an AI agent for advanced browser automation.

**Claude Command:**
```
Please create an AI agent called "form-filler" in session "automation"
```

#### execute_agent_task
Execute tasks using AI agents.

**Claude Commands:**
```
Please use agent "form-filler" to fill out the contact form on this page
Please use agent "navigator" to find and click the login button
Please use agent "shopper" to search for laptops and add one to cart
```

#### get_agent_history
Get the action history for an agent.

**Claude Command:**
```
Please get the action history for agent "form-filler"
```

## Complex Workflow Examples

### E-commerce Automation
```
Please create a browser session "shopping", navigate to amazon.com, search for "mechanical keyboards", take a screenshot of the results, click on the first product, and then close the session
```

### Form Automation
```
Please create a browser session "contact", navigate to example.com/contact, create an AI agent "form-bot", use the agent to fill out the contact form with realistic data, submit it, and take a screenshot of the confirmation
```

### Multi-tab Research
```
Please create a browser session "research", open tabs for google.com, github.com, and stackoverflow.com, search for "MCP servers" on each, take screenshots of all results, and provide a summary
```

### Coolify Deployment Pipeline
```
Please list all my Coolify projects, create a new GitHub app from https://github.com/user/new-project in the first available project, watch the deployment progress, test the health endpoint when deployed, and show me the final application info
```

This comprehensive guide covers all 65 MCP tools with practical examples for both natural language commands and direct API calls.