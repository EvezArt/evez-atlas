#!/usr/bin/env python3
"""
Debrief script for automation assistant telemetry

Reads telemetry from src/memory/audit.jsonl and generates a summary report.
"""

import json
import statistics
from pathlib import Path
from collections import defaultdict
from typing import List, Dict, Any


def load_telemetry(audit_file: str = "src/memory/audit.jsonl") -> List[Dict[str, Any]]:
    """Load all telemetry entries from the audit file."""
    entries = []
    audit_path = Path(audit_file)
    
    if not audit_path.exists():
        return entries
    
    with open(audit_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                # Filter for automation assistant events (those with run_id)
                if 'run_id' in entry:
                    entries.append(entry)
            except json.JSONDecodeError:
                continue
    
    return entries


def analyze_telemetry(entries: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze telemetry entries and compute statistics."""
    if not entries:
        return {
            "total_runs": 0,
            "per_backend": {},
            "overall": {
                "total_events": 0,
                "success_count": 0,
                "error_count": 0,
                "failure_rate": 0.0
            }
        }
    
    # Group by run_id
    runs = defaultdict(list)
    for entry in entries:
        runs[entry.get('run_id', 'unknown')].append(entry)
    
    # Per-backend statistics
    backend_stats = defaultdict(lambda: {
        "count": 0,
        "success": 0,
        "errors": 0,
        "latencies": []
    })
    
    total_success = 0
    total_errors = 0
    
    for entry in entries:
        event = entry.get('event', '')
        backend = entry.get('backend', 'unknown')
        success = entry.get('success', False)
        latency = entry.get('latency_ms', 0)
        
        if event in ['helper_spawn', 'backend_call', 'task_complete']:
            backend_stats[backend]["count"] += 1
            if success:
                backend_stats[backend]["success"] += 1
                total_success += 1
            else:
                backend_stats[backend]["errors"] += 1
                total_errors += 1
            
            if latency > 0:
                backend_stats[backend]["latencies"].append(latency)
    
    # Compute percentiles and failure rates
    per_backend = {}
    for backend, stats in backend_stats.items():
        latencies = stats["latencies"]
        per_backend[backend] = {
            "count": stats["count"],
            "success": stats["success"],
            "errors": stats["errors"],
            "failure_rate": stats["errors"] / stats["count"] if stats["count"] > 0 else 0.0,
            "p50_latency_ms": statistics.median(latencies) if latencies else 0.0,
            "p95_latency_ms": statistics.quantiles(latencies, n=20)[18] if len(latencies) >= 20 else (max(latencies) if latencies else 0.0),
            "avg_latency_ms": statistics.mean(latencies) if latencies else 0.0
        }
    
    total_events = total_success + total_errors
    failure_rate = total_errors / total_events if total_events > 0 else 0.0
    
    # Determine health verdict
    if failure_rate < 0.05:
        health = "🟢 OK"
    elif failure_rate < 0.20:
        health = "🟡 Degraded"
    else:
        health = "🔴 Critical"
    
    return {
        "total_runs": len(runs),
        "per_backend": per_backend,
        "overall": {
            "total_events": total_events,
            "success_count": total_success,
            "error_count": total_errors,
            "failure_rate": failure_rate,
            "health": health
        }
    }


def generate_markdown_report(analysis: Dict[str, Any]) -> str:
    """Generate a markdown report from the analysis."""
    lines = [
        "# Automation Assistant Telemetry Debrief",
        "",
        f"**Generated:** {Path(__file__).name}",
        "",
        "## Overall Health",
        "",
        f"- **Status:** {analysis['overall']['health']}",
        f"- **Total Runs:** {analysis['total_runs']}",
        f"- **Total Events:** {analysis['overall']['total_events']}",
        f"- **Success:** {analysis['overall']['success_count']}",
        f"- **Errors:** {analysis['overall']['error_count']}",
        f"- **Failure Rate:** {analysis['overall']['failure_rate']:.2%}",
        "",
        "## Per-Backend Statistics",
        ""
    ]
    
    if not analysis['per_backend']:
        lines.append("*No backend data available*")
    else:
        for backend, stats in sorted(analysis['per_backend'].items()):
            lines.extend([
                f"### {backend}",
                "",
                f"- **Total Calls:** {stats['count']}",
                f"- **Success:** {stats['success']}",
                f"- **Errors:** {stats['errors']}",
                f"- **Failure Rate:** {stats['failure_rate']:.2%}",
                f"- **Average Latency:** {stats['avg_latency_ms']:.2f} ms",
                f"- **P50 Latency:** {stats['p50_latency_ms']:.2f} ms",
                f"- **P95 Latency:** {stats['p95_latency_ms']:.2f} ms",
                ""
            ])
    
    lines.extend([
        "## Metrics Explanation",
        "",
        "- **Failure Rate:** Percentage of operations that resulted in errors",
        "- **P50 Latency:** Median response time (50th percentile)",
        "- **P95 Latency:** 95th percentile response time",
        "",
        "## Health Verdicts",
        "",
        "- 🟢 **OK**: Failure rate < 5%",
        "- 🟡 **Degraded**: Failure rate 5-20%",
        "- 🔴 **Critical**: Failure rate > 20%",
        ""
    ])
    
    return "\n".join(lines)


def main():
    """Main debrief function."""
    print("=" * 70)
    print("Automation Assistant Telemetry Debrief")
    print("=" * 70)
    print()
    
    # Load telemetry
    print("Loading telemetry from src/memory/audit.jsonl...")
    entries = load_telemetry()
    print(f"Found {len(entries)} automation assistant telemetry entries")
    print()
    
    if not entries:
        print("⚠️  No telemetry data found. Run automation_assistant_demo.py first.")
        return
    
    # Analyze
    print("Analyzing telemetry...")
    analysis = analyze_telemetry(entries)
    print()
    
    # Print console summary
    print("=" * 70)
    print("Summary")
    print("=" * 70)
    print(f"Overall Health: {analysis['overall']['health']}")
    print(f"Total Runs: {analysis['total_runs']}")
    print(f"Total Events: {analysis['overall']['total_events']}")
    print(f"Success: {analysis['overall']['success_count']}")
    print(f"Errors: {analysis['overall']['error_count']}")
    print(f"Failure Rate: {analysis['overall']['failure_rate']:.2%}")
    print()
    
    print("Per-Backend Stats:")
    for backend, stats in sorted(analysis['per_backend'].items()):
        print(f"  {backend}:")
        print(f"    Calls: {stats['count']}, Errors: {stats['errors']}, Failure: {stats['failure_rate']:.2%}")
        print(f"    Latency: avg={stats['avg_latency_ms']:.1f}ms, p50={stats['p50_latency_ms']:.1f}ms, p95={stats['p95_latency_ms']:.1f}ms")
    print()
    
    # Generate markdown report
    markdown = generate_markdown_report(analysis)
    
    # Save to file
    output_path = Path("docs/debrief")
    output_path.mkdir(parents=True, exist_ok=True)
    report_file = output_path / "latest.md"
    
    with open(report_file, 'w') as f:
        f.write(markdown)
    
    print(f"✅ Detailed report saved to: {report_file}")
    print("=" * 70)


if __name__ == "__main__":
    main()
