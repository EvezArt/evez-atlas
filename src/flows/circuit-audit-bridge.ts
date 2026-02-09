/**
 * EVEZ666 Threshold Navigation Mesh - Circuit Audit Bridge
 * Connects profit circuit to audit system with shared event format
 */

'use strict';

export interface CircuitEvent {
  id: string;
  type: 'revenue' | 'payout' | 'gate' | 'flow' | 'anomaly';
  timestamp: number;
  severity: 'info' | 'warning' | 'error' | 'critical';
  source: string;
  data: Record<string, any>;
}

export interface AuditEntry {
  timestamp: number;
  level: string;
  source: string;
  message: string;
  metadata?: Record<string, any>;
}

/**
 * Circuit-Audit bridge for event pipeline
 */
export class CircuitAuditBridge {
  private eventBuffer: CircuitEvent[] = [];
  private readonly MAX_BUFFER_SIZE = 1000;

  constructor() {}

  /**
   * Emit circuit event
   */
  emitCircuitEvent(event: CircuitEvent): void {
    // Add to buffer
    this.eventBuffer.push(event);

    // Trim buffer if needed
    if (this.eventBuffer.length > this.MAX_BUFFER_SIZE) {
      this.eventBuffer = this.eventBuffer.slice(-this.MAX_BUFFER_SIZE);
    }

    // In production, also send to audit system
    this.sendToAuditSystem(event);
  }

  /**
   * Create revenue event
   */
  createRevenueEvent(
    amount: number,
    processor: string,
    metadata?: Record<string, any>
  ): CircuitEvent {
    return {
      id: this.generateId(),
      type: 'revenue',
      timestamp: Date.now(),
      severity: 'info',
      source: 'wealth-flow',
      data: {
        amount,
        processor,
        ...metadata,
      },
    };
  }

  /**
   * Create gate event
   */
  createGateEvent(
    cell: string,
    allowed: boolean,
    reason: string,
    metadata?: Record<string, any>
  ): CircuitEvent {
    return {
      id: this.generateId(),
      type: 'gate',
      timestamp: Date.now(),
      severity: allowed ? 'info' : 'warning',
      source: 'zero-trust-gate',
      data: {
        cell,
        allowed,
        reason,
        ...metadata,
      },
    };
  }

  /**
   * Create anomaly event
   */
  createAnomalyEvent(
    cell: string,
    severity: number,
    action: string,
    metrics?: Record<string, any>
  ): CircuitEvent {
    return {
      id: this.generateId(),
      type: 'anomaly',
      timestamp: Date.now(),
      severity: severity > 75 ? 'critical' : severity > 40 ? 'error' : 'warning',
      source: 'anomaly-detector',
      data: {
        cell,
        severity,
        action,
        ...metrics,
      },
    };
  }

  /**
   * Create flow event
   */
  createFlowEvent(
    flow: string,
    operation: string,
    success: boolean,
    metadata?: Record<string, any>
  ): CircuitEvent {
    return {
      id: this.generateId(),
      type: 'flow',
      timestamp: Date.now(),
      severity: success ? 'info' : 'error',
      source: `${flow}-flow`,
      data: {
        flow,
        operation,
        success,
        ...metadata,
      },
    };
  }

  /**
   * Convert circuit event to audit entry
   */
  toAuditEntry(event: CircuitEvent): AuditEntry {
    return {
      timestamp: event.timestamp,
      level: event.severity.toUpperCase(),
      source: event.source,
      message: this.formatEventMessage(event),
      metadata: event.data,
    };
  }

  /**
   * Format event message
   */
  private formatEventMessage(event: CircuitEvent): string {
    switch (event.type) {
      case 'revenue':
        return `Revenue event: $${event.data.amount} via ${event.data.processor}`;
      case 'gate':
        return `Gate validation: ${event.data.cell} - ${event.data.allowed ? 'ALLOWED' : 'DENIED'} - ${event.data.reason}`;
      case 'anomaly':
        return `Anomaly detected: ${event.data.cell} - severity ${event.data.severity} - action: ${event.data.action}`;
      case 'flow':
        return `Flow operation: ${event.data.flow}.${event.data.operation} - ${event.data.success ? 'SUCCESS' : 'FAILED'}`;
      default:
        return `Event: ${event.type}`;
    }
  }

  /**
   * Send to audit system
   */
  private sendToAuditSystem(event: CircuitEvent): void {
    // In production, write to audit log file or send to audit service
    // For now, just log to console
    if (event.severity === 'critical' || event.severity === 'error') {
      console.error(`[CircuitAudit] ${this.formatEventMessage(event)}`);
    } else {
      console.log(`[CircuitAudit] ${this.formatEventMessage(event)}`);
    }
  }

  /**
   * Get recent events
   */
  getRecentEvents(limit: number = 100, type?: string): CircuitEvent[] {
    let events = this.eventBuffer;
    
    if (type) {
      events = events.filter((e) => e.type === type);
    }

    return events.slice(-limit);
  }

  /**
   * Get events by severity
   */
  getEventsBySeverity(severity: CircuitEvent['severity']): CircuitEvent[] {
    return this.eventBuffer.filter((e) => e.severity === severity);
  }

  /**
   * Get event statistics
   */
  getStatistics(): {
    total: number;
    byType: Record<string, number>;
    bySeverity: Record<string, number>;
  } {
    const byType: Record<string, number> = {};
    const bySeverity: Record<string, number> = {};

    for (const event of this.eventBuffer) {
      byType[event.type] = (byType[event.type] || 0) + 1;
      bySeverity[event.severity] = (bySeverity[event.severity] || 0) + 1;
    }

    return {
      total: this.eventBuffer.length,
      byType,
      bySeverity,
    };
  }

  /**
   * Clear event buffer (for testing)
   */
  clearBuffer(): void {
    this.eventBuffer = [];
  }

  /**
   * Generate unique ID
   */
  private generateId(): string {
    return `${Date.now()}-${Math.random().toString(36).slice(2, 11)}`;
  }
}

// Singleton instance
let bridgeInstance: CircuitAuditBridge | null = null;

/**
 * Get or create circuit audit bridge instance
 */
export function getCircuitAuditBridge(): CircuitAuditBridge {
  if (!bridgeInstance) {
    bridgeInstance = new CircuitAuditBridge();
  }
  return bridgeInstance;
}
