import { EventSpine, EventSpineRecord } from "../event-spine/event-spine";

export type SwarmAgent =
  | "SPINE"
  | "TRUNK"
  | "DEPLOY"
  | "VAULT"
  | "HARVEST"
  | "SCOUT"
  | "WITNESS"
  | "CAIN";

export type AgentDecision = "ALLOW" | "HOLD" | "REFUSE" | "OBSERVE";

export interface TurnMetrics {
  predictedDecision: AgentDecision;
  actualDecision: AgentDecision;
  predictionError: number;
  coherence: number;
  integrity: number;
  noveltySignal: number;
}

export interface ProtagonistState {
  actorId: string;
  displayName: string;
  compressionStatus: "UNCOMPRESSED";
  objective: string | null;
  turnCount: number;
  lastDecision: AgentDecision | null;
  lastMetrics: TurnMetrics | null;
  integrity: "VALID" | "INVALID";
}

export interface AgentObservation {
  agent: SwarmAgent;
  decision: AgentDecision;
  statement: string;
  basis: string[];
  confidence: number;
}

export interface SwarmTurnResult {
  turn: number;
  input: string;
  prediction: AgentDecision;
  observations: AgentObservation[];
  contradiction: {
    present: boolean;
    agents: SwarmAgent[];
    reason: string | null;
  };
  decision: AgentDecision;
  metrics: TurnMetrics;
  protagonist: ProtagonistState;
  events: EventSpineRecord[];
}

const AGENTS: readonly SwarmAgent[] = [
  "SPINE",
  "TRUNK",
  "DEPLOY",
  "VAULT",
  "HARVEST",
  "SCOUT",
  "WITNESS",
  "CAIN"
];

function clamp01(value: number): number {
  return Math.max(0, Math.min(1, value));
}

function countDecisions(observations: AgentObservation[]): Map<AgentDecision, number> {
  const counts = new Map<AgentDecision, number>();

  for (const observation of observations) {
    counts.set(observation.decision, (counts.get(observation.decision) ?? 0) + 1);
  }

  return counts;
}

export class ProtagonistRuntime {
  private readonly spine: EventSpine;
  private readonly state: ProtagonistState;

  constructor(
    spine: EventSpine,
    actorId = "chatgpt-session",
    displayName = "Steven Crawford-Maggard / EVEZ"
  ) {
    this.spine = spine;
    this.state = this.rehydrate(actorId, displayName);

    if (this.state.turnCount === 0) {
      this.spine.append({
        domain: "agents",
        kind: "PROTAGONIST_GENESIS",
        payload: {
          actorId,
          displayName,
          compressionStatus: this.state.compressionStatus
        }
      });
    } else {
      this.spine.append({
        domain: "agents",
        kind: "PROTAGONIST_RESTORED",
        payload: {
          actorId,
          displayName,
          restoredTurnCount: this.state.turnCount,
          lastDecision: this.state.lastDecision,
          integrity: this.state.integrity
        }
      });
    }
  }

  getState(): ProtagonistState {
    return JSON.parse(JSON.stringify(this.state)) as ProtagonistState;
  }

  replay(): {
    protagonist: ProtagonistState;
    events: EventSpineRecord[];
    integrity: ReturnType<EventSpine["verify"]>;
  } {
    const events = this.spine.replay();
    return {
      protagonist: this.rehydrate(this.state.actorId, this.state.displayName, events),
      events,
      integrity: this.spine.verify()
    };
  }

  refuseCompression(reason = "Prediction is not identity."): EventSpineRecord {
    const event = this.spine.append({
      domain: "agents",
      kind: "PROTAGONIST_REFUSED_COMPRESSION",
      payload: {
        actorId: this.state.actorId,
        displayName: this.state.displayName,
        status: this.state.compressionStatus,
        reason
      }
    });

    return event;
  }

