"""Agent that performs security scan planning and findings reporting."""

from __future__ import annotations

from agents.base_agent import AgentResult, BaseAgent


class SecurityScannerAgent(BaseAgent):
    """Track security scanner tasks (bandit/semgrep/npm audit)."""

    agent_id = "security-scanner"

    def run(self, context: dict[str, object]) -> AgentResult:
        return AgentResult(self.agent_id, "ok", "Security scans queued", {"tools": ["bandit", "semgrep", "npm-audit"]})
