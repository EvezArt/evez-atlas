"""
Quantum Threat Detection System - Core Module

This module provides quantum computing utilities for threat detection
using quantum-inspired algorithms and feature maps.
"""

import hashlib
import json
import math
from typing import Any, Dict, List, Optional, Tuple

# Supported hash algorithms for fingerprinting
SUPPORTED_ALGORITHMS = frozenset(["sha256", "sha384", "sha512", "sha3_256", "sha3_512"])

__all__ = [
    "QuantumFeatureMap",
    "ThreatFingerprint",
    "compute_fingerprint",
    "encode_features",
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
        algorithm: Hash algorithm to use
        
    Returns:
        Hexadecimal fingerprint string
    """
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