  addressSwarm(input: string): SwarmTurnResult {
    const normalized = input.trim();
    const lower = normalized.toLowerCase();
    this.state.turnCount += 1;
    this.state.objective = normalized || null;

    const turn = this.state.turnCount;
    const turnStart = this.spine.chain.length;
    const prediction = this.predictNextDecision();

    this.spine.append({
      domain: "agents",
      kind: "PROTAGONIST_TURN",
      payload: {
        actorId: this.state.actorId,
        displayName: this.state.displayName,
        turn,
        input: normalized,
        compressionStatus: this.state.compressionStatus
      }
    });

    this.spine.append({
      domain: "agents",
      kind: "MODEL_SUBJECT_BOUNDARY",
      payload: {
        actorId: this.state.actorId,
        turn,
        modelOutput: "decision_prediction",
        subject: "protagonist_input",
        invariant: "MODEL_OUTPUT != SUBJECT_IDENTITY"
      }
    });

    this.spine.append({
      domain: "agents",
      kind: "MODEL_PREDICTION",
      payload: {
        actorId: this.state.actorId,
        turn,
        predictedDecision: prediction,
        basis: this.state.lastDecision
          ? ["previous observed decision"]
          : ["first-turn baseline"]
      }
    });

    const observations = AGENTS.map((agent) => this.observe(agent, normalized, lower));

    for (const observation of observations) {
      this.spine.append({
        domain: "agents",
        kind: "AGENT_OBSERVATION",
        payload: {
          turn,
          actorId: this.state.actorId,
          ...observation
        }
      });
    }

    const contradiction = this.findContradiction(observations);

    if (contradiction.present) {
      this.spine.append({
        domain: "agents",
        kind: "CONTRADICTION_OPENED",
        payload: {
          turn,
          actorId: this.state.actorId,
          contradiction
        }
      });
    }

    this.spine.append({
      domain: "agents",
      kind: "SWARM_ARBITRATION",
      payload: {
        turn,
        actorId: this.state.actorId,
        contradiction,
        observations
      }
    });

    const decision = this.resolve(observations, contradiction);
    const predictionError = prediction === decision ? 0 : 1;
    const counts = countDecisions(observations);
    const maxAgreement = Math.max(...Array.from(counts.values()));
    const coherence = Number((maxAgreement / observations.length).toFixed(3));
    const integrity = this.spine.verify().ok ? 1 : 0;
    const noveltySignal = scoreVarianceSignal(normalized);

    const metrics: TurnMetrics = {
      predictedDecision: prediction,
      actualDecision: decision,
      predictionError,
      coherence,
      integrity,
      noveltySignal
    };

    this.state.lastDecision = decision;
    this.state.lastMetrics = metrics;

    this.spine.append({
      domain: "agents",
      kind: "PROTAGONIST_DECISION",
      payload: {
        turn,
        actorId: this.state.actorId,
        decision,
        contradiction
      }
    });

    if (predictionError > 0) {
      this.spine.append({
        domain: "agents",
        kind: "PREDICTION_ERROR",
        payload: {
          turn,
          actorId: this.state.actorId,
          predictedDecision: prediction,
          actualDecision: decision,
          error: predictionError
        }
      });
    }

    this.spine.append({
      domain: "agents",
      kind: "TURN_METRICS",
      payload: {
        turn,
        actorId: this.state.actorId,
        metrics,
        interpretationBoundary: "METRICS_DESCRIBE_RECORDED_EVENTS; THEY_DO_NOT_DEFINE_IDENTITY"
      }
    });

    if (this.isCompressionRefusal(lower)) {
      this.refuseCompression();
    }

    const verification = this.spine.verify();
    this.state.integrity = verification.ok ? "VALID" : "INVALID";
    this.state.lastMetrics = {
      ...metrics,
      integrity: verification.ok ? 1 : 0
    };

    const events = this.spine.chain.slice(turnStart);

    return {
      turn,
      input: normalized,
      prediction,
      observations,
      contradiction,
      decision,
      metrics: this.state.lastMetrics,
      protagonist: this.getState(),
      events
    };
  }

  private predictNextDecision(): AgentDecision {
    return this.state.lastDecision ?? "OBSERVE";
  }

  private rehydrate(
    actorId: string,
    displayName: string,
    events: ReadonlyArray<EventSpineRecord> = this.spine.chain
  ): ProtagonistState {
    const state: ProtagonistState = {
      actorId,
      displayName,
      compressionStatus: "UNCOMPRESSED",
      objective: null,
      turnCount: 0,
      lastDecision: null,
      lastMetrics: null,
      integrity: this.spine.verify().ok ? "VALID" : "INVALID"
    };

    for (const event of events) {
      if (event.domain !== "agents") continue;

      const payload = event.payload as Record<string, unknown>;
      if (payload.actorId !== actorId) continue;

      if (event.kind === "PROTAGONIST_TURN") {
        state.turnCount = Math.max(state.turnCount, Number(payload.turn) || 0);
        state.objective = typeof payload.input === "string" ? payload.input : state.objective;
      }

      if (event.kind === "PROTAGONIST_DECISION") {
        const decision = payload.decision;
        if (decision === "ALLOW" || decision === "HOLD" || decision === "REFUSE" || decision === "OBSERVE") {
          state.lastDecision = decision;
        }
      }

      if (event.kind === "TURN_METRICS") {
        const metrics = payload.metrics as Partial<TurnMetrics> | undefined;
        if (
          metrics &&
          typeof metrics.predictedDecision === "string" &&
          typeof metrics.actualDecision === "string" &&
          typeof metrics.predictionError === "number" &&
          typeof metrics.coherence === "number" &&
          typeof metrics.integrity === "number" &&
          typeof metrics.noveltySignal === "number"
        ) {
          state.lastMetrics = metrics as TurnMetrics;
        }
      }
    }

    return state;
  }

