"""
Agent Skills Framework - Event Logging

Provides core skill for logging agent events to sacred memory store.
This implements the "Memory is Sacred" tenet of autonomous agent operations.
"""

import json
import time
from pathlib import Path
from typing import Any, Dict, Optional


class EventLogger:
    """
    Sacred memory event logger for agent operations.
    
    Events are appended to events.jsonl with timestamps and metadata.
    This provides persistence across agent sessions.
    """
    
    def __init__(self, events_path: str = "data/events.jsonl"):
        """
        Initialize event logger.
        
        Args:
            events_path: Path to events JSONL file
        """
        self.events_path = Path(events_path)
        self.events_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create file if it doesn't exist
        if not self.events_path.exists():
            self.events_path.touch()
    
    def log_event(
        self, 
        event_type: str, 
        data: Dict[str, Any],
        agent_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Log an agent event to sacred memory.
        
        Args:
            event_type: Type of event (e.g., "forgive", "quantum_detect", "swarm_sync")
            data: Event-specific data payload
            agent_id: Optional agent identifier
            metadata: Optional additional metadata
            
        Returns:
            The logged event with timestamp and ID
        """
        event = {
            "timestamp": time.time(),
            "event_type": event_type,
            "agent_id": agent_id or "evez666-director",
            "data": data,
            "metadata": metadata or {}
        }
        
        # Append to JSONL file
        with self.events_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")
        
        return event
    
    def get_recent_events(self, limit: int = 100) -> list:
        """
        Retrieve recent events from sacred memory.
        
        Args:
            limit: Maximum number of events to return
            
        Returns:
            List of recent events
        """
        if not self.events_path.exists():
            return []
        
        events = []
        with self.events_path.open("r", encoding="utf-8") as f:
            for line in f:
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        
        # Return most recent events
        return events[-limit:] if len(events) > limit else events


# Singleton instance for skills to use
_event_logger = EventLogger()


def log_agent_event(event_type: str, data: dict, **kwargs) -> dict:
    """
    Convenience function for logging agent events.
    
    Args:
        event_type: Type of event
        data: Event data payload
        **kwargs: Additional arguments passed to EventLogger.log_event
        
    Returns:
        The logged event
    """
    return _event_logger.log_event(event_type, data, **kwargs)
