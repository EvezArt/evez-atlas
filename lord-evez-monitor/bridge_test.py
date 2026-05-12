#!/usr/bin/env python3
"""
bridge_test.py — Payload activity test for LORD -> EVEZ bridge
"""
import json
from datetime import datetime, timezone

def test_bridge(payload):
    required_fields = ["source", "action", "timestamp", "payload"]
    missing = [f for f in required_fields if f not in payload]
    if missing:
        return {"status": "FAIL", "missing": missing, "cors": "no-cors-required"}
    return {
        "status": "PASS",
        "source": payload["source"],
        "action": payload["action"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "cors": "no-cors-required"
    }

if __name__ == "__main__":
    demo = {"source": "LORD", "action": "spawn_agent", "timestamp": "2026-05-12T00:00:00Z", "payload": {"agent_type": "explorer"}}
    print(json.dumps(test_bridge(demo), indent=2))
