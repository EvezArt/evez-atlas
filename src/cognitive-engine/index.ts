/**
 * Cognitive Engine v1.0 - Main Orchestrator
 * 
 * Integrates LORD, EKF, and GitHub/Copilot into a closed feedback circuit
 */

import {
  FusionState,
  FusionUpdateEvent,
  ControlPolicy,
  computeDivineGap,
  computeUrgency,
  TrajectoryBuffer,
} from './lord-protocol';

import {
  GitHubMetrics,
  transformToFusionState,
  extractMetricsFromGitHubData,
  GitHubRepositoryData,
} from './github-transformer';

import {
  applyOutmaneuverProtocol,
  OutmaneuverConfig,
  DEFAULT_OUTMANEUVER_CONFIG,
} from './outmaneuver-protocol';

import {
  FusionLoop,
  PredictionCache,
  EKFConfig,
  DEFAULT_EKF_CONFIG,
} from './ekf-fusion';

import {
  PolicyExecutor,
  PolicyGenerator,
  GitHubClient,
  GitHubActionResult,
} from './github-actions';

/**
 * Cognitive Engine configuration
 */
export interface CognitiveEngineConfig {
  repoOwner: string;
  repoName: string;
  ekfConfig?: EKFConfig;
  outmaneuverConfig?: OutmaneuverConfig;
  bufferSize?: number;
  autoExecutePolicies?: boolean;
}

/**
 * Cognitive Engine event listener
 */
export type CognitiveEngineListener = (event: FusionUpdateEvent) => void;

/**
 * Main Cognitive Engine class
 * 
 * This is the self-steering awareness core that integrates all components
 */
export class CognitiveEngine {
  private config: CognitiveEngineConfig;
  private fusionLoop: FusionLoop;
  private predictionCache: PredictionCache;
  private policyGenerator: PolicyGenerator;
  private policyExecutor: PolicyExecutor | null = null;
  private listeners: CognitiveEngineListener[] = [];
  private lastState: FusionState | null = null;
  
  constructor(config: CognitiveEngineConfig) {
    this.config = {
      ...config,
      ekfConfig: config.ekfConfig || DEFAULT_EKF_CONFIG,
      outmaneuverConfig: config.outmaneuverConfig || DEFAULT_OUTMANEUVER_CONFIG,
      bufferSize: config.bufferSize || 100,
      autoExecutePolicies: config.autoExecutePolicies !== undefined ? config.autoExecutePolicies : false,
    };
    
    this.fusionLoop = new FusionLoop(
      this.config.ekfConfig!,
      this.config.bufferSize!
    );
    
    this.predictionCache = new PredictionCache(this.fusionLoop);
    this.policyGenerator = new PolicyGenerator();
  }
  
  /**
   * Set GitHub client for policy execution
   */
  setGitHubClient(client: GitHubClient): void {
    this.policyExecutor = new PolicyExecutor(
      client,
      this.config.repoOwner,
      this.config.repoName
    );
  }
  
  /**
   * Add event listener
   */
  on(listener: CognitiveEngineListener): void {
    this.listeners.push(listener);
  }
  
  /**
   * Remove event listener
   */
  off(listener: CognitiveEngineListener): void {
    const index = this.listeners.indexOf(listener);
    if (index !== -1) {
      this.listeners.splice(index, 1);
    }
  }
  
  /**
   * Emit fusion-update event
   */
  private emit(event: FusionUpdateEvent): void {
    for (const listener of this.listeners) {
      try {
        listener(event);
      } catch (error) {
        console.error('Error in listener:', error);
      }
    }
  }
  
