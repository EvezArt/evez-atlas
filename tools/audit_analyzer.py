#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import httpx

DEFAULT_BASE_URL = "http://localhost:8000"
API_KEY = "tier3_director"
RESOLVE_ENDPOINT = "/resolve-awareness"
LEGION_STATUS_ENDPOINT = "/legion-status"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Analyze audit logs for /resolve-awareness entries and summarize usage."
        )
    )
    parser.add_argument(
        "--base-url",
        default=DEFAULT_BASE_URL,
        help="Base URL for the local API (default: http://localhost:8000)",
    )
    parser.add_argument(
        "--audit-path",
        type=Path,
        help="Optional path to audit.jsonl (defaults to src/memory/audit.jsonl)",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        help="Optional output directory (defaults to tools/out)",
    )
    return parser.parse_args()


def load_audit_entries(audit_path: Path) -> list[dict[str, Any]]:
    if not audit_path.exists():
        return []
    entries: list[dict[str, Any]] = []
    with audit_path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                payload = json.loads(stripped)
            except json.JSONDecodeError as exc:
                print(
                    f"Skipping invalid JSON at line {line_number}: {exc}",
                    file=sys.stderr,
                )
                continue
            if isinstance(payload, dict):
                entries.append(payload)
            else:
                print(
                    f"Skipping non-object JSON at line {line_number}",
                    file=sys.stderr,
                )
    return entries


def extract_output_id(entry: dict[str, Any]) -> str | None:
    if isinstance(entry.get("entity_id"), str):
        return entry["entity_id"]
    result = entry.get("result")
    if isinstance(result, dict) and isinstance(result.get("output_id"), str):
        return result["output_id"]
    return None


def extract_api_key(entry: dict[str, Any]) -> str:
    if isinstance(entry.get("api_key"), str):
        return entry["api_key"]
    result = entry.get("result")
    if isinstance(result, dict) and isinstance(result.get("api_key"), str):
        return result["api_key"]
    return "unknown"


def collect_instantiation_map(client: httpx.Client) -> dict[str, Any]:
    instantiation_map: dict[str, Any] = {}
    response = client.get(LEGION_STATUS_ENDPOINT)
    response.raise_for_status()
    payload = response.json()
    entities = payload.get("entities", [])
    if isinstance(entities, list):
        for entity in entities:
            if not isinstance(entity, dict):
                continue
            output_id = entity.get("output_id")
            timestamp = entity.get("instantiation_timestamp")
            if output_id and timestamp is not None:
                instantiation_map[str(output_id)] = timestamp
    return instantiation_map


def fetch_instantiation_timestamp(
    client: httpx.Client, output_id: str
) -> tuple[bool, Any]:
    response = client.post(RESOLVE_ENDPOINT, json={"output_id": output_id})
    response.raise_for_status()
    payload = response.json()
    timestamp = payload.get("instantiation_timestamp")
    if timestamp is not None:
        return True, timestamp
    return False, None


def main() -> int:
    args = parse_args()
    base_dir = Path(__file__).resolve().parents[1]
    audit_path = args.audit_path or base_dir / "src" / "memory" / "audit.jsonl"
    out_dir = args.out_dir or base_dir / "tools" / "out"
    out_dir.mkdir(parents=True, exist_ok=True)

    entries = load_audit_entries(audit_path)
    resolve_entries = [
        entry
        for entry in entries
        if entry.get("endpoint") == RESOLVE_ENDPOINT
    ]

    api_key_counter = Counter()
    endpoint_counter = Counter()
    output_id_counter = Counter()
    output_ids: set[str] = set()

    for entry in resolve_entries:
        api_key_counter[extract_api_key(entry)] += 1
        endpoint = entry.get("endpoint") or "unknown"
        endpoint_counter[str(endpoint)] += 1
        output_id = extract_output_id(entry) or "unknown"
        output_id_counter[output_id] += 1
        if output_id != "unknown":
            output_ids.add(output_id)

    audit_summary = {
        "total_entries": len(resolve_entries),
        "counts": {
            "api_key": dict(api_key_counter),
            "endpoint": dict(endpoint_counter),
            "output_id": dict(output_id_counter),
        },
    }

    anomalies: list[dict[str, Any]] = []
    headers = {"X-API-Key": API_KEY}

    try:
        with httpx.Client(base_url=args.base_url, headers=headers, timeout=10.0) as client:
            instantiation_map = collect_instantiation_map(client)
            for output_id in sorted(output_ids):
                timestamp = instantiation_map.get(output_id)
                if timestamp is None:
                    try:
                        found, timestamp = fetch_instantiation_timestamp(client, output_id)
                    except httpx.HTTPError as exc:
                        anomalies.append(
                            {
                                "output_id": output_id,
                                "reason": "no_instantiation_timestamp_available",
                                "details": str(exc),
                            }
                        )
                        continue
                    if not found:
                        anomalies.append(
                            {
                                "output_id": output_id,
                                "reason": "no_instantiation_timestamp_available",
                            }
                        )
                else:
                    instantiation_map[output_id] = timestamp
    except httpx.HTTPError as exc:
        for output_id in sorted(output_ids):
            anomalies.append(
                {
                    "output_id": output_id,
                    "reason": "no_instantiation_timestamp_available",
                    "details": str(exc),
                }
            )

    (out_dir / "audit_summary.json").write_text(
        json.dumps(audit_summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (out_dir / "anomalies.json").write_text(
        json.dumps(anomalies, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
