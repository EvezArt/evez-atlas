"""Agent that identifies untested files and proposes generated tests."""

from __future__ import annotations

from pathlib import Path

from agents.base_agent import AgentResult, BaseAgent


class TestGeneratorAgent(BaseAgent):
    """Create test generation tasks by scanning src/tests gaps."""

    agent_id = "test-generator"

    def run(self, context: dict[str, object]) -> AgentResult:
        root = Path(str(context.get("root", ".")))
        src_files = [p for p in root.rglob("*.py") if "tests" not in p.parts and ".venv" not in p.parts]
        return AgentResult(self.agent_id, "ok", "Test opportunities identified", {"python_files": len(src_files)})
