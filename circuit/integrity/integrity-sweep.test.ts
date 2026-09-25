import assert from "assert";
import crypto from "crypto";
import fs from "fs";
import os from "os";
import path from "path";

import { EventSpine } from "../event-spine/event-spine";
import { ProtagonistRuntime } from "../protagonist/protagonist-runtime";
import { MultiViewVerifier } from "../../referee/multi-view";
import { ChallengeEngine } from "../../referee/challenge-engine";
import { AuthoritativeGameServer } from "../../game/server";
import { AgentNavigation } from "../../src/autonomy/navigation";
import { LimitBypassHandler } from "../../src/autonomy/limit-bypass";

function testChallengeEngine() {
  const spine = new EventSpine();
  const challengeEngine = new ChallengeEngine(spine);

  const capability = challengeEngine.issue("test-agent", "capability");
  const expected = crypto.createHash("sha256").update("atlas-v3").digest("hex");

  assert.equal(challengeEngine.verify(capability.id, expected).passed, true);
  assert.equal(challengeEngine.verify(capability.id, "not-the-answer").passed, false);

  const marker = spine.append({
    domain: "agents",
    kind: "AGENT_STATE",
    payload: { actorId: "test-agent", state: "READY" }
  });

  const integrity = challengeEngine.issue("test-agent", "integrity");
  assert.equal(challengeEngine.verify(integrity.id, marker.hash).passed, true);

  spine.append({
    domain: "agents",
    kind: "AGENT_STATE",
    payload: { actorId: "test-agent", state: "CHANGED" }
  });

  assert.equal(challengeEngine.verify(integrity.id, marker.hash).passed, false);
}

function testMultiViewCanonicalization() {
  const spine = new EventSpine();
  const verifier = new MultiViewVerifier(spine);

  const consistent = verifier.verify([
    { source: "a", timestamp: "t1", data: { z: 3, a: 1, nested: { b: 2, a: 1 } } },
    { source: "b", timestamp: "t2", data: { a: 1, nested: { a: 1, b: 2 }, z: 3 } }
  ]);

  assert.equal(consistent.consistent, true);

  const mismatch = verifier.verify([
    { source: "a", timestamp: "t1", data: { value: 1 } },
    { source: "b", timestamp: "t2", data: { value: 2 } },
    { source: "c", timestamp: "t3", data: { value: 3 } }
  ]);

  assert.equal(mismatch.consistent, false);
  assert.equal(mismatch.residue.mismatchCount, 2);
}

function testGameRollback() {
  const spine = new EventSpine();
  const server = new AuthoritativeGameServer(spine, "test-match");

  server.addPlayer("p1");
  server.processInput("p1", { dx: 2, dy: 3 });
  server.tick();

  server.processInput("p1", { dx: 7, dy: 8 });
  server.tick();

  assert.deepEqual(server.getState().players.p1, { x: 9, y: 11, health: 100 });

  server.rollback(1);

  assert.equal(server.getState().tick, 1);
  assert.deepEqual(server.getState().players.p1, { x: 2, y: 3, health: 100 });
  assert.equal(
    spine.chain.some((event) => event.kind === "ROLLBACK_APPLIED"),
    true
  );
}

async function testLimitRecoveryPolicy() {
  const spine = new EventSpine();
  const manifestPath = path.join(process.cwd(), "src", "autonomy", "agent_manifest.json");
  const navigation = new AgentNavigation(manifestPath);

  const legacyCompatible = new LimitBypassHandler(navigation, spine, { maxRetries: 0 });
  const result = await legacyCompatible.detectAndBypass(
    new Error("unauthorized"),
    "protected-operation"
  );

  assert.equal(result.success, false);
  assert.equal(result.applied, false);
  assert.ok(result.error);
  assert.equal(
    spine.chain.some((event) => event.kind === "RECOVERY_PROPOSED"),
    true
  );
}

function testPersistenceRejectsTamper() {
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), "atlas-integrity-"));
  const journalPath = path.join(directory, "events.jsonl");

  try {
    const spine = new EventSpine(journalPath);
    spine.append({
      domain: "atlas",
      kind: "INTEGRITY_TEST",
      payload: { value: 1 }
    });

    const tampered = JSON.parse(fs.readFileSync(journalPath, "utf8").trim());
    tampered.payload.value = 999;
    fs.writeFileSync(journalPath, JSON.stringify(tampered) + "\n", "utf8");

    assert.throws(() => new EventSpine(journalPath), /Refusing corrupt EventSpine journal/);
  } finally {
    fs.rmSync(directory, { recursive: true, force: true });
  }
}

async function run() {
  const spine = new EventSpine();
  const protagonist = new ProtagonistRuntime(spine, "sweep", "Integrity Sweep");

  const first = protagonist.addressSwarm("build the witness");
  const second = protagonist.addressSwarm("build the witness");

  assert.equal(first.metrics.predictionError, 1);
  assert.equal(second.metrics.predictionError, 0);
  assert.equal(protagonist.replay().integrity.ok, true);

  testChallengeEngine();
  testMultiViewCanonicalization();
  testGameRollback();
  await testLimitRecoveryPolicy();
  testPersistenceRejectsTamper();

  console.log(JSON.stringify({
    sweep: "PASS",
    protagonist: {
      turns: 2,
      firstPredictionError: first.metrics.predictionError,
      secondPredictionError: second.metrics.predictionError
    },
    modules: [
      "EventSpine persistence/tamper rejection",
      "Protagonist replay/prediction error",
      "ChallengeEngine evidence verification",
      "MultiView canonical comparison",
      "Authoritative game rollback",
      "Authorization-safe limit recovery"
    ]
  }, null, 2));
}

run().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
