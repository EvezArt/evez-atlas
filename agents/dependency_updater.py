"""Agent that scans dependency manifests and proposes safe upgrades."""

from __future__ import annotations

from pathlib import Path

from agents.base_agent import AgentResult, BaseAgent


class DependencyUpdaterAgent(BaseAgent):
    """Find package manifests and create update recommendations."""

    agent_id = "dependency-updater"

    def run(self, context: dict[str, object]) -> AgentResult:
        root = Path(str(context.get("root", ".")))
        manifests = [str(p) for p in root.rglob("package.json")] + [str(p) for p in root.rglob("requirements.txt")]
        return AgentResult(self.agent_id, "ok", "Dependency scan complete", {"manifests": manifests[:100]})
