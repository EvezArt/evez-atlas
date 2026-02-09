/**
 * EVEZ666 Threshold Navigation Mesh - Gauges
 * Gauge definitions on 0-100 scale for system metrics
 */

'use strict';

export interface GaugeReading {
  value: number; // 0-100 scale
  timestamp: number;
  status: 'optimal' | 'good' | 'warning' | 'critical';
}

export interface GaugeConfig {
  name: string;
  description: string;
  target: number; // Target value (0-100)
  thresholds: {
    optimal: number;
    good: number;
    warning: number;
  };
}

/**
 * Gauge system for monitoring key metrics
 */
export class Gauges {
  private readings: Map<string, GaugeReading[]> = new Map();
  private readonly MAX_HISTORY = 100;

  // Gauge configurations
  private configs: Map<string, GaugeConfig> = new Map([
    ['LatencyTolerance', {
      name: 'LatencyTolerance',
      description: '% of operations surviving 24h offline',
      target: 100,
      thresholds: { optimal: 95, good: 80, warning: 60 },
    }],
    ['ThresholdLock', {
      name: 'ThresholdLock',
      description: '% of gate breach attempts blocked',
      target: 100,
      thresholds: { optimal: 99, good: 95, warning: 85 },
    }],
    ['ResourceFlow', {
      name: 'ResourceFlow',
      description: 'Ratio of cached vs live throughput',
      target: 50,
      thresholds: { optimal: 40, good: 30, warning: 20 },
    }],
    ['ArchiveDepth', {
      name: 'ArchiveDepth',
      description: 'Document archive coverage and depth',
      target: 80,
      thresholds: { optimal: 75, good: 60, warning: 40 },
    }],
    ['PersonaEntropy', {
      name: 'PersonaEntropy',
      description: 'Diversity and rotation of active personas',
      target: 70,
      thresholds: { optimal: 65, good: 50, warning: 30 },
    }],
    ['ProofDensity', {
      name: 'ProofDensity',
      description: 'Verification and audit trail completeness',
      target: 90,
      thresholds: { optimal: 85, good: 70, warning: 50 },
    }],
    ['ThreatAwareness', {
      name: 'ThreatAwareness',
      description: 'Anomaly detection and response effectiveness',
      target: 85,
      thresholds: { optimal: 80, good: 65, warning: 45 },
    }],
  ]);

  constructor() {}

  /**
   * Record gauge reading
   */
  recordReading(gaugeName: string, value: number): GaugeReading {
    // Clamp value to 0-100
    value = Math.max(0, Math.min(100, value));

    const config = this.configs.get(gaugeName);
    if (!config) {
      throw new Error(`Unknown gauge: ${gaugeName}`);
    }

    const status = this.calculateStatus(value, config);

    const reading: GaugeReading = {
      value,
      timestamp: Date.now(),
      status,
    };

    // Store reading
    let history = this.readings.get(gaugeName);
    if (!history) {
      history = [];
      this.readings.set(gaugeName, history);
    }

    history.push(reading);

    // Trim history
    if (history.length > this.MAX_HISTORY) {
      history.shift();
    }

    return reading;
  }

  /**
   * Calculate status based on thresholds
   */
  private calculateStatus(
    value: number,
    config: GaugeConfig
  ): GaugeReading['status'] {
    if (value >= config.thresholds.optimal) {
      return 'optimal';
    } else if (value >= config.thresholds.good) {
      return 'good';
    } else if (value >= config.thresholds.warning) {
      return 'warning';
    } else {
      return 'critical';
    }
  }

  /**
   * Get current reading for a gauge
   */
  getCurrentReading(gaugeName: string): GaugeReading | null {
    const history = this.readings.get(gaugeName);
    if (!history || history.length === 0) {
      return null;
    }
    return history[history.length - 1];
  }

  /**
   * Get gauge history
   */
  getHistory(gaugeName: string, limit: number = 10): GaugeReading[] {
    const history = this.readings.get(gaugeName) || [];
    return history.slice(-limit);
  }

  /**
   * Get all current readings
   */
  getAllReadings(): Map<string, GaugeReading> {
    const readings = new Map<string, GaugeReading>();
    
    for (const [name, history] of this.readings.entries()) {
      if (history.length > 0) {
        readings.set(name, history[history.length - 1]);
      }
    }

    return readings;
  }

