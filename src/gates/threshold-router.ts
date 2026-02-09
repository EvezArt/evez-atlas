/**
 * EVEZ666 Threshold Navigation Mesh - Threshold Router
 * Multi-route navigation with failover logic
 */

'use strict';

export type ThresholdType = 'wealth' | 'info' | 'myth';
export type RouteStatus = 'primary' | 'secondary' | 'local';

/**
 * Route definition
 */
export interface RouteDefinition {
  threshold: ThresholdType;
  primary: string;
  secondary: string;
  localFallback: boolean;
}

/**
 * Route result
 */
export interface RouteResult {
  threshold: ThresholdType;
  endpoint: string;
  status: RouteStatus;
  latency: number;
  success: boolean;
}

/**
 * Navigation velocity metrics
 */
export interface NavVelocity {
  pathSwitchesPerWeek: number;
  successRate: number;
  averageLatency: number;
  period: {
    start: number;
    end: number;
  };
}

/**
 * Path metrics
 */
interface PathMetrics {
  attempts: number;
  successes: number;
  failures: number;
  totalLatency: number;
  lastAttempt: number;
}

/**
 * Threshold router for multi-route navigation
 */
export class ThresholdRouter {
  private routes: Map<ThresholdType, RouteDefinition> = new Map();
  private pathMetrics: Map<string, PathMetrics> = new Map();
  private pathSwitches: Array<{ timestamp: number; from: string; to: string }> = [];

  constructor() {
    this.initializeRoutes();
  }

  /**
   * Initialize default routes for each threshold
   */
  private initializeRoutes(): void {
    // Wealth threshold routes
    this.routes.set('wealth', {
      threshold: 'wealth',
      primary: 'https://api.stripe.com/v1',
      secondary: 'https://api-backup.stripe.com/v1',
      localFallback: true,
    });

    // Info threshold routes
    this.routes.set('info', {
      threshold: 'info',
      primary: 'https://archive-api.evez666.com',
      secondary: 'https://archive-backup.evez666.com',
      localFallback: true,
    });

    // Myth threshold routes
    this.routes.set('myth', {
      threshold: 'myth',
      primary: 'https://persona-api.evez666.com',
      secondary: 'https://persona-backup.evez666.com',
      localFallback: true,
    });
  }

  /**
   * Route a request through the best available path
   */
  async routeRequest(
    threshold: ThresholdType,
    payload: any
  ): Promise<RouteResult> {
    const route = this.routes.get(threshold);
    if (!route) {
      throw new Error(`No route defined for threshold: ${threshold}`);
    }

    // Try primary route
    const primaryResult = await this.attemptRoute(
      threshold,
      route.primary,
      'primary',
      payload
    );
    if (primaryResult.success) {
      return primaryResult;
    }

    // Record path switch
    this.recordPathSwitch(route.primary, route.secondary);

    // Try secondary route
    const secondaryResult = await this.attemptRoute(
      threshold,
      route.secondary,
      'secondary',
      payload
    );
    if (secondaryResult.success) {
      return secondaryResult;
    }

    // Try local fallback if enabled
    if (route.localFallback) {
      this.recordPathSwitch(route.secondary, 'local');
      return this.attemptLocalRoute(threshold, payload);
    }

    // All routes failed
    throw new Error(`All routes failed for threshold: ${threshold}`);
  }

  /**
   * Attempt a route
   */
  private async attemptRoute(
    threshold: ThresholdType,
    endpoint: string,
    status: RouteStatus,
    payload: any
  ): Promise<RouteResult> {
    const startTime = Date.now();
    const metricsKey = `${threshold}:${status}`;

    try {
      // Simulate network request (in production, use actual fetch)
      await this.simulateRequest(endpoint);

      const latency = Date.now() - startTime;
      this.recordMetrics(metricsKey, true, latency);

      return {
        threshold,
        endpoint,
        status,
        latency,
        success: true,
      };
    } catch (error) {
      const latency = Date.now() - startTime;
      this.recordMetrics(metricsKey, false, latency);

      return {
        threshold,
        endpoint,
        status,
        latency,
        success: false,
      };
    }
  }

  /**
   * Attempt local fallback route
   */
  private async attemptLocalRoute(
    threshold: ThresholdType,
    payload: any
  ): Promise<RouteResult> {
    const startTime = Date.now();
    const metricsKey = `${threshold}:local`;

    // Local routes always succeed (offline-first)
    const latency = Date.now() - startTime;
    this.recordMetrics(metricsKey, true, latency);

    return {
      threshold,
      endpoint: 'local',
      status: 'local',
      latency,
      success: true,
    };
  }

