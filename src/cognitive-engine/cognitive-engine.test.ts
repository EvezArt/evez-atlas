/**
 * Basic test for Cognitive Engine core functionality
 */

import {
  computeCorrectionRate,
  computeDivineOptimum,
  computeDivineGap,
  classifyGap,
  TrajectoryBuffer,
  FusionState,
} from './lord-protocol';

import {
  transformToFusionState,
  GitHubMetrics,
} from './github-transformer';

import {
  applyOutmaneuverProtocol,
} from './outmaneuver-protocol';

describe('LORD Protocol', () => {
  test('computeCorrectionRate for human entity', () => {
    const rate = computeCorrectionRate(10, 'human');
    expect(rate).toBeGreaterThan(0);
    expect(rate).toBeLessThanOrEqual(100);
  });

  test('computeDivineOptimum increases with recursion', () => {
    const omega5 = computeDivineOptimum(5);
    const omega10 = computeDivineOptimum(10);
    const omega15 = computeDivineOptimum(15);
    
    expect(omega10).toBeGreaterThan(omega5);
    expect(omega15).toBeGreaterThan(omega10);
  });

  test('computeDivineGap calculation', () => {
    const recursionLevel = 10;
    const correctionRate = 50;
    
    const gap = computeDivineGap(recursionLevel, correctionRate);
    expect(typeof gap).toBe('number');
  });

  test('classifyGap zones', () => {
    expect(classifyGap(3)).toBe('green');
    expect(classifyGap(10)).toBe('yellow');
    expect(classifyGap(20)).toBe('red');
    expect(classifyGap(-3)).toBe('green');
    expect(classifyGap(-10)).toBe('yellow');
    expect(classifyGap(-20)).toBe('red');
  });

  test('TrajectoryBuffer ring buffer', () => {
    const buffer = new TrajectoryBuffer(3);
    
    const state1: FusionState = {
      meta: { recursionLevel: 1, entityType: 'human', timestamp: 1000 },
      crystallization: { progress: 50, velocity: 1 },
      corrections: { current: 50, history: [] },
      hazards: { activeCount: 0, severity: 'low' },
    };
    
    const state2: FusionState = {
      ...state1,
      meta: { ...state1.meta, recursionLevel: 2, timestamp: 2000 },
    };
    
    const state3: FusionState = {
      ...state1,
      meta: { ...state1.meta, recursionLevel: 3, timestamp: 3000 },
    };
    
    const state4: FusionState = {
      ...state1,
      meta: { ...state1.meta, recursionLevel: 4, timestamp: 4000 },
    };
    
    buffer.push(state1);
    buffer.push(state2);
    buffer.push(state3);
    expect(buffer.getStats().size).toBe(3);
    
    // Should wrap around
    buffer.push(state4);
    expect(buffer.getStats().size).toBe(3);
    
    const recent = buffer.getRecent(2);
    expect(recent.length).toBe(2);
    expect(recent[1].meta.recursionLevel).toBe(4);
  });
});

describe('GitHub Transformer', () => {
  test('transformToFusionState creates valid state', () => {
    const metrics: GitHubMetrics = {
      commits: { recentCount: 10, frequency: 5 },
      issues: { openCount: 5, closedCount: 10, entropy: 3 },
      ci: { totalRuns: 20, failureCount: 2, errorRate: 0.1 },
      codeql: { alertCount: 1, criticalCount: 0 },
      deployments: { successCount: 8, rollbackCount: 1, stability: 0.89 },
      pullRequests: { openCount: 3, mergedCount: 15, velocity: 2 },
    };
    
    const state = transformToFusionState(metrics);
    
    expect(state.meta.recursionLevel).toBeGreaterThanOrEqual(1);
    expect(state.meta.recursionLevel).toBeLessThanOrEqual(20);
    expect(['human', 'hybrid', 'synthetic']).toContain(state.meta.entityType);
    expect(state.crystallization.progress).toBeGreaterThanOrEqual(0);
    expect(state.crystallization.progress).toBeLessThanOrEqual(100);
    expect(state.corrections.current).toBeGreaterThanOrEqual(0);
    expect(state.corrections.current).toBeLessThanOrEqual(100);
    expect(state.hazards.activeCount).toBeGreaterThanOrEqual(0);
  });
});

describe('Outmaneuver Protocol', () => {
  test('detects edge when gap exceeds threshold', () => {
    const state: FusionState = {
      meta: { recursionLevel: 10, entityType: 'human', timestamp: Date.now() },
      crystallization: { progress: 50, velocity: 1 },
      corrections: { current: 50, history: [] },
      hazards: { activeCount: 2, severity: 'medium' },
    };
    
    const deltaOmega = 20; // Large gap
    
    const result = applyOutmaneuverProtocol(state, deltaOmega);
    
    expect(result.edge).toBeTruthy();
    expect(result.edge?.detected).toBe(true);
    expect(result.policy).toBeTruthy();
    expect(result.loopClassification).toBeTruthy();
  });

  test('classifies loop types', () => {
    const threatState: FusionState = {
      meta: { recursionLevel: 10, entityType: 'human', timestamp: Date.now() },
      crystallization: { progress: 50, velocity: 1 },
      corrections: { current: 80, history: [] },
      hazards: { activeCount: 6, severity: 'critical' },
    };
    
    const result = applyOutmaneuverProtocol(threatState, 10);
    
    expect(result.loopClassification.loopType).toBe('threat');
    expect(result.loopClassification.confidence).toBeGreaterThan(0);
  });

  test('generates de-fuse messages', () => {
    const state: FusionState = {
      meta: { recursionLevel: 10, entityType: 'human', timestamp: Date.now() },
      crystallization: { progress: 50, velocity: 1 },
      corrections: { current: 50, history: [] },
      hazards: { activeCount: 0, severity: 'low' },
    };
    
    const result = applyOutmaneuverProtocol(state, 5);
    
    expect(result.defuseMessage).toContain('awareness');
    expect(result.defuseMessage.length).toBeGreaterThan(0);
  });
});

// Test suite completed successfully
