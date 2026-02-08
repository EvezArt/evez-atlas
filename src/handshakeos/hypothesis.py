"""
Hypothesis - Parallel model tracking

Tracks multiple parallel hypotheses (me/we/they/system models) with:
- Probability estimates
- Falsifier(s) - conditions that would disprove the hypothesis
- Domain-signature mixture vector (emergent classification)

Design Principles:
- No mandatory labels
- Parallel tracking of multiple perspectives
- Explicit falsification criteria
- Emergent domain signatures
"""

import time
import uuid
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, List, Any, Optional

from .event_record import DomainMixtureVector


class ModelPerspective(Enum):
    """Perspective of the hypothesis model"""
    ME = "me"  # First-person perspective
    WE = "we"  # Collective/group perspective
    THEY = "they"  # Third-party perspective
    SYSTEM = "system"  # System-level perspective
    UNKNOWN = "unknown"  # Unspecified perspective


@dataclass
class Falsifier:
    """
    Condition that would falsify/disprove a hypothesis.
    
    Explicit falsification criteria enable rigorous hypothesis testing.
    """
    
    # What condition would falsify this hypothesis?
    condition: str
    condition_details: Dict[str, Any] = field(default_factory=dict)
    
    # How to test this falsifier
    test_procedure: Optional[str] = None
    
    # Has this been tested?
    tested: bool = False
    test_result: Optional[bool] = None  # True = falsified, False = not falsified
    test_timestamp: Optional[float] = None
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class ParallelModel:
    """
    A single model/hypothesis in the parallel tracking system.
    
    Represents one perspective's view of reality with probability estimate,
    falsifiers, and emergent domain signature.
    """
    
    # Core identifiers
    model_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: float = field(default_factory=time.time)
    
    # Model content
    description: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    
    # Perspective
    perspective: ModelPerspective = ModelPerspective.UNKNOWN
    
    # Probability estimate (0.0 to 1.0)
    probability: float = 0.5
    probability_basis: Optional[str] = None
    
    # Falsification criteria
    falsifiers: List[Falsifier] = field(default_factory=list)
    
    # Emergent domain signature (can be empty/refined later)
    domain_mixture: Optional[DomainMixtureVector] = None
    
    # Evidence tracking
    supporting_events: List[str] = field(default_factory=list)
    contradicting_events: List[str] = field(default_factory=list)
    
    # Last updated
    updated_at: float = field(default_factory=time.time)
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def update_probability(self, new_probability: float, basis: Optional[str] = None) -> None:
        """Update probability estimate"""
        self.probability = max(0.0, min(1.0, new_probability))
        if basis:
            self.probability_basis = basis
        self.updated_at = time.time()
    
    def add_falsifier(self, condition: str, test_procedure: Optional[str] = None, **kwargs) -> Falsifier:
        """Add a falsifier to this model"""
        falsifier = Falsifier(
            condition=condition,
            test_procedure=test_procedure,
            **kwargs
        )
        self.falsifiers.append(falsifier)
        self.updated_at = time.time()
        return falsifier
    
    def add_evidence(self, event_id: str, supports: bool) -> None:
        """Add evidence for or against this model"""
        if supports:
            self.supporting_events.append(event_id)
        else:
            self.contradicting_events.append(event_id)
        self.updated_at = time.time()
    
    def is_falsified(self) -> bool:
        """Check if any falsifier has been confirmed"""
        return any(f.test_result is True for f in self.falsifiers)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['perspective'] = self.perspective.value
        if self.domain_mixture:
            data['domain_mixture'] = self.domain_mixture.to_dict()
        return data


