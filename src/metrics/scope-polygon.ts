/**
 * EVEZ666 Threshold Navigation Mesh - Scope Polygon
 * 8-axis scope polygon visualization and calculation
 */

'use strict';

export interface PolygonAxes {
  Archive: number;        // 0-10
  Persona: number;        // 0-10
  Proof: number;          // 0-10
  Gate: number;           // 0-10
  Threat: number;         // 0-10
  Myth: number;           // 0-10
  NavLatency: number;     // 0-10
  ResourceLock: number;   // 0-10
}

export interface PolygonData {
  axes: PolygonAxes;
  timestamp: number;
  area: number;
  balance: number;
}

/**
 * Scope polygon calculator and visualizer
 */
export class ScopePolygon {
  private history: PolygonData[] = [];
  private readonly MAX_HISTORY = 50;

  constructor() {}

  /**
   * Calculate polygon from current system state
   */
  calculatePolygon(metrics: {
    archiveDepth: number;           // 0-100
    personaEntropy: number;         // 0-100
    proofDensity: number;           // 0-100
    gateDensity: number;            // 0-100
    threatAwareness: number;        // 0-100
    mythFlowRate: number;           // 0-100
    latencyTolerance: number;       // 0-100
    resourceFlowRatio: number;      // 0-100
  }): PolygonData {
    // Convert 0-100 scale to 0-10 scale
    const axes: PolygonAxes = {
      Archive: this.scale100To10(metrics.archiveDepth),
      Persona: this.scale100To10(metrics.personaEntropy),
      Proof: this.scale100To10(metrics.proofDensity),
      Gate: this.scale100To10(metrics.gateDensity),
      Threat: this.scale100To10(metrics.threatAwareness),
      Myth: this.scale100To10(metrics.mythFlowRate),
      NavLatency: this.scale100To10(metrics.latencyTolerance),
      ResourceLock: this.scale100To10(metrics.resourceFlowRatio),
    };

    // Calculate polygon area (sum of triangular segments)
    const area = this.calculateArea(axes);

    // Calculate balance (standard deviation from mean)
    const balance = this.calculateBalance(axes);

    const data: PolygonData = {
      axes,
      timestamp: Date.now(),
      area,
      balance,
    };

    // Store in history
    this.history.push(data);
    if (this.history.length > this.MAX_HISTORY) {
      this.history.shift();
    }

    return data;
  }

  /**
   * Scale 0-100 to 0-10
   */
  private scale100To10(value: number): number {
    return Math.min(10, Math.max(0, value / 10));
  }

  /**
   * Calculate polygon area
   */
  private calculateArea(axes: PolygonAxes): number {
    const values = Object.values(axes);
    const n = values.length;
    
    // Simple approximation: sum of all axis values
    // In a real implementation, calculate actual polygon area
    const sum = values.reduce((acc, v) => acc + v, 0);
    const maxArea = n * 10; // Maximum possible area (all axes at 10)
    
    return (sum / maxArea) * 100; // Return as percentage
  }

  /**
   * Calculate polygon balance
   */
  private calculateBalance(axes: PolygonAxes): number {
    const values = Object.values(axes);
    
    // Calculate mean
    const mean = values.reduce((acc, v) => acc + v, 0) / values.length;
    
    // Calculate standard deviation
    const variance = values.reduce((acc, v) => acc + Math.pow(v - mean, 2), 0) / values.length;
    const stdDev = Math.sqrt(variance);
    
    // Convert to balance score (lower stdDev = higher balance)
    // Maximum stdDev for range 0-10 is ~5, so normalize
    const balance = Math.max(0, 100 - (stdDev * 20));
    
    return balance;
  }

  /**
   * Get current polygon
   */
  getCurrentPolygon(): PolygonData | null {
    if (this.history.length === 0) return null;
    return this.history[this.history.length - 1];
  }

  /**
   * Get polygon history
   */
  getHistory(limit: number = 10): PolygonData[] {
    return this.history.slice(-limit);
  }

  /**
   * Export polygon as ASCII art
   */
  exportPolygonASCII(data: PolygonData): string {
    const axes = data.axes;
    const width = 60;
    const lines: string[] = [];

    lines.push('╔' + '═'.repeat(width) + '╗');
    lines.push('║' + ' '.repeat(Math.floor((width - 18) / 2)) + 'EVEZ666 POLYGON' + ' '.repeat(Math.ceil((width - 18) / 2)) + '║');
    lines.push('╠' + '═'.repeat(width) + '╣');

    // Draw each axis
    for (const [name, value] of Object.entries(axes)) {
      const barLength = Math.round((value / 10) * 40);
      const bar = '█'.repeat(barLength) + '░'.repeat(40 - barLength);
      const padding = ' '.repeat(15 - name.length);
      lines.push(`║ ${name}${padding} ${bar} ${value.toFixed(1)} ║`);
    }

    lines.push('╠' + '═'.repeat(width) + '╣');
    lines.push(`║ Area: ${data.area.toFixed(1)}%  Balance: ${data.balance.toFixed(1)}%` + ' '.repeat(width - 32) + '║');
    lines.push('╚' + '═'.repeat(width) + '╝');

    return lines.join('\n');
  }

