import crypto from "crypto";
import fs from "fs";
import path from "path";

export type AtlasDomain =
  | "atlas"
  | "game"
  | "agents"
  | "fsc"
  | "governance"
  | "observability";

export interface EventSpineRecord<T = any> {
  id: string;
  index: number;
  timestamp: string;
  domain: AtlasDomain;
  kind: string;
  payload: T;
  prevHash: string | null;
  hash: string;
}

export class EventSpine {
  private _chain: EventSpineRecord[] = [];
  private readonly journalPath?: string;

  constructor(journalPath?: string) {
    this.journalPath = journalPath || undefined;

    if (!this.journalPath) return;

    this.loadJournal();
  }

  get chain(): ReadonlyArray<EventSpineRecord> {
    return this._chain;
  }

  append<T = any>(event: {
    domain: AtlasDomain;
    kind: string;
    payload: T;
  }): EventSpineRecord<T> {
    const index = this._chain.length;
    const timestamp = new Date().toISOString();
    const prevHash = index === 0 ? null : this._chain[index - 1].hash;

    const id = crypto.randomUUID();
    const base = {
      id,
      index,
      timestamp,
      domain: event.domain,
      kind: event.kind,
      payload: event.payload,
      prevHash,
    };

    const hash = this.computeHash(base);
    const record: EventSpineRecord<T> = { ...base, hash };

    if (this.journalPath) {
      fs.appendFileSync(this.journalPath, JSON.stringify(record) + "\n", "utf8");
    }

    this._chain.push(record);
    return record;
  }

  replay(): EventSpineRecord[] {
    return [...this._chain];
  }

  verify(): { ok: boolean; error?: string; index?: number } {
    for (let i = 0; i < this._chain.length; i++) {
      const rec = this._chain[i];
      const expectedHash = this.computeHash({
        id: rec.id,
        index: rec.index,
        timestamp: rec.timestamp,
        domain: rec.domain,
        kind: rec.kind,
        payload: rec.payload,
        prevHash: rec.prevHash,
      });

      if (rec.index !== i) {
        return { ok: false, error: "bad_index", index: i };
      }

      if (rec.hash !== expectedHash) {
        return { ok: false, error: "hash_mismatch", index: i };
      }

      if (i === 0 && rec.prevHash !== null) {
        return { ok: false, error: "bad_prev_hash_genesis", index: i };
      }

      if (i > 0 && rec.prevHash !== this._chain[i - 1].hash) {
        return { ok: false, error: "bad_prev_hash_link", index: i };
      }
    }

    return { ok: true };
  }

  toJSON(): EventSpineRecord[] {
    return this.replay();
  }

  static fromJSON(data: EventSpineRecord[]): EventSpine {
    const spine = new EventSpine();
    spine._chain = [...data];
    const verification = spine.verify();

    if (!verification.ok) {
      throw new Error(
        `Invalid EventSpine: ${verification.error} at index ${verification.index ?? "unknown"}`
      );
    }

    return spine;
  }

  private loadJournal(): void {
    if (!this.journalPath) return;

    const directory = path.dirname(this.journalPath);
    fs.mkdirSync(directory, { recursive: true });

    if (!fs.existsSync(this.journalPath)) return;

    const raw = fs.readFileSync(this.journalPath, "utf8").trim();
    if (!raw) return;

    const records = raw
      .split(/\r?\n/)
      .filter(Boolean)
      .map((line, lineIndex) => {
        try {
          return JSON.parse(line) as EventSpineRecord;
        } catch {
          throw new Error(`Invalid EventSpine journal JSON at line ${lineIndex + 1}`);
        }
      });

    this._chain = records;
    const verification = this.verify();

    if (!verification.ok) {
      throw new Error(
        `Refusing corrupt EventSpine journal: ${verification.error} at index ${verification.index ?? "unknown"}`
      );
    }
  }

  private computeHash(obj: any): string {
    const json = JSON.stringify(obj);
    return crypto.createHash("sha256").update(json).digest("hex");
  }
}
