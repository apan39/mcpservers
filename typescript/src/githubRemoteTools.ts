import { Octokit } from "@octokit/rest";
import { z } from "zod";

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

// Initialize with environment variable if available
if (process.env.GITHUB_TOKEN) {
  initializeGitHub(process.env.GITHUB_TOKEN);
} else {
  initializeGitHub(); // Anonymous access
}

export async function githubGetUser(): Promise<any> {
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

export async function githubListRepos(username?: string): Promise<any> {
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

export async function githubGetRepo(owner: string, repo: string): Promise<any> {
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

export async function githubListIssues(owner: string, repo: string, state: 'open' | 'closed' | 'all' = 'open'): Promise<any> {
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

export async function githubCreateIssue(owner: string, repo: string, title: string, body?: string, labels?: string[]): Promise<any> {
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

export async function githubListPRs(owner: string, repo: string, state: 'open' | 'closed' | 'all' = 'open'): Promise<any> {
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

export async function githubGetContents(owner: string, repo: string, path: string = ""): Promise<any> {
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

export async function githubSearchRepos(query: string, sort: 'stars' | 'forks' | 'updated' = 'stars'): Promise<any> {
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

// Create or update a file in a repository
export async function githubCreateOrUpdateFile(
  owner: string, 
  repo: string, 
  path: string, 
  content: string, 
  message: string,
  branch: string = 'main',
  sha?: string
): Promise<any> {
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
    // Encode content to base64
    const encodedContent = Buffer.from(content, 'utf-8').toString('base64');

    // Create or update the file
    const { data } = await octokit.rest.repos.createOrUpdateFileContents({
      owner,
      repo,
      path,
      message,
      content: encodedContent,
      branch,
      sha, // Include SHA if updating existing file
    });

    return {
      content: [
        {
          type: "text",
          text: `File ${path} ${sha ? 'updated' : 'created'} successfully!\nCommit SHA: ${data.commit.sha}\nCommit URL: ${data.commit.html_url}`,
        },
      ],
    };
  } catch (error: any) {
    return {
      content: [
        {
          type: "text",
          text: `Error ${sha ? 'updating' : 'creating'} file: ${error.message}`,
        },
      ],
    };
  }
}

// Get file SHA (needed for updates/deletes)
export async function githubGetFileSha(owner: string, repo: string, path: string, branch: string = 'main'): Promise<any> {
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
      ref: branch,
    });

    if (Array.isArray(data)) {
      return {
        content: [
          {
            type: "text",
            text: `Path ${path} is a directory, not a file`,
          },
        ],
      };
    }

    return {
      content: [
        {
          type: "text",
          text: `File SHA for ${path}: ${data.sha}`,
        },
      ],
    };
  } catch (error: any) {
    return {
      content: [
        {
          type: "text",
          text: `Error getting file SHA: ${error.message}`,
        },
      ],
    };
  }
}

// Add git submodule (creates .gitmodules and commits)
export async function githubAddSubmodule(
  owner: string,
  repo: string,
  submodulePath: string,
  submoduleUrl: string,
  branch: string = 'main',
  commitMessage?: string
): Promise<any> {
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
    // Check if .gitmodules already exists
    let gitmodulesContent = '';
    let gitmodulesSha: string | undefined;
    
    try {
      const { data: existingFile } = await octokit.rest.repos.getContent({
        owner,
        repo,
        path: '.gitmodules',
        ref: branch,
      });
      
      if (!Array.isArray(existingFile) && existingFile.type === 'file' && existingFile.content) {
        gitmodulesContent = Buffer.from(existingFile.content, 'base64').toString('utf-8');
        gitmodulesSha = existingFile.sha;
      }
    } catch (error) {
      // .gitmodules doesn't exist, will create new
    }

    // Create submodule entry
    const submoduleEntry = `\n[submodule "${submodulePath}"]\n\tpath = ${submodulePath}\n\turl = ${submoduleUrl}\n`;
    
    // Check if submodule already exists
    if (gitmodulesContent.includes(`[submodule "${submodulePath}"]`)) {
      return {
        content: [
          {
            type: "text",
            text: `Submodule '${submodulePath}' already exists in .gitmodules`,
          },
        ],
      };
    }

    // Add submodule to .gitmodules content
    const newGitmodulesContent = gitmodulesContent + submoduleEntry;

    // Create or update .gitmodules
    const message = commitMessage || `Add ${submodulePath} as git submodule`;
    
    const result = await githubCreateOrUpdateFile(
      owner,
      repo,
      '.gitmodules',
      newGitmodulesContent.trim(),
      message,
      branch,
      gitmodulesSha
    );

    return {
      content: [
        {
          type: "text",
          text: `Git submodule '${submodulePath}' added successfully!\nSubmodule URL: ${submoduleUrl}\n${result.content[0].text}`,
        },
      ],
    };
  } catch (error: any) {
    return {
      content: [
        {
          type: "text",
          text: `Error adding git submodule: ${error.message}`,
        },
      ],
    };
  }
}