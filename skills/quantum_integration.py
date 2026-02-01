"""
Quantum Integration Module

Provides integration hooks for quantum computing backends.
Supports both classical simulation and IBM Quantum hardware.
"""

import os
from typing import Dict, Any, Optional

from skills.event_logger import log_agent_event


class QuantumIntegration:
    """
    Manages quantum computing backend integration.
    
    Detects quantum mode from environment and provides
    appropriate configuration for quantum operations.
    """
    
    def __init__(self):
        """Initialize quantum integration."""
        self.mode = self._detect_mode()
        self.config = self._load_config()
    
    def _detect_mode(self) -> str:
        """
        Detect quantum mode from environment.
        
        Returns:
            'qsvc-ibm' for IBM Quantum, 'classical' for simulation
        """
        jubilee_mode = os.getenv("JUBILEE_MODE", "")
        if jubilee_mode == "qsvc-ibm":
            return "qsvc-ibm"
        return "classical"
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Load quantum configuration.
        
        Returns:
            Configuration dictionary
        """
        config = {
            "mode": self.mode,
            "backend": "classical_simulator",
            "max_qubits": 10
        }
        
        if self.mode == "qsvc-ibm":
            config.update({
                "backend": "ibm_quantum",
                "max_qubits": 127,  # IBM Quantum capabilities
                "touch_id": os.getenv("JUBILEE_TOUCH_ID", ""),
                "hmac_secret": os.getenv("JUBILEE_HMAC_SECRET", "")
            })
        
        return config
    
    def is_quantum_ready(self) -> bool:
        """
        Check if quantum backend is ready.
        
        Returns:
            True if quantum operations are available
        """
        if self.mode == "qsvc-ibm":
            # Check for required credentials
            has_touch_id = bool(self.config.get("touch_id"))
            has_secret = bool(self.config.get("hmac_secret"))
            return has_touch_id and has_secret
        
        # Classical mode is always ready
        return True
    
    def get_backend_info(self) -> Dict[str, Any]:
        """
        Get information about current quantum backend.
        
        Returns:
            Backend information dictionary
        """
        info = {
            "mode": self.mode,
            "backend": self.config["backend"],
            "max_qubits": self.config["max_qubits"],
            "ready": self.is_quantum_ready()
        }
        
        if self.mode == "qsvc-ibm":
            info["ibm_configured"] = bool(self.config.get("touch_id"))
        
        return info
    
    def log_quantum_operation(
        self,
        operation: str,
        qubits: int,
        result: Any,
        agent_id: Optional[str] = None
    ) -> dict:
        """
        Log a quantum operation to sacred memory.
        
        Args:
            operation: Name of quantum operation
            qubits: Number of qubits used
            result: Operation result
            agent_id: Optional agent identifier
            
        Returns:
            The logged event
        """
        return log_agent_event(
            "quantum_operation",
            {
                "operation": operation,
                "qubits": qubits,
                "backend": self.config["backend"],
                "result": result
            },
            agent_id=agent_id,
            metadata={"quantum_mode": self.mode}
        )


# Singleton instance
_quantum_integration = QuantumIntegration()


def get_quantum_integration() -> QuantumIntegration:
    """Get the global quantum integration instance."""
    return _quantum_integration


def is_quantum_mode() -> bool:
    """
    Check if running in quantum mode.
    
    Returns:
        True if quantum backend is enabled
    """
    return _quantum_integration.mode == "qsvc-ibm"


def get_quantum_config() -> Dict[str, Any]:
    """
    Get quantum configuration.
    
    Returns:
        Quantum backend configuration
    """
    return _quantum_integration.config.copy()
