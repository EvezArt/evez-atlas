"""In-memory pub/sub message bus with JSONL event logging."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Callable

Subscriber = Callable[["BusEvent"], None]


@dataclass
class BusEvent:
    """Event envelope published by autonomous agents."""

    agent_id: str
    event_type: str
    payload: dict[str, Any]
    timestamp: str


class MessageBus:
    """Simple message bus supporting topic subscriptions and persisted logs."""

    def __init__(self, log_path: str = "logs/agent_comms.jsonl") -> None:
        self.log_path = Path(log_path)
        self._subs: dict[str, list[Subscriber]] = defaultdict(list)

    def subscribe(self, event_type: str, subscriber: Subscriber) -> None:
        self._subs[event_type].append(subscriber)

    def publish(self, agent_id: str, event_type: str, payload: dict[str, Any]) -> BusEvent:
        event = BusEvent(
            agent_id=agent_id,
            event_type=event_type,
            payload=payload,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        self._append_log(event)
        for sub in self._subs.get(event_type, []):
            sub(event)
        return event

    def _append_log(self, event: BusEvent) -> None:
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        with self.log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(asdict(event)) + "\n")
