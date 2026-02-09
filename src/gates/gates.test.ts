/**
 * Tests for Zero Trust Gate and Threshold Router
 */

import { ZeroTrustGate, getZeroTrustGate } from '../gates/zero-trust';
import { ThresholdRouter, getThresholdRouter } from '../gates/threshold-router';

describe('ZeroTrustGate', () => {
  let gate: ZeroTrustGate;

  beforeEach(() => {
    gate = new ZeroTrustGate();
  });

  describe('validateGate', () => {
    it('should deny access without token', () => {
      const result = gate.validateGate('archive', null, {
        cell: 'archive',
        timestamp: Date.now(),
      });

      expect(result.allowed).toBe(false);
      expect(result.reason).toContain('Missing authentication token');
    });

    it('should deny access with invalid token', () => {
      const result = gate.validateGate('archive', 'invalid-token', {
        cell: 'archive',
        timestamp: Date.now(),
      });

      expect(result.allowed).toBe(false);
      expect(result.reason).toContain('Invalid or expired JWT');
    });

    it('should allow access with valid token', () => {
      // Create a mock JWT (base64 encoded header.payload.signature)
      const header = btoa(JSON.stringify({ alg: 'HS256', typ: 'JWT' }));
      const payload = btoa(JSON.stringify({
        sub: 'test-user',
        exp: Math.floor(Date.now() / 1000) + 3600, // 1 hour from now
      }));
      const signature = 'mock-signature';
      const token = `${header}.${payload}.${signature}`;

      const result = gate.validateGate('archive', token, {
        cell: 'archive',
        timestamp: Date.now(),
      });

      expect(result.allowed).toBe(true);
      expect(result.reason).toBe('Access granted');
    });

    it('should enforce rate limiting', () => {
      const header = btoa(JSON.stringify({ alg: 'HS256', typ: 'JWT' }));
      const payload = btoa(JSON.stringify({
        sub: 'test-user',
        exp: Math.floor(Date.now() / 1000) + 3600,
      }));
      const token = `${header}.${payload}.signature`;

      // Make requests up to the limit
      for (let i = 0; i < 100; i++) {
        gate.validateGate('archive', token, {
          cell: 'archive',
          timestamp: Date.now(),
        });
      }

      // Next request should be throttled
      const result = gate.validateGate('archive', token, {
        cell: 'archive',
        timestamp: Date.now(),
      });

      expect(result.allowed).toBe(false);
      expect(result.reason).toContain('Rate limit exceeded');
      expect(result.throttled).toBe(true);
    });
  });

  describe('detectAnomaly', () => {
    it('should detect request rate anomaly', () => {
      const result = gate.detectAnomaly({
        cell: 'revenue',
        requestRate: 300,
        historicalAverage: 100,
        errorRate: 0.01,
        latency: 100,
        timestamp: Date.now(),
      });

      expect(result.isAnomaly).toBe(true);
      expect(result.action).toBe('throttle');
      expect(result.metrics?.requestRateMultiplier).toBeGreaterThan(2);
    });

    it('should detect error rate anomaly', () => {
      const result = gate.detectAnomaly({
        cell: 'revenue',
        requestRate: 100,
        historicalAverage: 100,
        errorRate: 0.15, // 15% error rate
        latency: 100,
        timestamp: Date.now(),
      });

      expect(result.isAnomaly).toBe(true);
      expect(result.severity).toBeGreaterThan(40);
    });

    it('should trigger lockdown for severe anomalies', () => {
      const result = gate.detectAnomaly({
        cell: 'revenue',
        requestRate: 1000,
        historicalAverage: 100,
        errorRate: 0.25,
        latency: 100,
        timestamp: Date.now(),
      });

      expect(result.isAnomaly).toBe(true);
      expect(result.action).toBe('lockdown');
      expect(result.severity).toBeGreaterThan(75);
    });
  });

  describe('autoLockdown', () => {
    it('should lockdown a cell', async () => {
      await gate.autoLockdown('revenue', 'High anomaly detected');

      const header = btoa(JSON.stringify({ alg: 'HS256', typ: 'JWT' }));
      const payload = btoa(JSON.stringify({
        sub: 'test-user',
        exp: Math.floor(Date.now() / 1000) + 3600,
      }));
      const token = `${header}.${payload}.signature`;

      const result = gate.validateGate('revenue', token, {
        cell: 'revenue',
        timestamp: Date.now(),
      });

      expect(result.allowed).toBe(false);
      expect(result.reason).toContain('lockdown');
    });
  });
});

describe('ThresholdRouter', () => {
  let router: ThresholdRouter;

  beforeEach(() => {
    router = new ThresholdRouter();
    router.clearMetrics();
  });

  describe('routeRequest', () => {
    it('should route through available path', async () => {
      const result = await router.routeRequest('wealth', { test: true });

      expect(result.threshold).toBe('wealth');
      expect(result.success).toBe(true);
      expect(['primary', 'secondary', 'local']).toContain(result.status);
    });

    it('should eventually fall back to local route', async () => {
      // Make multiple requests - eventually should hit local fallback
      const results = [];
      for (let i = 0; i < 20; i++) {
        const result = await router.routeRequest('info', { test: true });
        results.push(result);
      }

      const localResults = results.filter(r => r.status === 'local');
      expect(localResults.length).toBeGreaterThan(0);
    });
  });

  describe('getNavVelocity', () => {
    it('should calculate navigation velocity', async () => {
      // Generate some traffic
      for (let i = 0; i < 10; i++) {
        await router.routeRequest('wealth', { test: true });
      }

      const velocity = router.getNavVelocity();

      expect(velocity.successRate).toBeGreaterThan(0);
      expect(velocity.successRate).toBeLessThanOrEqual(1);
      expect(velocity.pathSwitchesPerWeek).toBeGreaterThanOrEqual(0);
    });
  });

  describe('checkRouteHealth', () => {
    it('should assess route health', async () => {
      // Generate traffic
      for (let i = 0; i < 5; i++) {
        await router.routeRequest('myth', { test: true });
      }

      const health = router.checkRouteHealth('myth');

      expect(health.healthy).toBe(true);
      expect(['primary', 'secondary', 'local']).toContain(health.activeRoute);
      expect(health.message).toBeTruthy();
    });
  });

  describe('getThresholdMetrics', () => {
    it('should return metrics for a threshold', async () => {
      await router.routeRequest('wealth', { test: true });

      const metrics = router.getThresholdMetrics('wealth');

      expect(metrics).toHaveProperty('primary');
      expect(metrics).toHaveProperty('secondary');
      expect(metrics).toHaveProperty('local');
    });
  });
});

describe('Singleton instances', () => {
  it('should return same ZeroTrustGate instance', () => {
    const gate1 = getZeroTrustGate();
    const gate2 = getZeroTrustGate();
    expect(gate1).toBe(gate2);
  });

  it('should return same ThresholdRouter instance', () => {
    const router1 = getThresholdRouter();
    const router2 = getThresholdRouter();
    expect(router1).toBe(router2);
  });
});
