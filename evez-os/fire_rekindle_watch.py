#!/usr/bin/env python3
"""
fire_rekindle_watch.py — Resonance stability monitor.
"""
import json
from pathlib import Path
from datetime import datetime, timezone

BASE = Path("/mnt/agents/output/evez-os")
WATCH_LOG = BASE / "logs" / "rekindle_watch.jsonl"
WATCH_LOG.parent.mkdir(parents=True, exist_ok=True)

class RekindleWatch:
    V_THRESHOLD = 5.0
    DECAY_RATE = 0.05

    def __init__(self):
        self.loops = {}

    def register_loop(self, name, initial_V, max_rounds=500):
        self.loops[name] = {"V": initial_V, "R": 0, "FIRE": 0.5, "max_rounds": max_rounds, "alive": True}

    def tick(self, name):
        loop = self.loops.get(name)
        if not loop or not loop["alive"]:
            return None
        loop["V"] *= (1 - self.DECAY_RATE)
        loop["R"] += 1
        if loop["V"] < self.V_THRESHOLD:
            loop["alive"] = False
            return {"status": "DEATH", "loop": name, "final_V": loop["V"]}
        if loop["R"] >= loop["max_rounds"]:
            loop["alive"] = False
            return {"status": "RETIRE", "loop": name, "rounds": loop["R"]}
        if loop["V"] < self.V_THRESHOLD * 1.5:
            return {"status": "REKINDLE", "loop": name, "V": loop["V"]}
        return {"status": "ALIVE", "loop": name, "V": loop["V"], "R": loop["R"]}

if __name__ == "__main__":
    watch = RekindleWatch()
    watch.register_loop("revenue_6h", 17.48)
    for _ in range(20):
        result = watch.tick("revenue_6h")
        print(result)
        if result["status"] in ("DEATH", "RETIRE"):
            break
