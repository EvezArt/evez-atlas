"""Priority task queue with JSON persistence for autonomous agents."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import heapq
import json
from pathlib import Path
from typing import Any
from uuid import uuid4


@dataclass(order=True)
class PrioritizedTask:
    """Internal heap item for deterministic task ordering."""

    sort_index: tuple[int, float] = field(init=False, repr=False)
    priority: int
    created_ts: float
    task_id: str
    title: str
    category: str
    payload: dict[str, Any]
    status: str = "pending"

    def __post_init__(self) -> None:
        self.sort_index = (self.priority, self.created_ts)


class TaskQueue:
    """JSON-backed priority queue for bug fixes, improvements, and expansions."""

    def __init__(self, db_path: str = "data/agent_tasks.json") -> None:
        self.db_path = Path(db_path)
        self._heap: list[PrioritizedTask] = []
        self._index: dict[str, PrioritizedTask] = {}
        self._load()

    def add_task(self, title: str, category: str, payload: dict[str, Any], priority: int = 5) -> str:
        now = datetime.now(timezone.utc).timestamp()
        task_id = str(uuid4())
        task = PrioritizedTask(
            priority=priority,
            created_ts=now,
            task_id=task_id,
            title=title,
            category=category,
            payload=payload,
        )
        heapq.heappush(self._heap, task)
        self._index[task_id] = task
        self._persist()
        return task_id

    def pop_next(self) -> PrioritizedTask | None:
        while self._heap:
            task = heapq.heappop(self._heap)
            if task.status == "pending":
                task.status = "in_progress"
                self._persist()
                return task
        return None

    def mark_done(self, task_id: str) -> None:
        task = self._index[task_id]
        task.status = "completed"
        self._persist()

    def mark_failed(self, task_id: str, reason: str) -> None:
        task = self._index[task_id]
        task.status = f"failed:{reason}"
        self._persist()

    def list_tasks(self) -> list[dict[str, Any]]:
        return [asdict(t) for t in sorted(self._index.values(), key=lambda x: x.sort_index)]

    def _load(self) -> None:
        if not self.db_path.exists():
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            return
        records = json.loads(self.db_path.read_text())
        for item in records:
            task = PrioritizedTask(**item)
            heapq.heappush(self._heap, task)
            self._index[task.task_id] = task

    def _persist(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        serialized = [{k: v for k, v in asdict(t).items() if k != "sort_index"} for t in self._index.values()]
        self.db_path.write_text(json.dumps(serialized, indent=2))
