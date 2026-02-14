/**
 * GitHub Event to LORD Fusion State Transformer
 * 
 * Maps GitHub repository metrics and events to LORD consciousness metrics
 */

import {
  FusionState,
  EntityType,
  computeCorrectionRate,
  computeDivineOptimum,
  computeDivineGap,
} from './lord-protocol';

/**
 * GitHub repository metrics snapshot
 */
export interface GitHubMetrics {
  commits: {
    recentCount: number;           // Commits in last 24 hours
    frequency: number;             // Commits per day (7-day average)
  };
  issues: {
    openCount: number;
    closedCount: number;
    entropy: number;               // Diversity of issue types
  };
  ci: {
    totalRuns: number;
    failureCount: number;
    errorRate: number;            // failure / total
  };
  codeql: {
    alertCount: number;
    criticalCount: number;
  };
  deployments: {
    successCount: number;
    rollbackCount: number;
    stability: number;            // success / (success + rollback)
  };
  pullRequests: {
    openCount: number;
    mergedCount: number;
    velocity: number;             // PRs merged per week
  };
}

/**
 * Transform GitHub metrics into recursion level (1-20 scale)
 * 
 * Higher recursion = more complex/active development:
 * - High commit frequency
 * - High issue entropy (diverse concerns)
 * - Multiple abstraction layers visible in PRs
 */
export function computeRecursionLevel(metrics: GitHubMetrics): number {
  // Base level from commit frequency (0-8 points)
  const commitScore = Math.min(8, metrics.commits.frequency / 2);
  
  // Issue complexity (0-6 points)
  const issueScore = Math.min(6, metrics.issues.entropy * 2);
  
  // PR velocity indicates abstraction layers (0-4 points)
  const prScore = Math.min(4, metrics.pullRequests.velocity / 3);
  
  // Open issues suggest ongoing recursion (0-2 points)
  const openIssueScore = Math.min(2, metrics.issues.openCount / 10);
  
  const total = commitScore + issueScore + prScore + openIssueScore;
  
  // Scale to 1-20, with minimum of 1
  return Math.max(1, Math.min(20, Math.round(total)));
}

/**
 * Compute correction rate C(R) from CI errors and CodeQL findings
 * 
 * More errors = higher correction rate (system is actively fixing issues)
 */
export function computeCorrectionsFromCI(metrics: GitHubMetrics): number {
  // Base correction from CI failures
  const ciCorrections = metrics.ci.errorRate * 50; // 0-50 points
  
  // CodeQL findings require corrections
  const codeqlCorrections = Math.min(30, metrics.codeql.alertCount * 2); // 0-30 points
  
  // Active fixing (closed issues) shows corrections happening
  const fixingCorrections = Math.min(20, metrics.issues.closedCount / 5); // 0-20 points
  
  return Math.min(100, ciCorrections + codeqlCorrections + fixingCorrections);
}

/**
 * Compute crystallization progress from deployment stability
 * 
 * High crystallization = stable, well-formed code
 */
export function computeCrystallization(metrics: GitHubMetrics): {
  progress: number;
  velocity: number;
} {
  // Base progress from deployment stability
  let progress = metrics.deployments.stability * 100;
  
  // Reduce progress if there are open CodeQL alerts
  if (metrics.codeql.alertCount > 0) {
    progress *= 0.8;
  }
  
  // High CI error rate indicates low crystallization
  if (metrics.ci.errorRate > 0.3) {
    progress *= 0.7;
  }
  
  // Velocity is PR merge rate (normalized)
  const velocity = Math.min(10, metrics.pullRequests.velocity);
  
  return {
    progress: Math.max(0, Math.min(100, progress)),
    velocity,
  };
}

/**
 * Determine entity type based on automation level
 */
export function determineEntityType(metrics: GitHubMetrics): EntityType {
  // High automation + low human commit patterns = synthetic
  const automationRatio = metrics.ci.totalRuns / Math.max(1, metrics.commits.recentCount);
  
  if (automationRatio > 5) {
    return 'synthetic';  // Mostly automated
  } else if (automationRatio > 2) {
    return 'hybrid';     // Mixed human and automation
  } else {
    return 'human';      // Primarily human-driven
  }
}

/**
 * Compute hazard metrics from security and stability indicators
 */
export function computeHazards(metrics: GitHubMetrics): {
  activeCount: number;
  severity: 'low' | 'medium' | 'high' | 'critical';
} {
  let activeCount = 0;
  
  // Count hazards
  if (metrics.ci.errorRate > 0.5) activeCount++;
  if (metrics.codeql.alertCount > 0) activeCount += metrics.codeql.alertCount;
  if (metrics.codeql.criticalCount > 0) activeCount += metrics.codeql.criticalCount * 2;
  if (metrics.deployments.stability < 0.7) activeCount++;
  
  // Determine severity
  let severity: 'low' | 'medium' | 'high' | 'critical' = 'low';
  
  if (metrics.codeql.criticalCount > 0) {
    severity = 'critical';
  } else if (activeCount > 5 || metrics.ci.errorRate > 0.7) {
    severity = 'high';
  } else if (activeCount > 2 || metrics.codeql.alertCount > 3) {
    severity = 'medium';
  }
  
  return { activeCount, severity };
}

