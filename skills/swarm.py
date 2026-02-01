"""
Swarm Orchestration Module

Provides infrastructure for autonomous agent swarm coordination.
Implements swarm lifecycle management and inter-agent communication.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any

from skills.event_logger import log_agent_event


class SwarmAgent:
    """
    Represents an autonomous agent in the swarm.
    
    Each agent has an identity, capabilities (skills), and can
    communicate with other agents through signed messages.
    """
    
    def __init__(
        self,
        agent_id: str,
        soul_path: Optional[str] = None,
        skills: Optional[List[str]] = None
    ):
        """
        Initialize a swarm agent.
        
        Args:
            agent_id: Unique identifier for this agent
            soul_path: Path to SOUL.md file defining agent personality
            skills: List of skill module names this agent can use
        """
        self.agent_id = agent_id
        self.soul_path = Path(soul_path) if soul_path else Path("SOUL.md")
        self.skills = skills or []
        self.soul = self._load_soul()
        
    def _load_soul(self) -> Dict[str, Any]:
        """Load agent soul/personality from SOUL.md."""
        if not self.soul_path.exists():
            return {
                "identity": self.agent_id,
                "purpose": "Autonomous agent",
                "tenets": []
            }
        
        # Simple parsing of SOUL.md for configuration
        soul_data = {
            "identity": self.agent_id,
            "purpose": "Agent purpose not defined",
            "tenets": [],
            "capabilities": [],
            "raw": self.soul_path.read_text(encoding="utf-8")
        }
        
        return soul_data
    
    def log_event(self, event_type: str, data: dict, **kwargs) -> dict:
        """
        Log an event from this agent to sacred memory.
        
        Args:
            event_type: Type of event
            data: Event data
            **kwargs: Additional metadata
            
        Returns:
            The logged event
        """
        return log_agent_event(
            event_type, 
            data, 
            agent_id=self.agent_id,
            **kwargs
        )
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current agent status.
        
        Returns:
            Status dictionary with agent info
        """
        return {
            "agent_id": self.agent_id,
            "soul_loaded": bool(self.soul),
            "skills": self.skills,
            "quantum_ready": os.getenv("JUBILEE_MODE") == "qsvc-ibm"
        }


class SwarmOrchestrator:
    """
    Orchestrates multiple agents in a swarm configuration.
    
    Manages agent lifecycle, coordination, and inter-agent messaging.
    """
    
    def __init__(self):
        """Initialize swarm orchestrator."""
        self.agents: Dict[str, SwarmAgent] = {}
        self.swarm_config = self._load_swarm_config()
    
    def _load_swarm_config(self) -> Dict[str, Any]:
        """Load swarm configuration if available."""
        config_path = Path(".roo/swarm-config.json")
        if config_path.exists():
            with config_path.open("r", encoding="utf-8") as f:
                return json.load(f)
        return {
            "swarm_id": "evez666-swarm",
            "mode": "autonomous",
            "agents": []
        }
    
    def register_agent(
        self,
        agent_id: str,
        soul_path: Optional[str] = None,
        skills: Optional[List[str]] = None
    ) -> SwarmAgent:
        """
        Register a new agent in the swarm.
        
        Args:
            agent_id: Unique agent identifier
            soul_path: Path to agent's SOUL.md
            skills: List of skills this agent has
            
        Returns:
            The registered SwarmAgent instance
        """
        agent = SwarmAgent(agent_id, soul_path, skills)
        self.agents[agent_id] = agent
        
        # Log agent registration
        agent.log_event("swarm_registration", {
            "status": "registered",
            "skills": skills or []
        })
        
        return agent
    
    def get_swarm_status(self) -> Dict[str, Any]:
        """
        Get status of entire swarm.
        
        Returns:
            Dictionary with swarm-wide status information
        """
        return {
            "swarm_id": self.swarm_config.get("swarm_id"),
            "mode": self.swarm_config.get("mode"),
            "agent_count": len(self.agents),
            "agents": {
                agent_id: agent.get_status() 
                for agent_id, agent in self.agents.items()
            },
            "quantum_mode": os.getenv("JUBILEE_MODE", "classical")
        }
    
    def broadcast_event(self, event_type: str, data: dict) -> List[dict]:
        """
        Broadcast an event to all agents in the swarm.
        
        Args:
            event_type: Type of event to broadcast
            data: Event data
            
        Returns:
            List of acknowledgment responses from agents
        """
        responses = []
        for agent_id, agent in self.agents.items():
            response = agent.log_event(event_type, data, metadata={
                "broadcast": True,
                "origin": "orchestrator"
            })
            responses.append(response)
        
        return responses


# Singleton orchestrator instance
_orchestrator = SwarmOrchestrator()


def get_orchestrator() -> SwarmOrchestrator:
    """Get the global swarm orchestrator instance."""
    return _orchestrator


def register_swarm_agent(agent_id: str, **kwargs) -> SwarmAgent:
    """
    Convenience function to register an agent.
    
    Args:
        agent_id: Agent identifier
        **kwargs: Additional arguments for SwarmAgent
        
    Returns:
        The registered agent
    """
    return _orchestrator.register_agent(agent_id, **kwargs)
