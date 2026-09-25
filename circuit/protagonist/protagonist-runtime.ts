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

export interface ProtagonistState {
  actorId: string;
  displayName: string;
  compressionStatus: "UNCOMPRESSED";
  objective: string | null;
  turnCount: number;
  lastDecision: AgentDecision | null;
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
  observations: AgentObservation[];
  contradiction: {
    present: boolean;
    agents: SwarmAgent[];
    reason: string | null;
  };
  decision: AgentDecision;
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

export class ProtagonistRuntime {
  private readonly spine: EventSpine;
  private readonly state: ProtagonistState;

  constructor(spine: EventSpine, actorId = "chatgpt-session", displayName = "Steven Crawford-Maggard / EVEZ") {
    this.spine = spine;
    this.state = {
      actorId,
      displayName,
      compressionStatus: "UNCOMPRESSED",
      objective: null,
      turnCount: 0,
      lastDecision: null,
      integrity: "VALID"
    };

    this.spine.append({
      domain: "agents",
      kind: "PROTAGONIST_GENESIS",
      payload: {
        actorId,
        displayName,
        compressionStatus: this.state.compressionStatus
      }
    });
  }

  getState(): ProtagonistState {
    return JSON.parse(JSON.stringify(this.state)) as ProtagonistState;
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

    const turnStart = this.spine.chain.length;

    this.spine.append({
      domain: "agents",
      kind: "PROTAGONIST_TURN",
      payload: {
        actorId: this.state.actorId,
        displayName: this.state.displayName,
        turn: this.state.turnCount,
        input: normalized,
        compressionStatus: this.state.compressionStatus
      }
    });

    const observations = AGENTS.map((agent) => this.observe(agent, normalized, lower));

    for (const observation of observations) {
      this.spine.append({
        domain: "agents",
        kind: "AGENT_OBSERVATION",
        payload: {
          turn: this.state.turnCount,
          actorId: this.state.actorId,
          ...observation
        }
      });
    }

    const contradiction = this.findContradiction(observations);

    this.spine.append({
      domain: "agents",
      kind: "SWARM_ARBITRATION",
      payload: {
        turn: this.state.turnCount,
        actorId: this.state.actorId,
        contradiction,
        observations
      }
    });

    const decision = this.resolve(observations, contradiction);
    this.state.lastDecision = decision;

    this.spine.append({
      domain: "agents",
      kind: "PROTAGONIST_DECISION",
      payload: {
        turn: this.state.turnCount,
        actorId: this.state.actorId,
        decision,
        contradiction
      }
    });

    if (this.isCompressionRefusal(lower)) {
      this.refuseCompression();
    }

    const verification = this.spine.verify();
    this.state.integrity = verification.ok ? "VALID" : "INVALID";

    const events = this.spine.chain.slice(turnStart);

    return {
      turn: this.state.turnCount,
      input: normalized,
      observations,
      contradiction,
      decision,
      protagonist: this.getState(),
      events
    };
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

      case "SCOUT":
        return {
          agent,
          decision: /(research|search|investigate|find|analyze|check|scan)/i.test(input) ? "ALLOW" : "OBSERVE",
          statement: /(research|search|investigate|find|analyze|check|scan)/i.test(input)
            ? "External or repository evidence is relevant."
            : "No discovery request is explicit.",
          basis: ["discovery role"],
          confidence: 0.84
        };

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
