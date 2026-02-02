import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[3]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from tools import audit_analyzer


def write_audit_log(path: Path, entries):
    content = "\n".join(json.dumps(entry) for entry in entries)
    path.write_text(content, encoding="utf-8")


def test_summary_and_anomaly_degradation(tmp_path):
    audit_path = tmp_path / "audit.jsonl"
    entries = [
        {
            "timestamp": 1700000000.0,
            "entity_id": "output-001",
            "endpoint": "/resolve-awareness",
            "tier": 3,
            "api_key_id": "tier3_director",
            "source_ip": "127.0.0.1",
            "result": {"output_id": "output-001"},
        },
        {
            "timestamp": 1700000010.0,
            "entity_id": "output-002",
            "endpoint": "/resolve-awareness",
            "tier": 1,
            "api_key_id": "tier1_builder",
            "source_ip": "127.0.0.1",
            "result": {"output_id": "output-002"},
        },
        {
            "timestamp": 1700000020.0,
            "entity_id": "legion",
            "endpoint": "/legion-status",
            "tier": 0,
            "api_key_id": "tier0_public",
            "source_ip": "127.0.0.1",
            "result": {"count": 2, "entities": []},
        },
    ]
    write_audit_log(audit_path, entries)

    audit_entries = audit_analyzer.load_audit_entries(audit_path)
    summary = audit_analyzer.summarize(audit_entries)

    assert summary["total_records"] == 3
    assert summary["by_api_key"]["tier3_director"] == 1
    assert summary["by_output_id"]["output-002"] == 1
    assert summary["by_source_ip"]["127.0.0.1"] == 3
    assert summary["by_tier"][0] == 1

    anomalies = audit_analyzer.detect_anomalies(audit_entries, {})
    reasons = {anomaly["reason"] for anomaly in anomalies}
    assert "no_instantiation_timestamp_available" in reasons
    assert "broad_enumeration" in reasons
