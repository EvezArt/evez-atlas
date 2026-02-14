/**
 * GitHub Webhook Listener Service
 * 
 * Listens to GitHub webhooks and transforms events into LORD fusion states
 * Runs as a serverless function or persistent daemon
 */

import { CognitiveEngine } from './index';
import { GitHubRepositoryData } from './github-transformer';
import * as crypto from 'crypto';

/**
 * Webhook event types we care about
 */
export type WebhookEventType = 
  | 'push'
  | 'pull_request'
  | 'issues'
  | 'workflow_run'
  | 'code_scanning_alert'
  | 'deployment_status';

/**
 * Webhook payload (simplified)
 */
export interface WebhookPayload {
  action?: string;
  repository: {
    name: string;
    owner: { login: string };
  };
  [key: string]: any;
}

/**
 * GitHub API fetcher interface
 */
export interface GitHubAPIFetcher {
  fetchCommits(owner: string, repo: string, count?: number): Promise<any[]>;
  fetchIssues(owner: string, repo: string): Promise<any[]>;
  fetchWorkflowRuns(owner: string, repo: string, count?: number): Promise<any[]>;
  fetchCodeScanningAlerts(owner: string, repo: string): Promise<any[]>;
  fetchDeployments(owner: string, repo: string, count?: number): Promise<any[]>;
  fetchPullRequests(owner: string, repo: string): Promise<any[]>;
}

/**
 * Webhook handler that integrates with Cognitive Engine
 */
export class WebhookHandler {
  private engine: CognitiveEngine;
  private apiFetcher: GitHubAPIFetcher;
  
  constructor(engine: CognitiveEngine, apiFetcher: GitHubAPIFetcher) {
    this.engine = engine;
    this.apiFetcher = apiFetcher;
  }
  
  /**
   * Handle incoming webhook
   */
  async handleWebhook(eventType: WebhookEventType, payload: WebhookPayload): Promise<void> {
    console.log(`📥 Received webhook: ${eventType}`);
    
    const { repository } = payload;
    const owner = repository.owner.login;
    const repo = repository.name;
    
    // Fetch current repository state
    const data = await this.fetchRepositoryData(owner, repo);
    
    // Process through cognitive engine
    const event = await this.engine.processGitHubData(data);
    
    console.log(`✅ Processed webhook: R=${event.state.meta.recursionLevel}, ΔΩ=${event.deltaOmega.toFixed(1)}`);
  }
  
  /**
   * Fetch complete repository data for analysis
   */
  private async fetchRepositoryData(owner: string, repo: string): Promise<GitHubRepositoryData> {
    const [commits, issues, workflowRuns, codeAlerts, deployments, pullRequests] = await Promise.all([
      this.apiFetcher.fetchCommits(owner, repo, 50),
      this.apiFetcher.fetchIssues(owner, repo),
      this.apiFetcher.fetchWorkflowRuns(owner, repo, 20),
      this.apiFetcher.fetchCodeScanningAlerts(owner, repo),
      this.apiFetcher.fetchDeployments(owner, repo, 10),
      this.apiFetcher.fetchPullRequests(owner, repo),
    ]);
    
    return {
      commits,
      issues,
      workflow_runs: workflowRuns,
      code_scanning_alerts: codeAlerts,
      deployments,
      pull_requests: pullRequests,
    };
  }
}

/**
 * Express/HTTP server wrapper for webhook handler
 * 
 * Example usage with Express:
 * ```typescript
 * const app = express();
 * const server = createWebhookServer(engine, apiFetcher);
 * app.post('/webhook', server.getHandler());
 * ```
 */
export class WebhookServer {
  private webhookHandler: WebhookHandler;
  
  constructor(engine: CognitiveEngine, apiFetcher: GitHubAPIFetcher) {
    this.webhookHandler = new WebhookHandler(engine, apiFetcher);
  }
  
