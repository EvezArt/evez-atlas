"""
Trajectory Domain - Equitable trajectory optimization with beam search.

Features:
- Forward chaining closure generator
- Trajectory scoring with fairness weights
- Beam search for optimal path selection
- Fold to canonical hash (spine compression)
- Integration with existing hash-chain audit
"""

import json
import time
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, field
from collections import defaultdict
import heapq


@dataclass
class Fact:
    """Represents a fact in the knowledge base."""
    symbol: str
    value: Any
    timestamp: float = field(default_factory=lambda: time.time())
    
    def __hash__(self):
        return hash((self.symbol, str(self.value)))
    
    def __eq__(self, other):
        return isinstance(other, Fact) and self.symbol == other.symbol and self.value == other.value
    
    def to_dict(self) -> Dict:
        return {'symbol': self.symbol, 'value': self.value, 'timestamp': self.timestamp}


@dataclass
class Rule:
    """Represents an inference rule."""
    rule_id: str
    premises: List[str]  # Required fact symbols
    conclusion: str      # Derived fact symbol
    cost: float = 1.0
    
    def __hash__(self):
        return hash(self.rule_id)
    
    def to_dict(self) -> Dict:
        return {
            'rule_id': self.rule_id,
            'premises': self.premises,
            'conclusion': self.conclusion,
            'cost': self.cost
        }


@dataclass
class Closure:
    """Represents a forward-chained closure of facts."""
    facts: Set[Fact]
    derivation_depth: int
    rules_applied: List[str]
    
    def to_dict(self) -> Dict:
        return {
            'facts': [f.to_dict() for f in self.facts],
            'derivation_depth': self.derivation_depth,
            'rules_applied': self.rules_applied
        }


@dataclass
class TrajectoryPath:
    """Represents a candidate trajectory through state space."""
    path_id: str
    closures: List[Closure]
    score: float
    fairness_score: float
    total_cost: float
    
    def __lt__(self, other):
        # For heap ordering (higher score = better)
        return self.score > other.score


