import { Octokit } from "@octokit/rest";
import { z } from "zod";
import { CallToolResult } from "@modelcontextprotocol/sdk/types.js";

let octokit: Octokit | null = null;

// Initialize GitHub client
export function initializeGitHub(token?: string): void {
  if (token) {
    octokit = new Octokit({
      auth: token,
    });
  } else {
    // Anonymous access (rate limited)
    octokit = new Octokit();
  }
}

// Get current GitHub user info
export async function getCurrentUser(): Promise<CallToolResult> {
  if (!octokit) {
    return {
      content: [
        {
          type: "text",
          text: "GitHub client not initialized. Please authenticate first.",
        },
      ],
    };
  }

  try {
    const { data: user } = await octokit.rest.users.getAuthenticated();
    return {
      content: [
        {
          type: "text",
          text: `Authenticated as: ${user.login}\nName: ${user.name || 'N/A'}\nEmail: ${user.email || 'N/A'}\nPublic repos: ${user.public_repos}\nFollowers: ${user.followers}`,
        },
      ],
    };
  } catch (error: any) {
    return {
      content: [
        {
          type: "text",
          text: `Error getting user info: ${error.message}`,
        },
      ],
    };
  }
}

// List user repositories
export async function listRepositories(username?: string): Promise<CallToolResult> {
  if (!octokit) {
    return {
      content: [
        {
          type: "text",
          text: "GitHub client not initialized. Please authenticate first.",
        },
      ],
    };
  }

  try {
    let repos;
    if (username) {
      repos = await octokit.rest.repos.listForUser({
        username,
        sort: 'updated',
        per_page: 20,
      });
    } else {
      repos = await octokit.rest.repos.listForAuthenticatedUser({
        sort: 'updated',
        per_page: 20,
      });
    }

    const repoList = repos.data
      .map(repo => `${repo.name} - ${repo.description || 'No description'} (${repo.language || 'Unknown'}) - ${repo.updated_at}`)
      .join('\n');

    return {
      content: [
        {
          type: "text",
          text: `Repositories:\n${repoList}`,
        },
      ],
    };
  } catch (error: any) {
    return {
      content: [
        {
          type: "text",
          text: `Error listing repositories: ${error.message}`,
        },
      ],
    };
  }
}

// Get repository details
export async function getRepository(owner: string, repo: string): Promise<CallToolResult> {
  if (!octokit) {
    return {
      content: [
        {
          type: "text",
          text: "GitHub client not initialized. Please authenticate first.",
        },
      ],
    };
  }

  try {
    const { data: repository } = await octokit.rest.repos.get({
      owner,
      repo,
    });

    const details = `Repository: ${repository.full_name}
Description: ${repository.description || 'No description'}
Language: ${repository.language || 'Unknown'}
Stars: ${repository.stargazers_count}
Forks: ${repository.forks_count}
Issues: ${repository.open_issues_count}
Created: ${repository.created_at}
Updated: ${repository.updated_at}
URL: ${repository.html_url}
Clone URL: ${repository.clone_url}`;

    return {
      content: [
        {
          type: "text",
          text: details,
        },
      ],
    };
  } catch (error: any) {
    return {
      content: [
        {
          type: "text",
          text: `Error getting repository: ${error.message}`,
        },
      ],
    };
  }
}

// List issues for a repository
export async function listIssues(owner: string, repo: string, state: 'open' | 'closed' | 'all' = 'open'): Promise<CallToolResult> {
  if (!octokit) {
    return {
      content: [
        {
          type: "text",
          text: "GitHub client not initialized. Please authenticate first.",
        },
      ],
    };
  }

  try {
    const { data: issues } = await octokit.rest.issues.listForRepo({
      owner,
      repo,
      state,
      per_page: 20,
    });

    if (issues.length === 0) {
      return {
        content: [
          {
            type: "text",
            text: `No ${state} issues found in ${owner}/${repo}`,
          },
        ],
      };
    }

    const issueList = issues
      .map(issue => `#${issue.number}: ${issue.title} (${issue.state}) - ${issue.user?.login} - ${issue.created_at}`)
      .join('\n');

    return {
      content: [
        {
          type: "text",
          text: `Issues in ${owner}/${repo}:\n${issueList}`,
        },
      ],
    };
  } catch (error: any) {
    return {
      content: [
        {
          type: "text",
          text: `Error listing issues: ${error.message}`,
        },
      ],
    };
  }
}

