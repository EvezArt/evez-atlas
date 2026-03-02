#!/usr/bin/env python3
"""
A012 State Adapter
Reads from EVEZ-OS workspace hyperloop_state.json and provides
a normalized interface for A012 to consume.

Usage: python3 data/a012/state_adapter.py [path_to_hyperloop_state.json]
"""
import json, sys, os

DEFAULT_STATE_PATH = os.path.join(
    os.path.dirname(__file__), "../../..", 
    "cells/599dc7f9-0b2b-4460-b917-5104fcbb91ef/workspace/hyperloop_state.json"
)

def load_state(path: str = None) -> dict:
    p = path or DEFAULT_STATE_PATH
    with open(p) as f:
        raw = json.load(f)

    # Normalize to A012 expected schema
    return {
        "round": raw.get("round", 0),
        "V": raw.get("V", raw.get("V_global", 0.0)),
        "V_global": raw.get("V", raw.get("V_global", 0.0)),
        "fire_count": raw.get("fire_count", 0),
        "last_tweet": raw.get("last_tweet", {}),
        "fire_rounds": [],  # populated from ledger; A012 builds this on first run
    }

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else None
    state = load_state(path)
    print(json.dumps(state, indent=2))
