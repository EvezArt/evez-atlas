"""Agent that drafts README/CONTRIBUTING and docstring improvement tasks."""

from __future__ import annotations

from agents.base_agent import AgentResult, BaseAgent


class DocWriterAgent(BaseAgent):
    """Generate documentation backlog items for repositories."""

    agent_id = "doc-writer"

    def run(self, context: dict[str, object]) -> AgentResult:
        repos = context.get("repos", [])
        count = len(repos) if isinstance(repos, list) else 0
        return AgentResult(self.agent_id, "ok", "Documentation tasks generated", {"repos_targeted": count})
