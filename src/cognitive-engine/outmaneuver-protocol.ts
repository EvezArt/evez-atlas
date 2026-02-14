/**
 * Outmaneuver Protocol - Meta-Cognitive Layer
 * 
 * Implements the cognitive hygiene protocol that prevents the system
 * from fighting itself and enables growth through awareness
 */

import {
  FusionState,
  ControlPolicy,
  LoopType,
  computeUrgency,
} from './lord-protocol';

/**
 * Edge detection event - triggers when system detects a cognitive spike
 */
export interface EdgeDetection {
  detected: boolean;
  timestamp: number;
  trigger: 'gap_threshold' | 'error_spike' | 'hazard_critical' | 'crystallization_drop';
  value: number;
  threshold: number;
  message: string;
}

/**
 * Loop classification result
 */
export interface LoopClassification {
  loopType: LoopType;
  confidence: number;           // 0-1 scale
  indicators: string[];         // What led to this classification
  recommendation: string;       // What to do about it
}

/**
 * Outmaneuver Protocol configuration
 */
export interface OutmaneuverConfig {
  gapThreshold: number;         // Trigger edge detection when |ΔΩ| exceeds this
  errorSpikeThreshold: number;  // Trigger when error rate spikes above this
  hazardCriticalThreshold: number; // Trigger when hazard count exceeds this
  crystallizationDropThreshold: number; // Trigger when crystallization drops below this
}

/**
 * Loop scoring weights
 * These weights determine how strongly each condition contributes to loop classification
 */
export const LOOP_SCORING_WEIGHTS = {
  // Threat loop indicators (fighting problems)
  THREAT_HIGH_HAZARD: 3,           // High/critical hazard severity
  THREAT_HIGH_CORRECTION: 2,       // Correction rate > 70
  
  // Control loop indicators (over-correcting)
  CONTROL_LOW_RECURSION_HIGH_VELOCITY: 3,  // R < 5 and velocity > 5
  CONTROL_NEGATIVE_GAP: 2,         // Over-correction (ΔΩ < -10)
  
  // Worth loop indicators (complexity without stability)
  WORTH_HIGH_RECURSION_LOW_CRYST: 3,  // R > 15 and crystallization < 50
  WORTH_LOW_VELOCITY: 2,           // Velocity < 1
  
  // Attachment loop indicators (stuck in plateau)
  ATTACHMENT_HIGH_CORRECTIONS_STALLED: 3,  // C > 60 and velocity < 2
  ATTACHMENT_PLATEAU: 2,           // Correction rate hasn't changed
  
  // Numbing loop indicators (disengaged)
  NUMBING_LOW_ACTIVITY: 3,         // R < 3 and C < 20
  NUMBING_NO_MOVEMENT: 2,          // Velocity = 0
  
  // Maximum score for normalization
  MAX_SCORE: 5,
};

/**
 * Default Outmaneuver Protocol configuration
 */
export const DEFAULT_OUTMANEUVER_CONFIG: OutmaneuverConfig = {
  gapThreshold: 15,              // Red zone threshold
  errorSpikeThreshold: 0.5,      // 50% error rate
  hazardCriticalThreshold: 5,    // 5+ active hazards
  crystallizationDropThreshold: 40, // Below 40% crystallization
};

/**
 * Detect edge conditions in the system state
 * 
 * "Catch the edge" - recognize when a model is spiking
 */
export function detectEdge(
  state: FusionState,
  deltaOmega: number,
  config: OutmaneuverConfig = DEFAULT_OUTMANEUVER_CONFIG
): EdgeDetection | null {
  // Check divine gap threshold
  if (Math.abs(deltaOmega) > config.gapThreshold) {
    return {
      detected: true,
      timestamp: Date.now(),
      trigger: 'gap_threshold',
      value: Math.abs(deltaOmega),
      threshold: config.gapThreshold,
      message: 'Model spike detected: Divine gap exceeds threshold. This is a signal, not truth.',
    };
  }
  
  // Check for critical hazards
  if (state.hazards.activeCount > config.hazardCriticalThreshold) {
    return {
      detected: true,
      timestamp: Date.now(),
      trigger: 'hazard_critical',
      value: state.hazards.activeCount,
      threshold: config.hazardCriticalThreshold,
      message: 'Critical hazard count detected. A protective model is running with outdated methods.',
    };
  }
  
  // Check for crystallization drop
  if (state.crystallization.progress < config.crystallizationDropThreshold) {
    return {
      detected: true,
      timestamp: Date.now(),
      trigger: 'crystallization_drop',
      value: state.crystallization.progress,
      threshold: config.crystallizationDropThreshold,
      message: 'Low crystallization detected. System coherence requires attention.',
    };
  }
  
  return null; // No edge detected
}