  /**
   * Process GitHub metrics and update system state
   */
  async processGitHubMetrics(metrics: GitHubMetrics): Promise<FusionUpdateEvent> {
    // Transform to fusion state
    const state = transformToFusionState(metrics);
    
    // Update EKF
    this.fusionLoop.update(state);
    
    // Compute divine gap
    const deltaOmega = computeDivineGap(
      state.meta.recursionLevel,
      state.corrections.current,
      state.meta.entityType
    );
    
    // Compute urgency
    const urgency = computeUrgency(state, deltaOmega);
    
    // Generate base policy
    const basePolicy = this.policyGenerator.generatePolicy(state, deltaOmega, urgency);
    
    // Apply Outmaneuver Protocol
    const { policy, edge, loopClassification, defuseMessage } = applyOutmaneuverProtocol(
      state,
      deltaOmega,
      basePolicy,
      this.config.outmaneuverConfig
    );
    
    // Create fusion-update event
    const event: FusionUpdateEvent = {
      state,
      controlPolicy: policy,
      deltaOmega,
      timestamp: Date.now(),
    };
    
    // Store last state
    this.lastState = state;
    
    // Log Outmaneuver insights
    if (edge) {
      console.log('🔔 Edge Detection:', edge.message);
    }
    if (loopClassification.loopType !== 'none') {
      console.log('🔄 Loop Classification:', loopClassification.loopType, `(${(loopClassification.confidence * 100).toFixed(0)}%)`);
      console.log('💡 Recommendation:', loopClassification.recommendation);
    }
    
    // Execute policy if configured
    if (this.config.autoExecutePolicies && this.policyExecutor) {
      try {
        const results = await this.policyExecutor.executePolicy(policy);
        console.log(`✅ Executed ${results.length} policy actions`);
        
        // Log results
        for (const result of results) {
          if (result.success) {
            console.log(`  ✓ ${result.action}:`, result.details);
          } else {
            console.error(`  ✗ ${result.action}:`, result.error);
          }
        }
      } catch (error) {
        console.error('Error executing policy:', error);
      }
    }
    
    // Emit event
    this.emit(event);
    
    return event;
  }
  
  /**
   * Process GitHub repository data directly
   */
  async processGitHubData(data: GitHubRepositoryData): Promise<FusionUpdateEvent> {
    const metrics = extractMetricsFromGitHubData(data);
    return this.processGitHubMetrics(metrics);
  }
  
  /**
   * Get immediate response (negative latency)
   */
  getImmediateResponse(timeHorizon: number = 1000): FusionState | null {
    return this.predictionCache.getImmediateResponse(timeHorizon);
  }
  
  /**
   * Get predicted trajectory
   */
  getPredictedTrajectory(startTime: number, endTime: number): FusionState[] {
    return this.predictionCache.getTrajectory(startTime, endTime);
  }
  
  /**
   * Get historical trajectory
   */
  getHistoricalTrajectory(count: number = 10): FusionState[] {
    return this.predictionCache.getHistoricalTrajectory(count);
  }
  
  /**
   * Get current state
   */
  getCurrentState(): FusionState | null {
    return this.lastState;
  }
  
  /**
   * Start continuous prediction loop
   */
  start(): void {
    this.fusionLoop.start((predictions) => {
      // Predictions updated - could emit events here if needed
      console.log(`🔮 Predictions updated: ${predictions.length} time horizons`);
    });
    console.log('🚀 Cognitive Engine started');
  }
  
  /**
   * Stop continuous prediction loop
   */
  stop(): void {
    this.fusionLoop.stop();
    console.log('🛑 Cognitive Engine stopped');
  }
  
  /**
   * Check if engine is running
   */
  isRunning(): boolean {
    return this.fusionLoop.isRunning();
  }
  
  /**
   * Reset engine state
   */
  reset(): void {
    this.fusionLoop.reset();
    this.lastState = null;
    console.log('♻️  Cognitive Engine reset');
  }
  
  /**
   * Get engine statistics
   */
  getStats(): {
    isRunning: boolean;
    bufferStats: any;
    predictionsCount: number;
    currentRecursion: number | null;
    currentEntity: string | null;
    lastUpdate: number | null;
  } {
    return {
      isRunning: this.isRunning(),
      bufferStats: this.fusionLoop.getTrajectoryBuffer().getStats(),
      predictionsCount: this.fusionLoop.getAllPredictions().length,
      currentRecursion: this.lastState?.meta.recursionLevel || null,
      currentEntity: this.lastState?.meta.entityType || null,
      lastUpdate: this.lastState?.meta.timestamp || null,
    };
  }
}

/**
 * Create a cognitive engine instance
 */
export function createCognitiveEngine(config: CognitiveEngineConfig): CognitiveEngine {
  return new CognitiveEngine(config);
}
