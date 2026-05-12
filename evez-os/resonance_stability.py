#!/usr/bin/env python3
"""
resonance_stability.py — Causal chain integrity validator.
"""
import json, hashlib
from pathlib import Path
from datetime import datetime, timezone

BASE = Path("/mnt/agents/output/evez-os")
STABILITY_LOG = BASE / "logs" / "resonance_stability.jsonl"
STABILITY_LOG.parent.mkdir(parents=True, exist_ok=True)

class ResonanceStability:
    def validate_chain(self, chain_id, events):
        violations = []
        for i in range(1, len(events)):
            prev, curr = events[i-1], events[i]
            if curr.get("tick", 0) != prev.get("tick", 0) + 1:
                violations.append({"type": "TEMPORAL_GAP", "at": i})
            expected_hash = hashlib.sha256(json.dumps(prev, sort_keys=True).encode()).hexdigest()[:16]
            if curr.get("prev_hash") != expected_hash:
                violations.append({"type": "HASH_BREAK", "at": i})
            if not self._valid_transition(prev.get("state"), curr.get("state")):
                violations.append({"type": "INVALID_STATE", "at": i})
        result = {
            "chain_id": chain_id,
            "validated_at": datetime.now(timezone.utc).isoformat(),
            "events": len(events),
            "violations": violations,
            "stable": len(violations) == 0
        }
        with open(STABILITY_LOG, "a") as f:
            f.write(json.dumps(result) + "
")
        return result

    def _valid_transition(self, from_state, to_state):
        valid = {
            "INIT": ["OBSERVE", "TEST"], "OBSERVE": ["EVALUATE", "HOLD"],
            "EVALUATE": ["ACT", "TEST", "HOLD"], "ACT": ["VERIFY", "COMMIT"],
            "VERIFY": ["COMMIT", "ROLLBACK"], "COMMIT": ["INIT", "OBSERVE"],
            "HOLD": ["OBSERVE", "TEST"], "TEST": ["EVALUATE", "HOLD"],
            "ROLLBACK": ["INIT", "OBSERVE"]
        }
        return to_state in valid.get(from_state, [])

if __name__ == "__main__":
    rs = ResonanceStability()
    chain = [
        {"tick": 1, "state": "INIT", "prev_hash": "0"*16},
        {"tick": 2, "state": "OBSERVE", "prev_hash": hashlib.sha256(json.dumps({"tick":1,"state":"INIT","prev_hash":"0"*16}, sort_keys=True).encode()).hexdigest()[:16]},
        {"tick": 3, "state": "EVALUATE", "prev_hash": "bad_hash"}
    ]
    print(json.dumps(rs.validate_chain("test_chain", chain), indent=2))