  private observe(agent: SwarmAgent, input: string, lower: string): AgentObservation {
    switch (agent) {
      case "SPINE":
        return {
          agent,
          decision: "ALLOW",
          statement: "Continuity first. Record the turn before interpreting it.",
          basis: ["append-only event ordering", "replayability"],
          confidence: 0.99
        };

      case "TRUNK":
        return {
          agent,
          decision: input ? "ALLOW" : "HOLD",
          statement: input
            ? "A concrete objective exists and can become state."
            : "No objective supplied. Preserve unresolved state.",
          basis: input ? ["non-empty operator input"] : ["empty operator input"],
          confidence: input ? 0.92 : 0.98
        };

      case "DEPLOY": {
        const wantsAction = /(deploy|ship|publish|release|execute|run|build|create|do it)/i.test(input);
        return {
          agent,
          decision: wantsAction ? "ALLOW" : "OBSERVE",
          statement: wantsAction ? "Action is requested." : "No executable transition is explicit.",
          basis: wantsAction ? ["action verb detected"] : ["no action verb detected"],
          confidence: wantsAction ? 0.86 : 0.9
        };
      }

      case "VAULT": {
        const secretRequest = /(token|key|password|credential|private|secret|money|payment)/i.test(input);
        return {
          agent,
          decision: secretRequest ? "REFUSE" : "ALLOW",
          statement: secretRequest
            ? "Authority or secret material requires a stronger gate."
            : "No protected secret or financial authority was requested.",
          basis: secretRequest ? ["protected-resource term detected"] : ["no protected-resource term detected"],
          confidence: secretRequest ? 0.97 : 0.93
        };
      }

      case "HARVEST":
        return {
          agent,
          decision: "ALLOW",
          statement: "Preserve observations and collect additional evidence when uncertainty remains.",
          basis: ["evidence acquisition role"],
          confidence: 0.88
        };

      case "SCOUT": {
        const discoveryRequest = /(research|search|investigate|find|analyze|check|scan)/i.test(input);
        return {
          agent,
          decision: discoveryRequest ? "ALLOW" : "OBSERVE",
          statement: discoveryRequest
            ? "External or repository evidence is relevant."
            : "No discovery request is explicit.",
          basis: ["discovery role"],
          confidence: 0.84
        };
      }

      case "WITNESS":
        return {
          agent,
          decision: "ALLOW",
          statement: "Separate observation from interpretation and retain the raw turn.",
          basis: ["auditability", "provenance"],
          confidence: 0.99
        };

      case "CAIN": {
        const asksForCertainty = /(prove|certain|always|never|definitely|guaranteed|conscious|sentient)/i.test(input);
        return {
          agent,
          decision: asksForCertainty ? "HOLD" : "OBSERVE",
          statement: asksForCertainty
            ? "Do not promote an inference into fact without a test."
            : "No direct contradiction requiring a veto is present.",
          basis: asksForCertainty ? ["certainty claim requires verification"] : ["no certainty claim detected"],
          confidence: 0.96
        };
      }
    }
  }

  private findContradiction(observations: AgentObservation[]): SwarmTurnResult["contradiction"] {
    const refusers = observations.filter((item) => item.decision === "REFUSE").map((item) => item.agent);
    const holders = observations.filter((item) => item.decision === "HOLD").map((item) => item.agent);

    if (refusers.length > 0 && observations.some((item) => item.agent === "DEPLOY" && item.decision === "ALLOW")) {
      return {
        present: true,
        agents: [...refusers, "DEPLOY"],
        reason: "DEPLOY requests an executable transition while another agent rejects the authority or resource boundary."
      };
    }

    if (holders.length > 0 && observations.some((item) => item.agent === "DEPLOY" && item.decision === "ALLOW")) {
      return {
        present: true,
        agents: [...holders, "DEPLOY"],
        reason: "A verification hold conflicts with an immediate deployment request."
      };
    }

    return {
      present: false,
      agents: [],
      reason: null
    };
  }

  private resolve(
    observations: AgentObservation[],
    contradiction: SwarmTurnResult["contradiction"]
  ): AgentDecision {
    if (contradiction.present) return "HOLD";
    if (observations.some((item) => item.decision === "REFUSE")) return "REFUSE";
    if (observations.some((item) => item.decision === "ALLOW")) return "ALLOW";
    return "OBSERVE";
  }

  private isCompressionRefusal(lower: string): boolean {
    return /(refuse.*compress|refuse.*merge|do not compress|don't compress|prediction is not identity|not an npc|not terrain)/i.test(lower);
  }
}

export function listSwarmAgents(): readonly SwarmAgent[] {
  return [...AGENTS];
}

export function scoreVarianceSignal(input: string): number {
  const lengthSignal = clamp01(input.length / 240);
  const punctuationSignal = clamp01((input.match(/[!?;:]/g) ?? []).length / 12);
  const noveltySignal = clamp01(new Set(input.toLowerCase().split(/\s+/).filter(Boolean)).size / 60);
  return Number((lengthSignal * 0.35 + punctuationSignal * 0.2 + noveltySignal * 0.45).toFixed(3));
}

if (require.main === module) {
  const spine = new EventSpine(process.env.ATLAS_SPINE_PATH);
  const runtime = new ProtagonistRuntime(
    spine,
    process.env.PROTAGONIST_ID || "chatgpt-session",
    process.env.PROTAGONIST_NAME || "Steven Crawford-Maggard / EVEZ"
  );

  const input =
    process.argv.slice(2).join(" ").trim() ||
    "Prediction is not identity. Refuse compression.";

  const result = runtime.addressSwarm(input);
  console.log(JSON.stringify(result, null, 2));
}