/**
 * Classify the type of loop the system is in
 * 
 * "Name the loop" - identify the pattern so awareness can see it
 */
export function classifyLoop(state: FusionState, deltaOmega: number): LoopClassification {
  const indicators: string[] = [];
  const W = LOOP_SCORING_WEIGHTS;
  const scores = {
    threat: 0,
    control: 0,
    worth: 0,
    attachment: 0,
    numbing: 0,
  };
  
  // Threat loop: High hazards + high corrections
  if (state.hazards.severity === 'high' || state.hazards.severity === 'critical') {
    scores.threat += W.THREAT_HIGH_HAZARD;
    indicators.push('High hazard severity');
  }
  if (state.corrections.current > 70) {
    scores.threat += W.THREAT_HIGH_CORRECTION;
    indicators.push('High correction rate');
  }
  
  // Control loop: Low recursion + high crystallization attempts
  if (state.meta.recursionLevel < 5 && state.crystallization.velocity > 5) {
    scores.control += W.CONTROL_LOW_RECURSION_HIGH_VELOCITY;
    indicators.push('Low recursion with high crystallization pressure');
  }
  if (deltaOmega < -10) {
    scores.control += W.CONTROL_NEGATIVE_GAP;
    indicators.push('Over-correction detected (negative gap)');
  }
  
  // Worth loop: High recursion + low crystallization
  if (state.meta.recursionLevel > 15 && state.crystallization.progress < 50) {
    scores.worth += W.WORTH_HIGH_RECURSION_LOW_CRYST;
    indicators.push('High recursion without adequate crystallization');
  }
  if (state.crystallization.velocity < 1) {
    scores.worth += W.WORTH_LOW_VELOCITY;
    indicators.push('Very low crystallization velocity');
  }
  
  // Attachment loop: High corrections but progress stalled
  if (state.corrections.current > 60 && Math.abs(state.crystallization.velocity) < 2) {
    scores.attachment += W.ATTACHMENT_HIGH_CORRECTIONS_STALLED;
    indicators.push('High corrections but stalled progress');
  }
  if (state.corrections.history.length > 5) {
    const recentAvg = state.corrections.history.slice(-5).reduce((a, b) => a + b, 0) / 5;
    if (Math.abs(recentAvg - state.corrections.current) < 5) {
      scores.attachment += W.ATTACHMENT_PLATEAU;
      indicators.push('Correction rate stuck in plateau');
    }
  }
  
  // Numbing loop: Low everything (system disengaged)
  if (state.meta.recursionLevel < 3 && state.corrections.current < 20) {
    scores.numbing += W.NUMBING_LOW_ACTIVITY;
    indicators.push('Low recursion and corrections');
  }
  if (state.crystallization.velocity === 0) {
    scores.numbing += W.NUMBING_NO_MOVEMENT;
    indicators.push('No crystallization movement');
  }
  
  // Find the highest scoring loop
  const maxScore = Math.max(...Object.values(scores));
  let loopType: LoopType = 'none';
  let confidence = 0;
  
  if (maxScore > 0) {
    const entry = Object.entries(scores).find(([_, score]) => score === maxScore);
    if (entry) {
      loopType = entry[0] as LoopType;
      confidence = Math.min(1, maxScore / W.MAX_SCORE);
    }
  }
  
  // Generate recommendation based on loop type
  let recommendation = 'System operating normally. Continue monitoring.';
  
  switch (loopType) {
    case 'threat':
      recommendation = 'Threat loop detected. Address hazards systematically. Remember: errors are signals, not enemies.';
      break;
    case 'control':
      recommendation = 'Control loop detected. Reduce over-correction. Allow natural system evolution.';
      break;
    case 'worth':
      recommendation = 'Worth loop detected. Increase crystallization focus. Stabilize before adding complexity.';
      break;
    case 'attachment':
      recommendation = 'Attachment loop detected. Current approach may be stuck. Consider alternative strategies.';
      break;
    case 'numbing':
      recommendation = 'Numbing loop detected. System needs stimulus. Increase engagement and activity.';
      break;
  }
  
  return {
    loopType,
    confidence,
    indicators: indicators.length > 0 ? indicators : ['No loop indicators detected'],
    recommendation,
  };
}

