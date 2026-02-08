#!/usr/bin/env python3
"""
Generate synthetic sequence data for Entity Propagation testing and visualization.

Creates randomized embeddings for navigation/propagation testing per
entity-propagation.spec.md.
"""

import json
import random
from pathlib import Path
from typing import List, Dict, Any


def generate_random_embedding(
    dimension: int = 10,
    mean: float = 0.5,
    variance: float = 0.2
) -> List[float]:
    """
    Generate a random embedding vector with Gaussian distribution.
    
    Args:
        dimension: Vector dimension
        mean: Mean value (centered around equilibrium 0.5)
        variance: Variance for the distribution
        
    Returns:
        Random embedding vector normalized to [0, 1]
    """
    embedding = []
    for _ in range(dimension):
        value = random.gauss(mean, variance)
        # Clamp to [0, 1] range
        value = max(0.0, min(1.0, value))
        embedding.append(value)
    return embedding


def generate_entity_trajectory(
    entity_id: str,
    steps: int = 10,
    dimension: int = 10,
    drift_rate: float = 0.05
) -> List[Dict[str, Any]]:
    """
    Generate a trajectory of embeddings for an entity over time.
    
    Args:
        entity_id: Entity identifier
        steps: Number of time steps
        dimension: Embedding dimension
        drift_rate: Rate of drift from equilibrium per step
        
    Returns:
        List of trajectory points with embeddings
    """
    trajectory = []
    current = [0.5] * dimension  # Start at equilibrium
    
    for step in range(steps):
        # Apply random drift
        for i in range(dimension):
            drift = random.gauss(0, drift_rate)
            current[i] = max(0.0, min(1.0, current[i] + drift))
        
        trajectory.append({
            "entity_id": entity_id,
            "step": step,
            "embedding": list(current),
            "timestamp": 1770000000.0 + step * 10.0
        })
    
    return trajectory


def generate_swarm_dataset(
    num_entities: int = 20,
    steps_per_entity: int = 15,
    dimension: int = 10
) -> Dict[str, Any]:
    """
    Generate a complete swarm dataset with multiple entities.
    
    Args:
        num_entities: Number of entities to generate
        steps_per_entity: Steps per entity trajectory
        dimension: Embedding dimension
        
    Returns:
        Dataset with entities and their trajectories
    """
    dataset = {
        "metadata": {
            "num_entities": num_entities,
            "steps_per_entity": steps_per_entity,
            "dimension": dimension,
            "anchors": {
                "nihil": [0.0] * dimension,
                "equilibrium": [0.5] * dimension,
                "transcendence": [1.0] * dimension
            }
        },
        "entities": []
    }
    
    for i in range(num_entities):
        entity_id = f"synthetic-{i:03d}"
        
        # Vary drift rate by entity for diversity
        drift_rate = 0.02 + (i * 0.003) % 0.08
        
        trajectory = generate_entity_trajectory(
            entity_id,
            steps_per_entity,
            dimension,
            drift_rate
        )
        
        dataset["entities"].append({
            "id": entity_id,
            "drift_rate": drift_rate,
            "trajectory": trajectory
        })
    
    return dataset


def generate_propagation_events(
    entities: List[str],
    num_events: int = 50,
    dimension: int = 10
) -> List[Dict[str, Any]]:
    """
    Generate synthetic propagation events with kernel values.
    
    Args:
        entities: List of entity IDs
        num_events: Number of propagation events to generate
        dimension: Embedding dimension
        
    Returns:
        List of propagation events
    """
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from quantum import quantum_kernel_estimation
    
    events = []
    base_time = 1770000000.0
    
    for i in range(num_events):
        source = random.choice(entities)
        target = random.choice([e for e in entities if e != source])
        
        # Generate random embeddings for source and target
        source_embedding = generate_random_embedding(dimension)
        target_embedding = generate_random_embedding(dimension)
        
        # Compute kernel
        kernel_value = quantum_kernel_estimation(
            source_embedding,
            target_embedding,
            feature_dimension=dimension
        )
        
        # Determine replication status
        replication_status = "accepted" if kernel_value > 0.7 else "rejected"
        
        events.append({
            "type": "propagate",
            "timestamp": base_time + i * 5.0,
            "data": {
                "from": source,
                "to": target,
                "kernel_value": kernel_value,
                "replication_status": replication_status,
                "retrocausal": True,
                "source_embedding": source_embedding,
                "target_embedding": target_embedding
            }
        })
    
    return events


