/**
 * Cognitive Engine Runner
 * 
 * Standalone script that runs the cognitive engine once
 * Used by GitHub Actions workflow
 */

import { Octokit } from '@octokit/rest';
import { createCognitiveEngine } from './index';
import { GitHubAPIFetcher } from './webhook-service';
import { GitHubClient } from './github-actions';
import * as fs from 'fs';

// Configuration from environment
const GITHUB_TOKEN = process.env.GITHUB_TOKEN || '';
const REPO_OWNER = process.env.REPO_OWNER || 'EvezArt';
const REPO_NAME = process.env.REPO_NAME || 'Evez666';
const AUTO_EXECUTE = process.env.AUTO_EXECUTE_POLICIES === 'true' || false;

// Initialize Octokit
const octokit = new Octokit({
  auth: GITHUB_TOKEN,
});

/**
 * GitHub API Fetcher implementation
 */
const apiFetcher: GitHubAPIFetcher = {
  async fetchCommits(owner: string, repo: string, count: number = 50) {
    try {
      const { data } = await octokit.repos.listCommits({
        owner,
        repo,
        per_page: count,
      });
      return data;
    } catch (error) {
      console.error('Error fetching commits:', error);
      return [];
    }
  },

  async fetchIssues(owner: string, repo: string) {
    try {
      const { data } = await octokit.issues.listForRepo({
        owner,
        repo,
        state: 'all',
        per_page: 100,
      });
      return data;
    } catch (error) {
      console.error('Error fetching issues:', error);
      return [];
    }
  },

  async fetchWorkflowRuns(owner: string, repo: string, count: number = 20) {
    try {
      const { data } = await octokit.actions.listWorkflowRunsForRepo({
        owner,
        repo,
        per_page: count,
      });
      return data.workflow_runs;
    } catch (error) {
      console.error('Error fetching workflow runs:', error);
      return [];
    }
  },

  async fetchCodeScanningAlerts(owner: string, repo: string) {
    try {
      const { data } = await octokit.codeScanning.listAlertsForRepo({
        owner,
        repo,
        state: 'open',
      });
      return data;
    } catch (error) {
      console.error('Error fetching code scanning alerts:', error);
      return [];
    }
  },

  async fetchDeployments(owner: string, repo: string, count: number = 10) {
    try {
      const { data } = await octokit.repos.listDeployments({
        owner,
        repo,
        per_page: count,
      });
      return data;
    } catch (error) {
      console.error('Error fetching deployments:', error);
      return [];
    }
  },

  async fetchPullRequests(owner: string, repo: string) {
    try {
      const { data } = await octokit.pulls.list({
        owner,
        repo,
        state: 'all',
        per_page: 100,
      });
      return data;
    } catch (error) {
      console.error('Error fetching pull requests:', error);
      return [];
    }
  },
};

/**
 * GitHub Client implementation
 */
const githubClient: GitHubClient = {
  async createIssue(title: string, body: string, labels?: string[]) {
    const { data } = await octokit.issues.create({
      owner: REPO_OWNER,
      repo: REPO_NAME,
      title,
      body,
      labels,
    });
    return data;
  },

  async addLabels(issueNumber: number, labels: string[]) {
    const { data } = await octokit.issues.addLabels({
      owner: REPO_OWNER,
      repo: REPO_NAME,
      issue_number: issueNumber,
      labels,
    });
    return data;
  },

  async assignCopilot(issueNumber: number) {
    // In GitHub, we can't directly assign to @copilot
    // Instead, we add a label that triggers Copilot
    return this.addLabels(issueNumber, ['copilot']);
  },

  async createComment(issueNumber: number, body: string) {
    const { data } = await octokit.issues.createComment({
      owner: REPO_OWNER,
      repo: REPO_NAME,
      issue_number: issueNumber,
      body,
    });
    return data;
  },

  async createPullRequest(title: string, body: string, head: string, base: string) {
    const { data } = await octokit.pulls.create({
      owner: REPO_OWNER,
      repo: REPO_NAME,
      title,
      body,
      head,
      base,
    });
    return data;
  },
};

/**
 * Main runner function
 */