  /**
   * Calculate latency tolerance gauge
   */
  calculateLatencyTolerance(
    offlineCapable: number,
    total: number
  ): GaugeReading {
    const value = total > 0 ? (offlineCapable / total) * 100 : 100;
    return this.recordReading('LatencyTolerance', value);
  }

  /**
   * Calculate threshold lock gauge
   */
  calculateThresholdLock(
    blocked: number,
    totalAttempts: number
  ): GaugeReading {
    const value = totalAttempts > 0 ? (blocked / totalAttempts) * 100 : 100;
    return this.recordReading('ThresholdLock', value);
  }

  /**
   * Calculate resource flow gauge
   */
  calculateResourceFlow(
    cached: number,
    live: number
  ): GaugeReading {
    const total = cached + live;
    const value = total > 0 ? (cached / total) * 100 : 0;
    return this.recordReading('ResourceFlow', value);
  }

  /**
   * Calculate archive depth gauge
   */
  calculateArchiveDepth(
    documentCount: number,
    targetCount: number = 1000
  ): GaugeReading {
    const value = Math.min(100, (documentCount / targetCount) * 100);
    return this.recordReading('ArchiveDepth', value);
  }

  /**
   * Calculate persona entropy gauge
   */
  calculatePersonaEntropy(
    activePersonas: number,
    totalPersonas: number,
    rotationRate: number
  ): GaugeReading {
    const diversityScore = totalPersonas > 0
      ? (activePersonas / totalPersonas) * 50
      : 0;
    const rotationScore = Math.min(50, rotationRate * 10);
    const value = diversityScore + rotationScore;
    return this.recordReading('PersonaEntropy', value);
  }

  /**
   * Calculate proof density gauge
   */
  calculateProofDensity(
    auditedEvents: number,
    totalEvents: number
  ): GaugeReading {
    const value = totalEvents > 0 ? (auditedEvents / totalEvents) * 100 : 0;
    return this.recordReading('ProofDensity', value);
  }

  /**
   * Calculate threat awareness gauge
   */
  calculateThreatAwareness(
    detectedAnomalies: number,
    totalRequests: number,
    falsePositiveRate: number
  ): GaugeReading {
    const detectionRate = totalRequests > 0
      ? (detectedAnomalies / totalRequests) * 100
      : 0;
    const accuracy = 100 - (falsePositiveRate * 100);
    const value = (detectionRate * 0.3) + (accuracy * 0.7);
    return this.recordReading('ThreatAwareness', value);
  }

  /**
   * Get gauge configuration
   */
  getConfig(gaugeName: string): GaugeConfig | null {
    return this.configs.get(gaugeName) || null;
  }

  /**
   * Get all gauge configurations
   */
  getAllConfigs(): Map<string, GaugeConfig> {
    return new Map(this.configs);
  }

  /**
   * Get system health summary
   */
  getHealthSummary(): {
    overall: 'optimal' | 'good' | 'warning' | 'critical';
    gauges: { name: string; value: number; status: string }[];
  } {
    const readings = this.getAllReadings();
    const gauges: { name: string; value: number; status: string }[] = [];
    
    let totalValue = 0;
    let count = 0;

    for (const [name, reading] of readings.entries()) {
      gauges.push({
        name,
        value: reading.value,
        status: reading.status,
      });
      totalValue += reading.value;
      count++;
    }

    const averageValue = count > 0 ? totalValue / count : 0;
    
    let overall: 'optimal' | 'good' | 'warning' | 'critical';
    if (averageValue >= 85) {
      overall = 'optimal';
    } else if (averageValue >= 70) {
      overall = 'good';
    } else if (averageValue >= 50) {
      overall = 'warning';
    } else {
      overall = 'critical';
    }

    return { overall, gauges };
  }

  /**
   * Clear all readings (for testing)
   */
  clearReadings(): void {
    this.readings.clear();
  }
}

// Singleton instance
let gaugesInstance: Gauges | null = null;

/**
 * Get or create gauges instance
 */
export function getGauges(): Gauges {
  if (!gaugesInstance) {
    gaugesInstance = new Gauges();
  }
  return gaugesInstance;
}