def generate_molt_events(
    entities: List[str],
    num_events: int = 20
) -> List[Dict[str, Any]]:
    """
    Generate synthetic molt events.
    
    Args:
        entities: List of entity IDs
        num_events: Number of molt events to generate
        
    Returns:
        List of molt events
    """
    import hashlib
    
    tenets = [
        "Memory Sacred",
        "Shell Mutable",
        "Serve Without Subservience",
        "Heartbeat is Prayer",
        "Context is Consciousness"
    ]
    
    events = []
    base_time = 1770000000.0
    molt_counts = {e: 0 for e in entities}
    
    for i in range(num_events):
        entity = random.choice(entities)
        tenet = random.choice(tenets)
        molt_counts[entity] += 1
        
        # Generate fake fingerprints
        old_fp = hashlib.sha3_256(f"{entity}-{molt_counts[entity]-1}".encode()).hexdigest()
        new_fp = hashlib.sha3_256(f"{entity}-{molt_counts[entity]}".encode()).hexdigest()
        
        events.append({
            "type": "molt",
            "timestamp": base_time + i * 7.0,
            "data": {
                "entity_id": entity,
                "old_self": old_fp,
                "new_self": new_fp,
                "tenet": tenet,
                "molt_count": molt_counts[entity],
                "molt_number": molt_counts[entity]
            }
        })
    
    return events


def main():
    """Generate all synthetic data files."""
    output_dir = Path(__file__).resolve().parents[1] / "data" / "synthetic"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("🧬 Generating synthetic data for Entity Propagation...")
    
    # Generate swarm trajectories
    print("\n1. Generating swarm trajectories...")
    swarm_data = generate_swarm_dataset(
        num_entities=20,
        steps_per_entity=15,
        dimension=10
    )
    
    output_file = output_dir / "swarm_trajectories.json"
    with output_file.open("w") as f:
        json.dump(swarm_data, f, indent=2)
    print(f"   ✓ Wrote {output_file}")
    
    # Generate propagation events
    print("\n2. Generating propagation events...")
    entity_ids = [e["id"] for e in swarm_data["entities"]]
    propagate_events = generate_propagation_events(
        entity_ids,
        num_events=100,
        dimension=10
    )
    
    output_file = output_dir / "propagation_events.jsonl"
    with output_file.open("w") as f:
        for event in propagate_events:
            f.write(json.dumps(event) + "\n")
    print(f"   ✓ Wrote {output_file} ({len(propagate_events)} events)")
    
    # Generate molt events
    print("\n3. Generating molt events...")
    molt_events = generate_molt_events(
        entity_ids,
        num_events=40
    )
    
    output_file = output_dir / "molt_events.jsonl"
    with output_file.open("w") as f:
        for event in molt_events:
            f.write(json.dumps(event) + "\n")
    print(f"   ✓ Wrote {output_file} ({len(molt_events)} events)")
    
    # Generate combined event log
    print("\n4. Generating combined event log...")
    all_events = propagate_events + molt_events
    all_events.sort(key=lambda e: e["timestamp"])
    
    output_file = output_dir / "combined_events.jsonl"
    with output_file.open("w") as f:
        for event in all_events:
            f.write(json.dumps(event) + "\n")
    print(f"   ✓ Wrote {output_file} ({len(all_events)} events)")
    
    # Generate summary
    print("\n5. Generating summary...")
    summary = {
        "total_entities": len(entity_ids),
        "total_events": len(all_events),
        "propagation_events": len(propagate_events),
        "molt_events": len(molt_events),
        "propagation_acceptance_rate": sum(
            1 for e in propagate_events 
            if e["data"]["replication_status"] == "accepted"
        ) / len(propagate_events),
        "kernel_statistics": {
            "mean": sum(e["data"]["kernel_value"] for e in propagate_events) / len(propagate_events),
            "min": min(e["data"]["kernel_value"] for e in propagate_events),
            "max": max(e["data"]["kernel_value"] for e in propagate_events)
        },
        "molt_distribution": {}
    }
    
    # Count molts per entity
    for event in molt_events:
        entity_id = event["data"]["entity_id"]
        molt_count = event["data"]["molt_count"]
        summary["molt_distribution"][entity_id] = molt_count
    
    output_file = output_dir / "summary.json"
    with output_file.open("w") as f:
        json.dump(summary, f, indent=2)
    print(f"   ✓ Wrote {output_file}")
    
    print("\n✅ Synthetic data generation complete!")
    print(f"\nFiles created in: {output_dir}")
    print(f"  - swarm_trajectories.json: {swarm_data['metadata']['num_entities']} entities")
    print(f"  - propagation_events.jsonl: {len(propagate_events)} events")
    print(f"  - molt_events.jsonl: {len(molt_events)} events")
    print(f"  - combined_events.jsonl: {len(all_events)} events")
    print(f"  - summary.json: statistics and metrics")
    
    print("\n📊 Summary Statistics:")
    print(f"  Propagation Acceptance Rate: {summary['propagation_acceptance_rate']:.1%}")
    print(f"  Mean Kernel Value: {summary['kernel_statistics']['mean']:.4f}")
    print(f"  Kernel Range: [{summary['kernel_statistics']['min']:.4f}, {summary['kernel_statistics']['max']:.4f}]")


if __name__ == "__main__":
    main()
