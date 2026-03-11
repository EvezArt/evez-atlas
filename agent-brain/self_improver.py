"""Self-improver agent that analyzes local code and proposes patches/PR metadata."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class ImprovementProposal:
    """Represents a generated self-improvement proposal."""

    title: str
    body: str
    risk: str
    files: list[str]


class SelfImprover:
    """Analyzes selected modules and drafts actionable improvements."""

    def __init__(self, root: str = ".") -> None:
        self.root = Path(root)

    def generate_proposals(self) -> list[ImprovementProposal]:
        proposals: list[ImprovementProposal] = []
        for py_file in self.root.glob("agents/*.py"):
            text = py_file.read_text(encoding="utf-8")
            if "TODO" in text:
                proposals.append(
                    ImprovementProposal(
                        title=f"Resolve TODOs in {py_file.name}",
                        body="Automated self-improver detected TODO markers and generated cleanup task.",
                        risk="low",
                        files=[str(py_file)],
                    )
                )
        return proposals

    def as_tasks(self) -> list[dict[str, Any]]:
        return [
            {"title": p.title, "category": "self-improvement", "payload": {"body": p.body, "files": p.files}, "priority": 2}
            for p in self.generate_proposals()
        ]