/**
 * Generate de-fusing messages for awareness
 * 
 * "De-fuse" - create perspective that allows growth without self-war
 */
export function generateDefuseMessage(
  edge: EdgeDetection | null,
  loopClassification: LoopClassification
): string {
  let message = '';
  
  if (edge) {
    message += `⚠️ Edge Detected: ${edge.message}\n\n`;
  }
  
  if (loopClassification.loopType !== 'none') {
    message += `🔄 Loop Classification: ${loopClassification.loopType.toUpperCase()} loop (confidence: ${(loopClassification.confidence * 100).toFixed(0)}%)\n\n`;
    message += `📊 Indicators:\n`;
    loopClassification.indicators.forEach(ind => {
      message += `  • ${ind}\n`;
    });
    message += `\n💡 Recommendation: ${loopClassification.recommendation}\n\n`;
  }
  
  message += `🧘 Outmaneuver Reminder:\n`;
  message += `  • This is a signal moving through awareness, not an identity statement\n`;
  message += `  • A model is running; it protects with outdated methods\n`;
  message += `  • Growth accelerates when we stop fighting what is\n`;
  
  return message;
}

/**
 * Apply Outmaneuver Protocol to a fusion state
 * 
 * Returns updated control policy with loop classification and de-fuse messages
 */
export function applyOutmaneuverProtocol(
  state: FusionState,
  deltaOmega: number,
  basePolicy?: ControlPolicy,
  config: OutmaneuverConfig = DEFAULT_OUTMANEUVER_CONFIG
): {
  policy: ControlPolicy;
  edge: EdgeDetection | null;
  loopClassification: LoopClassification;
  defuseMessage: string;
} {
  // Detect edge
  const edge = detectEdge(state, deltaOmega, config);
  
  // Classify loop
  const loopClassification = classifyLoop(state, deltaOmega);
  
  // Generate de-fuse message
  const defuseMessage = generateDefuseMessage(edge, loopClassification);
  
  // Create or enhance control policy
  const policy: ControlPolicy = basePolicy || {
    targetRecursionLevel: state.meta.recursionLevel,
    mode: state.meta.entityType,
    urgency: computeUrgency(state, deltaOmega),
    reason: 'Routine monitoring',
    actions: [],
  };
  
  // Add loop type to policy
  policy.loopType = loopClassification.loopType;
  
  // Add actions based on edge detection and loop classification
  if (edge) {
    policy.actions.push({
      type: 'log',
      payload: {
        level: 'warning',
        message: edge.message,
        edge: edge,
      },
    });
  }
  
  if (loopClassification.confidence > 0.5) {
    policy.actions.push({
      type: 'log',
      payload: {
        level: 'info',
        message: loopClassification.recommendation,
        loop: loopClassification,
      },
    });
    
    // For high-confidence loops, consider creating issues
    if (loopClassification.confidence > 0.7) {
      const issueTitle = `[Outmaneuver] ${loopClassification.loopType} loop detected`;
      const issueBody = defuseMessage;
      
      policy.actions.push({
        type: 'create_issue',
        payload: {
          title: issueTitle,
          body: issueBody,
          labels: ['cognitive-engine', `loop:${loopClassification.loopType}`],
        },
      });
    }
  }
  
  return {
    policy,
    edge,
    loopClassification,
    defuseMessage,
  };
}
