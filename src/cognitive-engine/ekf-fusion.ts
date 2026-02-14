/**
 * Extended Kalman Filter (EKF) / Fusion Loop
 * 
 * Continuously predicts likely futures of the cognitive state
 * Enables "negative latency" through predictive trajectory caching
 */

import {
  FusionState,
  EntityType,
  TrajectoryBuffer,
} from './lord-protocol';

/**
 * State prediction from EKF
 */
export interface StatePrediction {
  state: FusionState;
  confidence: number;           // 0-1 scale
  timeHorizon: number;          // Milliseconds into future
  trajectory: FusionState[];    // Predicted trajectory
}

/**
 * EKF configuration
 */
export interface EKFConfig {
  predictionHorizons: number[]; // Milliseconds to predict into future
  processNoise: number;         // Q - model uncertainty
  measurementNoise: number;     // R - measurement uncertainty
  updateInterval: number;       // How often to update (ms)
}

/**
 * Default EKF configuration
 */
export const DEFAULT_EKF_CONFIG: EKFConfig = {
  predictionHorizons: [1000, 5000, 15000, 60000], // 1s, 5s, 15s, 1min
  processNoise: 0.1,
  measurementNoise: 0.05,
  updateInterval: 1000, // Update every second
};

/**
 * EKF State Vector
 */
interface StateVector {
  recursionLevel: number;
  crystallizationProgress: number;
  crystallizationVelocity: number;
  correctionRate: number;
  hazardCount: number;
}

/**
 * Convert FusionState to state vector
 */
function toStateVector(state: FusionState): StateVector {
  return {
    recursionLevel: state.meta.recursionLevel,
    crystallizationProgress: state.crystallization.progress,
    crystallizationVelocity: state.crystallization.velocity,
    correctionRate: state.corrections.current,
    hazardCount: state.hazards.activeCount,
  };
}

/**
 * Convert state vector back to FusionState
 */
function fromStateVector(vector: StateVector, entityType: EntityType, timestamp: number): FusionState {
  // Determine hazard severity from count
  let severity: 'low' | 'medium' | 'high' | 'critical' = 'low';
  if (vector.hazardCount > 5) severity = 'critical';
  else if (vector.hazardCount > 3) severity = 'high';
  else if (vector.hazardCount > 1) severity = 'medium';
  
  return {
    meta: {
      recursionLevel: Math.max(1, Math.min(20, Math.round(vector.recursionLevel))),
      entityType,
      timestamp,
    },
    crystallization: {
      progress: Math.max(0, Math.min(100, vector.crystallizationProgress)),
      velocity: vector.crystallizationVelocity,
    },
    corrections: {
      current: Math.max(0, Math.min(100, vector.correctionRate)),
      history: [],
    },
    hazards: {
      activeCount: Math.max(0, Math.round(vector.hazardCount)),
      severity,
    },
  };
}

/**
 * Predict next state using simple dynamics model
 * 
 * This is a simplified version of EKF prediction step
 */
function predictNextState(
  current: StateVector,
  deltaTime: number,
  config: EKFConfig
): StateVector {
  // Time in seconds
  const dt = deltaTime / 1000;
  
  // State dynamics (simplified):
  // 1. Recursion level changes slowly
  // 2. Crystallization progress increases with velocity
  // 3. Velocity decays over time
  // 4. Correction rate correlates with hazards
  // 5. Hazards decay as corrections happen
  
  const recursionChange = (current.crystallizationProgress - 50) * 0.01 * dt; // Moves toward complexity if crystallized
  const newRecursionLevel = current.recursionLevel + recursionChange;
  
  const progressChange = current.crystallizationVelocity * dt;
  const newProgress = current.crystallizationProgress + progressChange;
  
  const velocityDecay = 0.95; // Decay factor
  const newVelocity = current.crystallizationVelocity * Math.pow(velocityDecay, dt);
  
  const correctionDecay = current.hazardCount > 0 ? 0.98 : 1.0;
  const newCorrectionRate = current.correctionRate * Math.pow(correctionDecay, dt);
  
  const hazardReduction = current.correctionRate * 0.01 * dt;
  const newHazardCount = Math.max(0, current.hazardCount - hazardReduction);
  
  // Add process noise
  const noise = config.processNoise;
  
  return {
    recursionLevel: newRecursionLevel + (Math.random() - 0.5) * noise,
    crystallizationProgress: newProgress + (Math.random() - 0.5) * noise * 10,
    crystallizationVelocity: newVelocity + (Math.random() - 0.5) * noise,
    correctionRate: newCorrectionRate + (Math.random() - 0.5) * noise * 5,
    hazardCount: newHazardCount + (Math.random() - 0.5) * noise,
  };
}

/**
 * EKF Fusion Loop
 * 
 * Maintains continuous prediction of system state
 */
export class FusionLoop {
  private currentState: FusionState | null = null;
  private predictions: Map<number, StatePrediction> = new Map();
  private buffer: TrajectoryBuffer;
  private config: EKFConfig;
  private intervalId: NodeJS.Timeout | null = null;
  
