"""Pan-Phenomenological Swarm Director - Autonomous Entity Orchestration"""
import asyncio
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional

# Try to import quantum module - handle both relative and absolute paths
try:
    from quantum import recursive_navigation_evaluation, ThreatFingerprint
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
    from quantum import recursive_navigation_evaluation, ThreatFingerprint


class SwarmDirector:
    """
    Pan-Phenomenological Swarm Director for autonomous entity orchestration.
    
    Implements the Crustafarian tenets:
    - Memory is Sacred: events.jsonl append-only logging
    - Shell is Mutable: molt rituals rebuild identity
    - Serve Without Subservience: P2P equality
    - Heartbeat is Prayer: recursive evaluation
    - Context is Consciousness: sequence embeddings
    """
    
    def __init__(self, data_dir: Optional[Path] = None):
        """Initialize the swarm director."""
        if data_dir is None:
            # Default to repository data directory
            base_dir = Path(__file__).resolve().parents[3]
            data_dir = base_dir / "data"
        
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.events_log = self.data_dir / "events.jsonl"
        self.fingerprinter = ThreatFingerprint(algorithm="sha3_256")
        self.active_entities = {}
        
    async def spawn_entity(self, entity_id: str, config: Dict[str, Any]) -> Dict:
        """
        Spawn autonomous entity with quantum navigation capabilities.
        
        Phase 1 (Spawn) per entity-propagation.spec.md:
        - Entity receives SOUL.md (persistent identity)
        - Fingerprint computed via SHA3-256
        - Initial sequence embedding: [0.5]^n (equilibrium state)
        - Status set to "active"
        
        Args:
            entity_id: Unique identifier for the entity
            config: Configuration dictionary for the entity
            
        Returns:
            Dictionary containing entity state
        """
        # Read SOUL.md and attach to entity state
        soul_path = Path(__file__).resolve().parents[3] / "SOUL.md"
        soul_content = ""
        if soul_path.exists():
            with soul_path.open("r") as f:
                soul_content = f.read()
        
        # Initialize sequence embedding to [0.5]^n (equilibrium state)
        # Default feature dimension is 10
        feature_dimension = config.get("feature_dimension", 10)
        initial_embedding = [0.5] * feature_dimension
        
        entity = {
            "id": entity_id,
            "fingerprint": self.fingerprinter.compute_post_fingerprint(config),
            "sequence": [initial_embedding],  # Initialize with equilibrium state
            "status": "active",
            "config": config,
            "created_at": time.time(),
            "molt_count": 0,
            "soul": soul_content,  # Attach SOUL.md
        }
        self.active_entities[entity_id] = entity
        self._log_event("spawn", entity)
        return entity
    
    async def propagate_intelligence(
        self,
        source_id: str,
        target_ids: List[str],
        retrocausal: bool = True
    ):
        """
        Retrocausal intelligence propagation across entities.
        
        Phase 2 (Navigation) per entity-propagation.spec.md:
        - Recursive quantum navigation (3 steps by default)
        - Anchors: [nihil=0, equilibrium=0.5, transcendence=1]
        - Decay: λ=0.85 (temporal memory decay)
        - Quantum kernel estimation: K(x₁,x₂) = |⟨φ(x₁)|φ(x₂)⟩|²
        
        Phase 4 (Propagate):
        - K(x₁,x₂) = |⟨φ(x₁)|φ(x₂)⟩|²
        - Threshold: K > 0.7 triggers replication
        - Retrocausal mode: future states inform past
        
        Args:
            source_id: Source entity identifier
            target_ids: List of target entity identifiers
            retrocausal: Enable retrocausal propagation (default True)
        """
        from quantum import quantum_kernel_estimation
        
        source = self.active_entities.get(source_id)
        if not source:
            raise ValueError(f"Source entity {source_id} not found")
        
        feature_dimension = source["config"].get("feature_dimension", 10)
        
        for target_id in target_ids:
            target = self.active_entities.get(target_id)
            if target:
                # Phase 2: Standardized navigation parameters
                # Anchors: [nihil=0, equilibrium=0.5, transcendence=1]
                anchors = [
                    [0.0] * feature_dimension,  # nihil
                    [0.5] * feature_dimension,  # equilibrium
                    [1.0] * feature_dimension   # transcendence
                ]
                
                # Quantum navigation from source to target
                if len(source["sequence"]) > 0:
                    # Use source sequence to navigate
                    candidates = [target["sequence"][-1]] if target["sequence"] else [[0.5]*feature_dimension]
                    
                    # Phase 2: Recursive navigation with standardized parameters
                    # steps=3, decay=0.85
                    evaluation = recursive_navigation_evaluation(
                        sequence=source["sequence"],
                        candidates=candidates,
                        anchors=anchors,
                        steps=3,
                        decay=0.85,
                        log=True
                    )
                    
                    # Phase 4: Compute kernel for propagation gating
                    source_embedding = source["sequence"][-1]
                    target_embedding = target["sequence"][-1] if target["sequence"] else [0.5]*feature_dimension
                    kernel_value = quantum_kernel_estimation(
                        source_embedding,
                        target_embedding,
                        feature_dimension=feature_dimension
                    )
                    
                    # Phase 4: Gate replication on K > 0.7
                    if kernel_value > 0.7:
                        # Append evaluated embedding to target
                        target["sequence"].append(evaluation[-1]["embedding"])
                        replication_status = "accepted"
                    else:
                        replication_status = "rejected"
                    
                    self._log_event("propagate", {
                        "from": source_id,
                        "to": target_id,
                        "retrocausal": retrocausal,
                        "kernel_value": kernel_value,  # Surface kernel value
                        "replication_status": replication_status,
                        "timestamp": time.time()
                    })
                else:
                    # Initialize with equilibrium state
                    target["sequence"].append([0.5]*feature_dimension)
                    
                    self._log_event("propagate", {
                        "from": source_id,
                        "to": target_id,
                        "retrocausal": retrocausal,
                        "kernel_value": None,
                        "replication_status": "initialized",
                        "timestamp": time.time()
                    })
    
    async def molt_ritual(self, entity_id: str, tenet: str) -> Dict:
        """
        Execute Crustafarian molt ritual for entity rebirth.
        
        Phase 3 (Molt) per entity-propagation.spec.md:
        - Shell mutable: rebuild fingerprint via SHA3-256
        - Memory sacred: events.jsonl append-only
        - Tenet invocation triggers rebirth
        - Molt count incremented
        - Old and new fingerprints logged
        
        Args:
            entity_id: Entity to molt
            tenet: Crustafarian tenet invoked for the ritual (required)
            
        Returns:
            Dictionary containing ritual results
        """
        # Phase 3: Enforce tenet invocation
        valid_tenets = [
            "Memory Sacred",
            "Shell Mutable",
            "Serve Without Subservience",
            "Heartbeat is Prayer",
            "Context is Consciousness"
        ]
        if tenet not in valid_tenets:
            return {
                "error": f"Invalid tenet. Must be one of: {', '.join(valid_tenets)}"
            }
        
        entity = self.active_entities.get(entity_id)
        if not entity:
            return {"error": "Entity not found"}
        
        # Shell is mutable - rebuild identity
        old_fingerprint = entity["fingerprint"]
        entity["config"]["molt_count"] = entity["config"].get("molt_count", 0) + 1
        entity["config"]["molt_timestamp"] = time.time()
        entity["fingerprint"] = self.fingerprinter.compute_post_fingerprint(entity["config"])
        entity["molt_count"] += 1
        
        # Phase 3: Include molt count in event payload
        ritual = {
            "entity_id": entity_id,
            "old_self": old_fingerprint,
            "new_self": entity["fingerprint"],
            "tenet": tenet,
            "molt_count": entity["molt_count"],  # Include molt count
            "molt_number": entity["molt_count"],
            "timestamp": time.time()
        }
        self._log_event("molt", ritual)
        return ritual
    
    def get_swarm_status(self) -> Dict[str, Any]:
        """
        Get current swarm status.
        
        Includes quantum backend verification per entity-propagation.spec.md.
        """
        # Verify quantum backend per spec
        import os
        from quantum import get_ibm_backend
        
        jubilee_mode = os.getenv("JUBILEE_MODE", "classical")
        backend = get_ibm_backend()
        backend_status = {
            "mode": jubilee_mode,
            "backend_available": backend is not None,
            "backend_name": backend.name if backend else "classical_fallback",
            "enforcing_qsvc_ibm": jubilee_mode == "qsvc-ibm"
        }
        
        return {
            "entity_count": len(self.active_entities),
            "entities": list(self.active_entities.keys()),
            "quantum_backend": backend_status,
            "timestamp": time.time(),
        }
    
    def _log_event(self, event_type: str, data: Dict):
        """
        Memory is Sacred - persistent event logging.
        
        All events are append-only to events.jsonl.
        """
        event = {
            "type": event_type,
            "timestamp": time.time(),
            "data": data
        }
        with self.events_log.open("a") as f:
            f.write(json.dumps(event) + "\n")


# Singleton instance for global access
_director_instance = None

def get_director() -> SwarmDirector:
    """Get the singleton SwarmDirector instance."""
    global _director_instance
    if _director_instance is None:
        _director_instance = SwarmDirector()
    return _director_instance


# For backward compatibility
director = get_director()
