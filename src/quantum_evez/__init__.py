"""
QuantumEVEZ - Quantum Computing Framework

A comprehensive quantum computing framework emphasizing:
- Entanglement physics simulation
- Self-verification mechanisms
- Security features
- Accessible quantum algorithms
"""

__version__ = "0.1.0"

from .entanglement import BellState, EPRPair, EntanglementSimulator
from .error_correction import QuantumErrorCorrection, ShorCode, SteaneCode
from .security import QuantumSecurity, AnomalyDetector

__all__ = [
    "BellState",
    "EPRPair",
    "EntanglementSimulator",
    "QuantumErrorCorrection",
    "ShorCode",
    "SteaneCode",
    "QuantumSecurity",
    "AnomalyDetector",
]