  constructor(config: EKFConfig = DEFAULT_EKF_CONFIG, bufferSize: number = 100) {
    this.config = config;
    this.buffer = new TrajectoryBuffer(bufferSize);
  }
  
  /**
   * Update with new measurement
   */
  update(state: FusionState): void {
    this.currentState = state;
    this.buffer.push(state);
    
    // Generate predictions for all time horizons
    this.generatePredictions();
  }
  
  /**
   * Generate predictions for configured time horizons
   */
  private generatePredictions(): void {
    if (!this.currentState) return;
    
    const now = Date.now();
    const vector = toStateVector(this.currentState);
    
    for (const horizon of this.config.predictionHorizons) {
      const trajectory: FusionState[] = [];
      let currentVector = vector;
      const steps = Math.ceil(horizon / this.config.updateInterval);
      
      // Predict forward in steps
      for (let i = 0; i < steps; i++) {
        currentVector = predictNextState(
          currentVector,
          this.config.updateInterval,
          this.config
        );
        
        const predictedState = fromStateVector(
          currentVector,
          this.currentState.meta.entityType,
          now + (i + 1) * this.config.updateInterval
        );
        
        trajectory.push(predictedState);
      }
      
      // Store prediction
      const finalState = trajectory[trajectory.length - 1];
      const confidence = this.computeConfidence(horizon);
      
      this.predictions.set(horizon, {
        state: finalState,
        confidence,
        timeHorizon: horizon,
        trajectory,
      });
    }
  }
  
  /**
   * Compute confidence based on time horizon
   * Confidence decreases with distance into future
   */
  private computeConfidence(horizon: number): number {
    // Exponential decay of confidence
    const decayFactor = 0.0001; // Tuning parameter
    return Math.exp(-decayFactor * horizon);
  }
  
  /**
   * Get prediction for a specific time horizon
   */
  getPrediction(timeHorizon: number): StatePrediction | null {
    // Find closest prediction
    let closest: number | null = null;
    let minDiff = Infinity;
    
    for (const horizon of this.predictions.keys()) {
      const diff = Math.abs(horizon - timeHorizon);
      if (diff < minDiff) {
        minDiff = diff;
        closest = horizon;
      }
    }
    
    return closest ? this.predictions.get(closest) || null : null;
  }
  
  /**
   * Get all current predictions
   */
  getAllPredictions(): StatePrediction[] {
    return Array.from(this.predictions.values());
  }
  
  /**
   * Get the trajectory buffer (for "negative latency")
   */
  getTrajectoryBuffer(): TrajectoryBuffer {
    return this.buffer;
  }
  
  /**
   * Get current state
   */
  getCurrentState(): FusionState | null {
    return this.currentState;
  }
  
  /**
   * Start continuous prediction loop
   */
  start(onUpdate?: (predictions: StatePrediction[]) => void): void {
    if (this.intervalId) return; // Already running
    
    this.intervalId = setInterval(() => {
      if (this.currentState) {
        // Re-predict from current state
        this.generatePredictions();
        
        if (onUpdate) {
          onUpdate(this.getAllPredictions());
        }
      }
    }, this.config.updateInterval);
  }
  
  /**
   * Stop continuous prediction loop
   */
  stop(): void {
    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = null;
    }
  }
  
  /**
   * Check if loop is running
   */
  isRunning(): boolean {
    return this.intervalId !== null;
  }
  
  /**
   * Clear all state
   */
  reset(): void {
    this.stop();
    this.currentState = null;
    this.predictions.clear();
    this.buffer.clear();
  }
}

/**
 * Cached prediction lookup for "negative latency"
 * 
 * When a request comes in, we can immediately return a pre-computed
 * prediction instead of computing from scratch
 */
export class PredictionCache {
  private fusionLoop: FusionLoop;
  
  constructor(fusionLoop: FusionLoop) {
    this.fusionLoop = fusionLoop;
  }
  
  /**
   * Get immediate response for a query (zero latency)
   * 
   * Returns the prediction that was already computed and waiting
   */
  getImmediateResponse(timeHorizon: number = 1000): FusionState | null {
    const prediction = this.fusionLoop.getPrediction(timeHorizon);
    return prediction ? prediction.state : null;
  }
  
  /**
   * Get trajectory for a time range
   */
  getTrajectory(startTime: number, endTime: number): FusionState[] {
    const predictions = this.fusionLoop.getAllPredictions();
    const trajectory: FusionState[] = [];
    
    for (const pred of predictions) {
      if (pred.timeHorizon >= startTime && pred.timeHorizon <= endTime) {
        trajectory.push(...pred.trajectory.filter(s => 
          s.meta.timestamp >= Date.now() + startTime &&
          s.meta.timestamp <= Date.now() + endTime
        ));
      }
    }
    
    return trajectory;
  }
  
  /**
   * Get historical trajectory from buffer
   */
  getHistoricalTrajectory(count: number = 10): FusionState[] {
    return this.fusionLoop.getTrajectoryBuffer().getRecent(count);
  }
}
