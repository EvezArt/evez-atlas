import { EventSpine } from "../circuit/event-spine/event-spine";

interface View {
  source: string;
  timestamp: string;
  data: any;
}

function canonicalize(value: any): any {
  if (Array.isArray(value)) return value.map(canonicalize);

  if (value && typeof value === "object") {
    return Object.keys(value)
      .sort()
      .reduce((result: Record<string, any>, key) => {
        result[key] = canonicalize(value[key]);
        return result;
      }, {});
  }

  return value;
}

function canonicalJson(value: any): string {
  return JSON.stringify(canonicalize(value));
}

export class MultiViewVerifier {
  constructor(private spine: EventSpine) {}

  verify(views: View[]): { consistent: boolean; residue?: any } {
    if (views.length < 2) {
      this.spine.append({
        domain: "governance",
        kind: "MULTI_VIEW_INSUFFICIENT",
        payload: { viewCount: views.length }
      });
      return { consistent: true };
    }

    const baseline = canonicalJson(views[0].data);
    const mismatches: Array<{
      source1: string;
      source2: string;
      baselineHash: string;
      observedHash: string;
      diff: "mismatch_detected";
    }> = [];

    for (let i = 1; i < views.length; i++) {
      const observed = canonicalJson(views[i].data);
      if (observed !== baseline) {
        mismatches.push({
          source1: views[0].source,
          source2: views[i].source,
          baselineHash: hash(baseline),
          observedHash: hash(observed),
          diff: "mismatch_detected"
        });
      }
    }

    if (mismatches.length > 0) {
      this.spine.append({
        domain: "governance",
        kind: "MULTI_VIEW_MISMATCH",
        payload: {
          viewCount: views.length,
          mismatchCount: mismatches.length,
          mismatches
        }
      });

      return {
        consistent: false,
        residue: { mismatchCount: mismatches.length, mismatches }
      };
    }

    this.spine.append({
      domain: "governance",
      kind: "MULTI_VIEW_CONSISTENT",
      payload: {
        viewCount: views.length,
        canonicalHash: hash(baseline)
      }
    });

    return { consistent: true };
  }
}

function hash(value: string): string {
  let h1 = 0xdeadbeef;
  let h2 = 0x41c6ce57;

  for (let i = 0; i < value.length; i++) {
    const ch = value.charCodeAt(i);
    h1 = Math.imul(h1 ^ ch, 2654435761);
    h2 = Math.imul(h2 ^ ch, 1597334677);
  }

  return (h1 >>> 0).toString(16).padStart(8, "0") +
    (h2 >>> 0).toString(16).padStart(8, "0");
}
