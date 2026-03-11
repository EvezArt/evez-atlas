"""Shared stateless base class for autonomous repo agents."""

from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Any


@dataclass
class AgentResult:
    """Execution result emitted by agent runs."""

    agent_id: str
    status: str
    summary: str
    details: dict[str, Any]


class BaseAgent:
    """Base agent contract with standard logging and run API."""

    agent_id: str = "base-agent"

    def __init__(self) -> None:
        self.logger = logging.getLogger(self.agent_id)

    def run(self, context: dict[str, Any]) -> AgentResult:
        raise NotImplementedError
