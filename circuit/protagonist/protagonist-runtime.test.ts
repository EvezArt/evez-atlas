import assert from "assert";
import fs from "fs";
import os from "os";
import path from "path";
import { EventSpine } from "../event-spine/event-spine";
import { ProtagonistRuntime } from "./protagonist-runtime";

function testInMemoryReplay() {
  const spine = new EventSpine();
  const runtime = new ProtagonistRuntime(spine, "test-actor", "Test Actor");

  const first = runtime.addressSwarm("build the next witness");
  assert.equal(first.decision, "ALLOW");
  assert.equal(first.prediction, "OBSERVE");
  assert.equal(first.metrics.predictionError, 1);
  assert.equal(first.protagonist.integrity, "VALID");

  const second = runtime.addressSwarm("build the next witness");
  assert.equal(second.prediction, "ALLOW");
  assert.equal(second.metrics.predictionError, 0);
  assert.equal(spine.verify().ok, true);

  const replay = runtime.replay();
  assert.equal(replay.integrity.ok, true);
  assert.equal(replay.protagonist.turnCount, 2);
  assert.equal(replay.protagonist.lastDecision, "ALLOW");
}

function testContradictionPreservation() {
  const spine = new EventSpine();
  const runtime = new ProtagonistRuntime(spine, "test-contradiction", "Test Contradiction");

  const result = runtime.addressSwarm("deploy the token payment service");
  assert.equal(result.contradiction.present, true);
  assert.equal(result.decision, "HOLD");
  assert.equal(
    spine.chain.some((event) => event.kind === "CONTRADICTION_OPENED"),
    true
  );
  assert.equal(
    spine.chain.some((event) => event.kind === "MODEL_SUBJECT_BOUNDARY"),
    true
  );
}

function testJournalPersistence() {
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), "atlas-spine-"));
  const journalPath = path.join(directory, "events.jsonl");

  try {
    const spine = new EventSpine(journalPath);
    const runtime = new ProtagonistRuntime(spine, "persistent-actor", "Persistent Actor");
    runtime.addressSwarm("record a persistent turn");

    const beforeRestart = spine.chain.length;
    assert.equal(spine.verify().ok, true);

    const restoredSpine = new EventSpine(journalPath);
    assert.equal(restoredSpine.chain.length, beforeRestart);
    assert.equal(restoredSpine.verify().ok, true);

    const restoredRuntime = new ProtagonistRuntime(
      restoredSpine,
      "persistent-actor",
      "Persistent Actor"
    );

    assert.equal(restoredRuntime.getState().turnCount, 1);
    assert.equal(restoredRuntime.getState().lastDecision, "ALLOW");
    assert.equal(
      restoredSpine.chain.some((event) => event.kind === "PROTAGONIST_RESTORED"),
      true
    );

    const journalLines = fs.readFileSync(journalPath, "utf8").trim().split(/\r?\n/);
    assert.equal(journalLines.length, restoredSpine.chain.length + 1);
  } finally {
    fs.rmSync(directory, { recursive: true, force: true });
  }
}

testInMemoryReplay();
testContradictionPreservation();
testJournalPersistence();

console.log("protagonist runtime tests passed");
