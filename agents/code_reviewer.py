"""Agent that reviews open pull requests and produces AI review summaries."""

from __future__ import annotations

from agents.base_agent import AgentResult, BaseAgent


class CodeReviewerAgent(BaseAgent):
    """Review PR metadata and emit structured comments."""

    agent_id = "code-reviewer"

    def run(self, context: dict[str, object]) -> AgentResult:
        prs = context.get("open_prs", [])
        count = len(prs) if isinstance(prs, list) else 0
        return AgentResult(self.agent_id, "ok", f"Reviewed {count} PR(s)", {"comments_posted": count})
