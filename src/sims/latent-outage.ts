/**
 * EVEZ666 Threshold Navigation Mesh - Latent Outage Simulation
 * Monte Carlo simulation for extended connectivity loss scenarios
 */

'use strict';

export interface OutageScenario {
  duration: number; // hours
  dataLoss: number; // percentage
  revenueImpact: number; // dollars
  narrativeGap: number; // missed posts
  survivalScore: number; // 0-100
}

export interface SimulationResult {
  scenarios: OutageScenario[];
  averageSurvivalScore: number;
  worstCase: OutageScenario;
  bestCase: OutageScenario;
  recommendations: string[];
}

/**
 * Latent outage simulator
 */
export class LatentOutageSimulator {
  constructor() {}

  /**
   * Run Monte Carlo simulation
   */
  async simulate(
    runs: number = 1000,
    minDuration: number = 1,
    maxDuration: number = 72
  ): Promise<SimulationResult> {
    console.log(`[LatentOutage] Running ${runs} Monte Carlo simulations...`);

    const scenarios: OutageScenario[] = [];

    for (let i = 0; i < runs; i++) {
      // Random outage duration
      const duration = Math.random() * (maxDuration - minDuration) + minDuration;
      
      // Simulate scenario
      const scenario = this.simulateScenario(duration);
      scenarios.push(scenario);
    }

    // Calculate statistics
    const averageSurvivalScore = scenarios.reduce((sum, s) => sum + s.survivalScore, 0) / runs;
    
    const worstCase = scenarios.reduce((worst, s) => 
      s.survivalScore < worst.survivalScore ? s : worst
    );
    
    const bestCase = scenarios.reduce((best, s) => 
      s.survivalScore > best.survivalScore ? s : best
    );

    // Generate recommendations
    const recommendations = this.generateRecommendations(scenarios);

    return {
      scenarios,
      averageSurvivalScore,
      worstCase,
      bestCase,
      recommendations,
    };
  }

  /**
   * Simulate a single scenario
   */
  private simulateScenario(duration: number): OutageScenario {
    // Model data loss (increases with duration)
    const dataLossBase = Math.min(100, duration * 0.5);
    const dataLossVariance = Math.random() * 20 - 10;
    const dataLoss = Math.max(0, Math.min(100, dataLossBase + dataLossVariance));

    // Model revenue impact
    // Assumptions:
    // - $1000/day baseline revenue
    // - Local sim captures 70% offline
    // - Loss increases with duration due to customer churn
    const dailyRevenue = 1000;
    const offlineCapture = 0.70;
    const churnMultiplier = Math.min(2, 1 + (duration / 72) * 0.5);
    const revenueImpact = (duration / 24) * dailyRevenue * (1 - offlineCapture) * churnMultiplier;

    // Model narrative gap (missed posts)
    // Assumptions:
    // - 5 posts per day baseline
    // - Can queue 80% offline
    const postsPerDay = 5;
    const offlineQueueRate = 0.80;
    const narrativeGap = Math.round((duration / 24) * postsPerDay * (1 - offlineQueueRate));

    // Calculate survival score
    const dataLossScore = (100 - dataLoss) * 0.4;
    const revenueScore = Math.max(0, 100 - (revenueImpact / dailyRevenue * 20)) * 0.4;
    const narrativeScore = Math.max(0, 100 - (narrativeGap * 5)) * 0.2;
    const survivalScore = Math.round(dataLossScore + revenueScore + narrativeScore);

    return {
      duration,
      dataLoss,
      revenueImpact,
      narrativeGap,
      survivalScore,
    };
  }

