/**
 * EVEZ666 Threshold Navigation Mesh - Meters
 * Trend meters for tracking velocity and momentum
 */

'use strict';

export interface MeterReading {
  value: number;
  trend: 'increasing' | 'stable' | 'decreasing';
  timestamp: number;
}

export interface MeterConfig {
  name: string;
  description: string;
  unit: string;
}

/**
 * Meter system for tracking trends
 */
export class Meters {
  private readings: Map<string, MeterReading[]> = new Map();
  private readonly MAX_HISTORY = 100;

  // Meter configurations
  private configs: Map<string, MeterConfig> = new Map([
    ['NavVelocity', {
      name: 'NavVelocity',
      description: 'Path switches per week with auto-route success rate',
      unit: 'switches/week',
    }],
    ['GateDensity', {
      name: 'GateDensity',
      description: 'Thresholds enforced across cells/flows',
      unit: 'gates',
    }],
    ['FlywheelMomentum', {
      name: 'FlywheelMomentum',
      description: 'Digital/service/tool revenue linkage strength',
      unit: 'correlation',
    }],
  ]);

  constructor() {}

  /**
   * Record meter reading
   */
  recordReading(meterName: string, value: number): MeterReading {
    const config = this.configs.get(meterName);
    if (!config) {
      throw new Error(`Unknown meter: ${meterName}`);
    }

    // Calculate trend
    const history = this.readings.get(meterName) || [];
    const trend = this.calculateTrend(value, history);

    const reading: MeterReading = {
      value,
      trend,
      timestamp: Date.now(),
    };

    // Store reading
    if (!this.readings.has(meterName)) {
      this.readings.set(meterName, []);
    }

    const updatedHistory = this.readings.get(meterName)!;
    updatedHistory.push(reading);

    // Trim history
    if (updatedHistory.length > this.MAX_HISTORY) {
      updatedHistory.shift();
    }

    return reading;
  }

  /**
   * Calculate trend based on recent history
   */
  private calculateTrend(
    currentValue: number,
    history: MeterReading[]
  ): MeterReading['trend'] {
    if (history.length < 3) {
      return 'stable';
    }

    // Get average of last 3 readings
    const recentReadings = history.slice(-3);
    const average = recentReadings.reduce((sum, r) => sum + r.value, 0) / 3;

    // Calculate percentage change
    const changePercent = ((currentValue - average) / average) * 100;

    if (changePercent > 5) {
      return 'increasing';
    } else if (changePercent < -5) {
      return 'decreasing';
    } else {
      return 'stable';
    }
  }

  /**
   * Get current reading for a meter
   */
  getCurrentReading(meterName: string): MeterReading | null {
    const history = this.readings.get(meterName);
    if (!history || history.length === 0) {
      return null;
    }
    return history[history.length - 1];
  }

  /**
   * Get meter history
   */
  getHistory(meterName: string, limit: number = 10): MeterReading[] {
    const history = this.readings.get(meterName) || [];
    return history.slice(-limit);
  }

  /**
   * Get all current readings
   */
  getAllReadings(): Map<string, MeterReading> {
    const readings = new Map<string, MeterReading>();
    
    for (const [name, history] of this.readings.entries()) {
      if (history.length > 0) {
        readings.set(name, history[history.length - 1]);
      }
    }

    return readings;
  }

  /**
   * Calculate navigation velocity meter
   */
  calculateNavVelocity(
    pathSwitches: number,
    successRate: number
  ): MeterReading {
    // Weight path switches by success rate
    const value = pathSwitches * successRate;
    return this.recordReading('NavVelocity', value);
  }

  /**
   * Calculate gate density meter
   */
  calculateGateDensity(
    activeGates: number,
    totalCells: number,
    validationRate: number
  ): MeterReading {
    // Gate density = (active gates / total cells) * validation rate
    const density = totalCells > 0
      ? (activeGates / totalCells) * validationRate
      : 0;
    const value = density * 100; // Scale to percentage
    return this.recordReading('GateDensity', value);
  }

  /**
   * Calculate flywheel momentum meter
   */
  calculateFlywheelMomentum(
    digitalRevenue: number,
    serviceRevenue: number,
    toolRevenue: number
  ): MeterReading {
    // Calculate correlation strength between revenue streams
    const total = digitalRevenue + serviceRevenue + toolRevenue;
    
    if (total === 0) {
      return this.recordReading('FlywheelMomentum', 0);
    }

    // Calculate balance (ideal is 33% each)
    const digitalRatio = digitalRevenue / total;
    const serviceRatio = serviceRevenue / total;
    const toolRatio = toolRevenue / total;

    // Calculate deviation from ideal balance
    const idealRatio = 1 / 3;
    const deviation = Math.abs(digitalRatio - idealRatio) +
                     Math.abs(serviceRatio - idealRatio) +
                     Math.abs(toolRatio - idealRatio);

    // Convert to momentum score (lower deviation = higher momentum)
    const momentum = Math.max(0, 100 - (deviation * 150));

    return this.recordReading('FlywheelMomentum', momentum);
  }

  /**
   * Get meter configuration
   */
  getConfig(meterName: string): MeterConfig | null {
    return this.configs.get(meterName) || null;
  }

  /**
   * Get all meter configurations
   */
  getAllConfigs(): Map<string, MeterConfig> {
    return new Map(this.configs);
  }

  /**
   * Get trend summary
   */
  getTrendSummary(): {
    increasing: string[];
    stable: string[];
    decreasing: string[];
  } {
    const increasing: string[] = [];
    const stable: string[] = [];
    const decreasing: string[] = [];

    const readings = this.getAllReadings();

    for (const [name, reading] of readings.entries()) {
      switch (reading.trend) {
        case 'increasing':
          increasing.push(name);
          break;
        case 'stable':
          stable.push(name);
          break;
        case 'decreasing':
          decreasing.push(name);
          break;
      }
    }

    return { increasing, stable, decreasing };
  }

  /**
   * Clear all readings (for testing)
   */
  clearReadings(): void {
    this.readings.clear();
  }
}

// Singleton instance
let metersInstance: Meters | null = null;

/**
 * Get or create meters instance
 */
export function getMeters(): Meters {
  if (!metersInstance) {
    metersInstance = new Meters();
  }
  return metersInstance;
}
