# GitHub MCP Tools

This TypeScript MCP server provides comprehensive GitHub API integration tools for connecting to your GitHub account.

## Setup

1. **Generate a GitHub Personal Access Token:**
   - Go to https://github.com/settings/tokens
   - Click "Generate new token (classic)"
   - Select scopes: `repo`, `user`, `issues`, `pull_requests`
   - Copy the generated token

2. **Configure Environment:**
   ```bash
   cp .env.example .env
   # Edit .env and add your GitHub token
   GITHUB_TOKEN=your_token_here
   ```

3. **Install Dependencies:**
   ```bash
   npm install
   npm run build
   ```

## Available Tools

### Authentication & User Info
- **`github-get-user`** - Get information about the authenticated GitHub user

### Repository Management
- **`github-list-repos`** - List repositories for a user (or authenticated user)
  - `username` (optional): Username to list repositories for
- **`github-get-repo`** - Get detailed information about a specific repository
  - `owner`: Repository owner/organization
  - `repo`: Repository name
- **`github-search-repos`** - Search for repositories on GitHub
  - `query`: Search query
  - `sort` (optional): Sort order (`stars`, `forks`, `updated`)

### Issue Management
- **`github-list-issues`** - List issues for a repository
  - `owner`: Repository owner/organization
  - `repo`: Repository name
  - `state` (optional): Issue state filter (`open`, `closed`, `all`)
- **`github-create-issue`** - Create a new issue in a repository
  - `owner`: Repository owner/organization
  - `repo`: Repository name
  - `title`: Issue title
  - `body` (optional): Issue description/body
  - `labels` (optional): Array of issue labels

### Pull Request Management
- **`github-list-prs`** - List pull requests for a repository
  - `owner`: Repository owner/organization
  - `repo`: Repository name
  - `state` (optional): PR state filter (`open`, `closed`, `all`)

### Repository Contents
- **`github-get-contents`** - Get contents of a repository directory or file
  - `owner`: Repository owner/organization
  - `repo`: Repository name
  - `path` (optional): Path to directory or file (empty for root)

## Usage Examples

```bash
# Get user info
github-get-user

# List your repositories
github-list-repos

# List repositories for a specific user
github-list-repos --username octocat

# Get repository details
github-get-repo --owner microsoft --repo vscode

# List open issues
github-list-issues --owner facebook --repo react

# Create a new issue
github-create-issue --owner myorg --repo myrepo --title "Bug report" --body "Description of the bug"

# Search repositories
github-search-repos --query "machine learning python" --sort stars

# Get repository contents
github-get-contents --owner nodejs --repo node --path "lib"
```

## Security Notes

- Store your GitHub token securely in the `.env` file
- Never commit your `.env` file to version control
- The server supports both authenticated and anonymous access (anonymous has lower rate limits)
- Tokens should have minimal required scopes for security

## Rate Limiting

- Authenticated requests: 5,000 requests per hour
- Unauthenticated requests: 60 requests per hour

## Running the Server

```bash
# Development mode
npm run dev

# Production mode
npm run build
npm start
```