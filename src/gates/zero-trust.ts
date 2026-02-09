/**
 * EVEZ666 Threshold Navigation Mesh - Zero Trust Gate
 * Zero-trust ingress controller with JWT validation and anomaly detection
 */

'use strict';

export type CellType = 'archive' | 'revenue' | 'persona' | 'router';
export type AnomalyAction = 'warn' | 'throttle' | 'lockdown';

/**
 * Gate validation context
 */
export interface GateContext {
  cell: CellType;
  requestRate?: number;
  historicalAverage?: number;
  timestamp: number;
  metadata?: Record<string, any>;
}

/**
 * Gate validation result
 */
export interface GateValidationResult {
  allowed: boolean;
  reason: string;
  throttled?: boolean;
}

/**
 * Anomaly detection result
 */
export interface AnomalyDetectionResult {
  isAnomaly: boolean;
  severity: number; // 0-100 scale
  action: AnomalyAction;
  metrics?: {
    requestRateMultiplier: number;
    deviation: number;
  };
}

/**
 * Flow metrics for anomaly detection
 */
export interface FlowMetrics {
  cell: CellType;
  requestRate: number;
  historicalAverage: number;
  errorRate: number;
  latency: number;
  timestamp: number;
}

/**
 * Rate limiter state
 */
interface RateLimitState {
  requests: number[];
  windowStart: number;
}

/**
 * Zero-trust gate controller
 */
export class ZeroTrustGate {
  private rateLimits: Map<string, RateLimitState> = new Map();
  private readonly RATE_WINDOW_MS = 60000; // 1 minute
  private readonly DEFAULT_RATE_LIMIT = 100; // requests per minute
  private readonly ANOMALY_THRESHOLD = 3.0; // 3x normal rate

  constructor() {}

  /**
   * Validate gate access with JWT and context
   */
  validateGate(
    cell: CellType,
    token: string | null,
    _context: GateContext
  ): GateValidationResult {
    // JWT validation
    if (!token) {
      return {
        allowed: false,
        reason: 'Missing authentication token',
      };
    }

    if (!this.validateJWT(token)) {
      return {
        allowed: false,
        reason: 'Invalid or expired JWT token',
      };
    }

    // Check rate limiting
    const rateLimitKey = `${cell}:${this.extractSubject(token)}`;
    if (!this.checkRateLimit(rateLimitKey)) {
      return {
        allowed: false,
        reason: 'Rate limit exceeded',
        throttled: true,
      };
    }

    // Check for lockdown state
    if (this.isLockedDown(cell)) {
      return {
        allowed: false,
        reason: 'Cell is in lockdown mode',
      };
    }

    return {
      allowed: true,
      reason: 'Access granted',
    };
  }

  /**
   * Detect anomalies in flow metrics
   */
  detectAnomaly(flowMetrics: FlowMetrics): AnomalyDetectionResult {
    const { requestRate, historicalAverage, errorRate } = flowMetrics;

    // Calculate request rate multiplier
    const multiplier = historicalAverage > 0
      ? requestRate / historicalAverage
      : 1.0;

    // Calculate deviation score
    const deviation = Math.abs(requestRate - historicalAverage);
    const normalizedDeviation = historicalAverage > 0
      ? deviation / historicalAverage
      : 0;

    // Check for anomaly conditions
    const isRateAnomaly = multiplier > this.ANOMALY_THRESHOLD;
    const isErrorAnomaly = errorRate > 0.1; // 10% error rate
    const isAnomaly = isRateAnomaly || isErrorAnomaly;

    // Calculate severity (0-100)
    let severity = 0;
    if (isRateAnomaly) {
      severity += Math.min(50, multiplier * 10);
    }
    if (isErrorAnomaly) {
      severity += Math.min(50, errorRate * 100);
    }
    severity = Math.min(100, severity);

    // Determine action
    let action: AnomalyAction = 'warn';
    if (severity > 75) {
      action = 'lockdown';
    } else if (severity > 40) {
      action = 'throttle';
    }

    return {
      isAnomaly,
      severity,
      action,
      metrics: {
        requestRateMultiplier: multiplier,
        deviation: normalizedDeviation,
      },
    };
  }

  /**
   * Execute auto-lockdown for compromised cell
   */
  async autoLockdown(cell: CellType, reason: string): Promise<void> {
    console.warn(`[ZeroTrust] Auto-lockdown initiated for cell: ${cell}, reason: ${reason}`);
    
    // In a real implementation, this would:
    // 1. Set lockdown flag in persistent storage
    // 2. Notify monitoring systems
    // 3. Isolate the cell from other cells
    // 4. Continue operations in other cells
    
    // For now, we'll just log it
    const lockdownState = {
      cell,
      reason,
      timestamp: Date.now(),
      active: true,
    };
    
    // Store in memory (in production, use persistent storage)
    this.lockdownStates.set(cell, lockdownState);
  }

  /**
   * Release lockdown for a cell
   */
  async releaseLockdown(cell: CellType): Promise<void> {
    console.log(`[ZeroTrust] Releasing lockdown for cell: ${cell}`);
    this.lockdownStates.delete(cell);
  }

  /**
   * Check if cell is in lockdown
   */
  private isLockedDown(cell: CellType): boolean {
    return this.lockdownStates.has(cell);
  }

  private lockdownStates: Map<CellType, any> = new Map();

  /**
   * Validate JWT token (simplified implementation)
   */
  private validateJWT(token: string): boolean {
    try {
      // Basic format check
      const parts = token.split('.');
      if (parts.length !== 3) {
        return false;
      }

      // Decode payload
      const payload = JSON.parse(atob(parts[1]));

      // Check expiration
      if (payload.exp && Date.now() >= payload.exp * 1000) {
        return false;
      }

      return true;
    } catch (error) {
      return false;
    }
  }

  /**
   * Extract subject from JWT
   */
  private extractSubject(token: string): string {
    try {
      const parts = token.split('.');
      const payload = JSON.parse(atob(parts[1]));
      return payload.sub || 'anonymous';
    } catch (error) {
      return 'anonymous';
    }
  }

  /**
   * Check rate limit for a key
   */
  private checkRateLimit(key: string): boolean {
    const now = Date.now();
    let state = this.rateLimits.get(key);

    if (!state) {
      state = {
        requests: [],
        windowStart: now,
      };
      this.rateLimits.set(key, state);
    }

    // Clean old requests outside the window
    state.requests = state.requests.filter(
      (timestamp) => now - timestamp < this.RATE_WINDOW_MS
    );

    // Check if under limit
    if (state.requests.length >= this.DEFAULT_RATE_LIMIT) {
      return false;
    }

    // Add current request
    state.requests.push(now);
    return true;
  }

  /**
   * Get current rate limit status for a cell
   */
  getRateLimitStatus(cell: CellType, subject: string): {
    requests: number;
    limit: number;
    remaining: number;
  } {
    const key = `${cell}:${subject}`;
    const state = this.rateLimits.get(key);
    const requests = state ? state.requests.length : 0;

    return {
      requests,
      limit: this.DEFAULT_RATE_LIMIT,
      remaining: Math.max(0, this.DEFAULT_RATE_LIMIT - requests),
    };
  }

  /**
   * Clear rate limit state (for testing)
   */
  clearRateLimits(): void {
    this.rateLimits.clear();
  }
}

// Singleton instance
let gateInstance: ZeroTrustGate | null = null;

/**
 * Get or create zero trust gate instance
 */
export function getZeroTrustGate(): ZeroTrustGate {
  if (!gateInstance) {
    gateInstance = new ZeroTrustGate();
  }
  return gateInstance;
}
