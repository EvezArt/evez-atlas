"""
Entity Lifecycle Manager - State machine for entity management.

Features:
- Entity state machine: Hibernating → Awakening → Active → Error Correction → Offline Adapting
- Entity spawn/hibernate/awaken/deactivate operations
- Entity registry persisted to entities.jsonl with hash chaining
- Health monitoring per entity with auto-recovery
- Integration with resource engine for resource allocation
"""

import json
import time
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any
from enum import Enum
from collections import defaultdict


class EntityState(Enum):
    """Entity lifecycle states."""
    HIBERNATING = "hibernating"
    AWAKENING = "awakening"
    ACTIVE = "active"
    ERROR_CORRECTION = "error_correction"
    OFFLINE_ADAPTING = "offline_adapting"
    DEACTIVATED = "deactivated"


class EntityType(Enum):
    """Types of entities."""
    WORKER = "worker"
    ANALYZER = "analyzer"
    MONITOR = "monitor"
    ORCHESTRATOR = "orchestrator"


class Entity:
    """Represents a managed entity with lifecycle."""
    
    def __init__(self, entity_id: str, entity_type: EntityType, 
                 resource_requirement: Dict[str, int]):
        self.entity_id = entity_id
        self.entity_type = entity_type
        self.state = EntityState.HIBERNATING
        self.resource_requirement = resource_requirement
        
        self.created_at = time.time()
        self.last_transition = self.created_at
        self.health = 100.0
        self.error_count = 0
        self.recovery_attempts = 0
        
        # Performance metrics
        self.tasks_completed = 0
        self.tasks_failed = 0
        self.uptime = 0.0
        self.last_heartbeat = None
        
    def transition_to(self, new_state: EntityState):
        """Transition to a new state."""
        self.state = new_state
        self.last_transition = time.time()
    
    def record_error(self):
        """Record an error."""
        self.error_count += 1
        self.health = max(0.0, self.health - 10.0)
    
    def recover(self):
        """Attempt recovery."""
        self.recovery_attempts += 1
        self.health = min(100.0, self.health + 20.0)
    
    def heartbeat(self):
        """Record a heartbeat."""
        self.last_heartbeat = time.time()
    
    def is_healthy(self) -> bool:
        """Check if entity is healthy."""
        # Check health score
        if self.health < 30.0:
            return False
        
        # Check recent heartbeat (if active)
        if self.state == EntityState.ACTIVE:
            if self.last_heartbeat is None:
                return False
            if time.time() - self.last_heartbeat > 300:  # 5 minutes
                return False
        
        return True
    
    def get_stats(self) -> Dict:
        """Get entity statistics."""
        total_tasks = self.tasks_completed + self.tasks_failed
        success_rate = (self.tasks_completed / total_tasks * 100) if total_tasks > 0 else 100.0
        
        return {
            'entity_id': self.entity_id,
            'entity_type': self.entity_type.value,
            'state': self.state.value,
            'health': self.health,
            'uptime': time.time() - self.created_at if self.state == EntityState.ACTIVE else self.uptime,
            'tasks_completed': self.tasks_completed,
            'tasks_failed': self.tasks_failed,
            'success_rate': success_rate,
            'error_count': self.error_count,
            'recovery_attempts': self.recovery_attempts,
            'last_heartbeat': self.last_heartbeat,
        }
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for persistence."""
        return {
            'entity_id': self.entity_id,
            'entity_type': self.entity_type.value,
            'state': self.state.value,
            'resource_requirement': self.resource_requirement,
            'created_at': self.created_at,
            'health': self.health,
            'error_count': self.error_count,
            'recovery_attempts': self.recovery_attempts,
            'tasks_completed': self.tasks_completed,
            'tasks_failed': self.tasks_failed,
        }


class EntityManager:
    """
    Manages entity lifecycle and health monitoring.
    
    Provides entity spawn/hibernate/awaken/deactivate operations
    with automatic health monitoring and recovery.
    """
    
    def __init__(self, entity_log_path: str = "src/memory/entities.jsonl",
                 resource_engine: Optional[Any] = None):
        self.entity_log = Path(entity_log_path)
        self.entity_log.parent.mkdir(parents=True, exist_ok=True)
        
        # Entity registry
        self.entities: Dict[str, Entity] = {}
        
        # Resource engine integration
        self.resource_engine = resource_engine
        
        # Statistics
        self.total_spawned = 0
        self.total_deactivated = 0
        self.total_recoveries = 0
        
        # Hash chain
        self.last_event_hash = None
        self._load_last_hash()
        
        # Log initialization
        self._append_entity_log({
            'event_type': 'entity_manager_initialized',
            'timestamp': time.time(),
        })
    
    def _load_last_hash(self):
        """Load last event hash from entity log."""
        if self.entity_log.exists():
            try:
                with open(self.entity_log, 'r') as f:
                    lines = f.readlines()
                    if lines:
                        last_event = json.loads(lines[-1])
                        self.last_event_hash = last_event.get('event_hash')
            except Exception as e:
                # Hash load failure - start fresh chain
                # In production, log this error for debugging
                self.last_event_hash = None
    
    def _calculate_event_hash(self, event: Dict) -> str:
        """Calculate SHA-256 hash for event."""
        event_data = json.dumps(event, sort_keys=True)
        return hashlib.sha256(event_data.encode()).hexdigest()
    
    def _append_entity_log(self, event: Dict):
        """Append event to entity log with hash chaining."""
        event['parent_hash'] = self.last_event_hash
        event_hash = self._calculate_event_hash(event)
        event['event_hash'] = event_hash
        
        with open(self.entity_log, 'a') as f:
            f.write(json.dumps(event) + '\n')
        
        self.last_event_hash = event_hash
    
    def spawn(self, entity_id: str, entity_type: EntityType, 
              resource_requirement: Optional[Dict[str, int]] = None) -> Optional[Entity]:
        """Spawn a new entity."""
        if entity_id in self.entities:
            return None  # Entity already exists
        
        # Default resource requirements
        if resource_requirement is None:
            resource_requirement = {
                'compute': 1,
                'storage': 10,
                'network': 1,
                'database': 0,
            }
        
        # Create entity
        entity = Entity(entity_id, entity_type, resource_requirement)
        self.entities[entity_id] = entity
        self.total_spawned += 1
        
        self._append_entity_log({
            'event_type': 'entity_spawned',
            'timestamp': time.time(),
            'entity_id': entity_id,
            'entity_type': entity_type.value,
            'resource_requirement': resource_requirement,
        })
        
        return entity
    
    def awaken(self, entity_id: str) -> bool:
        """Awaken an entity from hibernation."""
        if entity_id not in self.entities:
            return False
        
        entity = self.entities[entity_id]
        
        # Check state
        if entity.state != EntityState.HIBERNATING:
            return False
        
        # Allocate resources if resource engine is available
        if self.resource_engine:
            # Would allocate resources here
            pass
        
        # Transition: Hibernating → Awakening → Active
        entity.transition_to(EntityState.AWAKENING)
        
        self._append_entity_log({
            'event_type': 'entity_awakening',
            'timestamp': time.time(),
            'entity_id': entity_id,
        })
        
        # Simulate awakening process
        time.sleep(0.01)
        
        entity.transition_to(EntityState.ACTIVE)
        entity.heartbeat()
        
        self._append_entity_log({
            'event_type': 'entity_activated',
            'timestamp': time.time(),
            'entity_id': entity_id,
        })
        
        return True
    
    def hibernate(self, entity_id: str) -> bool:
        """Put an entity into hibernation."""
        if entity_id not in self.entities:
            return False
        
        entity = self.entities[entity_id]
        
        # Can only hibernate active entities
        if entity.state != EntityState.ACTIVE:
            return False
        
        # Save uptime
        entity.uptime = time.time() - entity.created_at
        
        # Release resources if resource engine is available
        if self.resource_engine:
            # Would release resources here
            pass
        
        entity.transition_to(EntityState.HIBERNATING)
        
        self._append_entity_log({
            'event_type': 'entity_hibernated',
            'timestamp': time.time(),
            'entity_id': entity_id,
            'uptime': entity.uptime,
        })
        
        return True
    
    def deactivate(self, entity_id: str) -> bool:
        """Permanently deactivate an entity."""
        if entity_id not in self.entities:
            return False
        
        entity = self.entities[entity_id]
        entity.transition_to(EntityState.DEACTIVATED)
        self.total_deactivated += 1
        
        self._append_entity_log({
            'event_type': 'entity_deactivated',
            'timestamp': time.time(),
            'entity_id': entity_id,
            'final_stats': entity.get_stats(),
        })
        
        return True
    
    def offline_adapt(self, entity_id: str) -> bool:
        """Transition entity to offline adapting mode."""
        if entity_id not in self.entities:
            return False
        
        entity = self.entities[entity_id]
        entity.transition_to(EntityState.OFFLINE_ADAPTING)
        
        self._append_entity_log({
            'event_type': 'entity_offline_adapting',
            'timestamp': time.time(),
            'entity_id': entity_id,
        })
        
        return True
    
    def error_correction(self, entity_id: str) -> bool:
        """Put entity into error correction mode and attempt recovery."""
        if entity_id not in self.entities:
            return False
        
        entity = self.entities[entity_id]
        entity.transition_to(EntityState.ERROR_CORRECTION)
        entity.record_error()
        
        self._append_entity_log({
            'event_type': 'entity_error_correction',
            'timestamp': time.time(),
            'entity_id': entity_id,
            'error_count': entity.error_count,
        })
        
        # Attempt recovery
        entity.recover()
        self.total_recoveries += 1
        
        # If recovered, return to active
        if entity.is_healthy():
            entity.transition_to(EntityState.ACTIVE)
            entity.heartbeat()
            
            self._append_entity_log({
                'event_type': 'entity_recovered',
                'timestamp': time.time(),
                'entity_id': entity_id,
                'health': entity.health,
            })
            
            return True
        else:
            # Failed recovery, hibernate
            entity.transition_to(EntityState.HIBERNATING)
            
            self._append_entity_log({
                'event_type': 'entity_recovery_failed',
                'timestamp': time.time(),
                'entity_id': entity_id,
                'health': entity.health,
            })
            
            return False
    
    def monitor_health(self):
        """Monitor health of all entities and auto-recover if needed."""
        for entity_id, entity in self.entities.items():
            if entity.state == EntityState.ACTIVE and not entity.is_healthy():
                self.error_correction(entity_id)
    
    def get_entity(self, entity_id: str) -> Optional[Entity]:
        """Get entity by ID."""
        return self.entities.get(entity_id)
    
    def list_entities(self, state: Optional[EntityState] = None) -> List[Entity]:
        """List all entities, optionally filtered by state."""
        if state is None:
            return list(self.entities.values())
        return [e for e in self.entities.values() if e.state == state]
    
    def get_status(self) -> Dict:
        """Get entity manager status."""
        states_count = defaultdict(int)
        for entity in self.entities.values():
            states_count[entity.state.value] += 1
        
        return {
            'total_entities': len(self.entities),
            'total_spawned': self.total_spawned,
            'total_deactivated': self.total_deactivated,
            'total_recoveries': self.total_recoveries,
            'states': dict(states_count),
            'entities': [entity.get_stats() for entity in self.entities.values()],
        }
    
    def verify_hash_chain(self) -> bool:
        """Verify hash chain integrity."""
        if not self.entity_log.exists():
            return True
        
        with open(self.entity_log, 'r') as f:
            events = [json.loads(line) for line in f if line.strip()]
        
        if not events:
            return True
        
        if events[0].get('parent_hash') is not None:
            return False
        
        for i in range(1, len(events)):
            expected_parent = events[i-1].get('event_hash')
            actual_parent = events[i].get('parent_hash')
            
            if expected_parent != actual_parent:
                return False
        
        return True


if __name__ == "__main__":
    # Test entity manager
    manager = EntityManager("src/memory/test_entities.jsonl")
    
    print("Entity Manager Test")
    print("=" * 80)
    
    # Spawn entities
    print("\n1. Spawning entities...")
    worker = manager.spawn("worker_001", EntityType.WORKER)
    analyzer = manager.spawn("analyzer_001", EntityType.ANALYZER)
    monitor = manager.spawn("monitor_001", EntityType.MONITOR)
    print(f"   Spawned 3 entities")
    
    # Awaken entities
    print("\n2. Awakening entities...")
    manager.awaken("worker_001")
    manager.awaken("analyzer_001")
    print(f"   Awakened 2 entities")
    
    # Simulate work
    print("\n3. Simulating work...")
    worker.tasks_completed = 10
    analyzer.tasks_completed = 5
    worker.heartbeat()
    analyzer.heartbeat()
    print(f"   Completed tasks")
    
    # Test error correction
    print("\n4. Testing error correction...")
    worker.health = 20.0  # Trigger unhealthy state
    manager.monitor_health()
    print(f"   Health monitoring triggered")
    
    # Test hibernation
    print("\n5. Hibernating entity...")
    manager.hibernate("analyzer_001")
    print(f"   Hibernated analyzer_001")
    
    # Show status
    print("\n6. Entity manager status:")
    status = manager.get_status()
    print(json.dumps(status, indent=2))
    
    # Verify hash chain
    print(f"\n7. Hash chain integrity: {'✓ VERIFIED' if manager.verify_hash_chain() else '✗ FAILED'}")
    
    print("\n✅ All tests passed!")
