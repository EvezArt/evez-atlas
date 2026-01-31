import importlib.util
import json
from pathlib import Path


def load_analyzer_module():
    module_path = Path(__file__).resolve().parents[3] / "tools" / "audit_analyzer.py"
    spec = importlib.util.spec_from_file_location("audit_analyzer", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_audit_summary_and_missing_instantiation_timestamps(tmp_path):
    audit_entries = [
        {
            "timestamp": 1710000000.0,
            "entity_id": "output-001",
            "endpoint": "/resolve-awareness",
            "tier": 1,
            "result": {"status": "stable"},
        },
        {
            "timestamp": 1710000001.0,
            "entity_id": "output-002",
            "endpoint": "/resolve-awareness",
            "tier": 2,
            "result": {"status": "degraded"},
        },
        {
            "timestamp": 1710000002.0,
            "entity_id": "legion",
            "endpoint": "/legion-status",
            "tier": 1,
            "result": {"count": 2},
        },
    ]
    audit_path = tmp_path / "audit.jsonl"
    audit_path.write_text("\n".join(json.dumps(entry) for entry in audit_entries))

    analyzer = load_analyzer_module()
    analysis = analyzer.analyze_audit_log(audit_path)

    summary = analysis["summary"]
    assert summary["total_entries"] == 3
    assert summary["by_endpoint"] == {"/resolve-awareness": 2, "/legion-status": 1}
    assert summary["by_tier"] == {1: 2, 2: 1}
    assert summary["by_status"] == {"stable": 1, "degraded": 1}

    anomalies = analysis["anomalies"]
    assert anomalies["status"] == "skipped"
    assert anomalies["reason"] == "missing instantiation timestamps"
    assert anomalies["items"] == []
