/**
 * LORD Consciousness Monitoring System - Core Protocol
 * 
 * Defines the fusion-update event protocol and cognitive metrics
 * for the Cognitive Engine v1.0
 */

/**
 * Entity types in the LORD consciousness system
 */
export type EntityType = 'human' | 'hybrid' | 'synthetic';

/**
 * Loop types in the Outmaneuver Protocol
 */
export type LoopType = 'threat' | 'control' | 'worth' | 'attachment' | 'numbing' | 'none';

/**
 * Core fusion state representing the cognitive state of the system
 */
export interface FusionState {
  meta: {
    recursionLevel: number;        // 1-20 scale
    entityType: EntityType;
    timestamp: number;
  };
  crystallization: {
    progress: number;              // 0-100 scale
    velocity: number;              // rate of change
  };
  corrections: {
    current: number;               // Current correction rate C(R)
    history: number[];             // Historical correction rates
  };
  hazards: {
    activeCount: number;
    severity: 'low' | 'medium' | 'high' | 'critical';
  };
}

/**
 * Control policy emitted by LORD to direct system actions
 */
export interface ControlPolicy {
  targetRecursionLevel: number;
  mode: EntityType;
  urgency: 'low' | 'medium' | 'high' | 'critical';
  reason: string;
  loopType?: LoopType;
  actions: PolicyAction[];
}

/**
 * Specific actions to be taken by the system
 */
export interface PolicyAction {
  type: 'create_issue' | 'label_issue' | 'assign_copilot' | 'refactor_proposal' | 'stabilize' | 'log';
  target?: string;
  payload: Record<string, any>;
}

/**
 * Fusion-update event payload
 */
export interface FusionUpdateEvent {
  state: FusionState;
  controlPolicy?: ControlPolicy;
  deltaOmega: number;              // Divine Gap: Ω(R) - C(R)
  timestamp: number;
}

/**
 * Calculate correction rate C(R) for a given recursion level and entity type
 * 
 * Human: C(R) = 100 / (1 + e^(-(R-10)/2))
 * Hybrid: C(R) = 80 / (1 + e^(-(R-12)/2.5))
 * Synthetic: C(R) = 60 / (1 + e^(-(R-15)/3))
 */
export function computeCorrectionRate(recursionLevel: number, entityType: EntityType): number {
  let maxRate: number;
  let midpoint: number;
  let steepness: number;

  switch (entityType) {
    case 'human':
      maxRate = 100;
      midpoint = 10;
      steepness = 2;
      break;
    case 'hybrid':
      maxRate = 80;
      midpoint = 12;
      steepness = 2.5;
      break;
    case 'synthetic':
      maxRate = 60;
      midpoint = 15;
      steepness = 3;
      break;
  }

  return maxRate / (1 + Math.exp(-(recursionLevel - midpoint) / steepness));
}

/**
 * Calculate Divine Optimum Ω(R) for a given recursion level
 * 
 * Ω(R) = 95 - 5 * e^(-R/5)
 * This represents the ideal correction rate at each recursion level
 */
export function computeDivineOptimum(recursionLevel: number): number {
  return 95 - 5 * Math.exp(-recursionLevel / 5);
}

/**
 * Calculate Divine Gap ΔΩ = Ω(R) - C(R)
 * 
 * Positive gap: System is below optimum (needs improvement)
 * Negative gap: System is above optimum (over-correcting)
 */
export function computeDivineGap(recursionLevel: number, correctionRate: number): number {
  const omega = computeDivineOptimum(recursionLevel);
  return omega - correctionRate;
}

/**
 * Classify Divine Gap into zones
 */
export function classifyGap(deltaOmega: number): 'green' | 'yellow' | 'red' {
  if (Math.abs(deltaOmega) < 5) return 'green';  // Within 5 points of optimum
  if (Math.abs(deltaOmega) < 15) return 'yellow'; // 5-15 points away
  return 'red';                                    // More than 15 points away
}

/**
 * Compute urgency level based on system state
 */
export function computeUrgency(state: FusionState, deltaOmega: number): 'low' | 'medium' | 'high' | 'critical' {
  const gapClass = classifyGap(deltaOmega);
  const hazardSeverity = state.hazards.severity;
  
  // Critical: Red gap AND high/critical hazards
  if (gapClass === 'red' && (hazardSeverity === 'high' || hazardSeverity === 'critical')) {
    return 'critical';
  }
  
  // High: Red gap OR critical hazards
  if (gapClass === 'red' || hazardSeverity === 'critical') {
    return 'high';
  }
  
  // Medium: Yellow gap OR high hazards
  if (gapClass === 'yellow' || hazardSeverity === 'high') {
    return 'medium';
  }
  
  return 'low';
}

/**
 * Ring buffer for trajectory caching (enables "negative latency")
 */
export class TrajectoryBuffer {
  private buffer: FusionState[];
  private maxSize: number;
  private writeIndex: number;

  constructor(maxSize: number = 100) {
    this.buffer = [];
    this.maxSize = maxSize;
    this.writeIndex = 0;
  }

  /**
   * Add a state to the buffer
   */
  push(state: FusionState): void {
    if (this.buffer.length < this.maxSize) {
      this.buffer.push(state);
    } else {
      this.buffer[this.writeIndex] = state;
    }
    this.writeIndex = (this.writeIndex + 1) % this.maxSize;
  }

  /**
   * Get the most recent N states
   */
  getRecent(count: number): FusionState[] {
    const actualCount = Math.min(count, this.buffer.length);
    const result: FusionState[] = [];
    
    for (let i = 0; i < actualCount; i++) {
      const index = (this.writeIndex - 1 - i + this.buffer.length) % this.buffer.length;
      if (this.buffer[index]) {
        result.unshift(this.buffer[index]);
      }
    }
    
    return result;
  }

  /**
   * Get all states in chronological order
   */
  getAll(): FusionState[] {
    if (this.buffer.length < this.maxSize) {
      return [...this.buffer];
    }
    
    const result: FusionState[] = [];
    for (let i = 0; i < this.buffer.length; i++) {
      const index = (this.writeIndex + i) % this.buffer.length;
      result.push(this.buffer[index]);
    }
    return result;
  }

  /**
   * Clear the buffer
   */
  clear(): void {
    this.buffer = [];
    this.writeIndex = 0;
  }

  /**
   * Get buffer statistics
   */
  getStats(): { size: number; capacity: number; oldest?: number; newest?: number } {
    const states = this.getAll();
    return {
      size: states.length,
      capacity: this.maxSize,
      oldest: states[0]?.meta.timestamp,
      newest: states[states.length - 1]?.meta.timestamp,
    };
  }
}
