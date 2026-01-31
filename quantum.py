"""
Quantum Threat Detection System - Core Module

This module provides quantum computing utilities for threat detection
using quantum-inspired algorithms and feature maps.
"""

import hashlib
import json
import math
from typing import Any, Dict, List, Optional

# Supported hash algorithms for fingerprinting
SUPPORTED_ALGORITHMS = frozenset(["sha256", "sha384", "sha512", "sha3_256", "sha3_512"])

__all__ = [
    "QuantumFeatureMap",
    "ThreatFingerprint",
    "compute_fingerprint",
    "encode_features",
    "evaluate_navigation_sequence",
    "manifold_projection",
    "predict_navigation_probabilities",
    "quantum_kernel_estimation",
]


class QuantumFeatureMap:
    """
    Implements a quantum feature map for encoding classical data
    into a quantum state representation.
    
    This is a classical simulation of the ZZFeatureMap used in
    quantum machine learning for threat detection.
    
    Note:
        This is a classical simulation and does not provide true quantum
        advantage. For production use with real quantum hardware, use
        qiskit.circuit.library.ZZFeatureMap with IBM Quantum backends.
        The simulation is limited to 10 qubits to maintain reasonable
        performance (2^10 = 1024 state vector elements).
    """
    
    # Maximum qubits for classical simulation (2^10 = 1024 amplitudes)
    MAX_SIMULATION_QUBITS = 10
    
    def __init__(self, feature_dimension: int = 10, reps: int = 2):
        """
        Initialize the quantum feature map.
        
        Args:
            feature_dimension: Number of input features
            reps: Number of repetitions of the feature map circuit
        """
        self.feature_dimension = feature_dimension
        self.reps = reps
        self._num_qubits = min(feature_dimension, self.MAX_SIMULATION_QUBITS)
    
    @property
    def num_qubits(self) -> int:
        """Return the number of qubits used in the feature map."""
        return self._num_qubits
    
    def encode(self, features: List[float]) -> List[complex]:
        """
        Encode classical features into a quantum state vector.
        
        Args:
            features: List of numerical features to encode
            
        Returns:
            List of complex amplitudes representing the quantum state
        """
        if len(features) < self.feature_dimension:
            features = features + [0.0] * (self.feature_dimension - len(features))
        
        # Simulate quantum state encoding using rotation angles
        state_size = 2 ** self._num_qubits
        state = [complex(1.0 / math.sqrt(state_size))] * state_size
        
        # Apply feature-dependent rotations
        for rep in range(self.reps):
            for i, feat in enumerate(features[:self._num_qubits]):
                angle = feat * math.pi * (rep + 1)
                for j in range(state_size):
                    if (j >> i) & 1:
                        state[j] *= complex(math.cos(angle), math.sin(angle))
        
        # Normalize
        norm = math.sqrt(sum(abs(s) ** 2 for s in state))
        if norm > 0:
            state = [s / norm for s in state]
        
        return state


