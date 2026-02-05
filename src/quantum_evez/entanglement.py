"""
Quantum Entanglement Physics Module

Simulates Bell states, EPR pairs, and entanglement phenomena with support
for noisy channels and temporal effects.
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple

import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator


class BellStateType(Enum):
    """Standard Bell state basis"""
    PHI_PLUS = "Φ+"    # (|00⟩ + |11⟩)/√2
    PHI_MINUS = "Φ-"   # (|00⟩ - |11⟩)/√2
    PSI_PLUS = "Ψ+"    # (|01⟩ + |10⟩)/√2
    PSI_MINUS = "Ψ-"   # (|01⟩ - |10⟩)/√2


@dataclass
class BellState:
    """Represents a Bell state with metadata"""
    state_type: BellStateType
    fidelity: float = 1.0
    creation_time: float = 0.0
    
    def __post_init__(self):
        if not 0 <= self.fidelity <= 1:
            raise ValueError("Fidelity must be between 0 and 1")


@dataclass
class EPRPair:
    """Einstein-Podolsky-Rosen entangled pair"""
    qubit_a: int
    qubit_b: int
    bell_state: BellState
    distance: float = 0.0  # Spatial separation in arbitrary units
    
    def is_maximally_entangled(self) -> bool:
        """Check if the pair is maximally entangled"""
        return self.bell_state.fidelity > 0.95


class EntanglementSimulator:
    """
    Simulates quantum entanglement with noise and decoherence effects
    """
    
    def __init__(self, noise_model=None, shots: int = 1000):
        """
        Initialize the entanglement simulator
        
        Args:
            noise_model: Optional Qiskit noise model
            shots: Number of measurement shots for simulation
        """
        self.noise_model = noise_model
        self.shots = shots
        self.backend = AerSimulator()
        
    def create_bell_state(
        self, 
        state_type: BellStateType = BellStateType.PHI_PLUS
    ) -> Tuple[QuantumCircuit, BellState]:
        """
        Create a Bell state quantum circuit
        
        Args:
            state_type: Type of Bell state to create
            
        Returns:
            Tuple of (circuit, bell_state_metadata)
        """
        qr = QuantumRegister(2, 'q')
        cr = ClassicalRegister(2, 'c')
        qc = QuantumCircuit(qr, cr)
        
        # Create base entanglement (Φ+)
        qc.h(qr[0])
        qc.cx(qr[0], qr[1])
        
        # Apply transformations for different Bell states
        if state_type == BellStateType.PHI_MINUS:
            qc.z(qr[0])
        elif state_type == BellStateType.PSI_PLUS:
            qc.x(qr[1])
        elif state_type == BellStateType.PSI_MINUS:
            qc.z(qr[0])
            qc.x(qr[1])
            
        bell_state = BellState(state_type=state_type)
        return qc, bell_state
    
    def create_epr_pair(
        self, 
        qubit_indices: Tuple[int, int] = (0, 1),
        state_type: BellStateType = BellStateType.PHI_PLUS
    ) -> EPRPair:
        """
        Create an EPR pair
        
        Args:
            qubit_indices: Tuple of (qubit_a_index, qubit_b_index)
            state_type: Type of Bell state for the EPR pair
            
        Returns:
            EPRPair object
        """
        qc, bell_state = self.create_bell_state(state_type)
        
        return EPRPair(
            qubit_a=qubit_indices[0],
            qubit_b=qubit_indices[1],
            bell_state=bell_state,
            distance=abs(qubit_indices[1] - qubit_indices[0])
        )
    
    def measure_entanglement_fidelity(self, circuit: QuantumCircuit) -> float:
        """
        Measure the fidelity of an entangled state
        
        Args:
            circuit: Quantum circuit to measure
            
        Returns:
            Fidelity value between 0 and 1
        """
        # Add measurement operations
        qc = circuit.copy()
        qc.measure_all()
        
        # Simulate
        job = self.backend.run(qc, shots=self.shots, noise_model=self.noise_model)
        result = job.result()
        counts = result.get_counts()
        
        # Calculate fidelity based on correlation
        # For a perfect Bell state (Φ+), we expect only |00⟩ and |11⟩
        correlated = counts.get('00', 0) + counts.get('11', 0)
        uncorrelated = counts.get('01', 0) + counts.get('10', 0)
        
        fidelity = correlated / (correlated + uncorrelated) if (correlated + uncorrelated) > 0 else 0.0
        return fidelity
    
    def simulate_noisy_channel(
        self,
        circuit: QuantumCircuit,
        depolarizing_prob: float = 0.01,
        amplitude_damping_prob: float = 0.01
    ) -> QuantumCircuit:
        """
        Add noise to a quantum circuit
        
        Args:
            circuit: Input circuit
            depolarizing_prob: Probability of depolarizing error
            amplitude_damping_prob: Probability of amplitude damping
            
        Returns:
            Circuit with noise applied
        """
        # Note: In a full implementation, we would use Qiskit's noise models
        # This is a simplified version
        noisy_circuit = circuit.copy()
        
        # Add depolarizing channels (simplified representation)
        for qubit in range(circuit.num_qubits):
            if np.random.random() < depolarizing_prob:
                noisy_circuit.id(qubit)  # Placeholder for noise
                
        return noisy_circuit
    
    def create_ghz_state(self, num_qubits: int = 3) -> QuantumCircuit:
        """
        Create a GHZ (Greenberger-Horne-Zeilinger) state for multi-party entanglement
        
        Args:
            num_qubits: Number of qubits to entangle
            
        Returns:
            Quantum circuit creating GHZ state
        """
        qr = QuantumRegister(num_qubits, 'q')
        qc = QuantumCircuit(qr)
        
        # Create GHZ state: (|00...0⟩ + |11...1⟩)/√2
        qc.h(qr[0])
        for i in range(1, num_qubits):
            qc.cx(qr[0], qr[i])
            
        return qc
