"""
QuantumEVEZ - Quantum Computing Framework

A comprehensive quantum computing framework emphasizing:
- Entanglement physics simulation
- Self-verification mechanisms
- Security features
- Accessible quantum algorithms
"""

__version__ = "0.1.0"

from .entanglement import BellState, BellStateType, EPRPair, EntanglementSimulator
from .error_correction import QuantumErrorCorrection, ShorCode, SteaneCode, FidelityChecker
from .security import QuantumSecurity, AnomalyDetector, ThreatLevel, SecurityEvent

__all__ = [
    "BellState",
    "BellStateType",
    "EPRPair",
    "EntanglementSimulator",
    "QuantumErrorCorrection",
    "ShorCode",
    "SteaneCode",
    "FidelityChecker",
    "QuantumSecurity",
    "AnomalyDetector",
    "ThreatLevel",
    "SecurityEvent",
]
