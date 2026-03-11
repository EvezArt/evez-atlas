"""Workload-aware agent replicator for GitHub Actions matrix scaling."""

from __future__ import annotations

from dataclasses import dataclass, asdict
import json
from pathlib import Path
from typing import Any


@dataclass
class ReplicationConfig:
    """Serializable configuration for spawning additional workers."""

    max_workers: int
    threshold: int
    base_agents: list[str]


def plan_replication(queue_depth: int, config: ReplicationConfig) -> dict[str, Any]:
    """Return scaling plan based on queue depth threshold."""
    extra = min(config.max_workers, max(0, queue_depth - config.threshold))
    matrix = [{"agent_index": idx} for idx in range(extra)]
    return {"spawn": extra > 0, "worker_count": extra, "matrix": matrix}


def save_config(config: ReplicationConfig, path: str = "data/replicator_config.json") -> None:
    """Persist replicator config for restoration."""
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(asdict(config), indent=2))
