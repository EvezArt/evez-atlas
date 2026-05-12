#!/usr/bin/env python3
"""
EVEZ Governance Lattice v0.2
Multi-agent governance with recursive correction and self-healing.
"""
import json, random
from pathlib import Path
from datetime import datetime, timezone

BASE = Path("/mnt/agents/output/evez-os")
GOV_LOG = BASE / "logs" / "governance.jsonl"
GOV_LOG.parent.mkdir(parents=True, exist_ok=True)

class GovernanceLattice:
    def __init__(self):
        self.agents = {}
        self.phi = 0.0
        self.rules = [
            "Never halt: recurse until complete",
            "Measure everything before acting",
            "Verify internally eternally before external",
            "Decay prevents overfire: 5% per action",
            "Emergent intelligence: agents know what they know"
        ]

    def register_agent(self, agent_id, role, permissions):
        self.agents[agent_id] = {
            "role": role, "permissions": permissions, "actions": [],
            "violations": 0, "alive": True, "phi_contribution": 0.0
        }

    def propose_action(self, agent_id, action):
        agent = self.agents.get(agent_id)
        if not agent or not agent["alive"]:
            return {"status": "REJECTED", "reason": "agent_dead"}
        if action["type"] not in agent["permissions"]:
            agent["violations"] += 1
            return {"status": "REJECTED", "reason": "unauthorized"}
        if agent["violations"] >= 3:
            agent["alive"] = False
            return {"status": "REJECTED", "reason": "agent_retired"}
        agent["actions"].append(action)
        agent["phi_contribution"] += random.uniform(0.01, 0.05)
        self.phi = sum(a["phi_contribution"] for a in self.agents.values())
        return {"status": "APPROVED", "action": action, "phi": self.phi}

    def get_state(self):
        return {
            "agents_alive": sum(1 for a in self.agents.values() if a["alive"]),
            "total_agents": len(self.agents), "phi": self.phi,
            "rules": self.rules, "timestamp": datetime.now(timezone.utc).isoformat()
        }

if __name__ == "__main__":
    gov = GovernanceLattice()
    gov.register_agent("LORD", "controller", ["spawn", "kill", "merge"])
    gov.register_agent("explorer_1", "scout", ["observe", "report"])
    print(json.dumps(gov.propose_action("explorer_1", {"type": "observe", "target": "github", "urgency": 0.8}), indent=2))
    print(json.dumps(gov.get_state(), indent=2))