// Create a new issue
export async function createIssue(owner: string, repo: string, title: string, body?: string, labels?: string[]): Promise<CallToolResult> {
  if (!octokit) {
    return {
      content: [
        {
          type: "text",
          text: "GitHub client not initialized. Please authenticate first.",
        },
      ],
    };
  }

  try {
    const { data: issue } = await octokit.rest.issues.create({
      owner,
      repo,
      title,
      body,
      labels,
    });

    return {
      content: [
        {
          type: "text",
          text: `Issue created successfully!\nIssue #${issue.number}: ${issue.title}\nURL: ${issue.html_url}`,
        },
      ],
    };
  } catch (error: any) {
    return {
      content: [
        {
          type: "text",
          text: `Error creating issue: ${error.message}`,
        },
      ],
    };
  }
}

// List pull requests
export async function listPullRequests(owner: string, repo: string, state: 'open' | 'closed' | 'all' = 'open'): Promise<CallToolResult> {
  if (!octokit) {
    return {
      content: [
        {
          type: "text",
          text: "GitHub client not initialized. Please authenticate first.",
        },
      ],
    };
  }

  try {
    const { data: prs } = await octokit.rest.pulls.list({
      owner,
      repo,
      state,
      per_page: 20,
    });

    if (prs.length === 0) {
      return {
        content: [
          {
            type: "text",
            text: `No ${state} pull requests found in ${owner}/${repo}`,
          },
        ],
      };
    }

    const prList = prs
      .map(pr => `#${pr.number}: ${pr.title} (${pr.state}) - ${pr.user?.login} - ${pr.created_at}`)
      .join('\n');

    return {
      content: [
        {
          type: "text",
          text: `Pull Requests in ${owner}/${repo}:\n${prList}`,
        },
      ],
    };
  } catch (error: any) {
    return {
      content: [
        {
          type: "text",
          text: `Error listing pull requests: ${error.message}`,
        },
      ],
    };
  }
}

// Get repository contents
export async function getContents(owner: string, repo: string, path: string = ""): Promise<CallToolResult> {
  if (!octokit) {
    return {
      content: [
        {
          type: "text",
          text: "GitHub client not initialized. Please authenticate first.",
        },
      ],
    };
  }

  try {
    const { data } = await octokit.rest.repos.getContent({
      owner,
      repo,
      path,
    });

    if (Array.isArray(data)) {
      // Directory listing
      const fileList = data
        .map(item => `${item.type === 'dir' ? '📁' : '📄'} ${item.name} (${item.type})`)
        .join('\n');

      return {
        content: [
          {
            type: "text",
            text: `Contents of ${owner}/${repo}/${path}:\n${fileList}`,
          },
        ],
      };
    } else {
      // Single file
      const content = data.type === 'file' && data.content 
        ? Buffer.from(data.content, 'base64').toString('utf-8')
        : 'Content not available';

      return {
        content: [
          {
            type: "text",
            text: `File: ${data.name}\nSize: ${data.size} bytes\nType: ${data.type}\n\nContent:\n${content}`,
          },
        ],
      };
    }
  } catch (error: any) {
    return {
      content: [
        {
          type: "text",
          text: `Error getting contents: ${error.message}`,
        },
      ],
    };
  }
}

// Search repositories
export async function searchRepositories(query: string, sort: 'stars' | 'forks' | 'updated' = 'stars'): Promise<CallToolResult> {
  if (!octokit) {
    return {
      content: [
        {
          type: "text",
          text: "GitHub client not initialized. Please authenticate first.",
        },
      ],
    };
  }

  try {
    const { data } = await octokit.rest.search.repos({
      q: query,
      sort,
      per_page: 10,
    });

    if (data.items.length === 0) {
      return {
        content: [
          {
            type: "text",
            text: `No repositories found for query: "${query}"`,
          },
        ],
      };
    }

    const repoList = data.items
      .map(repo => `${repo.full_name} - ${repo.description || 'No description'} (⭐ ${repo.stargazers_count})`)
      .join('\n');

    return {
      content: [
        {
          type: "text",
          text: `Search results for "${query}":\n${repoList}`,
        },
      ],
    };
  } catch (error: any) {
    return {
      content: [
        {
          type: "text",
          text: `Error searching repositories: ${error.message}`,
        },
      ],
    };
  }
}