/**
 * Main transformer: GitHub metrics → LORD fusion state
 */
export function transformToFusionState(metrics: GitHubMetrics): FusionState {
  const recursionLevel = computeRecursionLevel(metrics);
  const entityType = determineEntityType(metrics);
  const crystallization = computeCrystallization(metrics);
  const hazards = computeHazards(metrics);
  
  // Current correction rate from CI/CodeQL
  const current = computeCorrectionsFromCI(metrics);
  
  return {
    meta: {
      recursionLevel,
      entityType,
      timestamp: Date.now(),
    },
    crystallization,
    corrections: {
      current,
      history: [], // Will be populated by the continuous loop
    },
    hazards,
  };
}

/**
 * Extract GitHub metrics from GitHub API responses
 */
export interface GitHubRepositoryData {
  commits?: any[];
  issues?: any[];
  workflow_runs?: any[];
  code_scanning_alerts?: any[];
  deployments?: any[];
  pull_requests?: any[];
}

/**
 * Compute metrics from raw GitHub API data
 */
export function extractMetricsFromGitHubData(data: GitHubRepositoryData): GitHubMetrics {
  // Analyze commits
  const now = Date.now();
  const dayMs = 24 * 60 * 60 * 1000;
  const commits = data.commits || [];
  
  const recentCommits = commits.filter((c: any) => {
    const commitDate = new Date(c.commit?.author?.date || c.commit?.committer?.date).getTime();
    return (now - commitDate) < dayMs;
  });
  
  // Calculate 7-day average
  const weekCommits = commits.filter((c: any) => {
    const commitDate = new Date(c.commit?.author?.date || c.commit?.committer?.date).getTime();
    return (now - commitDate) < (7 * dayMs);
  });
  const frequency = weekCommits.length / 7;
  
  // Analyze issues
  const issues = data.issues || [];
  const openIssues = issues.filter((i: any) => i.state === 'open');
  const closedIssues = issues.filter((i: any) => i.state === 'closed');
  
  // Issue entropy: diversity of labels
  const labelSet = new Set();
  issues.forEach((i: any) => {
    (i.labels || []).forEach((l: any) => labelSet.add(l.name));
  });
  const entropy = Math.min(5, labelSet.size / 2); // Normalize to 0-5
  
  // Analyze CI runs
  const workflowRuns = data.workflow_runs || [];
  const recentRuns = workflowRuns.slice(0, 20); // Last 20 runs
  const failures = recentRuns.filter((r: any) => r.conclusion === 'failure').length;
  const errorRate = recentRuns.length > 0 ? failures / recentRuns.length : 0;
  
  // Analyze CodeQL alerts
  const codeqlAlerts = data.code_scanning_alerts || [];
  const openAlerts = codeqlAlerts.filter((a: any) => a.state === 'open');
  const criticalAlerts = openAlerts.filter((a: any) => 
    a.rule?.security_severity_level === 'critical' || a.rule?.severity === 'error'
  );
  
  // Analyze deployments
  const deployments = data.deployments || [];
  const recentDeployments = deployments.slice(0, 10);
  const successfulDeployments = recentDeployments.filter((d: any) => d.state === 'success').length;
  const failedDeployments = recentDeployments.filter((d: any) => d.state === 'failure').length;
  const stability = recentDeployments.length > 0 
    ? successfulDeployments / recentDeployments.length 
    : 1.0;
  
  // Analyze PRs
  const pullRequests = data.pull_requests || [];
  const mergedPRs = pullRequests.filter((pr: any) => pr.merged_at);
  const weekPRs = mergedPRs.filter((pr: any) => {
    const mergedDate = new Date(pr.merged_at).getTime();
    return (now - mergedDate) < (7 * dayMs);
  });
  const prVelocity = weekPRs.length / 7;
  
  return {
    commits: {
      recentCount: recentCommits.length,
      frequency,
    },
    issues: {
      openCount: openIssues.length,
      closedCount: closedIssues.length,
      entropy,
    },
    ci: {
      totalRuns: recentRuns.length,
      failureCount: failures,
      errorRate,
    },
    codeql: {
      alertCount: openAlerts.length,
      criticalCount: criticalAlerts.length,
    },
    deployments: {
      successCount: successfulDeployments,
      rollbackCount: failedDeployments,
      stability,
    },
    pullRequests: {
      openCount: pullRequests.filter((pr: any) => pr.state === 'open').length,
      mergedCount: mergedPRs.length,
      velocity: prVelocity,
    },
  };
}