  /**
   * Simulate network request (placeholder)
   */
  private async simulateRequest(endpoint: string): Promise<void> {
    // In production, use: await fetch(endpoint, { method: 'POST', body: JSON.stringify(payload) })
    // For now, simulate with a timeout
    return new Promise((resolve, reject) => {
      // Simulate 90% success rate for primary/secondary, 100% for local
      const shouldSucceed = Math.random() > 0.1 || endpoint === 'local';
      const delay = Math.random() * 100 + 50; // 50-150ms

      setTimeout(() => {
        if (shouldSucceed) {
          resolve();
        } else {
          reject(new Error('Simulated network failure'));
        }
      }, delay);
    });
  }

  /**
   * Record path metrics
   */
  private recordMetrics(key: string, success: boolean, latency: number): void {
    let metrics = this.pathMetrics.get(key);
    if (!metrics) {
      metrics = {
        attempts: 0,
        successes: 0,
        failures: 0,
        totalLatency: 0,
        lastAttempt: 0,
      };
      this.pathMetrics.set(key, metrics);
    }

    metrics.attempts++;
    if (success) {
      metrics.successes++;
    } else {
      metrics.failures++;
    }
    metrics.totalLatency += latency;
    metrics.lastAttempt = Date.now();
  }

  /**
   * Record path switch
   */
  private recordPathSwitch(from: string, to: string): void {
    this.pathSwitches.push({
      timestamp: Date.now(),
      from,
      to,
    });

    // Keep only last 1000 switches
    if (this.pathSwitches.length > 1000) {
      this.pathSwitches = this.pathSwitches.slice(-1000);
    }
  }

  /**
   * Get navigation velocity metrics
   */
  getNavVelocity(): NavVelocity {
    const now = Date.now();
    const oneWeekAgo = now - 7 * 24 * 60 * 60 * 1000;

    // Filter switches in the last week
    const recentSwitches = this.pathSwitches.filter(
      (sw) => sw.timestamp >= oneWeekAgo
    );

    // Calculate success rate across all paths
    let totalAttempts = 0;
    let totalSuccesses = 0;
    let totalLatency = 0;

    for (const metrics of this.pathMetrics.values()) {
      totalAttempts += metrics.attempts;
      totalSuccesses += metrics.successes;
      totalLatency += metrics.totalLatency;
    }

    const successRate = totalAttempts > 0
      ? totalSuccesses / totalAttempts
      : 1.0;

    const averageLatency = totalSuccesses > 0
      ? totalLatency / totalSuccesses
      : 0;

    return {
      pathSwitchesPerWeek: recentSwitches.length,
      successRate,
      averageLatency,
      period: {
        start: oneWeekAgo,
        end: now,
      },
    };
  }

  /**
   * Get metrics for a specific threshold
   */
  getThresholdMetrics(threshold: ThresholdType): {
    primary: PathMetrics | null;
    secondary: PathMetrics | null;
    local: PathMetrics | null;
  } {
    return {
      primary: this.pathMetrics.get(`${threshold}:primary`) || null,
      secondary: this.pathMetrics.get(`${threshold}:secondary`) || null,
      local: this.pathMetrics.get(`${threshold}:local`) || null,
    };
  }

  /**
   * Check route health
   */
  checkRouteHealth(threshold: ThresholdType): {
    healthy: boolean;
    activeRoute: RouteStatus;
    message: string;
  } {
    const metrics = this.getThresholdMetrics(threshold);

    // Check primary health
    if (metrics.primary && metrics.primary.successes > 0) {
      const successRate = metrics.primary.successes / metrics.primary.attempts;
      if (successRate > 0.8) {
        return {
          healthy: true,
          activeRoute: 'primary',
          message: 'Primary route healthy',
        };
      }
    }

    // Check secondary health
    if (metrics.secondary && metrics.secondary.successes > 0) {
      const successRate = metrics.secondary.successes / metrics.secondary.attempts;
      if (successRate > 0.8) {
        return {
          healthy: true,
          activeRoute: 'secondary',
          message: 'Secondary route active (primary degraded)',
        };
      }
    }

    // Fall back to local
    return {
      healthy: true,
      activeRoute: 'local',
      message: 'Local-only mode (all remote routes unavailable)',
    };
  }

  /**
   * Clear metrics (for testing)
   */
  clearMetrics(): void {
    this.pathMetrics.clear();
    this.pathSwitches = [];
  }
}

// Singleton instance
let routerInstance: ThresholdRouter | null = null;

/**
 * Get or create threshold router instance
 */
export function getThresholdRouter(): ThresholdRouter {
  if (!routerInstance) {
    routerInstance = new ThresholdRouter();
  }
  return routerInstance;
}
