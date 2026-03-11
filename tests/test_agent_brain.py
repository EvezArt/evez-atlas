"""Tests for autonomous agent brain core modules."""

from __future__ import annotations

import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "agent-brain"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agent_registry import AgentRegistry
from task_queue import TaskQueue
from comms.message_bus import MessageBus
from replicator import ReplicationConfig, plan_replication


def test_task_queue_priority(tmp_path: Path) -> None:
    queue = TaskQueue(str(tmp_path / "tasks.json"))
    queue.add_task("low", "improve", {}, priority=5)
    queue.add_task("high", "bug", {}, priority=1)
    first = queue.pop_next()
    assert first is not None
    assert first.title == "high"


def test_agent_registry_round_trip(tmp_path: Path) -> None:
    path = tmp_path / "registry.json"
    registry = AgentRegistry(str(path))
    registry.register("a1", "Role")
    registry.log("a1", "hello")
    loaded = json.loads(path.read_text())
    assert loaded[0]["agent_id"] == "a1"
    assert "hello" in loaded[0]["output_log"]


def test_message_bus_logging(tmp_path: Path) -> None:
    log_file = tmp_path / "events.jsonl"
    bus = MessageBus(str(log_file))
    bus.publish("agent", "event", {"x": 1})
    assert log_file.exists()
    assert '"event_type": "event"' in log_file.read_text()


def test_replication_plan() -> None:
    config = ReplicationConfig(max_workers=10, threshold=2, base_agents=["doc-writer"])
    plan = plan_replication(queue_depth=7, config=config)
    assert plan["spawn"] is True
    assert plan["worker_count"] == 5
