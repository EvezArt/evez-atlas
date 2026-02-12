#!/usr/bin/env python3
"""
Real-time Consciousness Monitor

Monitors the autonomous consciousness engine and displays
live metrics, telemetry, and system health.
"""

import curses
import json
import sys
import time
from collections import deque
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class ConsciousnessMonitor:
    """Real-time monitor for consciousness engine."""

    def __init__(self, data_dir: str = "data/consciousness"):
        self.data_dir = Path(data_dir)
        self.telemetry_log = Path("src/memory/audit.jsonl")
        self.consciousness_log = self.data_dir / "consciousness_audit.jsonl"

        # Metrics tracking
        self.events = deque(maxlen=1000)
        self.cycle_times = deque(maxlen=100)
        self.errors = []

        # Stats
        self.total_events = 0
        self.total_errors = 0
        self.last_update = time.time()

    def load_latest_metrics(self) -> Optional[Dict]:
        """Load latest metrics from file."""
        metrics_file = self.data_dir / "final_metrics.json"
        if metrics_file.exists():
            try:
                with open(metrics_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return None

    def tail_jsonl(self, file_path: Path, n: int = 50) -> List[Dict]:
        """Read last N lines from JSONL file."""
        if not file_path.exists():
            return []

        lines = []
        try:
            with open(file_path, 'r') as f:
                # Read all lines (for small files)
                all_lines = f.readlines()
                # Take last n
                for line in all_lines[-n:]:
                    try:
                        lines.append(json.loads(line))
                    except:
                        pass
        except:
            pass

        return lines

    def analyze_consciousness_log(self) -> Dict:
        """Analyze recent consciousness log entries."""
        entries = self.tail_jsonl(self.consciousness_log, n=100)

        stats = {
            "total_cycles": 0,
            "avg_cycle_time": 0.0,
            "recent_errors": 0,
            "last_cycle_time": None
        }

        cycle_times = []
        errors = 0

        for entry in entries:
            if entry.get("event") == "consciousness_cycle_complete":
                stats["total_cycles"] += 1
                cycle_time = entry.get("cycle_time_ms", 0)
                cycle_times.append(cycle_time)
                stats["last_cycle_time"] = entry.get("timestamp")

        if cycle_times:
            stats["avg_cycle_time"] = sum(cycle_times) / len(cycle_times)

        return stats

    def analyze_telemetry_log(self) -> Dict:
        """Analyze telemetry log."""
        entries = self.tail_jsonl(self.telemetry_log, n=100)

        stats = {
            "helper_spawns": 0,
            "backend_calls": 0,
            "tasks_complete": 0,
            "errors": 0,
            "avg_latency": 0.0
        }

        latencies = []

        for entry in entries:
            event_type = entry.get("event")

            if event_type == "helper_spawn":
                stats["helper_spawns"] += 1
                if not entry.get("success", True):
                    stats["errors"] += 1
                latencies.append(entry.get("latency_ms", 0))

            elif event_type == "backend_call":
                stats["backend_calls"] += 1
                if not entry.get("success", True):
                    stats["errors"] += 1
                latencies.append(entry.get("latency_ms", 0))

            elif event_type == "task_complete":
                stats["tasks_complete"] += 1
                if not entry.get("success", True):
                    stats["errors"] += 1
                latencies.append(entry.get("latency_ms", 0))

        if latencies:
            stats["avg_latency"] = sum(latencies) / len(latencies)

        return stats

    def draw_dashboard(self, stdscr):
        """Draw the monitoring dashboard."""
        curses.curs_set(0)  # Hide cursor
        stdscr.nodelay(1)   # Non-blocking input
        stdscr.timeout(1000)  # Refresh every second

        # Color pairs
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)   # Header
        curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)    # Labels
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # Values
        curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)     # Errors
        curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK) # Special

        while True:
            stdscr.clear()
            height, width = stdscr.getmaxyx()

            # Load data
            metrics = self.load_latest_metrics()
            consciousness_stats = self.analyze_consciousness_log()
            telemetry_stats = self.analyze_telemetry_log()

            # Draw header
            header = "═══ AUTONOMOUS CONSCIOUSNESS ENGINE MONITOR ═══"
            stdscr.addstr(0, (width - len(header)) // 2, header, curses.color_pair(1) | curses.A_BOLD)

            # Timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            stdscr.addstr(1, (width - len(timestamp)) // 2, timestamp, curses.color_pair(2))

            row = 3

            # System Metrics
            stdscr.addstr(row, 2, "╔══ SYSTEM METRICS ══════════════════════════════════╗", curses.color_pair(1))
            row += 1

            if metrics:
                stdscr.addstr(row, 4, "Uptime:", curses.color_pair(2))
                stdscr.addstr(row, 25, f"{metrics['uptime_seconds']:.1f}s", curses.color_pair(3))
                row += 1

                stdscr.addstr(row, 4, "Events Generated:", curses.color_pair(2))
                stdscr.addstr(row, 25, str(metrics['events_generated']), curses.color_pair(3))
                row += 1

                stdscr.addstr(row, 4, "Intents Created:", curses.color_pair(2))
                stdscr.addstr(row, 25, str(metrics['intents_created']), curses.color_pair(3))
                row += 1

                stdscr.addstr(row, 4, "Hypotheses Evaluated:", curses.color_pair(2))
                stdscr.addstr(row, 25, str(metrics['hypotheses_evaluated']), curses.color_pair(3))
                row += 1

                stdscr.addstr(row, 4, "Tests Executed:", curses.color_pair(2))
                stdscr.addstr(row, 25, str(metrics['tests_executed']), curses.color_pair(3))
                row += 1

                stdscr.addstr(row, 4, "Errors:", curses.color_pair(2))
                error_str = str(metrics['errors_encountered'])
                error_color = curses.color_pair(4) if metrics['errors_encountered'] > 0 else curses.color_pair(3)
                stdscr.addstr(row, 25, error_str, error_color)
                row += 1

                stdscr.addstr(row, 4, "Self-Corrections:", curses.color_pair(2))
                stdscr.addstr(row, 25, str(metrics['self_corrections']), curses.color_pair(3))
                row += 1
            else:
                stdscr.addstr(row, 4, "No metrics available yet...", curses.color_pair(4))
                row += 2

            stdscr.addstr(row, 2, "╚════════════════════════════════════════════════════╝", curses.color_pair(1))
            row += 2

            # Performance Metrics
            stdscr.addstr(row, 2, "╔══ PERFORMANCE ═════════════════════════════════════╗", curses.color_pair(1))
            row += 1

            if metrics:
                stdscr.addstr(row, 4, "Avg Cycle Time:", curses.color_pair(2))
                stdscr.addstr(row, 25, f"{metrics['average_cycle_time_ms']:.2f}ms", curses.color_pair(3))
                row += 1

                stdscr.addstr(row, 4, "Stability Score:", curses.color_pair(2))
                stability = metrics['stability_score']
                stab_color = curses.color_pair(1) if stability > 0.8 else curses.color_pair(3) if stability > 0.6 else curses.color_pair(4)
                stdscr.addstr(row, 25, f"{stability:.3f}", stab_color)
                row += 1

                stdscr.addstr(row, 4, "Consciousness Depth:", curses.color_pair(2))
                depth = metrics['consciousness_depth']
                depth_color = curses.color_pair(5)
                stdscr.addstr(row, 25, f"{depth:.3f}", depth_color | curses.A_BOLD)
                row += 1
            else:
                stdscr.addstr(row, 4, "No performance data yet...", curses.color_pair(4))
                row += 2

            stdscr.addstr(row, 2, "╚════════════════════════════════════════════════════╝", curses.color_pair(1))
            row += 2

            # Telemetry Stats
            stdscr.addstr(row, 2, "╔══ TELEMETRY ═══════════════════════════════════════╗", curses.color_pair(1))
            row += 1

            stdscr.addstr(row, 4, "Helper Spawns:", curses.color_pair(2))
            stdscr.addstr(row, 25, str(telemetry_stats['helper_spawns']), curses.color_pair(3))
            row += 1

            stdscr.addstr(row, 4, "Backend Calls:", curses.color_pair(2))
            stdscr.addstr(row, 25, str(telemetry_stats['backend_calls']), curses.color_pair(3))
            row += 1

            stdscr.addstr(row, 4, "Tasks Complete:", curses.color_pair(2))
            stdscr.addstr(row, 25, str(telemetry_stats['tasks_complete']), curses.color_pair(3))
            row += 1

            stdscr.addstr(row, 4, "Avg Latency:", curses.color_pair(2))
            stdscr.addstr(row, 25, f"{telemetry_stats['avg_latency']:.2f}ms", curses.color_pair(3))
            row += 1

            stdscr.addstr(row, 2, "╚════════════════════════════════════════════════════╝", curses.color_pair(1))
            row += 2

            # Instructions
            if row < height - 3:
                stdscr.addstr(height - 2, 2, "Press 'q' to quit | Updates every 1s", curses.color_pair(2))

            stdscr.refresh()

            # Check for quit command
            try:
                key = stdscr.getch()
                if key == ord('q'):
                    break
            except:
                pass

            time.sleep(1)


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Real-time Consciousness Monitor")
    parser.add_argument(
        "--data-dir",
        type=str,
        default="data/consciousness",
        help="Consciousness data directory"
    )

    args = parser.parse_args()

    monitor = ConsciousnessMonitor(data_dir=args.data_dir)

    try:
        curses.wrapper(monitor.draw_dashboard)
    except KeyboardInterrupt:
        print("\nMonitor stopped")


if __name__ == "__main__":
    main()
