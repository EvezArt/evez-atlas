#!/usr/bin/env python3
"""Analyze audit logs for time-order anomalies (local-only, consent-only)."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import httpx

BASE_DIR = Path(__file__).resolve().parents[1]
AUDIT_LOG_PATH = BASE_DIR / "src" / "memory" / "audit.jsonl"
OUT_DIR = BASE_DIR / "tools" / "out"
TIER_PUBLIC = 0
SUSPICIOUS_ENDPOINTS = {"/navigation-ui", "/navigation-ui/data", "/legion-status"}


@dataclass
class AuditEntry:
    output_id: str
    endpoint: str
    api_key: str
    timestamp: Optional[float]
    tier: int = 0
    source_ip: str = "unknown"


def _parse_timestamp(value: Any) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
            return dt.timestamp()
        except ValueError:
            return None
    return None


def load_audit_entries(path: Path) -> List[AuditEntry]:
    entries: List[AuditEntry] = []
    if not path.exists():
        return entries
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        endpoint = record.get("endpoint", "")
        output_id = (
            record.get("output_id")
            or record.get("entity_id")
            or record.get("result", {}).get("output_id")
            or "unknown"
        )
        # Prefer explicit api_key, then api_key_id, then fingerprint to handle evolving log formats.
        api_key = (
            record.get("api_key")
            or record.get("api_key_id")
            or record.get("api_key_fingerprint")
            or "unknown"
        )
        entries.append(
            AuditEntry(
                output_id=output_id,
                endpoint=endpoint,
                api_key=api_key,
                timestamp=_parse_timestamp(record.get("timestamp")),
                tier=int(record.get("tier", 0)),
                source_ip=record.get("source_ip", "unknown"),
            )
        )
    return entries


def summarize(entries: Iterable[AuditEntry]) -> Dict[str, Any]:
    by_api_key = Counter()
    by_endpoint = Counter()
    by_output_id = Counter()
    by_source_ip = Counter()
    by_tier = Counter()
    total = 0
    for entry in entries:
        total += 1
        by_api_key[entry.api_key] += 1
        by_endpoint[entry.endpoint] += 1
        by_output_id[entry.output_id] += 1
        by_source_ip[entry.source_ip] += 1
        by_tier[entry.tier] += 1
    return {
        "total_records": total,
        "by_api_key": dict(by_api_key),
        "by_endpoint": dict(by_endpoint),
        "by_output_id": dict(by_output_id),
        "by_source_ip": dict(by_source_ip),
        "by_tier": dict(by_tier),
    }


def fetch_instantiation_timestamps(api_base: str, api_key: str) -> Dict[str, float]:
    instantiation_map: Dict[str, float] = {}
    try:
        with httpx.Client(timeout=5.0) as client:
            response = client.get(
                f"{api_base}/legion-status",
                headers={"X-API-Key": api_key},
            )
            response.raise_for_status()
            payload = response.json()
    except (httpx.RequestError, httpx.HTTPStatusError, ValueError):
        return instantiation_map

    for entity in payload.get("entities", []):
        output_id = entity.get("output_id")
        metadata = entity.get("metadata", {}) if isinstance(entity, dict) else {}
        for key in ("instantiated_at", "created_at", "timestamp"):
            if key in metadata:
                ts = _parse_timestamp(metadata.get(key))
                if ts is not None and output_id:
                    instantiation_map[output_id] = ts
                    break
    return instantiation_map


def detect_anomalies(
    entries: Iterable[AuditEntry],
    instantiation_map: Dict[str, float],
) -> List[Dict[str, Any]]:
    entry_list = list(entries)
    resolve_entries = []
    exposure_entries = []
    for entry in entry_list:
        if "/resolve-awareness" in entry.endpoint:
            resolve_entries.append(entry)
        if entry.endpoint in SUSPICIOUS_ENDPOINTS:
            exposure_entries.append(entry)
    first_seen: Dict[str, float] = {}
    for entry in resolve_entries:
        if entry.timestamp is None:
            continue
        if entry.output_id not in first_seen or entry.timestamp < first_seen[entry.output_id]:
            first_seen[entry.output_id] = entry.timestamp

    anomalies: List[Dict[str, Any]] = []
    for output_id, first_timestamp in first_seen.items():
        instantiated_at = instantiation_map.get(output_id)
        if instantiated_at is None:
            anomalies.append(
                {
                    "output_id": output_id,
                    "first_audit_timestamp": first_timestamp,
                    "reason": "no_instantiation_timestamp_available",
                }
            )
            continue
        if instantiated_at > first_timestamp:
            anomalies.append(
                {
                    "output_id": output_id,
                    "first_audit_timestamp": first_timestamp,
                    "instantiated_at": instantiated_at,
                    "delta_seconds": instantiated_at - first_timestamp,
                }
            )
    anomalies.extend(_detect_exposure_precursors(exposure_entries))
    return anomalies


def _detect_exposure_precursors(entries: Iterable[AuditEntry]) -> List[Dict[str, Any]]:
    suspicious: List[Dict[str, Any]] = []
    for entry in entries:
        if entry.api_key == "unknown":
            continue
        if entry.endpoint.startswith("/navigation-ui"):
            suspicious.append(
                {
                    "output_id": entry.output_id,
                    "endpoint": entry.endpoint,
                    "api_key": entry.api_key,
                    "source_ip": entry.source_ip,
                    "reason": "navigation_access",
                    "tier": entry.tier,
                    "first_audit_timestamp": entry.timestamp,
                }
            )
            continue
        if entry.endpoint == "/legion-status" and entry.tier == TIER_PUBLIC:
            suspicious.append(
                {
                    "output_id": entry.output_id,
                    "endpoint": entry.endpoint,
                    "api_key": entry.api_key,
                    "source_ip": entry.source_ip,
                    "reason": "broad_enumeration",
                    "tier": entry.tier,
                    "first_audit_timestamp": entry.timestamp,
                }
            )
    return suspicious


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--api-key", default="tier3_director")
    parser.add_argument("--api-base", default="http://localhost:8000")
    parser.add_argument("--audit-log", default=str(AUDIT_LOG_PATH))
    args = parser.parse_args()

    audit_path = Path(args.audit_log)
    entries = load_audit_entries(audit_path)

    summary = summarize(entries)
    write_json(OUT_DIR / "audit_summary.json", summary)

    instantiation_map = fetch_instantiation_timestamps(args.api_base, args.api_key)
    anomalies = detect_anomalies(entries, instantiation_map)
    write_json(OUT_DIR / "anomalies.json", anomalies)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
