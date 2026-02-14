#!/usr/bin/env node
/**
 * LORD Dashboard Webhook Integration Server
 * Complete LORD Integration Guide - Chapter 18
 * 
 * Receives GitHub webhooks and updates LORD dashboard in real-time
 */

const express = require('express');
const crypto = require('crypto');
const WebSocket = require('ws');

const app = express();
app.use(express.json());

// Configuration
const PORT = process.env.WEBHOOK_PORT || 3002;
const WEBHOOK_SECRET = process.env.GITHUB_WEBHOOK_SECRET || 'your-secret-here';
const WS_PORT = process.env.WS_PORT || 3001;

// WebSocket server for real-time updates
const wss = new WebSocket.Server({ port: WS_PORT });

// Connected clients
const clients = new Set();

wss.on('connection', (ws) => {
  console.log('✅ New WebSocket client connected');
  clients.add(ws);
  
  ws.on('close', () => {
    clients.delete(ws);
    console.log('👋 Client disconnected');
  });
});

/**
 * Broadcast message to all connected clients
 */
function broadcast(message) {
  const data = JSON.stringify(message);
  clients.forEach(client => {
    if (client.readyState === WebSocket.OPEN) {
      client.send(data);
    }
  });
}

/**
 * Verify GitHub webhook signature
 */
function verifySignature(payload, signature) {
  const hmac = crypto.createHmac('sha256', WEBHOOK_SECRET);
  const digest = 'sha256=' + hmac.update(payload).digest('hex');
  return crypto.timingSafeEqual(
    Buffer.from(signature),
    Buffer.from(digest)
  );
}

/**
 * Process push event
 */
function handlePush(payload) {
  const { repository, commits, pusher, ref } = payload;
  
  const event = {
    type: 'push',
    timestamp: new Date().toISOString(),
    data: {
      repository: repository.full_name,
      branch: ref.replace('refs/heads/', ''),
      commits: commits.length,
      pusher: pusher.name,
      latest_commit: commits[commits.length - 1]?.message || 'No message'
    }
  };
  
  console.log(`📦 Push to ${event.data.repository}/${event.data.branch}`);
  broadcast(event);
}

/**
 * Process pull request event
 */
function handlePullRequest(payload) {
  const { action, pull_request, repository } = payload;
  
  const event = {
    type: 'pull_request',
    timestamp: new Date().toISOString(),
    data: {
      action,
      repository: repository.full_name,
      number: pull_request.number,
      title: pull_request.title,
      author: pull_request.user.login,
      state: pull_request.state
    }
  };
  
  console.log(`🔀 PR #${event.data.number} ${action} in ${event.data.repository}`);
  broadcast(event);
}

/**
 * Process issue event
 */
function handleIssue(payload) {
  const { action, issue, repository } = payload;
  
  const event = {
    type: 'issue',
    timestamp: new Date().toISOString(),
    data: {
      action,
      repository: repository.full_name,
      number: issue.number,
      title: issue.title,
      author: issue.user.login,
      state: issue.state
    }
  };
  
  console.log(`📋 Issue #${event.data.number} ${action} in ${event.data.repository}`);
  broadcast(event);
}

/**
 * Process workflow run event
 */
function handleWorkflowRun(payload) {
  const { action, workflow_run, repository } = payload;
  
  const event = {
    type: 'workflow_run',
    timestamp: new Date().toISOString(),
    data: {
      action,
      repository: repository.full_name,
      workflow: workflow_run.name,
      status: workflow_run.status,
      conclusion: workflow_run.conclusion,
      branch: workflow_run.head_branch
    }
  };
  
  console.log(`⚙️  Workflow ${event.data.workflow} ${action} (${event.data.status})`);
  broadcast(event);
}

/**
 * Main webhook endpoint
 */
app.post('/webhook', (req, res) => {
  // Verify signature
  const signature = req.headers['x-hub-signature-256'];
  const payload = JSON.stringify(req.body);
  
  if (!verifySignature(payload, signature)) {
    console.error('❌ Invalid webhook signature');
    return res.status(401).send('Invalid signature');
  }
  
  // Get event type
  const event = req.headers['x-github-event'];
  
  // Process event
  try {
    switch (event) {
      case 'push':
        handlePush(req.body);
        break;
      case 'pull_request':
        handlePullRequest(req.body);
        break;
      case 'issues':
        handleIssue(req.body);
        break;
      case 'workflow_run':
        handleWorkflowRun(req.body);
        break;
      default:
        console.log(`ℹ️  Unhandled event: ${event}`);
    }
    
    res.status(200).send('OK');
  } catch (error) {
    console.error('❌ Error processing webhook:', error);
    res.status(500).send('Internal error');
  }
});

/**
 * Health check endpoint
 */
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    webhook_server: 'running',
    websocket_clients: clients.size,
    uptime: process.uptime()
  });
});

/**
 * Start server
 */
app.listen(PORT, () => {
  console.log('🚀 LORD Webhook Integration Server');
  console.log('=' .repeat(60));
  console.log(`📡 Webhook endpoint: http://localhost:${PORT}/webhook`);
  console.log(`🔌 WebSocket server: ws://localhost:${WS_PORT}`);
  console.log(`🏥 Health check: http://localhost:${PORT}/health`);
  console.log('=' .repeat(60));
  console.log('✅ Server running and ready to receive webhooks');
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('👋 Shutting down gracefully...');
  wss.close();
  process.exit(0);
});