class ThreatFingerprint:
    """
    Generates cryptographic fingerprints for threat detection.
    
    Combines post-level, account-level, and domain-level fingerprinting
    for comprehensive threat analysis.
    """
    
    def __init__(self, algorithm: str = "sha256"):
        """
        Initialize the fingerprint generator.
        
        Args:
            algorithm: Hash algorithm to use. Supported: sha256, sha384, sha512,
                       sha3_256, sha3_512. MD5 is NOT supported due to known
                       cryptographic weaknesses.
        
        Raises:
            ValueError: If an unsupported algorithm is specified.
        """
        if algorithm not in SUPPORTED_ALGORITHMS:
            raise ValueError(
                f"Unsupported algorithm '{algorithm}'. "
                f"Use one of: {', '.join(sorted(SUPPORTED_ALGORITHMS))}"
            )
        self.algorithm = algorithm
    
    def compute_post_fingerprint(self, features: Dict[str, Any]) -> str:
        """
        Compute a fingerprint for a single post.
        
        Args:
            features: Dictionary of post features
            
        Returns:
            Hexadecimal fingerprint string
        """
        normalized = self._normalize_features(features)
        data = json.dumps(normalized, sort_keys=True).encode()
        return hashlib.new(self.algorithm, data).hexdigest()
    
    def compute_account_fingerprint(
        self, 
        post_fingerprints: List[str],
        window_size: int = 10
    ) -> str:
        """
        Compute an account-level fingerprint from recent posts.
        
        Args:
            post_fingerprints: List of post fingerprints
            window_size: Number of recent posts to consider
            
        Returns:
            Hexadecimal account fingerprint
        """
        recent = post_fingerprints[-window_size:]
        combined = "".join(sorted(recent))
        return hashlib.new(self.algorithm, combined.encode()).hexdigest()
    
    def compute_domain_fingerprint(
        self,
        account_fingerprints: List[str],
        weights: Optional[List[float]] = None
    ) -> str:
        """
        Compute an environmental domain fingerprint from multiple accounts.
        
        Args:
            account_fingerprints: List of account fingerprints
            weights: Optional weights for each account
            
        Returns:
            Hexadecimal domain fingerprint
        """
        if weights is None:
            weights = [1.0] * len(account_fingerprints)
        elif len(weights) != len(account_fingerprints):
            raise ValueError(
                f"Length mismatch: {len(account_fingerprints)} fingerprints but "
                f"{len(weights)} weights provided. They must be equal."
            )
        
        # Combine with weights
        weighted = []
        for fp, w in zip(account_fingerprints, weights):
            weighted.append(f"{fp}:{w:.4f}")
        
        combined = "|".join(weighted)
        return hashlib.new(self.algorithm, combined.encode()).hexdigest()
    
    def _normalize_features(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize features for consistent hashing."""
        result = {}
        for key in sorted(features.keys()):
            value = features[key]
            if isinstance(value, float):
                result[key] = round(value, 6)
            elif isinstance(value, (list, tuple)):
                result[key] = [
                    round(v, 6) if isinstance(v, float) else v 
                    for v in value
                ]
            else:
                result[key] = value
        return result


def compute_fingerprint(data: Any, algorithm: str = "sha256") -> str:
    """
    Compute a cryptographic fingerprint for arbitrary data.
    
    Args:
        data: Data to fingerprint (will be JSON-serialized)
        algorithm: Hash algorithm to use. Supported: sha256, sha384, sha512,
                   sha3_256, sha3_512. MD5/SHA1 are NOT supported.
        
    Returns:
        Hexadecimal fingerprint string
    
    Raises:
        ValueError: If an unsupported algorithm is specified.
    """
    if algorithm not in SUPPORTED_ALGORITHMS:
        raise ValueError(
            f"Unsupported algorithm '{algorithm}'. "
            f"Use one of: {', '.join(sorted(SUPPORTED_ALGORITHMS))}"
        )
    
    if isinstance(data, (dict, list)):
        serialized = json.dumps(data, sort_keys=True, default=str)
    else:
        serialized = str(data)
    
    return hashlib.new(algorithm, serialized.encode()).hexdigest()


def encode_features(
    features: List[float],
    feature_dimension: int = 10,
    reps: int = 2
) -> List[complex]:
    """
    Encode classical features into a quantum state vector.
    
    Args:
        features: List of numerical features
        feature_dimension: Target feature dimension
        reps: Number of encoding repetitions
        
    Returns:
        Quantum state vector as list of complex amplitudes
    """
    feature_map = QuantumFeatureMap(feature_dimension, reps)
    return feature_map.encode(features)


def quantum_kernel_estimation(
    x1: List[float],
    x2: List[float],
    feature_dimension: int = 10,
    reps: int = 2
) -> float:
    """
    Estimate the quantum kernel between two feature vectors.
    
    The quantum kernel measures the similarity between two data points
    in the quantum feature space, which can capture non-linear relationships.
    
    Args:
        x1: First feature vector
        x2: Second feature vector
        feature_dimension: Dimension of the feature map
        reps: Number of feature map repetitions
        
    Returns:
        Kernel value between 0 and 1
    """
    feature_map = QuantumFeatureMap(feature_dimension, reps)
    
    state1 = feature_map.encode(x1)
    state2 = feature_map.encode(x2)
    
    # Compute fidelity (inner product magnitude squared)
    inner_product = sum(
        s1.conjugate() * s2 
        for s1, s2 in zip(state1, state2)
    )
    
    return abs(inner_product) ** 2


def _softmax(scores: List[float]) -> List[float]:
    """Compute a numerically stable softmax for a list of scores."""
    if not scores:
        return []
    max_score = max(scores)
    exp_scores = [math.exp(score - max_score) for score in scores]
    total = sum(exp_scores)
    if total == 0:
        return [1.0 / len(scores)] * len(scores)
    return [score / total for score in exp_scores]


def manifold_projection(
    features: List[float],
    anchors: List[List[float]],
    feature_dimension: int = 10,
    reps: int = 2
) -> List[float]:
    """
    Project a feature vector onto a quantum-informed manifold.
    
    Uses quantum kernel similarity against anchor vectors to produce
    a probability distribution over manifold regions.
    
    Args:
        features: Feature vector to project.
        anchors: Anchor vectors defining the manifold regions.
        feature_dimension: Dimension of the feature map.
        reps: Number of feature map repetitions.
        
    Returns:
        Probability distribution over anchors (sums to 1).
    """
    if not anchors:
        return []
    
    similarities = [
        quantum_kernel_estimation(features, anchor, feature_dimension, reps)
        for anchor in anchors
    ]
    total = sum(similarities)
    if total == 0:
        return [1.0 / len(anchors)] * len(anchors)
    return [value / total for value in similarities]


def predict_navigation_probabilities(
    sequence: List[List[float]],
    candidates: List[List[float]],
    decay: float = 0.85,
    feature_dimension: int = 10,
    reps: int = 2
) -> List[float]:
    """
    Predict navigation probabilities for candidate next steps.
    
    Scores each candidate by comparing it to the sequence history using
    a decayed quantum kernel similarity, then normalizes via softmax.
    
    Args:
        sequence: Observed sequence of feature vectors (oldest -> newest).
        candidates: Candidate feature vectors for the next step.
        decay: Exponential decay for older steps (0-1).
        feature_dimension: Dimension of the feature map.
        reps: Number of feature map repetitions.
        
    Returns:
        Probability distribution over candidates (sums to 1).
    """
    if not candidates:
        return []
    if not sequence:
        return [1.0 / len(candidates)] * len(candidates)
    
    weights = [decay ** idx for idx in range(len(sequence))]
    weights.reverse()
    
    scores = []
    for candidate in candidates:
        score = 0.0
        for weight, step in zip(weights, sequence):
            score += weight * quantum_kernel_estimation(
                candidate,
                step,
                feature_dimension,
                reps,
            )
        scores.append(score)
    
    return _softmax(scores)


def evaluate_navigation_sequence(
    sequence: List[List[float]],
    candidates: List[List[float]],
    anchors: List[List[float]],
    decay: float = 0.85,
    feature_dimension: int = 10,
    reps: int = 2
) -> Dict[str, Any]:
    """
    Evaluate navigation sequencing using manifold projection and prediction.
    
    Args:
        sequence: Observed sequence of feature vectors (oldest -> newest).
        candidates: Candidate feature vectors for the next step.
        anchors: Anchor vectors defining the manifold regions.
        decay: Exponential decay for older steps (0-1).
        feature_dimension: Dimension of the feature map.
        reps: Number of feature map repetitions.
        
    Returns:
        Dictionary with projection scores, candidate probabilities, and
        ranked candidate indices.
    """
    projection = manifold_projection(
        sequence[-1] if sequence else [0.0] * feature_dimension,
        anchors,
        feature_dimension,
        reps,
    )
    probabilities = predict_navigation_probabilities(
        sequence,
        candidates,
        decay,
        feature_dimension,
        reps,
    )
    
    ranked = sorted(
        range(len(probabilities)),
        key=lambda idx: probabilities[idx],
        reverse=True,
    )
    
    return {
        "manifold_projection": projection,
        "candidate_probabilities": probabilities,
        "ranked_candidates": ranked,
    }