  /**
   * Export polygon as JSON
   */
  exportPolygonJSON(data: PolygonData): string {
    return JSON.stringify(data, null, 2);
  }

  /**
   * Export polygon as SVG
   */
  exportPolygonSVG(data: PolygonData): string {
    const axes = data.axes;
    const axisNames = Object.keys(axes);
    const values = Object.values(axes);
    const n = values.length;
    
    const size = 400;
    const center = size / 2;
    const radius = size / 2 - 50;
    
    // Calculate polygon points
    const points: { x: number; y: number }[] = [];
    
    for (let i = 0; i < n; i++) {
      const angle = (Math.PI * 2 * i) / n - Math.PI / 2;
      const value = values[i];
      const r = (value / 10) * radius;
      const x = center + r * Math.cos(angle);
      const y = center + r * Math.sin(angle);
      points.push({ x, y });
    }
    
    // Build SVG
    const svg = [];
    svg.push(`<svg width="${size}" height="${size}" xmlns="http://www.w3.org/2000/svg">`);
    svg.push(`  <rect width="${size}" height="${size}" fill="#1a1a2e"/>`);
    
    // Draw grid circles
    for (let i = 1; i <= 10; i++) {
      const r = (i / 10) * radius;
      const opacity = i === 10 ? 0.3 : 0.1;
      svg.push(`  <circle cx="${center}" cy="${center}" r="${r}" fill="none" stroke="#e2b714" stroke-width="1" opacity="${opacity}"/>`);
    }
    
    // Draw axis lines
    for (let i = 0; i < n; i++) {
      const angle = (Math.PI * 2 * i) / n - Math.PI / 2;
      const x = center + radius * Math.cos(angle);
      const y = center + radius * Math.sin(angle);
      svg.push(`  <line x1="${center}" y1="${center}" x2="${x}" y2="${y}" stroke="#0f3460" stroke-width="1" opacity="0.5"/>`);
    }
    
    // Draw polygon
    const polygonPoints = points.map(p => `${p.x},${p.y}`).join(' ');
    svg.push(`  <polygon points="${polygonPoints}" fill="#e2b714" fill-opacity="0.3" stroke="#e2b714" stroke-width="2"/>`);
    
    // Draw axis labels
    for (let i = 0; i < n; i++) {
      const angle = (Math.PI * 2 * i) / n - Math.PI / 2;
      const labelRadius = radius + 30;
      const x = center + labelRadius * Math.cos(angle);
      const y = center + labelRadius * Math.sin(angle);
      svg.push(`  <text x="${x}" y="${y}" text-anchor="middle" fill="#e2b714" font-size="12" font-family="monospace">${axisNames[i]}</text>`);
    }
    
    // Add title
    svg.push(`  <text x="${center}" y="30" text-anchor="middle" fill="#e2b714" font-size="16" font-weight="bold" font-family="monospace">EVEZ666 POLYGON</text>`);
    
    // Add metrics
    svg.push(`  <text x="10" y="${size - 20}" fill="#e2b714" font-size="12" font-family="monospace">Area: ${data.area.toFixed(1)}%  Balance: ${data.balance.toFixed(1)}%</text>`);
    
    svg.push('</svg>');
    
    return svg.join('\n');
  }

  /**
   * Compare two polygons
   */
  comparePolygons(data1: PolygonData, data2: PolygonData): {
    areaDiff: number;
    balanceDiff: number;
    axisDiffs: Record<string, number>;
  } {
    const axisDiffs: Record<string, number> = {};
    
    for (const key of Object.keys(data1.axes) as Array<keyof PolygonAxes>) {
      axisDiffs[key] = data2.axes[key] - data1.axes[key];
    }
    
    return {
      areaDiff: data2.area - data1.area,
      balanceDiff: data2.balance - data1.balance,
      axisDiffs,
    };
  }

  /**
   * Clear history (for testing)
   */
  clearHistory(): void {
    this.history = [];
  }
}

// Singleton instance
let polygonInstance: ScopePolygon | null = null;

/**
 * Get or create scope polygon instance
 */
export function getScopePolygon(): ScopePolygon {
  if (!polygonInstance) {
    polygonInstance = new ScopePolygon();
  }
  return polygonInstance;
}
