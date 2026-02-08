#!/usr/bin/env python3
"""
Entity Propagation CLI Visual Output

Provides ASCII tables and summaries for entity lifecycle actions
per entity-propagation.spec.md.
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import List, Dict, Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.mastra.agents.swarm_director import SwarmDirector


def print_header(title: str):
    """Print a formatted header."""
    width = 80
    print("\n" + "=" * width)
    print(f" {title}".center(width))
    print("=" * width + "\n")


def print_table(headers: List[str], rows: List[List[str]]):
    """Print an ASCII table."""
    if not rows:
        print("(No data)")
        return
    
    # Calculate column widths
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))
    
    # Print header
    header_row = " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers))
    print(header_row)
    print("-" * len(header_row))
    
    # Print rows
    for row in rows:
        print(" | ".join(str(cell).ljust(col_widths[i]) for i, cell in enumerate(row)))


def format_fingerprint(fp: str, length: int = 16) -> str:
    """Format fingerprint for display."""
    if len(fp) > length:
        return fp[:length] + "..."
    return fp


def format_embedding(embedding: List[float], precision: int = 2) -> str:
    """Format embedding vector for display."""
    if not embedding:
        return "[]"
    if len(embedding) > 5:
        # Show first 3 and last 2
        formatted = [f"{v:.{precision}f}" for v in embedding[:3]]
        formatted.append("...")
        formatted.extend([f"{v:.{precision}f}" for v in embedding[-2:]])
        return "[" + ", ".join(formatted) + "]"
    return "[" + ", ".join(f"{v:.{precision}f}" for v in embedding) + "]"


async def show_swarm_status():
    """Display current swarm status."""
    print_header("🦀 Entity Swarm Status")
    
    director = SwarmDirector()
    status = director.get_swarm_status()
    
    print(f"Entity Count: {status['entity_count']}")
    print(f"Timestamp: {status['timestamp']:.2f}")
    print()
    
    # Quantum backend info
    backend = status.get('quantum_backend', {})
    print("Quantum Backend:")
    print(f"  Mode: {backend.get('mode', 'unknown')}")
    print(f"  Backend: {backend.get('backend_name', 'unknown')}")
    print(f"  Available: {'✓' if backend.get('backend_available') else '✗'}")
    print(f"  Enforcing qsvc-ibm: {'✓' if backend.get('enforcing_qsvc_ibm') else '✗'}")
    print()
    
    # Entity table
    if status['entity_count'] > 0:
        print_header("Active Entities")
        
        headers = ["Entity ID", "Status", "Molt Count", "Sequence Len", "Fingerprint"]
        rows = []
        
        for entity_id in status['entities']:
            entity = director.active_entities.get(entity_id, {})
            rows.append([
                entity_id,
                entity.get('status', 'unknown'),
                str(entity.get('molt_count', 0)),
                str(len(entity.get('sequence', []))),
                format_fingerprint(entity.get('fingerprint', ''))
            ])
        
        print_table(headers, rows)
    else:
        print("No active entities")


async def show_entity_details(entity_id: str):
    """Display detailed information about an entity."""
    print_header(f"🦀 Entity Details: {entity_id}")
    
    director = SwarmDirector()
    entity = director.active_entities.get(entity_id)
    
    if not entity:
        print(f"Entity '{entity_id}' not found")
        return
    
    print(f"ID: {entity['id']}")
    print(f"Status: {entity['status']}")
    print(f"Fingerprint: {entity['fingerprint']}")
    print(f"Molt Count: {entity['molt_count']}")
    print(f"Created At: {entity['created_at']:.2f}")
    print()
    
    # Sequence embeddings
    print("Sequence Embeddings:")
    if entity['sequence']:
        for i, embedding in enumerate(entity['sequence']):
            print(f"  Step {i}: {format_embedding(embedding)}")
    else:
        print("  (empty)")
    print()
    
    # Config
    print("Configuration:")
    for key, value in entity.get('config', {}).items():
        print(f"  {key}: {value}")


async def show_propagation_kernels():
    """Display kernel matrix for entity propagation."""
    print_header("🦀 Propagation Kernel Matrix (K > 0.7 threshold)")
    
    from quantum import quantum_kernel_estimation
    
    director = SwarmDirector()
    entity_ids = list(director.active_entities.keys())
    
    if len(entity_ids) < 2:
        print("Need at least 2 entities for kernel computation")
        return
    
    # Compute kernel matrix
    headers = ["Source", "Target", "Kernel K(x₁,x₂)", "Threshold", "Status"]
    rows = []
    
    for i, eid1 in enumerate(entity_ids):
        for j, eid2 in enumerate(entity_ids):
            if i <= j:
                e1 = director.active_entities[eid1]
                e2 = director.active_entities[eid2]
                
                seq1 = e1.get('sequence', [[0.5]*10])
                seq2 = e2.get('sequence', [[0.5]*10])
                
                if seq1 and seq2:
                    k = quantum_kernel_estimation(seq1[-1], seq2[-1])
                    threshold_met = k > 0.7
                    status_icon = "✓ ACCEPT" if threshold_met else "✗ REJECT"
                    
                    rows.append([
                        eid1,
                        eid2,
                        f"{k:.4f}",
                        "0.7",
                        status_icon
                    ])
    
    print_table(headers, rows)


async def show_event_log(count: int = 10, event_type: str = None):
    """Display recent events from the log."""
    print_header(f"🦀 Recent Events (last {count})")
    
    director = SwarmDirector()
    events_file = director.events_log
    
    if not events_file.exists():
        print("No events logged yet")
        return
    
    # Read last N events
    events = []
    with events_file.open("r") as f:
        for line in f:
            try:
                event = json.loads(line.strip())
                if event_type is None or event.get('type') == event_type:
                    events.append(event)
            except json.JSONDecodeError:
                pass
    
    # Show last N
    recent = events[-count:] if len(events) > count else events
    
    if not recent:
        print("No events found")
        return
    
    # Print event summary
    headers = ["Type", "Timestamp", "Summary"]
    rows = []
    
    for event in recent:
        event_type = event.get('type', 'unknown')
        timestamp = event.get('timestamp', 0)
        data = event.get('data', {})
        
        # Create summary based on type
        if event_type == 'spawn':
            summary = f"Entity: {data.get('id', 'unknown')}"
        elif event_type == 'propagate':
            kernel = data.get('kernel_value', 'N/A')
            status = data.get('replication_status', 'unknown')
            summary = f"{data.get('from', '?')} → {data.get('to', '?')} K={kernel} ({status})"
        elif event_type == 'molt':
            summary = f"Entity: {data.get('entity_id', '?')} Tenet: {data.get('tenet', '?')} Count: {data.get('molt_count', 0)}"
        else:
            summary = str(data)
        
        rows.append([
            event_type,
            f"{timestamp:.2f}",
            summary[:50]
        ])
    
    print_table(headers, rows)
    print()
    print(f"Total events in log: {len(events)}")


async def demo_lifecycle():
    """Demonstrate full entity lifecycle with visual output."""
    print_header("🦀 Entity Lifecycle Demo")
    
    director = SwarmDirector()
    
    # Spawn entities
    print("\n[Phase 1: SPAWN] Creating entities with equilibrium state [0.5]^10...")
    e1 = await director.spawn_entity("demo-1", {"role": "source", "feature_dimension": 10})
    e2 = await director.spawn_entity("demo-2", {"role": "target", "feature_dimension": 10})
    print(f"✓ Spawned demo-1: {format_fingerprint(e1['fingerprint'])}")
    print(f"✓ Spawned demo-2: {format_fingerprint(e2['fingerprint'])}")
    
    # Propagate
    print("\n[Phase 2: NAVIGATE] Propagating intelligence with K>0.7 threshold...")
    await director.propagate_intelligence("demo-1", ["demo-2"])
    print("✓ Propagation complete (check events.jsonl for kernel values)")
    
    # Molt
    print("\n[Phase 3: MOLT] Executing molt ritual...")
    result = await director.molt_ritual("demo-1", "Shell Mutable")
    print(f"✓ Molt complete: {format_fingerprint(result['old_self'])} → {format_fingerprint(result['new_self'])}")
    print(f"  Molt count: {result['molt_count']}")
    
    # Status
    print("\n[Phase 4: STATUS] Final swarm state...")
    await show_swarm_status()


async def main():
    """Main CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Entity Propagation CLI Visual Tool")
    parser.add_argument("command", choices=["status", "details", "kernels", "events", "demo"],
                       help="Command to execute")
    parser.add_argument("--entity", help="Entity ID (for 'details' command)")
    parser.add_argument("--count", type=int, default=10, help="Number of events to show")
    parser.add_argument("--type", help="Filter events by type")
    
    args = parser.parse_args()
    
    try:
        if args.command == "status":
            await show_swarm_status()
        elif args.command == "details":
            if not args.entity:
                print("Error: --entity required for 'details' command")
                sys.exit(1)
            await show_entity_details(args.entity)
        elif args.command == "kernels":
            await show_propagation_kernels()
        elif args.command == "events":
            await show_event_log(args.count, args.type)
        elif args.command == "demo":
            await demo_lifecycle()
    except KeyboardInterrupt:
        print("\n\nInterrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
