import { githubGetContents, githubGetRepo } from "./githubRemoteTools.js";

// Parse repository URL from Coolify format to GitHub owner/repo
function parseRepoUrl(repoUrl: string): { owner: string, repo: string } | null {
  // Handle various formats:
  // - "apan39/mcpservers.git"
  // - "https://github.com/apan39/mcpservers.git"
  // - "git@github.com:apan39/mcpservers.git"
  
  let match;
  
  // Remove .git suffix if present
  const cleanUrl = repoUrl.replace(/\.git$/, '');
  
  // Try different patterns
  if (cleanUrl.includes('github.com/')) {
    // https://github.com/owner/repo or git@github.com:owner/repo
    match = cleanUrl.match(/github\.com[\/:]([^\/]+)\/([^\/]+)$/);
  } else if (cleanUrl.includes('/')) {
    // Simple format: owner/repo
    match = cleanUrl.match(/^([^\/]+)\/([^\/]+)$/);
  }
  
  if (match) {
    return {
      owner: match[1],
      repo: match[2]
    };
  }
  
  return null;
}

export async function coolifyInvestigateApp(coolifyAppInfo: any): Promise<any> {
  try {
    // Extract repository information from Coolify app
    const gitRepo = coolifyAppInfo.git_repository || coolifyAppInfo.repository;
    if (!gitRepo) {
      return {
        content: [
          {
            type: "text",
            text: "No Git repository information found in Coolify application data.",
          },
        ],
      };
    }

    const parsed = parseRepoUrl(gitRepo);
    if (!parsed) {
      return {
        content: [
          {
            type: "text",
            text: `Could not parse repository URL: ${gitRepo}`,
          },
        ],
      };
    }

    // Get repository details
    const repoDetails = await githubGetRepo(parsed.owner, parsed.repo);
    
    // Get repository structure (root directory)
    const repoContents = await githubGetContents(parsed.owner, parsed.repo, "");

    // Try to get key files
    const keyFiles = ['README.md', 'package.json', 'Dockerfile', '.env.example', 'requirements.txt'];
    const fileContents: any[] = [];
    
    for (const fileName of keyFiles) {
      try {
        const fileContent = await githubGetContents(parsed.owner, parsed.repo, fileName);
        if (fileContent.content && fileContent.content[0] && !fileContent.content[0].text.includes('Error getting contents')) {
          fileContents.push({
            file: fileName,
            content: fileContent.content[0].text
          });
        }
      } catch (error) {
        // File doesn't exist, continue
      }
    }

    // Compile investigation report
    let report = `# Coolify Application Repository Investigation\n\n`;
    report += `**Coolify App:** ${coolifyAppInfo.name || 'Unknown'}\n`;
    report += `**Status:** ${coolifyAppInfo.status || 'Unknown'}\n`;
    report += `**Repository:** ${gitRepo}\n`;
    report += `**Branch:** ${coolifyAppInfo.git_branch || coolifyAppInfo.branch || 'main'}\n\n`;
    
    // Add repository details
    if (repoDetails.content && repoDetails.content[0]) {
      report += `## Repository Details\n`;
      report += `${repoDetails.content[0].text}\n\n`;
    }
    
    // Add repository structure
    if (repoContents.content && repoContents.content[0]) {
      report += `## Repository Structure\n`;
      report += `${repoContents.content[0].text}\n\n`;
    }
    
    // Add key file contents
    if (fileContents.length > 0) {
      report += `## Key Files Analysis\n\n`;
      for (const file of fileContents) {
        report += `### ${file.file}\n`;
        report += `\`\`\`\n${file.content}\n\`\`\`\n\n`;
      }
    }

    return {
      content: [
        {
          type: "text",
          text: report,
        },
      ],
    };

  } catch (error: any) {
    return {
      content: [
        {
          type: "text",
          text: `Error investigating Coolify application repository: ${error.message}`,
        },
      ],
    };
  }
}

export async function coolifyAnalyzeRepo(repoUrl: string, specificPath?: string): Promise<any> {
  try {
    const parsed = parseRepoUrl(repoUrl);
    if (!parsed) {
      return {
        content: [
          {
            type: "text",
            text: `Could not parse repository URL: ${repoUrl}`,
          },
        ],
      };
    }

    let report = `# Repository Analysis: ${parsed.owner}/${parsed.repo}\n\n`;

    if (specificPath) {
      // Analyze specific path
      const pathContents = await githubGetContents(parsed.owner, parsed.repo, specificPath);
      if (pathContents.content && pathContents.content[0]) {
        report += `## Analysis of: ${specificPath}\n`;
        report += `${pathContents.content[0].text}\n\n`;
      }
    } else {
      // General analysis
      const repoDetails = await githubGetRepo(parsed.owner, parsed.repo);
      const rootContents = await githubGetContents(parsed.owner, parsed.repo, "");
      
      if (repoDetails.content && repoDetails.content[0]) {
        report += `## Repository Overview\n`;
        report += `${repoDetails.content[0].text}\n\n`;
      }
      
      if (rootContents.content && rootContents.content[0]) {
        report += `## Root Directory Structure\n`;
        report += `${rootContents.content[0].text}\n\n`;
      }

      // Try to analyze common configuration files
      const configFiles = ['package.json', 'Dockerfile', 'docker-compose.yml', 'requirements.txt', 'setup.py'];
      
      for (const configFile of configFiles) {
        try {
          const fileContent = await githubGetContents(parsed.owner, parsed.repo, configFile);
          if (fileContent.content && fileContent.content[0] && !fileContent.content[0].text.includes('Error getting contents')) {
            report += `## ${configFile} Analysis\n`;
            report += `\`\`\`\n${fileContent.content[0].text}\n\`\`\`\n\n`;
          }
        } catch (error) {
          // File doesn't exist, continue
        }
      }
    }

    return {
      content: [
        {
          type: "text",
          text: report,
        },
      ],
    };

  } catch (error: any) {
    return {
      content: [
        {
          type: "text",
          text: `Error analyzing repository: ${error.message}`,
        },
      ],
    };
  }
}