  /**
   * Express middleware handler
   */
  async handleRequest(req: any, res: any): Promise<void> {
    try {
      // Get event type from header
      const eventType = req.headers['x-github-event'] as WebhookEventType;
      
      if (!eventType) {
        res.status(400).json({ error: 'Missing X-GitHub-Event header' });
        return;
      }
      
      // Verify webhook signature if secret is configured
      const secret = process.env.GITHUB_WEBHOOK_SECRET;
      if (secret) {
        const signature = req.headers['x-hub-signature-256'];
        if (!signature || !this.verifySignature(req.body, signature as string, secret)) {
          res.status(401).json({ error: 'Invalid signature' });
          return;
        }
      }
      
      // Handle webhook
      await this.webhookHandler.handleWebhook(eventType, req.body);
      
      res.status(200).json({ success: true, message: 'Webhook processed' });
    } catch (error) {
      console.error('Error handling webhook:', error);
      res.status(500).json({ 
        error: 'Internal server error', 
        message: error instanceof Error ? error.message : String(error)
      });
    }
  }
  
  /**
   * Verify GitHub webhook signature using HMAC-SHA256
   */
  private verifySignature(payload: any, signature: string, secret: string): boolean {
    const hmac = crypto.createHmac('sha256', secret);
    const digest = 'sha256=' + hmac.update(JSON.stringify(payload)).digest('hex');
    return crypto.timingSafeEqual(Buffer.from(signature), Buffer.from(digest));
  }
  
  /**
   * Get handler function bound to this instance
   */
  getHandler() {
    return this.handleRequest.bind(this);
  }
}

/**
 * Create webhook server instance
 */
export function createWebhookServer(
  engine: CognitiveEngine,
  apiFetcher: GitHubAPIFetcher
): WebhookServer {
  return new WebhookServer(engine, apiFetcher);
}

/**
 * Polling-based alternative for environments without webhooks
 * 
 * Polls GitHub API periodically instead of waiting for webhooks
 */
export class PollingService {
  private engine: CognitiveEngine;
  private apiFetcher: GitHubAPIFetcher;
  private intervalId: NodeJS.Timeout | null = null;
  private owner: string;
  private repo: string;
  private pollInterval: number;
  
  constructor(
    engine: CognitiveEngine,
    apiFetcher: GitHubAPIFetcher,
    owner: string,
    repo: string,
    pollInterval: number = 60000 // Default: 1 minute
  ) {
    this.engine = engine;
    this.apiFetcher = apiFetcher;
    this.owner = owner;
    this.repo = repo;
    this.pollInterval = pollInterval;
  }
  
  /**
   * Start polling
   */
  start(): void {
    if (this.intervalId) {
      console.warn('Polling already started');
      return;
    }
    
    console.log(`🔄 Starting polling service (interval: ${this.pollInterval}ms)`);
    
    // Poll immediately
    this.poll();
    
    // Then poll at interval
    this.intervalId = setInterval(() => {
      this.poll();
    }, this.pollInterval);
  }
  
  /**
   * Stop polling
   */
  stop(): void {
    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = null;
      console.log('🛑 Polling service stopped');
    }
  }
  
  /**
   * Execute one poll cycle
   */
  private async poll(): Promise<void> {
    try {
      console.log(`📊 Polling ${this.owner}/${this.repo}...`);
      
      const data = await this.fetchRepositoryData();
      const event = await this.engine.processGitHubData(data);
      
      console.log(`✅ Poll complete: R=${event.state.meta.recursionLevel}, ΔΩ=${event.deltaOmega.toFixed(1)}`);
    } catch (error) {
      console.error('Error during poll:', error);
    }
  }
  
  /**
   * Fetch repository data
   */
  private async fetchRepositoryData(): Promise<GitHubRepositoryData> {
    const [commits, issues, workflowRuns, codeAlerts, deployments, pullRequests] = await Promise.all([
      this.apiFetcher.fetchCommits(this.owner, this.repo, 50),
      this.apiFetcher.fetchIssues(this.owner, this.repo),
      this.apiFetcher.fetchWorkflowRuns(this.owner, this.repo, 20),
      this.apiFetcher.fetchCodeScanningAlerts(this.owner, this.repo),
      this.apiFetcher.fetchDeployments(this.owner, this.repo, 10),
      this.apiFetcher.fetchPullRequests(this.owner, this.repo),
    ]);
    
    return {
      commits,
      issues,
      workflow_runs: workflowRuns,
      code_scanning_alerts: codeAlerts,
      deployments,
      pull_requests: pullRequests,
    };
  }
}

/**
 * Create polling service instance
 */
export function createPollingService(
  engine: CognitiveEngine,
  apiFetcher: GitHubAPIFetcher,
  owner: string,
  repo: string,
  pollInterval?: number
): PollingService {
  return new PollingService(engine, apiFetcher, owner, repo, pollInterval);
}