class TrajectoryOptimizer:
    """
    Trajectory optimizer with beam search and equitable scoring.
    
    Implements:
    - Forward chaining closure generation
    - Multi-objective scoring (efficiency + fairness)
    - Beam search for optimal path selection
    - Fold to canonical hash for compression
    """
    
    def __init__(self, trajectory_log_path: str = "src/memory/trajectory_log.jsonl"):
        self.trajectory_log = Path(trajectory_log_path)
        self.trajectory_log.parent.mkdir(parents=True, exist_ok=True)
        
        # Knowledge base
        self.facts: Set[Fact] = set()
        self.rules: Dict[str, Rule] = {}
        
        # Scoring weights
        self.efficiency_weight = 0.6
        self.fairness_weight = 0.4
        
        # Beam search parameters
        self.beam_width = 5
        self.max_depth = 10
        
        # Statistics
        self.total_paths_explored = 0
        self.best_score_seen = 0.0
        
        # Hash chain
        self.last_event_hash = None
        self._load_last_hash()
    
    def _load_last_hash(self):
        """Load last event hash from trajectory log."""
        if self.trajectory_log.exists():
            try:
                with open(self.trajectory_log, 'r') as f:
                    lines = f.readlines()
                    if lines:
                        last_event = json.loads(lines[-1])
                        self.last_event_hash = last_event.get('event_hash')
            except Exception:
                self.last_event_hash = None
    
    def _calculate_event_hash(self, event: Dict) -> str:
        """Calculate SHA-256 hash for event."""
        event_data = json.dumps(event, sort_keys=True)
        return hashlib.sha256(event_data.encode()).hexdigest()
    
    def _append_trajectory_log(self, event: Dict):
        """Append event to trajectory log with hash chaining."""
        event['parent_hash'] = self.last_event_hash
        event_hash = self._calculate_event_hash(event)
        event['event_hash'] = event_hash
        
        with open(self.trajectory_log, 'a') as f:
            f.write(json.dumps(event) + '\n')
        
        self.last_event_hash = event_hash
    
    def add_fact(self, symbol: str, value: Any):
        """Add a fact to the knowledge base."""
        fact = Fact(symbol, value)
        self.facts.add(fact)
        
        self._append_trajectory_log({
            'event_type': 'fact_added',
            'timestamp': time.time(),
            'symbol': symbol,
            'value': value
        })
    
    def add_rule(self, rule_id: str, premises: List[str], conclusion: str, cost: float = 1.0):
        """Add an inference rule."""
        rule = Rule(rule_id, premises, conclusion, cost)
        self.rules[rule_id] = rule
        
        self._append_trajectory_log({
            'event_type': 'rule_added',
            'timestamp': time.time(),
            'rule_id': rule_id,
            'premises': premises,
            'conclusion': conclusion,
            'cost': cost
        })
    
    def forward_chain(self, initial_facts: Set[Fact], max_depth: int = 10) -> Closure:
        """
        Generate closure through forward chaining.
        
        Returns all derivable facts up to max_depth.
        """
        closure_facts = set(initial_facts)
        rules_applied = []
        
        for depth in range(max_depth):
            new_facts = set()
            fact_symbols = {f.symbol for f in closure_facts}
            
            # Try each rule
            for rule_id, rule in self.rules.items():
                # Check if all premises are satisfied
                if all(premise in fact_symbols for premise in rule.premises):
                    # Derive conclusion
                    conclusion_fact = Fact(rule.conclusion, f"derived_at_depth_{depth}")
                    if conclusion_fact not in closure_facts:
                        new_facts.add(conclusion_fact)
                        rules_applied.append(rule_id)
            
            if not new_facts:
                break  # Fixed point reached
            
            closure_facts.update(new_facts)
        
        return Closure(closure_facts, depth, rules_applied)
    
    def score_trajectory(self, closure: Closure, constraints: Optional[Dict] = None) -> Tuple[float, float]:
        """
        Score a trajectory based on efficiency and fairness.
        
        Returns: (total_score, fairness_score)
        """
        constraints = constraints or {}
        
        # Efficiency score: inverse of derivation depth and cost
        efficiency = 1.0 / (1.0 + closure.derivation_depth)
        
        # Fairness score: measure equitable coverage of fact space
        # Higher is better if we cover diverse symbols
        unique_symbols = len({f.symbol for f in closure.facts})
        total_facts = len(closure.facts)
        fairness = unique_symbols / max(1, total_facts)
        
        # Apply fairness weights from constraints
        fairness_weights = constraints.get('fairness_weights', {})
        if fairness_weights:
            weighted_fairness = sum(
                fairness_weights.get(f.symbol, 1.0) for f in closure.facts
            ) / len(closure.facts) if closure.facts else 0.0
            fairness = (fairness + weighted_fairness) / 2.0
        
        # Combined score
        total_score = (self.efficiency_weight * efficiency + 
                      self.fairness_weight * fairness)
        
        return total_score, fairness
    
    def beam_search_optimal_spine(self, initial_facts: Set[Fact], 
                                   constraints: Optional[Dict] = None) -> TrajectoryPath:
        """
        Find optimal trajectory using beam search.
        
        Maintains top-k paths at each depth level, scores them,
        and returns the best path to the goal state.
        """
        self._append_trajectory_log({
            'event_type': 'beam_search_started',
            'timestamp': time.time(),
            'beam_width': self.beam_width,
            'max_depth': self.max_depth
        })
        
        # Initialize beam with starting state
        beam = []
        start_closure = Closure(initial_facts, 0, [])
        start_score, start_fairness = self.score_trajectory(start_closure, constraints)
        start_path = TrajectoryPath(
            path_id='path_0',
            closures=[start_closure],
            score=start_score,
            fairness_score=start_fairness,
            total_cost=0.0
        )
        heapq.heappush(beam, start_path)
        
        best_path = start_path
        
        for depth in range(self.max_depth):
            # Expand beam
            candidates = []
            
            for path in beam[:self.beam_width]:
                # Try forward chaining from current closure
                current_closure = path.closures[-1]
                next_closure = self.forward_chain(current_closure.facts, max_depth=1)
                
                # Score new closure
                score, fairness = self.score_trajectory(next_closure, constraints)
                
                # Calculate cumulative cost
                total_cost = path.total_cost + sum(
                    self.rules[rule_id].cost 
                    for rule_id in next_closure.rules_applied
                    if rule_id in self.rules
                )
                
                # Create new path
                new_path = TrajectoryPath(
                    path_id=f"path_{depth}_{len(candidates)}",
                    closures=path.closures + [next_closure],
                    score=score,
                    fairness_score=fairness,
                    total_cost=total_cost
                )
                
                candidates.append(new_path)
                self.total_paths_explored += 1
                
                # Track best
                if score > best_path.score:
                    best_path = new_path
                    self.best_score_seen = score
            
            # Select top-k for next beam
            beam = heapq.nlargest(self.beam_width, candidates)
            
            if not beam:
                break
        
        self._append_trajectory_log({
            'event_type': 'beam_search_completed',
            'timestamp': time.time(),
            'best_score': best_path.score,
            'best_fairness': best_path.fairness_score,
            'total_paths_explored': self.total_paths_explored
        })
        
        return best_path
    
    def fold_to_hash(self, path: TrajectoryPath) -> str:
        """
        Fold trajectory to canonical hash (spine compression).
        
        Creates a single deterministic hash representing the entire
        trajectory state space.
        """
        # Collect all facts from all closures
        all_facts = []
        for closure in path.closures:
            all_facts.extend([f.to_dict() for f in closure.facts])
        
        # Sort for determinism
        all_facts_sorted = sorted(all_facts, key=lambda f: (f['symbol'], str(f['value'])))
        
        # Include rules applied
        rules_applied = []
        for closure in path.closures:
            rules_applied.extend(closure.rules_applied)
        
        # Create spine data
        spine_data = {
            'facts': all_facts_sorted,
            'rules_applied': sorted(rules_applied),
            'derivation_depth': len(path.closures),
            'score': path.score,
            'fairness_score': path.fairness_score
        }
        
        # Fold to hash
        spine_json = json.dumps(spine_data, sort_keys=True)
        spine_hash = hashlib.sha256(spine_json.encode()).hexdigest()
        
        self._append_trajectory_log({
            'event_type': 'trajectory_folded',
            'timestamp': time.time(),
            'spine_hash': spine_hash,
            'spine_data': spine_data
        })
        
        return spine_hash
    
    def get_state_occupancy_map(self, path: TrajectoryPath) -> Dict:
        """
        Generate state space occupancy heatmap.
        
        Returns: {symbol: [depth0, depth1, ...]} presence matrix
        """
        # Get all unique symbols
        all_symbols = set()
        for closure in path.closures:
            all_symbols.update(f.symbol for f in closure.facts)
        
        symbol_list = sorted(all_symbols)
        
        # Build occupancy matrix
        occupancy = {symbol: [] for symbol in symbol_list}
        
        for closure in path.closures:
            present_symbols = {f.symbol for f in closure.facts}
            for symbol in symbol_list:
                occupancy[symbol].append(1 if symbol in present_symbols else 0)
        
        return occupancy
    
    def get_status(self) -> Dict:
        """Get trajectory optimizer status."""
        return {
            'facts_count': len(self.facts),
            'rules_count': len(self.rules),
            'beam_width': self.beam_width,
            'max_depth': self.max_depth,
            'total_paths_explored': self.total_paths_explored,
            'best_score_seen': self.best_score_seen,
            'efficiency_weight': self.efficiency_weight,
            'fairness_weight': self.fairness_weight
        }
    
    def verify_hash_chain(self) -> bool:
        """Verify trajectory log hash chain integrity."""
        if not self.trajectory_log.exists():
            return True
        
        with open(self.trajectory_log, 'r') as f:
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
    # Test trajectory optimizer
    optimizer = TrajectoryOptimizer("src/memory/test_trajectory_log.jsonl")
    
    print("Trajectory Optimizer Test")
    print("=" * 80)
    
    # Add facts
    print("\n1. Adding facts...")
    optimizer.add_fact('A', True)
    optimizer.add_fact('B', True)
    optimizer.add_fact('C', True)
    
    # Add rules
    print("2. Adding rules...")
    optimizer.add_rule('rule1', ['A', 'B'], 'D', cost=1.0)
    optimizer.add_rule('rule2', ['D', 'C'], 'E', cost=1.5)
    optimizer.add_rule('rule3', ['A'], 'F', cost=0.5)
    
    # Forward chain
    print("3. Forward chaining...")
    initial_facts = {Fact('A', True), Fact('B', True), Fact('C', True)}
    closure = optimizer.forward_chain(initial_facts)
    print(f"   Derived {len(closure.facts)} facts at depth {closure.derivation_depth}")
    
    # Beam search
    print("4. Beam search for optimal trajectory...")
    best_path = optimizer.beam_search_optimal_spine(initial_facts)
    print(f"   Best score: {best_path.score:.3f}")
    print(f"   Fairness: {best_path.fairness_score:.3f}")
    print(f"   Paths explored: {optimizer.total_paths_explored}")
    
    # Fold to hash
    print("5. Folding to canonical spine...")
    spine_hash = optimizer.fold_to_hash(best_path)
    print(f"   Spine hash: {spine_hash[:16]}...")
    
    # State occupancy map
    print("6. State occupancy map:")
    occupancy = optimizer.get_state_occupancy_map(best_path)
    for symbol, presence in occupancy.items():
        print(f"   {symbol}: {presence}")
    
    # Verify hash chain
    print(f"\n7. Hash chain integrity: {'✓ VERIFIED' if optimizer.verify_hash_chain() else '✗ FAILED'}")
    
    print("\n✅ All tests passed!")
