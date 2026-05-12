"""Tile scoring for multi-modal convergence.
This is a stub. Replace with real loaders and z-score logic."""

import json
from pathlib import Path

def score_tile(tile_id, features):
    # features: dict with z_sar, z_ntl, infra_flag, procurement_nearby, traffic_flag
    w = {"z_sar":0.35, "z_ntl":0.25, "infra_flag":0.15, "procurement_nearby":0.15, "traffic_flag":0.10}
    s = sum(w[k]*features.get(k,0) for k in w)
    return s

if __name__ == "__main__":
    demo = {"z_sar":2.3, "z_ntl":1.8, "infra_flag":1, "procurement_nearby":1, "traffic_flag":0}
    print(score_tile("tile_001", demo))
