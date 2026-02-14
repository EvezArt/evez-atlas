// GitHub Autonomous Operations Skill for OpenClaw
// Provides autonomous GitHub operations (issues, PRs, comments)
// SAFE_MODE: All operations are logged but not executed by default

export default {
  name: 'github-autonomous',
  version: '1.0.0',
  description: 'Enables autonomous GitHub operations',
  
  /**
   * Initialize Octokit client
   * @returns {Object|null} Octokit client or null if not available
   */
  initClient() {
    // Check if we have the GitHub token
    if (!process.env.GITHUB_TOKEN) {
      console.warn('[GitHub] GITHUB_TOKEN not found in environment');
      return null;
    }
    
    // Try to load Octokit package
    try {
      const { Octokit } = require('@octokit/rest');
      return new Octokit({
        auth: process.env.GITHUB_TOKEN
      });
    } catch (e) {
      console.warn('[GitHub] @octokit/rest package not available:', e.message);
      console.warn('[GitHub] Install with: npm install @octokit/rest');
      return null;
    }
  },
  
  /**
   * Create a GitHub issue
   * @param {Object} params - Issue parameters
   * @returns {Object} Created issue
   */
  async createIssue(params) {
    const { owner, repo, title, body, labels, assignees } = params;
    
    // In SAFE_MODE, don't make actual API calls
    if (process.env.SAFE_MODE !== 'false') {
      console.log('[SAFE_MODE] GitHub issue creation logged but not executed:');
      console.log('Repository:', `${owner}/${repo}`);
      console.log('Title:', title);
      console.log('Labels:', labels);
      return {
        safeMode: true,
        action: 'create_issue',
        params
      };
    }
    
    const client = this.initClient();
    if (!client) {
      return { error: 'GitHub client not available. Check token and package installation.' };
    }
    
    try {
      const response = await client.issues.create({
        owner,
        repo,
        title,
        body,
        labels: labels || [],
        assignees: assignees || []
      });
      
      return {
        success: true,
        issue: response.data,
        url: response.data.html_url
      };
    } catch (e) {
      console.error('[GitHub] Error creating issue:', e.message);
      return {
        error: e.message,
        action: 'create_issue'
      };
    }
  },
  
  /**
   * Create a pull request
   * @param {Object} params - PR parameters
   * @returns {Object} Created PR
   */
  async createPullRequest(params) {
    const { owner, repo, title, body, head, base, draft } = params;
    
    // In SAFE_MODE, don't make actual API calls
    if (process.env.SAFE_MODE !== 'false') {
      console.log('[SAFE_MODE] GitHub PR creation logged but not executed:');
      console.log('Repository:', `${owner}/${repo}`);
      console.log('Title:', title);
      console.log('Branches:', `${head} -> ${base}`);
      return {
        safeMode: true,
        action: 'create_pr',
        params
      };
    }
    
    const client = this.initClient();
    if (!client) {
      return { error: 'GitHub client not available. Check token and package installation.' };
    }
    
    try {
      const response = await client.pulls.create({
        owner,
        repo,
        title,
        body,
        head,
        base: base || 'main',
        draft: draft || false
      });
      
      return {
        success: true,
        pr: response.data,
        url: response.data.html_url
      };
    } catch (e) {
      console.error('[GitHub] Error creating PR:', e.message);
      return {
        error: e.message,
        action: 'create_pr'
      };
    }
  },
  
  /**
   * Add comment to issue or PR
   * @param {Object} params - Comment parameters
   * @returns {Object} Created comment
   */
  async addComment(params) {
    const { owner, repo, issue_number, body } = params;
    
    // In SAFE_MODE, don't make actual API calls
    if (process.env.SAFE_MODE !== 'false') {
      console.log('[SAFE_MODE] GitHub comment logged but not executed:');
      console.log('Issue:', `${owner}/${repo}#${issue_number}`);
      console.log('Comment:', body.substring(0, 100) + '...');
      return {
        safeMode: true,
        action: 'add_comment',
        params
      };
    }
    
    const client = this.initClient();
    if (!client) {
      return { error: 'GitHub client not available. Check token and package installation.' };
    }
    
    try {
      const response = await client.issues.createComment({
        owner,
        repo,
        issue_number,
        body
      });
      
      return {
        success: true,
        comment: response.data,
        url: response.data.html_url
      };
    } catch (e) {
      console.error('[GitHub] Error adding comment:', e.message);
      return {
        error: e.message,
        action: 'add_comment'
      };
    }
  },
  
  /**
   * List repository issues
   * @param {Object} params - Query parameters
   * @returns {Array} List of issues
   */
  async listIssues(params) {
    const { owner, repo, state, labels } = params;
    
    const client = this.initClient();
    if (!client) {
      return { error: 'GitHub client not available. Check token and package installation.' };
    }
    
    try {
      const response = await client.issues.listForRepo({
        owner,
        repo,
        state: state || 'open',
        labels: labels ? labels.join(',') : undefined
      });
      
      return {
        success: true,
        issues: response.data,
        count: response.data.length
      };
    } catch (e) {
      console.error('[GitHub] Error listing issues:', e.message);
      return {
        error: e.message,
        action: 'list_issues'
      };
    }
  },
  
  /**
   * Get repository information
   * @param {Object} params - Repository parameters
   * @returns {Object} Repository data
   */
  async getRepository(params) {
    const { owner, repo } = params;
    
    const client = this.initClient();
    if (!client) {
      return { error: 'GitHub client not available. Check token and package installation.' };
    }
    
    try {
      const response = await client.repos.get({
        owner,
        repo
      });
      
      return {
        success: true,
        repository: response.data
      };
    } catch (e) {
      console.error('[GitHub] Error getting repository:', e.message);
      return {
        error: e.message,
        action: 'get_repository'
      };
    }
  },
  
  /**
   * Called when skill is loaded
   * @param {Object} agent - The agent instance
   */
  async onLoad(agent) {
    console.log('🐙 GitHub autonomous operations enabled');
    console.log(`   SAFE_MODE: ${process.env.SAFE_MODE !== 'false' ? 'ON (no GitHub writes)' : 'OFF (GitHub writes active)'}`);
    console.log(`   GitHub Token: ${process.env.GITHUB_TOKEN ? '✓ Configured' : '✗ Missing'}`);
    
    // Test initialization
    const client = this.initClient();
    if (client) {
      console.log('   GitHub client: ✓ Ready');
    } else {
      console.log('   GitHub client: ✗ Not available');
    }
    
    // Make methods available to agent
    if (agent) {
      agent.github = {
        createIssue: this.createIssue.bind(this),
        createPullRequest: this.createPullRequest.bind(this),
        addComment: this.addComment.bind(this),
        listIssues: this.listIssues.bind(this),
        getRepository: this.getRepository.bind(this)
      };
    }
  },
  
  /**
   * Called when skill is unloaded
   */
  async onUnload() {
    console.log('🐙 GitHub autonomous operations disabled');
  }
};
