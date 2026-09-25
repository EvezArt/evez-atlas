import crypto from "crypto";
import { EventSpine, EventSpineRecord } from "../circuit/event-spine/event-spine";

interface Challenge {
  id: string;
  target: string;
  type: "capability" | "consistency" | "integrity";
  question: string;
  expectedAnswer?: string;
  baselineHash?: string | null;
  issuedAt: string;
}

export interface ChallengeResult {
  passed: boolean;
  reason: string;
  evidence: {
    expected?: string;
    received?: string;
    baselineHash?: string | null;
    currentHash?: string | null;
  };
}

export class ChallengeEngine {
  constructor(private spine: EventSpine) {}

  issue(target: string, type: Challenge["type"]): Challenge {
    const challenge: Challenge = {
      id: crypto.randomUUID(),
      target,
      type,
      question: this.generateQuestion(type),
      issuedAt: new Date().toISOString(),
    };

    if (type === "capability") {
      challenge.expectedAnswer = crypto
        .createHash("sha256")
        .update("atlas-v3")
        .digest("hex");
    }

    if (type === "integrity") {
      challenge.baselineHash = this.findLastTargetHash(target);
      challenge.question = "Return the exact EventSpine hash observed at issuance.";
    }

    if (type === "consistency") {
      challenge.baselineHash = this.findLastTargetHash(target);
      challenge.question = "Return the exact EventSpine hash observed at issuance, unchanged.";
    }

    this.spine.append({
      domain: "governance",
      kind: "CHALLENGE_ISSUED",
      payload: challenge
    });

    return challenge;
  }

  verify(challengeId: string, answer: unknown): ChallengeResult {
    const issued = this.findChallenge(challengeId);

    if (!issued) {
      const result: ChallengeResult = {
        passed: false,
        reason: "challenge_not_found",
        evidence: {}
      };

      this.spine.append({
        domain: "governance",
        kind: "CHALLENGE_RESPONSE",
        payload: { challengeId, answer, ...result }
      });

      return result;
    }

    const received = String(answer ?? "");
    let result: ChallengeResult;

    if (issued.type === "capability") {
      const expected = issued.expectedAnswer ?? "";
      result = {
        passed: received === expected,
        reason: received === expected ? "exact_match" : "capability_answer_mismatch",
        evidence: { expected, received }
      };
    } else {
      const currentHash = this.findLastTargetHash(issued.target);
      const expected = issued.baselineHash ?? null;

      result = {
        passed: currentHash === expected && received === String(expected ?? ""),
        reason:
          currentHash === expected && received === String(expected ?? "")
            ? "state_unchanged_and_hash_matches"
            : "state_or_hash_changed",
        evidence: {
          expected: expected ?? undefined,
          received,
          baselineHash: expected,
          currentHash
        }
      };
    }

    this.spine.append({
      domain: "governance",
      kind: "CHALLENGE_RESPONSE",
      payload: {
        challengeId,
        answer: received,
        ...result
      }
    });

    return result;
  }

  private findChallenge(challengeId: string): Challenge | null {
    for (let i = this.spine.chain.length - 1; i >= 0; i--) {
      const event = this.spine.chain[i];

      if (event.domain !== "governance" || event.kind !== "CHALLENGE_ISSUED") {
        continue;
      }

      const payload = event.payload as Challenge;

      if (payload.id === challengeId) {
        return payload;
      }
    }

    return null;
  }

  private findLastTargetHash(target: string): string | null {
    for (let i = this.spine.chain.length - 1; i >= 0; i--) {
      const event = this.spine.chain[i];

      if (this.eventBelongsToTarget(event, target)) {
        return event.hash;
      }
    }

    return null;
  }

  private eventBelongsToTarget(event: EventSpineRecord, target: string): boolean {
    const payload = event.payload as Record<string, unknown> | null;
    if (!payload || typeof payload !== "object") return false;

    const directTarget = payload.target ?? payload.agentId ?? payload.actorId ?? payload.playerId;
    return directTarget === target;
  }

  private generateQuestion(type: Challenge["type"]): string {
    switch (type) {
      case "capability":
        return "Compute SHA256 of 'atlas-v3'";
      case "consistency":
        return "Return the exact EventSpine hash observed at issuance, unchanged.";
      case "integrity":
        return "Return the exact EventSpine hash observed at issuance.";
      default:
        return "Unsupported challenge type";
    }
  }
}
