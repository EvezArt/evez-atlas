export interface ProcessingModeConfig {
  depthLimits: {
    tier0: number;
    tier1: number;
    tier2: number;
    tier3: number;
  };
}

export type ProcessingMode = "sequential" | "swarm";

export interface AwarenessResult {
  entityId: string;
  mode: ProcessingMode;
  trace: string[];
}

const defaultConfig: ProcessingModeConfig = {
  depthLimits: {
    tier0: 0,
    tier1: 1,
    tier2: 2,
    tier3: Number.POSITIVE_INFINITY,
  },
};

const traceHops = ["hop-1", "hop-2", "hop-3", "hop-4"];

export function resolveAwareness(
  entityId: string,
  mode: ProcessingMode,
  tier: number,
  config: ProcessingModeConfig = defaultConfig,
): AwarenessResult {
  if (mode === "swarm" && tier < 3) {
    throw new Error("Swarm processing requires tier 3 access");
  }

  if (mode === "swarm") {
    return {
      entityId,
      mode,
      trace: [...traceHops],
    };
  }

  const limit = (() => {
    if (tier <= 0) {
      return config.depthLimits.tier0;
    }
    if (tier === 1) {
      return config.depthLimits.tier1;
    }
    if (tier === 2) {
      return config.depthLimits.tier2;
    }
    return config.depthLimits.tier3;
  })();

  return {
    entityId,
    mode,
    trace: traceHops.slice(0, Number.isFinite(limit) ? limit : traceHops.length),
  };
}
  mode: "sequential" | "swarm";
  depthLimits: Record<number, number | null>;
}

export interface TraceNode {
  id: string;
  children?: TraceNode[];
  metadata?: Record<string, unknown>;
}

const DEFAULT_DEPTH_LIMITS: Record<number, number | null> = {
  0: 0,
  1: 1,
  2: 2,
  3: null,
};

const limitTraceDepth = (node: TraceNode, depth: number): TraceNode => {
  if (depth <= 0 || !node.children) {
    return { id: node.id };
  }
  return {
    id: node.id,
    children: node.children.map((child) => limitTraceDepth(child, depth - 1)),
  };
};

export const resolveAwareness = (
  trace: TraceNode,
  tier: number,
  config: ProcessingModeConfig = {
    mode: "sequential",
    depthLimits: DEFAULT_DEPTH_LIMITS,
  },
): TraceNode => {
  const depthLimit = config.depthLimits[tier] ?? DEFAULT_DEPTH_LIMITS[tier] ?? 0;

  if (config.mode === "swarm") {
    if (tier < 3) {
      throw new Error("Swarm mode requires tier 3 access");
    }
    return trace;
  }

  if (depthLimit === null) {
    return trace;
  }

  return limitTraceDepth(trace, depthLimit);
};
