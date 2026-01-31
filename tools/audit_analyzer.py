"""Analyze audit logs for summary counts and anomalies."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable


def load_audit_entries(path: Path) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    if not path.exists():
        return entries
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    return entries


def build_summary(entries: Iterable[dict[str, Any]]) -> dict[str, Dict[Any, int]]:
    endpoint_counts: Counter[str] = Counter()
    tier_counts: Counter[Any] = Counter()
    status_counts: Counter[str] = Counter()

    total_entries = 0
    for entry in entries:
        total_entries += 1
        endpoint_counts[entry.get("endpoint", "unknown")] += 1
        tier_counts[entry.get("tier", "unknown")] += 1
        result = entry.get("result", {})
        if isinstance(result, dict) and "status" in result:
            status_counts[result["status"]] += 1

    return {
        "total_entries": total_entries,
        "by_endpoint": dict(endpoint_counts),
        "by_tier": dict(tier_counts),
        "by_status": dict(status_counts),
    }


def analyze_anomalies(entries: Iterable[dict[str, Any]]) -> dict[str, Any]:
    instantiation_times = []
    for entry in entries:
        result = entry.get("result", {})
        if isinstance(result, dict) and "instantiation_timestamp" in result:
            instantiation_times.append(result["instantiation_timestamp"])

    if not instantiation_times:
        return {
            "status": "skipped",
            "reason": "missing instantiation timestamps",
            "items": [],
        }

    anomalies = []
    for entry in entries:
        result = entry.get("result", {})
        if not isinstance(result, dict):
            continue
        instantiation_timestamp = result.get("instantiation_timestamp")
        if instantiation_timestamp is None:
            continue
        audit_timestamp = entry.get("timestamp")
        if audit_timestamp is None:
            continue
        if instantiation_timestamp > audit_timestamp:
            anomalies.append(
                {
                    "entity_id": entry.get("entity_id"),
                    "issue": "instantiation_after_audit",
                    "instantiation_timestamp": instantiation_timestamp,
                    "audit_timestamp": audit_timestamp,
                }
            )

    return {
        "status": "ok" if not anomalies else "flagged",
        "items": anomalies,
    }


def analyze_audit_log(path: Path) -> dict[str, Any]:
    entries = load_audit_entries(path)
    return {
        "summary": build_summary(entries),
        "anomalies": analyze_anomalies(entries),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze audit logs.")
    parser.add_argument(
        "--audit-log",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "src" / "memory" / "audit.jsonl",
    )
    parser.add_argument("--api-key", required=True)
    parser.add_argument("--api-base", required=True)
    args = parser.parse_args()

    analysis = analyze_audit_log(args.audit_log)
    print(json.dumps(analysis, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
