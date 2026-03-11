"""Registry for tracking autonomous agent metadata and logs."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any


@dataclass
class AgentState:
    """Single agent status record."""

    agent_id: str
    role: str
    status: str
    last_heartbeat: str
    output_log: list[str]


class AgentRegistry:
    """JSON-backed registry for active autonomous workers."""

    def __init__(self, path: str = "data/agent_registry.json") -> None:
        self.path = Path(path)
        self._agents: dict[str, AgentState] = {}
        self._load()

    def register(self, agent_id: str, role: str) -> None:
        now = datetime.now(timezone.utc).isoformat()
        self._agents[agent_id] = AgentState(agent_id=agent_id, role=role, status="running", last_heartbeat=now, output_log=[])
        self._persist()

    def heartbeat(self, agent_id: str, status: str = "running") -> None:
        agent = self._agents[agent_id]
        agent.last_heartbeat = datetime.now(timezone.utc).isoformat()
        agent.status = status
        self._persist()

    def log(self, agent_id: str, line: str) -> None:
        self._agents[agent_id].output_log.append(line)
        self._persist()

    def list_agents(self) -> list[dict[str, Any]]:
        return [asdict(v) for v in self._agents.values()]

    def _load(self) -> None:
        if not self.path.exists():
            self.path.parent.mkdir(parents=True, exist_ok=True)
            return
        data = json.loads(self.path.read_text())
        for item in data:
            self._agents[item["agent_id"]] = AgentState(**item)

    def _persist(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps([asdict(v) for v in self._agents.values()], indent=2))
