"""ETL skeleton for MarineCadastreAIS.
Populate API keys in environment variables and replace placeholders.
All requests must respect terms of service and applicable law.
"""

from pathlib import Path
import os, json, time

def run(config):
    # TODO: implement API pulls and write normalized JSONL to data/...
    out = Path(config.get("out_dir", "data")) / "ais_tracks.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)
    # Placeholder example record
    record = {"source":"MarineCadastreAIS","status":"placeholder","ts":time.time()}
    with open(out, "a") as f:
        f.write(json.dumps(record) + "\n")
    return str(out)
