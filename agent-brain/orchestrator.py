"""Master orchestration loop for autonomous multi-repo agent operations."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path
import sys
import time
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "agent-brain"))
sys.path.insert(0, str(ROOT))

from agent_registry import AgentRegistry
from health_monitor import HealthMonitor
from self_improver import SelfImprover
from task_queue import TaskQueue
from comms.message_bus import MessageBus
from agents.code_reviewer import CodeReviewerAgent
from agents.dependency_updater import DependencyUpdaterAgent
from agents.deployment_agent import DeploymentAgent
from agents.doc_writer import DocWriterAgent
from agents.performance_optimizer import PerformanceOptimizerAgent
from agents.security_scanner import SecurityScannerAgent
from agents.test_generator import TestGeneratorAgent


def build_agents() -> list[Any]:
    """Instantiate all specialized agent workers."""
    return [
        CodeReviewerAgent(),
        DependencyUpdaterAgent(),
        DocWriterAgent(),
        TestGeneratorAgent(),
        SecurityScannerAgent(),
        PerformanceOptimizerAgent(),
        DeploymentAgent(),
    ]


def run_once(context: dict[str, Any]) -> None:
    """Execute one full orchestration cycle."""
    queue = TaskQueue()
    registry = AgentRegistry()
    monitor = HealthMonitor(registry)
    bus = MessageBus()

    for task in SelfImprover(str(ROOT)).as_tasks():
        queue.add_task(task["title"], task["category"], task["payload"], task["priority"])

    for agent in build_agents():
        registry.register(agent.agent_id, agent.__class__.__name__)
        result = agent.run(context)
        registry.log(agent.agent_id, result.summary)
        registry.heartbeat(agent.agent_id, result.status)
        bus.publish(agent.agent_id, "run.completed", {"summary": result.summary, "details": result.details})

    restarted = monitor.check_and_restart(lambda agent_id: registry.heartbeat(agent_id, "restarted"))
    if restarted:
        logging.warning("Restarted stale agents: %s", restarted)


def main() -> None:
    """Run orchestrator continuously or as single pass."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--loop", action="store_true", help="Run forever")
    parser.add_argument("--interval", type=int, default=900, help="Loop interval seconds")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    context: dict[str, Any] = {"root": str(ROOT), "repos": ["Evez666"], "open_prs": []}

    if not args.loop:
        run_once(context)
        return

    while True:
        run_once(context)
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
