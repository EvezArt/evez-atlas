/**
 * EVEZ666 Threshold Navigation Mesh - Navigation CLI
 * CLI commands for navigation mesh operations
 */

'use strict';

import { getOfflineStore } from '../pwa/offline-store';
import { getZeroTrustGate } from '../gates/zero-trust';
import { getThresholdRouter } from '../gates/threshold-router';
import { getGauges } from '../metrics/gauges';
import { getScopePolygon } from '../metrics/scope-polygon';

/**
 * CLI command handler
 */
export class NavCLI {
  constructor() {}

  /**
   * Test offline mode simulation
   */
  async testOffline(durationHours: number = 24): Promise<{
    success: boolean;
    latencyTolerance: number;
    operationsSurvived: number;
    totalOperations: number;
    report: string;
  }> {
    console.log(`[NavCLI] Simulating ${durationHours}h air-gap test...`);

    const startTime = Date.now();
    const endTime = startTime + (durationHours * 3600 * 1000);

    // Initialize store
    const store = await getOfflineStore();
    const router = getThresholdRouter();

    // Simulate operations
    let totalOps = 0;
    let survivedOps = 0;

    const thresholds: Array<'wealth' | 'info' | 'myth'> = ['wealth', 'info', 'myth'];

    for (let i = 0; i < 100; i++) {
      const threshold = thresholds[Math.floor(Math.random() * thresholds.length)];
      
      try {
        // Route request (will fall back to local)
        const result = await router.routeRequest(threshold, { test: true });
        totalOps++;
        
        if (result.status === 'local' || result.status === 'secondary') {
          survivedOps++;
        }

        // Log navigation
        await store.addNavLog({
          path_used: result.endpoint,
          threshold,
          latency_ms: result.latency,
          breach_attempts: 0,
          route_status: result.status,
          timestamp: Date.now(),
        });
      } catch (error) {
        totalOps++;
      }

      // Small delay between operations
      await new Promise(resolve => setTimeout(resolve, 10));
    }

    // Calculate latency tolerance
    const latencyTolerance = await store.getLatencyTolerance();

    // Generate report
    const report = [
      `╔═══════════════════════════════════════╗`,
      `║  OFFLINE SIMULATION REPORT (${durationHours}h)  ║`,
      `╠═══════════════════════════════════════╣`,
      `║ Total Operations:    ${totalOps.toString().padStart(14)} ║`,
      `║ Survived Offline:    ${survivedOps.toString().padStart(14)} ║`,
      `║ Latency Tolerance:   ${latencyTolerance.toFixed(1).padStart(11)}%  ║`,
      `║ Status: ${latencyTolerance >= 80 ? 'PASS ✓' : 'FAIL ✗'}             ║`,
      `╚═══════════════════════════════════════╝`,
    ].join('\n');

    console.log(report);

    return {
      success: latencyTolerance >= 80,
      latencyTolerance,
      operationsSurvived: survivedOps,
      totalOperations: totalOps,
      report,
    };
  }

  /**
   * Show gate status
   */
  async gateStatus(): Promise<string> {
    console.log('[NavCLI] Fetching gate status...');

    const store = await getOfflineStore();
    const gates = await store.getAllGateStates();

    const lines = [
      `╔════════════════════════════════════════════════════════╗`,
      `║                    GATE STATUS                         ║`,
      `╠════════════════════════════════════════════════════════╣`,
    ];

    if (gates.length === 0) {
      lines.push(`║ No gates configured                                    ║`);
    } else {
      for (const gate of gates) {
        const cellId = gate.cell_id.padEnd(15);
        const anomalies = gate.anomaly_count.toString().padStart(3);
        const lockdown = gate.lockdown ? '🔒 YES' : '✓  NO';
        lines.push(`║ ${cellId}  Anomalies: ${anomalies}  Lockdown: ${lockdown}  ║`);
      }
    }

    lines.push(`╚════════════════════════════════════════════════════════╝`);

    const output = lines.join('\n');
    console.log(output);
    return output;
  }

  /**
   * Force sync with remote
   */
  async syncForce(): Promise<{
    success: boolean;
    synced: number;
    conflicts: number;
    message: string;
  }> {
    console.log('[NavCLI] Forcing sync with remote...');

    const store = await getOfflineStore();

    try {
      const result = await store.syncToRemote();

      const message = `Sync completed: ${result.synced} resources synced, ${result.conflicts} conflicts`;
      console.log(`[NavCLI] ${message}`);

      return {
        success: true,
        synced: result.synced,
        conflicts: result.conflicts,
        message,
      };
    } catch (error) {
      const message = `Sync failed: ${error}`;
      console.error(`[NavCLI] ${message}`);

      return {
        success: false,
        synced: 0,
        conflicts: 0,
        message,
      };
    }
  }