@dataclass
class Hypothesis:
    """
    Hypothesis with parallel model tracking (me/we/they/system).
    
    Maintains multiple perspectives simultaneously, each with their own
    probability, falsifiers, and domain signatures.
    
    Design:
    - No single "correct" model
    - All perspectives tracked in parallel
    - Emergent understanding from model convergence/divergence
    """
    
    # Core identifiers
    hypothesis_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: float = field(default_factory=time.time)
    
    # Hypothesis content
    name: str = ""
    description: str = ""
    
    # Parallel models (me/we/they/system)
    models: Dict[str, ParallelModel] = field(default_factory=dict)
    
    # Links to system objects
    related_events: List[str] = field(default_factory=list)
    related_intents: List[str] = field(default_factory=list)
    related_tests: List[str] = field(default_factory=list)
    
    # Last updated
    updated_at: float = field(default_factory=time.time)
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_model(
        self,
        perspective: ModelPerspective,
        description: str,
        probability: float = 0.5,
        **kwargs
    ) -> ParallelModel:
        """Add a model from a specific perspective"""
        model = ParallelModel(
            description=description,
            perspective=perspective,
            probability=probability,
            **kwargs
        )
        self.models[model.model_id] = model
        self.updated_at = time.time()
        return model
    
    def get_models_by_perspective(self, perspective: ModelPerspective) -> List[ParallelModel]:
        """Get all models from a specific perspective"""
        return [
            model for model in self.models.values()
            if model.perspective == perspective
        ]
    
    def get_consensus_probability(self) -> float:
        """
        Calculate consensus probability across all models.
        
        Simple average for now, could be weighted by confidence later.
        """
        if not self.models:
            return 0.0
        
        return sum(m.probability for m in self.models.values()) / len(self.models)
    
    def get_perspective_divergence(self) -> float:
        """
        Calculate how much perspectives diverge.
        
        Returns standard deviation of probabilities (0 = perfect agreement).
        """
        if len(self.models) < 2:
            return 0.0
        
        probs = [m.probability for m in self.models.values()]
        mean = sum(probs) / len(probs)
        variance = sum((p - mean) ** 2 for p in probs) / len(probs)
        return variance ** 0.5
    
    def add_test_link(self, test_id: str) -> None:
        """Link a test to this hypothesis"""
        if test_id not in self.related_tests:
            self.related_tests.append(test_id)
            self.updated_at = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        # Convert models dict to proper format
        data['models'] = {
            model_id: model.to_dict()
            for model_id, model in self.models.items()
        }
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Hypothesis':
        """Create from dictionary"""
        # Handle models reconstruction
        if 'models' in data and isinstance(data['models'], dict):
            models = {}
            for model_id, model_data in data['models'].items():
                # Handle perspective enum
                if 'perspective' in model_data and isinstance(model_data['perspective'], str):
                    model_data['perspective'] = ModelPerspective(model_data['perspective'])
                
                # Handle domain mixture
                if 'domain_mixture' in model_data and isinstance(model_data['domain_mixture'], dict):
                    dmv_data = model_data['domain_mixture']
                    custom = dmv_data.pop('custom_domains', {})
                    model_data['domain_mixture'] = DomainMixtureVector(
                        custom_domains=custom,
                        **{k: v for k, v in dmv_data.items() if k != 'custom_domains'}
                    )
                
                # Handle falsifiers
                if 'falsifiers' in model_data:
                    model_data['falsifiers'] = [
                        Falsifier(**f) if isinstance(f, dict) else f
                        for f in model_data['falsifiers']
                    ]
                
                models[model_id] = ParallelModel(**model_data)
            
            data['models'] = models
        
        return cls(**data)


class HypothesisRegistry:
    """
    Registry for tracking hypotheses and their models.
    
    Enables querying, comparison, and analysis of parallel hypotheses.
    """
    
    def __init__(self):
        """Initialize hypothesis registry"""
        self.hypotheses: Dict[str, Hypothesis] = {}
    
    def register(self, hypothesis: Hypothesis) -> None:
        """Register a new hypothesis"""
        self.hypotheses[hypothesis.hypothesis_id] = hypothesis
    
    def get(self, hypothesis_id: str) -> Optional[Hypothesis]:
        """Get hypothesis by ID"""
        return self.hypotheses.get(hypothesis_id)
    
    def query_by_perspective(self, perspective: ModelPerspective) -> List[Hypothesis]:
        """Get all hypotheses that have models from this perspective"""
        return [
            hyp for hyp in self.hypotheses.values()
            if any(m.perspective == perspective for m in hyp.models.values())
        ]
    
    def get_high_confidence(self, threshold: float = 0.75) -> List[Hypothesis]:
        """Get hypotheses with consensus probability above threshold"""
        return [
            hyp for hyp in self.hypotheses.values()
            if hyp.get_consensus_probability() >= threshold
        ]
    
    def get_controversial(self, threshold: float = 0.3) -> List[Hypothesis]:
        """Get hypotheses with high perspective divergence"""
        return [
            hyp for hyp in self.hypotheses.values()
            if hyp.get_perspective_divergence() >= threshold
        ]
