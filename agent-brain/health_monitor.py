"""Heartbeat monitor that detects and restarts failed agents."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Callable

from agent_registry import AgentRegistry


class HealthMonitor:
    """Monitors agent heartbeats and invokes restart callbacks on stale agents."""

    def __init__(self, registry: AgentRegistry, timeout_seconds: int = 120) -> None:
        self.registry = registry
        self.timeout_seconds = timeout_seconds

    def check_and_restart(self, restart_fn: Callable[[str], None]) -> list[str]:
        restarted: list[str] = []
        now = datetime.now(timezone.utc)
        for agent in self.registry.list_agents():
            last = datetime.fromisoformat(agent["last_heartbeat"])
            if now - last > timedelta(seconds=self.timeout_seconds):
                restart_fn(agent["agent_id"])
                restarted.append(agent["agent_id"])
        return restarted
