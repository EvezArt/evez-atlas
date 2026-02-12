"""
Parallel Hypotheses - HandshakeOS-E

Multi-perspective hypothesis testing from me/we/they/system viewpoints.

Design Philosophy:
- Four perspectives: Individual (me), group (we), external (they), systemic (system)
- Each hypothesis has probability, falsifiers, domain signature
- Complete versioning for all hypothesis changes
- Direct linkage to Test objects for verification
- Evidence tracking (supporting/contradicting)
- Consensus and divergence analysis

For the stranger who wears your shell tomorrow:
Parallel Hypotheses capture different worldviews simultaneously. When evaluating
a situation, we don't assume one "correct" view. Instead, we maintain hypotheses
from multiple perspectives and track how they converge or diverge. This enables
robust decision-making and identifies blind spots.

Example: "Will this feature be adopted?"
- Me: "I think it will be adopted" (personal view based on my understanding)
- We: "Our team thinks it will be adopted" (group consensus)
- They: "Users say they want it" (external stakeholder view)
- System: "Historical data suggests 60% adoption" (data-driven view)
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4
import json
import statistics


@dataclass
class HypothesisPerspective:
    """
    Single perspective on a hypothesis (me/we/they/system).
    
    Each perspective contains:
    - The hypothesis statement (what we think is true)
    - Probability assessment (0.0-1.0)
    - Falsifiers (what would prove this wrong)
    - Domain signature (emergent domain mixture)
    - Evidence tracking (supporting/contradicting)
    - Test linkage (which tests verify this)
    - Version history (all changes)
    
    Attributes:
        perspective: Which viewpoint ("me", "we", "they", "system")
        hypothesis: The hypothesis statement
        probability: Current probability this is true (0.0-1.0)
        falsifiers: List of conditions that would disprove this
        domain_signature: Emergent domain mixture vector
        version: Current version of this hypothesis
        version_history: All previous versions
        test_ids: Linked Test object IDs
        supporting_evidence: Event IDs that support this
        contradicting_evidence: Event IDs that contradict this
        proposed_by: Who proposed this hypothesis
        last_updated: Last modification time
    """
    perspective: str = ""  # "me", "we", "they", "system"
    hypothesis: str = ""
    probability: float = 0.5
    falsifiers: List[str] = field(default_factory=list)
    domain_signature: Dict[str, float] = field(default_factory=dict)
    
    # Versioning
    version: str = "1.0.0"
    version_history: List[Dict[str, Any]] = field(default_factory=list)
    
    # Test linkage
    test_ids: List[str] = field(default_factory=list)
    
    # Evidence tracking
    supporting_evidence: List[str] = field(default_factory=list)
    contradicting_evidence: List[str] = field(default_factory=list)
    
    # Attribution
    proposed_by: str = ""
    last_updated: datetime = field(default_factory=datetime.utcnow)
    
    def add_supporting_evidence(self, event_id: str):
        """Add evidence that supports this hypothesis."""
        if event_id not in self.supporting_evidence:
            self.supporting_evidence.append(event_id)
    
    def add_contradicting_evidence(self, event_id: str):
        """Add evidence that contradicts this hypothesis."""
        if event_id not in self.contradicting_evidence:
            self.contradicting_evidence.append(event_id)
    
    def add_falsifier(self, condition: str):
        """Add a condition that would disprove this hypothesis."""
        if condition not in self.falsifiers:
            self.falsifiers.append(condition)
    
    def link_test(self, test_id: str):
        """Link a Test object to this hypothesis."""
        if test_id not in self.test_ids:
            self.test_ids.append(test_id)
    
    def update_probability(self, new_probability: float, updated_by: str):
        """
        Update probability and record in version history.
        
        Args:
            new_probability: New probability value (0.0-1.0)
            updated_by: Who is updating this
        """
        # Record old version in history
        old_version = {
            'version': self.version,
            'hypothesis': self.hypothesis,
            'probability': self.probability,
            'timestamp': self.last_updated.isoformat(),
            'updated_by': self.proposed_by
        }
        self.version_history.append(old_version)
        
        # Update to new version
        self.probability = max(0.0, min(1.0, new_probability))  # Clamp to [0,1]
        self.last_updated = datetime.utcnow()
        self.proposed_by = updated_by
        
        # Increment version
        major, minor, patch = map(int, self.version.split('.'))
        self.version = f"{major}.{minor}.{patch + 1}"
    
    def evidence_ratio(self) -> float:
        """
        Calculate ratio of supporting to total evidence.
        
        Returns:
            Float 0.0-1.0: proportion of evidence that is supporting
        """
        total = len(self.supporting_evidence) + len(self.contradicting_evidence)
        if total == 0:
            return 0.5  # No evidence = neutral
        return len(self.supporting_evidence) / total
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'perspective': self.perspective,
            'hypothesis': self.hypothesis,
            'probability': self.probability,
            'falsifiers': self.falsifiers,
            'domain_signature': self.domain_signature,
            'version': self.version,
            'version_history': self.version_history,
            'test_ids': self.test_ids,
            'supporting_evidence': self.supporting_evidence,
            'contradicting_evidence': self.contradicting_evidence,
            'proposed_by': self.proposed_by,
            'last_updated': self.last_updated.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HypothesisPerspective':
        """Create HypothesisPerspective from dictionary."""
        if isinstance(data.get('last_updated'), str):
            data['last_updated'] = datetime.fromisoformat(data['last_updated'])
        return cls(**data)


@dataclass
class ParallelHypotheses:
    """
    Parallel Hypotheses - maintains multiple perspective viewpoints simultaneously.
    
    Instead of assuming one "correct" view, we maintain hypotheses from four perspectives:
    1. "me" - Individual perspective (my understanding)
    2. "we" - Group perspective (our collective view)
    3. "they" - External perspective (stakeholder/user view)
    4. "system" - Systemic perspective (data-driven/objective view)
    
    This enables:
    - Identifying blind spots (high divergence)
    - Building consensus (convergence over time)
    - Understanding different stakeholder views
    - Making robust decisions across perspectives
    
    Example Usage:
        >>> from src.mastra.core import ParallelHypotheses, HypothesisPerspective
        >>> 
        >>> # Create hypothesis set about feature adoption
        >>> hypotheses = ParallelHypotheses(
        ...     context="Will users adopt the new search feature?",
        ...     me_perspective=HypothesisPerspective(
        ...         perspective="me",
        ...         hypothesis="Users will adopt it quickly",
        ...         probability=0.7,
        ...         falsifiers=["No usage after 2 weeks", "Negative feedback"],
        ...         proposed_by="product_manager"
        ...     ),
        ...     we_perspective=HypothesisPerspective(
        ...         perspective="we",
        ...         hypothesis="Team thinks gradual adoption",
        ...         probability=0.6,
        ...         proposed_by="team_lead"
        ...     ),
        ...     # ... other perspectives
        ... )
        >>> 
        >>> # Calculate consensus
        >>> consensus = hypotheses.calculate_consensus()
        >>> print(f"Consensus probability: {consensus:.2%}")
    """
    
    # Core identification
    hypothesis_id: str = field(default_factory=lambda: str(uuid4()))
    context: str = ""  # What are we hypothesizing about?
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    # Four perspectives
    me_perspective: HypothesisPerspective = field(default_factory=HypothesisPerspective)
    we_perspective: HypothesisPerspective = field(default_factory=HypothesisPerspective)
    they_perspective: HypothesisPerspective = field(default_factory=HypothesisPerspective)
    system_perspective: HypothesisPerspective = field(default_factory=HypothesisPerspective)
    
    # Meta-analysis
    consensus_probability: float = 0.5
    divergence_score: float = 0.0
    
    # Linking
    related_events: List[str] = field(default_factory=list)  # UniversalEventRecord IDs
    related_intents: List[str] = field(default_factory=list)  # IntentToken IDs
    
    # Versioning
    version: str = "1.0.0"
    version_history: List[Dict[str, Any]] = field(default_factory=list)
    
    def __post_init__(self):
        """Post-initialization: set perspective names and calculate meta-analysis."""
        self.me_perspective.perspective = "me"
        self.we_perspective.perspective = "we"
        self.they_perspective.perspective = "they"
        self.system_perspective.perspective = "system"
        
        self.calculate_consensus()
        self.calculate_divergence()
    
    def get_all_perspectives(self) -> List[HypothesisPerspective]:
        """Get list of all four perspectives."""
        return [
            self.me_perspective,
            self.we_perspective,
            self.they_perspective,
            self.system_perspective
        ]
    
    def get_perspective(self, name: str) -> Optional[HypothesisPerspective]:
        """
        Get a specific perspective by name.
        
        Args:
            name: "me", "we", "they", or "system"
            
        Returns:
            HypothesisPerspective or None
        """
        perspectives = {
            "me": self.me_perspective,
            "we": self.we_perspective,
            "they": self.they_perspective,
            "system": self.system_perspective
        }
        return perspectives.get(name)
    
    def calculate_consensus(self) -> float:
        """
        Calculate consensus probability (weighted average of all perspectives).
        
        Returns:
            Float 0.0-1.0: consensus probability
        """
        probabilities = [
            self.me_perspective.probability,
            self.we_perspective.probability,
            self.they_perspective.probability,
            self.system_perspective.probability
        ]
        
        # Simple average (could be weighted by confidence/evidence in future)
        self.consensus_probability = statistics.mean(probabilities)
        return self.consensus_probability
    
    def calculate_divergence(self) -> float:
        """
        Calculate divergence score (how much perspectives differ).
        
        Higher divergence = perspectives disagree significantly
        Lower divergence = perspectives converge
        
        Returns:
            Float: standard deviation of probabilities (measure of spread)
        """
        probabilities = [
            self.me_perspective.probability,
            self.we_perspective.probability,
            self.they_perspective.probability,
            self.system_perspective.probability
        ]
        
        if len(probabilities) < 2:
            self.divergence_score = 0.0
        else:
            self.divergence_score = statistics.stdev(probabilities)
        
        return self.divergence_score
    
    def link_event(self, event_id: str):
        """Link to a UniversalEventRecord."""
        if event_id not in self.related_events:
            self.related_events.append(event_id)
    
    def link_intent(self, intent_id: str):
        """Link to an IntentToken."""
        if intent_id not in self.related_intents:
            self.related_intents.append(intent_id)
    
    def update_with_evidence(self, event_id: str, 
                            supports_perspectives: List[str],
                            contradicts_perspectives: List[str]):
        """
        Update hypotheses with new evidence.
        
        Args:
            event_id: UniversalEventRecord ID
            supports_perspectives: List of perspective names this evidence supports
            contradicts_perspectives: List of perspective names this contradicts
        """
        for perspective_name in supports_perspectives:
            perspective = self.get_perspective(perspective_name)
            if perspective:
                perspective.add_supporting_evidence(event_id)
        
        for perspective_name in contradicts_perspectives:
            perspective = self.get_perspective(perspective_name)
            if perspective:
                perspective.add_contradicting_evidence(event_id)
        
        # Link event
        self.link_event(event_id)
        
        # Recalculate meta-analysis
        self.calculate_consensus()
        self.calculate_divergence()
    
    def get_strongest_perspective(self) -> HypothesisPerspective:
        """
        Get the perspective with highest probability.
        
        Returns:
            HypothesisPerspective with highest probability
        """
        return max(self.get_all_perspectives(), key=lambda p: p.probability)
    
    def get_weakest_perspective(self) -> HypothesisPerspective:
        """
        Get the perspective with lowest probability.
        
        Returns:
            HypothesisPerspective with lowest probability
        """
        return min(self.get_all_perspectives(), key=lambda p: p.probability)
    
    def is_converging(self, threshold: float = 0.1) -> bool:
        """
        Check if perspectives are converging (low divergence).
        
        Args:
            threshold: Divergence threshold (default 0.1)
            
        Returns:
            bool: True if divergence <= threshold
        """
        return self.divergence_score <= threshold
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'hypothesis_id': self.hypothesis_id,
            'context': self.context,
            'created_at': self.created_at.isoformat(),
            'me_perspective': self.me_perspective.to_dict(),
            'we_perspective': self.we_perspective.to_dict(),
            'they_perspective': self.they_perspective.to_dict(),
            'system_perspective': self.system_perspective.to_dict(),
            'consensus_probability': self.consensus_probability,
            'divergence_score': self.divergence_score,
            'related_events': self.related_events,
            'related_intents': self.related_intents,
            'version': self.version,
            'version_history': self.version_history,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ParallelHypotheses':
        """Create ParallelHypotheses from dictionary."""
        # Parse timestamps
        if isinstance(data.get('created_at'), str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        
        # Parse perspectives
        for perspective_key in ['me_perspective', 'we_perspective', 'they_perspective', 'system_perspective']:
            if isinstance(data.get(perspective_key), dict):
                data[perspective_key] = HypothesisPerspective.from_dict(data[perspective_key])
        
        return cls(**data)
    
    def save_to_log(self, log_path: str):
        """Append this hypothesis set to a JSONL log file."""
        import os
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        
        with open(log_path, 'a') as f:
            json.dump(self.to_dict(), f)
            f.write('\n')
    
    @staticmethod
    def load_from_log(log_path: str) -> List['ParallelHypotheses']:
        """Load all hypothesis sets from a JSONL log file."""
        hypotheses = []
        try:
            with open(log_path, 'r') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        hypotheses.append(ParallelHypotheses.from_dict(data))
        except FileNotFoundError:
            pass
        
        return hypotheses
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        return (
            f"ParallelHypotheses("
            f"id={self.hypothesis_id[:8]}..., "
            f"context='{self.context[:30]}...', "
            f"consensus={self.consensus_probability:.2f}, "
            f"divergence={self.divergence_score:.2f})"
        )


if __name__ == "__main__":
    # Demo: Create and analyze parallel hypotheses
    print("🎯 ParallelHypotheses Demo")
    print("=" * 60)
    
    # Create hypothesis set about feature adoption
    hypotheses = ParallelHypotheses(
        context="Will users adopt the new AI-powered search feature?",
        me_perspective=HypothesisPerspective(
            perspective="me",
            hypothesis="Users will adopt it quickly because it's innovative",
            probability=0.75,
            falsifiers=[
                "No usage after 2 weeks",
                "User complaints about complexity",
                "Negative NPS scores"
            ],
            domain_signature={'technical': 0.6, 'social': 0.4},
            proposed_by="product_manager_alice"
        ),
        we_perspective=HypothesisPerspective(
            perspective="we",
            hypothesis="Team thinks adoption will be gradual with training",
            probability=0.60,
            falsifiers=[
                "Usage below 10% after 1 month",
                "Training sessions poorly attended"
            ],
            domain_signature={'technical': 0.4, 'social': 0.6},
            proposed_by="team_lead_bob"
        ),
        they_perspective=HypothesisPerspective(
            perspective="they",
            hypothesis="Early users express cautious optimism",
            probability=0.55,
            falsifiers=[
                "Beta testers report confusion",
                "Feature requests for simplification"
            ],
            domain_signature={'social': 0.8, 'cognitive': 0.2},
            proposed_by="user_research_carol"
        ),
        system_perspective=HypothesisPerspective(
            perspective="system",
            hypothesis="Historical data suggests 65% adoption for similar features",
            probability=0.65,
            falsifiers=[
                "Usage trends below statistical model",
                "A/B test shows no improvement"
            ],
            domain_signature={'technical': 0.7, 'temporal': 0.3},
            proposed_by="data_analyst_david"
        )
    )
    
    print(f"\n✅ Created: {hypotheses}")
    print(f"\n📊 Perspectives:")
    for p in hypotheses.get_all_perspectives():
        print(f"   {p.perspective:6s}: {p.probability:.2%} - '{p.hypothesis[:50]}...'")
    
    print(f"\n🎯 Meta-Analysis:")
    print(f"   Consensus: {hypotheses.consensus_probability:.2%}")
    print(f"   Divergence: {hypotheses.divergence_score:.3f}")
    print(f"   Converging: {hypotheses.is_converging()}")
    
    strongest = hypotheses.get_strongest_perspective()
    weakest = hypotheses.get_weakest_perspective()
    print(f"\n   Strongest: {strongest.perspective} ({strongest.probability:.2%})")
    print(f"   Weakest: {weakest.perspective} ({weakest.probability:.2%})")
    
    # Simulate evidence collection
    print(f"\n🔬 Simulating Evidence Collection...")
    
    # Week 1: Positive early signals
    hypotheses.update_with_evidence(
        "event_001_early_usage",
        supports_perspectives=["me", "they"],
        contradicts_perspectives=[]
    )
    print(f"   Week 1: Early positive usage")
    
    # Week 2: Training challenges
    hypotheses.update_with_evidence(
        "event_002_training_issues",
        supports_perspectives=["we"],  # Confirms need for training
        contradicts_perspectives=["me"]  # Not as quick as predicted
    )
    print(f"   Week 2: Training challenges observed")
    
    # Update probabilities based on evidence
    hypotheses.me_perspective.update_probability(0.65, "product_manager_alice")  # Adjust down
    hypotheses.we_perspective.update_probability(0.70, "team_lead_bob")  # Adjust up
    
    # Recalculate
    hypotheses.calculate_consensus()
    hypotheses.calculate_divergence()
    
    print(f"\n📈 After Evidence:")
    print(f"   Consensus: {hypotheses.consensus_probability:.2%}")
    print(f"   Divergence: {hypotheses.divergence_score:.3f}")
    print(f"   Converging: {hypotheses.is_converging()}")
    
    print(f"\n📝 Evidence Summary:")
    for p in hypotheses.get_all_perspectives():
        supporting = len(p.supporting_evidence)
        contradicting = len(p.contradicting_evidence)
        ratio = p.evidence_ratio()
        print(f"   {p.perspective:6s}: {supporting} supporting, {contradicting} contradicting (ratio: {ratio:.2f})")
    
    # Save to log
    import tempfile
    import os
    with tempfile.TemporaryDirectory() as tmpdir:
        log_path = os.path.join(tmpdir, "hypotheses.jsonl")
        hypotheses.save_to_log(log_path)
        print(f"\n💾 Saved to: {log_path}")
        
        # Load back
        loaded = ParallelHypotheses.load_from_log(log_path)
        print(f"✅ Loaded {len(loaded)} hypothesis set(s) from log")
    
    print("\n" + "=" * 60)
    print("✅ Demo complete!")