  /**
   * Generate recommendations based on scenarios
   */
  private generateRecommendations(scenarios: OutageScenario[]): string[] {
    const recommendations: string[] = [];

    // Analyze data loss patterns
    const avgDataLoss = scenarios.reduce((sum, s) => sum + s.dataLoss, 0) / scenarios.length;
    if (avgDataLoss > 20) {
      recommendations.push(
        `Increase cache size: Average data loss is ${avgDataLoss.toFixed(1)}%. Consider expanding IndexedDB storage quota.`
      );
    }

    // Analyze revenue impact
    const avgRevenueImpact = scenarios.reduce((sum, s) => sum + s.revenueImpact, 0) / scenarios.length;
    if (avgRevenueImpact > 500) {
      recommendations.push(
        `Strengthen revenue resilience: Average impact is $${avgRevenueImpact.toFixed(0)}. Improve local Stripe simulation accuracy.`
      );
    }

    // Analyze narrative gaps
    const avgNarrativeGap = scenarios.reduce((sum, s) => sum + s.narrativeGap, 0) / scenarios.length;
    if (avgNarrativeGap > 2) {
      recommendations.push(
        `Expand post queue: Average gap is ${avgNarrativeGap.toFixed(1)} posts. Increase local draft capacity.`
      );
    }

    // Analyze long-duration scenarios
    const longOutages = scenarios.filter(s => s.duration > 48);
    const longOutageAvgScore = longOutages.length > 0
      ? longOutages.reduce((sum, s) => sum + s.survivalScore, 0) / longOutages.length
      : 100;
    
    if (longOutageAvgScore < 60) {
      recommendations.push(
        `Prepare for extended outages: ${longOutages.length} scenarios (${(longOutages.length / scenarios.length * 100).toFixed(1)}%) lasted >48h with average score ${longOutageAvgScore.toFixed(1)}. Consider SMS fallback implementation.`
      );
    }

    // If no issues found
    if (recommendations.length === 0) {
      recommendations.push(
        'System is well-prepared for latent outages across all tested durations.'
      );
    }

    return recommendations;
  }

  /**
   * Format simulation report
   */
  formatReport(result: SimulationResult): string {
    const lines = [
      '╔═════════════════════════════════════════════════════════╗',
      '║         LATENT OUTAGE SIMULATION REPORT                ║',
      '╠═════════════════════════════════════════════════════════╣',
      `║ Total Scenarios: ${result.scenarios.length.toString().padStart(38)} ║`,
      `║ Average Survival Score: ${result.averageSurvivalScore.toFixed(1).padStart(29)}  ║`,
      '╠═════════════════════════════════════════════════════════╣',
      '║ WORST CASE:                                             ║',
      `║   Duration: ${result.worstCase.duration.toFixed(1).padStart(5)}h  Data Loss: ${result.worstCase.dataLoss.toFixed(1).padStart(5)}%        ║`,
      `║   Revenue Impact: $${result.worstCase.revenueImpact.toFixed(0).padStart(7)}                        ║`,
      `║   Narrative Gap: ${result.worstCase.narrativeGap.toString().padStart(3)} posts                           ║`,
      `║   Survival Score: ${result.worstCase.survivalScore.toString().padStart(3)}                              ║`,
      '╠═════════════════════════════════════════════════════════╣',
      '║ BEST CASE:                                              ║',
      `║   Duration: ${result.bestCase.duration.toFixed(1).padStart(5)}h  Data Loss: ${result.bestCase.dataLoss.toFixed(1).padStart(5)}%        ║`,
      `║   Revenue Impact: $${result.bestCase.revenueImpact.toFixed(0).padStart(7)}                        ║`,
      `║   Narrative Gap: ${result.bestCase.narrativeGap.toString().padStart(3)} posts                           ║`,
      `║   Survival Score: ${result.bestCase.survivalScore.toString().padStart(3)}                              ║`,
      '╠═════════════════════════════════════════════════════════╣',
      '║ RECOMMENDATIONS:                                        ║',
    ];

    for (const rec of result.recommendations) {
      // Word wrap recommendations
      const words = rec.split(' ');
      let line = '║ • ';
      for (const word of words) {
        if (line.length + word.length > 55) {
          lines.push(line.padEnd(57) + '║');
          line = '║   ' + word + ' ';
        } else {
          line += word + ' ';
        }
      }
      if (line.length > 4) {
        lines.push(line.padEnd(57) + '║');
      }
    }

    lines.push('╚═════════════════════════════════════════════════════════╝');

    return lines.join('\n');
  }

  /**
   * Export scenarios to CSV
   */
  exportCSV(scenarios: OutageScenario[]): string {
    const lines = [
      'Duration (hours),Data Loss (%),Revenue Impact ($),Narrative Gap (posts),Survival Score',
    ];

    for (const scenario of scenarios) {
      lines.push([
        scenario.duration.toFixed(2),
        scenario.dataLoss.toFixed(2),
        scenario.revenueImpact.toFixed(2),
        scenario.narrativeGap.toString(),
        scenario.survivalScore.toString(),
      ].join(','));
    }

    return lines.join('\n');
  }
}

// Singleton instance
let simulatorInstance: LatentOutageSimulator | null = null;

/**
 * Get or create simulator instance
 */
export function getLatentOutageSimulator(): LatentOutageSimulator {
  if (!simulatorInstance) {
    simulatorInstance = new LatentOutageSimulator();
  }
  return simulatorInstance;
}