async function run() {
  console.log('🧠 Cognitive Engine v1.0');
  console.log('========================');
  console.log(`Repository: ${REPO_OWNER}/${REPO_NAME}`);
  console.log(`Auto-execute policies: ${AUTO_EXECUTE}`);
  console.log('');

  // Create cognitive engine
  const engine = createCognitiveEngine({
    repoOwner: REPO_OWNER,
    repoName: REPO_NAME,
    autoExecutePolicies: AUTO_EXECUTE,
  });

  // Set GitHub client
  if (AUTO_EXECUTE) {
    engine.setGitHubClient(githubClient);
  }

  // Listen to events
  const logFile = 'cognitive-engine.log';
  const logs: string[] = [];

  engine.on((event) => {
    const logEntry = {
      timestamp: new Date(event.timestamp).toISOString(),
      recursionLevel: event.state.meta.recursionLevel,
      entityType: event.state.meta.entityType,
      crystallization: event.state.crystallization.progress.toFixed(1),
      corrections: event.state.corrections.current.toFixed(1),
      deltaOmega: event.deltaOmega.toFixed(1),
      hazards: event.state.hazards.activeCount,
      urgency: event.controlPolicy?.urgency || 'none',
      loopType: event.controlPolicy?.loopType || 'none',
      actions: event.controlPolicy?.actions.length || 0,
    };

    const logLine = JSON.stringify(logEntry);
    logs.push(logLine);
    console.log('📊 Fusion Update:', logEntry);
  });

  // Fetch current repository data
  console.log('📡 Fetching repository data...');
  const data = {
    commits: await apiFetcher.fetchCommits(REPO_OWNER, REPO_NAME, 50),
    issues: await apiFetcher.fetchIssues(REPO_OWNER, REPO_NAME),
    workflow_runs: await apiFetcher.fetchWorkflowRuns(REPO_OWNER, REPO_NAME, 20),
    code_scanning_alerts: await apiFetcher.fetchCodeScanningAlerts(REPO_OWNER, REPO_NAME),
    deployments: await apiFetcher.fetchDeployments(REPO_OWNER, REPO_NAME, 10),
    pull_requests: await apiFetcher.fetchPullRequests(REPO_OWNER, REPO_NAME),
  };

  console.log(`  ✓ ${data.commits.length} commits`);
  console.log(`  ✓ ${data.issues.length} issues`);
  console.log(`  ✓ ${data.workflow_runs.length} workflow runs`);
  console.log(`  ✓ ${data.code_scanning_alerts.length} code scanning alerts`);
  console.log(`  ✓ ${data.deployments.length} deployments`);
  console.log(`  ✓ ${data.pull_requests.length} pull requests`);
  console.log('');

  // Process through cognitive engine
  console.log('🔮 Processing through cognitive engine...');
  const event = await engine.processGitHubData(data);

  console.log('');
  console.log('📈 Results:');
  console.log(`  Recursion Level: ${event.state.meta.recursionLevel}`);
  console.log(`  Entity Type: ${event.state.meta.entityType}`);
  console.log(`  Crystallization: ${event.state.crystallization.progress.toFixed(1)}%`);
  console.log(`  Correction Rate: ${event.state.corrections.current.toFixed(1)}`);
  console.log(`  Divine Gap (ΔΩ): ${event.deltaOmega.toFixed(1)}`);
  console.log(`  Hazards: ${event.state.hazards.activeCount} (${event.state.hazards.severity})`);
  console.log(`  Urgency: ${event.controlPolicy?.urgency || 'none'}`);
  console.log(`  Loop Type: ${event.controlPolicy?.loopType || 'none'}`);

  if (event.controlPolicy && event.controlPolicy.actions.length > 0) {
    console.log('');
    console.log('🎬 Actions:');
    event.controlPolicy.actions.forEach((action, i) => {
      console.log(`  ${i + 1}. ${action.type}`);
    });
  }

  // Write logs to file
  fs.writeFileSync(logFile, logs.join('\n'));
  console.log('');
  console.log(`✅ Complete! Logs written to ${logFile}`);

  // Get engine stats
  const stats = engine.getStats();
  console.log('');
  console.log('📊 Engine Statistics:');
  console.log(`  Buffer: ${stats.bufferStats.size}/${stats.bufferStats.capacity} states`);
  console.log(`  Predictions: ${stats.predictionsCount} time horizons`);
}

// Run and handle errors
run().catch((error) => {
  console.error('❌ Error:', error);
  process.exit(1);
});