  /**
   * Check route health for a threshold
   */
  async routeCheck(threshold: 'wealth' | 'info' | 'myth'): Promise<string> {
    console.log(`[NavCLI] Checking route health for threshold: ${threshold}`);

    const router = getThresholdRouter();
    const health = router.checkRouteHealth(threshold);
    const metrics = router.getThresholdMetrics(threshold);

    const lines = [
      `╔════════════════════════════════════════════════════════╗`,
      `║  ROUTE CHECK: ${threshold.toUpperCase().padEnd(39)} ║`,
      `╠════════════════════════════════════════════════════════╣`,
      `║ Status: ${health.healthy ? '✓ HEALTHY' : '✗ UNHEALTHY'}                                  ║`,
      `║ Active Route: ${health.activeRoute.padEnd(37)} ║`,
      `║ Message: ${health.message.padEnd(40)} ║`,
      `╠════════════════════════════════════════════════════════╣`,
    ];

    // Add metrics
    if (metrics.primary) {
      const successRate = (metrics.primary.successes / metrics.primary.attempts * 100).toFixed(1);
      const avgLatency = (metrics.primary.totalLatency / metrics.primary.successes).toFixed(0);
      lines.push(`║ Primary:   ${metrics.primary.attempts} attempts, ${successRate}% success, ${avgLatency}ms avg ║`);
    }
    if (metrics.secondary) {
      const successRate = (metrics.secondary.successes / metrics.secondary.attempts * 100).toFixed(1);
      const avgLatency = (metrics.secondary.totalLatency / metrics.secondary.successes).toFixed(0);
      lines.push(`║ Secondary: ${metrics.secondary.attempts} attempts, ${successRate}% success, ${avgLatency}ms avg ║`);
    }
    if (metrics.local) {
      lines.push(`║ Local:     ${metrics.local.attempts} attempts (always succeeds)       ║`);
    }

    lines.push(`╚════════════════════════════════════════════════════════╝`);

    const output = lines.join('\n');
    console.log(output);
    return output;
  }

  /**
   * Show current metrics dashboard
   */
  async dashboard(): Promise<string> {
    console.log('[NavCLI] Generating metrics dashboard...');

    const gauges = getGauges();
    const polygon = getScopePolygon();

    const health = gauges.getHealthSummary();
    const currentPolygon = polygon.getCurrentPolygon();

    const lines = [
      `╔════════════════════════════════════════════════════════╗`,
      `║              EVEZ666 NAVIGATION MESH                   ║`,
      `╠════════════════════════════════════════════════════════╣`,
      `║ Overall Health: ${health.overall.toUpperCase().padEnd(35)} ║`,
      `╠════════════════════════════════════════════════════════╣`,
    ];

    // Add gauges
    for (const gauge of health.gauges) {
      const name = gauge.name.padEnd(20);
      const value = gauge.value.toFixed(1).padStart(5);
      const status = gauge.status.padEnd(8);
      lines.push(`║ ${name} ${value}  ${status}           ║`);
    }

    // Add polygon info if available
    if (currentPolygon) {
      lines.push(`╠════════════════════════════════════════════════════════╣`);
      lines.push(`║ Polygon Area:    ${currentPolygon.area.toFixed(1).padStart(5)}%                          ║`);
      lines.push(`║ Polygon Balance: ${currentPolygon.balance.toFixed(1).padStart(5)}%                          ║`);
    }

    lines.push(`╚════════════════════════════════════════════════════════╝`);

    const output = lines.join('\n');
    console.log(output);
    return output;
  }
}

// Singleton instance
let cliInstance: NavCLI | null = null;

/**
 * Get or create nav CLI instance
 */
export function getNavCLI(): NavCLI {
  if (!cliInstance) {
    cliInstance = new NavCLI();
  }
  return cliInstance;
}

/**
 * Main CLI entry point
 */
export async function main(args: string[]): Promise<void> {
  const cli = getNavCLI();
  const command = args[0];

  try {
    switch (command) {
      case 'test-offline':
        const hours = parseInt(args[1]) || 24;
        await cli.testOffline(hours);
        break;

      case 'gate-status':
        await cli.gateStatus();
        break;

      case 'sync-force':
        await cli.syncForce();
        break;

      case 'route-check':
        const threshold = args[1] as 'wealth' | 'info' | 'myth';
        if (!threshold || !['wealth', 'info', 'myth'].includes(threshold)) {
          console.error('Usage: route-check <wealth|info|myth>');
          process.exit(1);
        }
        await cli.routeCheck(threshold);
        break;

      case 'dashboard':
        await cli.dashboard();
        break;

      default:
        console.log('EVEZ666 Navigation CLI');
        console.log('');
        console.log('Commands:');
        console.log('  test-offline [hours]   - Simulate offline operation (default: 24h)');
        console.log('  gate-status            - Show all gate states and anomaly counts');
        console.log('  sync-force             - Force sync with remote');
        console.log('  route-check <threshold> - Check route health (wealth|info|myth)');
        console.log('  dashboard              - Show metrics dashboard');
        process.exit(1);
    }
  } catch (error) {
    console.error(`Error: ${error}`);
    process.exit(1);
  }
}

// Run CLI if called directly
if (require.main === module) {
  main(process.argv.slice(2));
}
