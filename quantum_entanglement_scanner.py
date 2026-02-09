#!/usr/bin/env python3
"""
Quantum Entanglement Threat Scanner

Comprehensive threat detection system for quantum entanglement operations.
Provides full-stack scanning, measurement, error correction, and visualization.
"""

import json
import time
import math
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import os


@dataclass
class ThreatMeasurement:
    """Represents a single threat measurement."""
    timestamp: float
    entity_id: str
    threat_level: float  # 0.0 to 1.0
    entanglement_quality: float  # 0.0 to 1.0
    error_count: int
    state_coherence: float  # 0.0 to 1.0
    domain: str
    location: Tuple[float, float, float]  # 3D coordinates for visualization


@dataclass
class EntanglementState:
    """Represents the state of an entangled entity."""
    entity_id: str
    partner_ids: List[str]
    entanglement_strength: float
    last_measurement: float
    threat_detected: bool
    correction_needed: bool
    state_vector: List[float]


class QuantumEntanglementScanner:
    """
    Comprehensive quantum threat detection scanner for entanglement operations.
    
    Provides:
    - Full entanglement stack scanning
    - Threat measurement and detection
    - Error correction and validation
    - Visual mapping and radar capabilities
    - Continuous monitoring
    """
    
    def __init__(self, output_dir: str = "data/threat_scans"):
        """
        Initialize the entanglement scanner.
        
        Args:
            output_dir: Directory for saving scan results and maps
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        self.entangled_entities: Dict[str, EntanglementState] = {}
        self.measurement_history: List[ThreatMeasurement] = []
        self.threat_threshold = 0.7  # Threshold for threat detection
        self.correction_threshold = 0.5  # Threshold for error correction
        
        # Visualization grid (3D radar space)
        self.grid_size = 100
        self.scan_radius = 50.0
        
    def register_entanglement(
        self, 
        entity_id: str, 
        partner_ids: List[str],
        initial_state: Optional[List[float]] = None
    ) -> EntanglementState:
        """
        Register an entangled entity for monitoring.
        
        Args:
            entity_id: ID of the entity
            partner_ids: IDs of entangled partners
            initial_state: Initial quantum state vector
            
        Returns:
            EntanglementState object
        """
        if initial_state is None:
            # Initialize to balanced superposition
            dim = 8  # 8-dimensional state space
            initial_state = [1.0 / math.sqrt(dim)] * dim
        
        state = EntanglementState(
            entity_id=entity_id,
            partner_ids=partner_ids,
            entanglement_strength=1.0,
            last_measurement=time.time(),
            threat_detected=False,
            correction_needed=False,
            state_vector=initial_state
        )
        
        self.entangled_entities[entity_id] = state
        return state
    
    def full_stack_scan(self) -> Dict[str, Any]:
        """
        Perform a comprehensive scan of the entire entanglement stack.
        
        Measures all entangled entities, detects threats, and identifies
        correction needs.
        
        Returns:
            Comprehensive scan results dictionary
        """
        scan_time = time.time()
        results = {
            "timestamp": scan_time,
            "total_entities": len(self.entangled_entities),
            "threats_detected": 0,
            "corrections_needed": 0,
            "measurements": [],
            "overall_coherence": 0.0,
            "safety_level": 1.0
        }
        
        coherence_sum = 0.0
        threat_sum = 0.0
        
        for entity_id, state in self.entangled_entities.items():
            # Perform measurement
            measurement = self._measure_entity(entity_id, state)
            results["measurements"].append(asdict(measurement))
            
            # Update state based on measurement
            if measurement.threat_level > self.threat_threshold:
                state.threat_detected = True
                results["threats_detected"] += 1
                threat_sum += measurement.threat_level
            else:
                state.threat_detected = False
            
            if measurement.state_coherence < self.correction_threshold:
                state.correction_needed = True
                results["corrections_needed"] += 1
            else:
                state.correction_needed = False
            
            coherence_sum += measurement.state_coherence
            state.last_measurement = scan_time
        
        # Calculate overall metrics
        if len(self.entangled_entities) > 0:
            results["overall_coherence"] = coherence_sum / len(self.entangled_entities)
            results["safety_level"] = 1.0 - (threat_sum / len(self.entangled_entities))
        
        # Save to history
        self._save_scan_results(results)
        
        return results
    
    def _measure_entity(self, entity_id: str, state: EntanglementState) -> ThreatMeasurement:
        """
        Measure a single entangled entity for threats.
        
        Args:
            entity_id: Entity identifier
            state: Current entanglement state
            
        Returns:
            ThreatMeasurement object
        """
        # Calculate threat metrics
        threat_level = self._calculate_threat_level(state)
        entanglement_quality = self._calculate_entanglement_quality(state)
        state_coherence = self._calculate_coherence(state.state_vector)
        
        # Generate 3D position for visualization (based on state vector)
        position = self._state_to_position(state.state_vector)
        
        # Count errors in state
        error_count = sum(1 for v in state.state_vector if abs(v) < 0.01)
        
        measurement = ThreatMeasurement(
            timestamp=time.time(),
            entity_id=entity_id,
            threat_level=threat_level,
            entanglement_quality=entanglement_quality,
            error_count=error_count,
            state_coherence=state_coherence,
            domain=state.partner_ids[0] if state.partner_ids else "unknown",
            location=position
        )
        
        self.measurement_history.append(measurement)
        return measurement
    
    def _calculate_threat_level(self, state: EntanglementState) -> float:
        """Calculate threat level for an entangled entity."""
        # Threat increases with:
        # 1. Low entanglement strength
        # 2. Time since last measurement
        # 3. State vector anomalies
        
        time_factor = min(1.0, (time.time() - state.last_measurement) / 60.0)
        strength_factor = 1.0 - state.entanglement_strength
        
        # Check for state anomalies
        state_variance = sum((v - 0.125) ** 2 for v in state.state_vector) / len(state.state_vector)
        anomaly_factor = min(1.0, state_variance * 10)
        
        threat_level = (time_factor * 0.3 + strength_factor * 0.4 + anomaly_factor * 0.3)
        return max(0.0, min(1.0, threat_level))
    
    def _calculate_entanglement_quality(self, state: EntanglementState) -> float:
        """Calculate quality of entanglement."""
        # Quality based on:
        # 1. Number of partners
        # 2. Entanglement strength
        # 3. State coherence
        
        partner_factor = min(1.0, len(state.partner_ids) / 5.0)
        strength_factor = state.entanglement_strength
        
        return (partner_factor * 0.3 + strength_factor * 0.7)
    
    def _calculate_coherence(self, state_vector: List[float]) -> float:
        """Calculate quantum coherence of state vector."""
        # Coherence = how close to uniform superposition
        ideal = 1.0 / math.sqrt(len(state_vector))
        variance = sum((v - ideal) ** 2 for v in state_vector) / len(state_vector)
        coherence = 1.0 - min(1.0, variance * len(state_vector))
        return coherence
    
    def _state_to_position(self, state_vector: List[float]) -> Tuple[float, float, float]:
        """Convert quantum state to 3D position for visualization."""
        # Use first 3 components, normalized to scan radius
        x = state_vector[0] * self.scan_radius if len(state_vector) > 0 else 0.0
        y = state_vector[1] * self.scan_radius if len(state_vector) > 1 else 0.0
        z = state_vector[2] * self.scan_radius if len(state_vector) > 2 else 0.0
        return (x, y, z)
    
    def apply_error_correction(self, entity_id: str) -> bool:
        """
        Apply quantum error correction to an entity.
        
        Args:
            entity_id: Entity to correct
            
        Returns:
            True if correction successful
        """
        if entity_id not in self.entangled_entities:
            return False
        
        state = self.entangled_entities[entity_id]
        
        # Restore coherence by normalizing state vector
        norm = math.sqrt(sum(v ** 2 for v in state.state_vector))
        if norm > 0:
            state.state_vector = [v / norm for v in state.state_vector]
        
        # Boost entanglement strength
        state.entanglement_strength = min(1.0, state.entanglement_strength + 0.1)
        state.correction_needed = False
        
        return True
    
    def generate_threat_map(self) -> Dict[str, Any]:
        """
        Generate a visual threat map from recent measurements.
        
        Returns:
            Dictionary containing map data for visualization
        """
        if not self.measurement_history:
            return {"message": "No measurements available"}
        
        # Get recent measurements (last 100)
        recent = self.measurement_history[-100:]
        
        # Create 3D grid
        grid = {}
        max_threat = 0.0
        
        for measurement in recent:
            x, y, z = measurement.location
            grid_pos = (
                int(x / self.scan_radius * 10),
                int(y / self.scan_radius * 10),
                int(z / self.scan_radius * 10)
            )
            
            if grid_pos not in grid:
                grid[grid_pos] = []
            grid[grid_pos].append(measurement.threat_level)
            max_threat = max(max_threat, measurement.threat_level)
        
        # Average threats per grid cell
        threat_map = {}
        for pos, threats in grid.items():
            threat_map[f"{pos[0]},{pos[1]},{pos[2]}"] = sum(threats) / len(threats)
        
        return {
            "timestamp": time.time(),
            "grid_resolution": 10,
            "scan_radius": self.scan_radius,
            "max_threat": max_threat,
            "threat_map": threat_map,
            "total_measurements": len(recent),
            "hotspots": self._identify_hotspots(threat_map)
        }
    
    def _identify_hotspots(self, threat_map: Dict[str, float]) -> List[Dict]:
        """Identify threat hotspots in the map."""
        hotspots = []
        for pos_str, threat_level in threat_map.items():
            if threat_level > self.threat_threshold:
                coords = [float(x) for x in pos_str.split(',')]
                hotspots.append({
                    "position": coords,
                    "threat_level": threat_level,
                    "priority": "high" if threat_level > 0.85 else "medium"
                })
        
        # Sort by threat level
        hotspots.sort(key=lambda x: x["threat_level"], reverse=True)
        return hotspots[:10]  # Return top 10 hotspots
    
    def continuous_monitoring_cycle(self, duration: float = 60.0, interval: float = 5.0) -> List[Dict]:
        """
        Run continuous monitoring for a specified duration.
        
        Args:
            duration: Total monitoring duration in seconds
            interval: Scan interval in seconds
            
        Returns:
            List of scan results
        """
        results = []
        start_time = time.time()
        
        while time.time() - start_time < duration:
            # Perform scan
            scan_result = self.full_stack_scan()
            results.append(scan_result)
            
            # Apply corrections if needed
            for entity_id, state in self.entangled_entities.items():
                if state.correction_needed:
                    self.apply_error_correction(entity_id)
            
            # Wait for next interval
            time.sleep(interval)
        
        return results
    
    def _save_scan_results(self, results: Dict[str, Any]):
        """Save scan results to file."""
        filename = os.path.join(
            self.output_dir,
            f"scan_{int(time.time())}.json"
        )
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
    
    def export_measurement_map(self, filename: Optional[str] = None) -> str:
        """
        Export complete measurement map for visualization.
        
        Args:
            filename: Output filename (auto-generated if None)
            
        Returns:
            Path to saved file
        """
        if filename is None:
            filename = os.path.join(
                self.output_dir,
                f"threat_map_{int(time.time())}.json"
            )
        
        threat_map = self.generate_threat_map()
        
        # Add full history
        threat_map["measurement_history"] = [
            asdict(m) for m in self.measurement_history[-1000:]  # Last 1000
        ]
        
        with open(filename, 'w') as f:
            json.dump(threat_map, f, indent=2)
        
        return filename
    
    def get_safety_status(self) -> Dict[str, Any]:
        """
        Get current safety status of the entanglement system.
        
        Returns:
            Dictionary with safety metrics
        """
        if not self.entangled_entities:
            return {
                "status": "no_entities",
                "safety_level": 1.0,
                "message": "No entangled entities registered"
            }
        
        total = len(self.entangled_entities)
        safe = sum(1 for s in self.entangled_entities.values() if not s.threat_detected)
        corrected = sum(1 for s in self.entangled_entities.values() if not s.correction_needed)
        
        safety_level = safe / total
        correction_rate = corrected / total
        
        if safety_level >= 0.9 and correction_rate >= 0.8:
            status = "optimal"
        elif safety_level >= 0.7:
            status = "acceptable"
        elif safety_level >= 0.5:
            status = "warning"
        else:
            status = "critical"
        
        return {
            "status": status,
            "safety_level": safety_level,
            "correction_rate": correction_rate,
            "total_entities": total,
            "safe_entities": safe,
            "threats_active": total - safe,
            "corrections_needed": total - corrected,
            "timestamp": time.time()
        }


def create_test_scenario():
    """Create a test scenario with multiple entangled entities."""
    scanner = QuantumEntanglementScanner()
    
    # Register test entities
    scanner.register_entanglement("entity_alpha", ["entity_beta", "entity_gamma"])
    scanner.register_entanglement("entity_beta", ["entity_alpha"])
    scanner.register_entanglement("entity_gamma", ["entity_alpha", "entity_delta"])
    scanner.register_entanglement("entity_delta", ["entity_gamma"])
    
    return scanner


if __name__ == "__main__":
    print("=" * 70)
    print("Quantum Entanglement Threat Scanner - Demo")
    print("=" * 70)
    
    # Create scanner
    scanner = create_test_scenario()
    
    print(f"\n✓ Registered {len(scanner.entangled_entities)} entangled entities")
    
    # Perform full scan
    print("\n🔍 Performing full stack scan...")
    results = scanner.full_stack_scan()
    
    print(f"   Total entities: {results['total_entities']}")
    print(f"   Threats detected: {results['threats_detected']}")
    print(f"   Corrections needed: {results['corrections_needed']}")
    print(f"   Overall coherence: {results['overall_coherence']:.3f}")
    print(f"   Safety level: {results['safety_level']:.3f}")
    
    # Generate threat map
    print("\n🗺️  Generating threat map...")
    threat_map = scanner.generate_threat_map()
    print(f"   Map generated with {threat_map['total_measurements']} measurements")
    print(f"   Hotspots identified: {len(threat_map['hotspots'])}")
    
    # Get safety status
    print("\n🛡️  Safety status:")
    status = scanner.get_safety_status()
    print(f"   Status: {status['status'].upper()}")
    print(f"   Safety level: {status['safety_level']:.1%}")
    print(f"   Safe entities: {status['safe_entities']}/{status['total_entities']}")
    
    # Export map
    print("\n💾 Exporting measurement map...")
    map_file = scanner.export_measurement_map()
    print(f"   Saved to: {map_file}")
    
    print("\n✅ Demo complete!")
