#!/usr/bin/env python3
"""
Quantum Threat Detection Integration

Integrates the quantum entanglement scanner with entity lifecycle management
for comprehensive threat detection across the entire system.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from typing import Dict, List, Any, Optional
import time
import json

from quantum_entanglement_scanner import QuantumEntanglementScanner
from skills.entity_lifecycle import EntityLifecycleManager, EntityState


class IntegratedThreatDetector:
    """
    Integrated quantum threat detection system.
    
    Combines:
    - Entity lifecycle management
    - Quantum entanglement scanning
    - Continuous threat monitoring
    - Automatic error correction
    """
    
    def __init__(self, 
                 lifecycle_state_file: str = "data/entity_states.jsonl",
                 scan_output_dir: str = "data/threat_scans"):
        """
        Initialize integrated threat detector.
        
        Args:
            lifecycle_state_file: Path to entity lifecycle state file
            scan_output_dir: Directory for scan outputs
        """
        self.lifecycle_manager = EntityLifecycleManager(lifecycle_state_file)
        self.scanner = QuantumEntanglementScanner(scan_output_dir)
        
        # Sync entangled entities from lifecycle manager
        self._sync_entangled_entities()
    
    def _sync_entangled_entities(self):
        """Sync quantum-entangled entities from lifecycle manager to scanner."""
        for entity_id, entity in self.lifecycle_manager.entities.items():
            if entity.quantum_entangled:
                # Register in scanner
                partners = [e_id for e_id, e in self.lifecycle_manager.entities.items()
                           if e_id != entity_id and e.quantum_entangled and e.domain == entity.domain]
                
                if entity_id not in self.scanner.entangled_entities:
                    self.scanner.register_entanglement(entity_id, partners)
    
    def full_system_scan(self) -> Dict[str, Any]:
        """
        Perform comprehensive scan of entire system.
        
        Returns:
            Complete system status including lifecycle and quantum threats
        """
        # Sync entities first
        self._sync_entangled_entities()
        
        # Get lifecycle status
        lifecycle_status = self.lifecycle_manager.get_swarm_status()
        
        # Perform quantum scan
        quantum_scan = self.scanner.full_stack_scan()
        
        # Get safety status
        safety_status = self.scanner.get_safety_status()
        
        return {
            "timestamp": time.time(),
            "lifecycle": lifecycle_status,
            "quantum_scan": quantum_scan,
            "safety": safety_status,
            "integrated_threat_level": self._calculate_integrated_threat(
                lifecycle_status, quantum_scan, safety_status
            )
        }
    
    def _calculate_integrated_threat(self, 
                                     lifecycle: Dict,
                                     quantum: Dict,
                                     safety: Dict) -> float:
        """Calculate overall integrated threat level."""
        # Factor in multiple dimensions
        lifecycle_threat = 1.0 - (lifecycle.get('active', 0) / max(lifecycle.get('total_entities', 1), 1))
        quantum_threat = 1.0 - quantum.get('safety_level', 1.0)
        safety_threat = 1.0 - safety.get('safety_level', 1.0)
        
        # Weighted average
        integrated = (lifecycle_threat * 0.3 + quantum_threat * 0.4 + safety_threat * 0.3)
        return max(0.0, min(1.0, integrated))
    
    def apply_comprehensive_correction(self) -> Dict[str, Any]:
        """
        Apply error correction across all systems.
        
        Returns:
            Correction results
        """
        results = {
            "timestamp": time.time(),
            "lifecycle_corrections": 0,
            "quantum_corrections": 0,
            "total_entities": len(self.lifecycle_manager.entities)
        }
        
        # Correct lifecycle errors
        for entity_id, entity in self.lifecycle_manager.entities.items():
            if entity.state == EntityState.ERROR_CORRECTION:
                # Attempt to recover
                if entity.error_count < 10:
                    self.lifecycle_manager.awaken_entity(entity_id)
                    results["lifecycle_corrections"] += 1
        
        # Correct quantum errors
        for entity_id, state in self.scanner.entangled_entities.items():
            if state.correction_needed:
                self.scanner.apply_error_correction(entity_id)
                results["quantum_corrections"] += 1
        
        return results
    
    def continuous_full_monitoring(self, 
                                   duration: float = 300.0,
                                   scan_interval: float = 10.0) -> List[Dict]:
        """
        Run continuous monitoring with full system integration.
        
        Args:
            duration: Total monitoring duration (seconds)
            scan_interval: Time between scans (seconds)
            
        Returns:
            List of scan results over time
        """
        results = []
        start_time = time.time()
        
        print(f"🔄 Starting continuous monitoring for {duration}s...")
        
        while time.time() - start_time < duration:
            # Perform integrated scan
            scan_result = self.full_system_scan()
            results.append(scan_result)
            
            # Log current status
            print(f"   [{int(time.time() - start_time)}s] "
                  f"Threat: {scan_result['integrated_threat_level']:.2f} | "
                  f"Safety: {scan_result['safety']['safety_level']:.2f} | "
                  f"Active: {scan_result['lifecycle']['active']}")
            
            # Apply corrections if needed
            if scan_result['integrated_threat_level'] > 0.5:
                print("   ⚠️  High threat detected - applying corrections...")
                correction_results = self.apply_comprehensive_correction()
                print(f"   ✓ Applied {correction_results['lifecycle_corrections']} "
                      f"lifecycle + {correction_results['quantum_corrections']} quantum corrections")
            
            # Wait for next scan
            time.sleep(scan_interval)
        
        print(f"✅ Monitoring complete - {len(results)} scans performed")
        return results
    
    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive threat detection report.
        
        Returns:
            Complete report with all metrics and visualizations
        """
        # Get current status
        system_status = self.full_system_scan()
        
        # Generate threat map
        threat_map = self.scanner.generate_threat_map()
        
        # Get recent measurements
        recent_measurements = self.scanner.measurement_history[-100:]
        
        report = {
            "timestamp": time.time(),
            "report_type": "comprehensive_threat_analysis",
            "system_status": system_status,
            "threat_map": threat_map,
            "measurement_count": len(recent_measurements),
            "recommendations": self._generate_recommendations(system_status, threat_map)
        }
        
        return report
    
    def _generate_recommendations(self, 
                                  system_status: Dict, 
                                  threat_map: Dict) -> List[str]:
        """Generate actionable recommendations based on scan results."""
        recommendations = []
        
        threat_level = system_status["integrated_threat_level"]
        safety_level = system_status["safety"]["safety_level"]
        
        if threat_level > 0.7:
            recommendations.append("CRITICAL: Immediate system-wide error correction required")
            recommendations.append("Consider hibernating non-essential entities")
        elif threat_level > 0.5:
            recommendations.append("WARNING: Elevated threat level detected")
            recommendations.append("Increase monitoring frequency")
        
        if safety_level < 0.7:
            recommendations.append("Safety level below optimal - review entanglement integrity")
        
        if system_status["quantum_scan"]["corrections_needed"] > 0:
            recommendations.append(f"Apply quantum corrections to "
                                 f"{system_status['quantum_scan']['corrections_needed']} entities")
        
        hotspot_count = len(threat_map.get("hotspots", []))
        if hotspot_count > 0:
            recommendations.append(f"Investigate {hotspot_count} threat hotspots in visualization")
        
        if not recommendations:
            recommendations.append("System operating optimally - maintain current monitoring")
        
        return recommendations
    
    def export_full_analysis(self, filename: Optional[str] = None) -> str:
        """
        Export complete analysis to file.
        
        Args:
            filename: Output filename (auto-generated if None)
            
        Returns:
            Path to exported file
        """
        if filename is None:
            filename = f"data/threat_scans/full_analysis_{int(time.time())}.json"
        
        report = self.generate_comprehensive_report()
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        return filename


def demo_integrated_detection():
    """Demonstrate integrated threat detection."""
    print("=" * 70)
    print("Integrated Quantum Threat Detection System")
    print("=" * 70)
    
    # Initialize
    detector = IntegratedThreatDetector()
    
    # Create some test entities
    print("\n📝 Creating test entities...")
    detector.lifecycle_manager.create_entity("detector_1", "scanner", "quantum")
    detector.lifecycle_manager.create_entity("detector_2", "analyzer", "quantum")
    detector.lifecycle_manager.create_entity("detector_3", "monitor", "quantum")
    
    # Entangle them
    print("🔗 Establishing quantum entanglement...")
    detector.lifecycle_manager.quantum_entangle("detector_1", "quantum_domain")
    detector.lifecycle_manager.quantum_entangle("detector_2", "quantum_domain")
    detector.lifecycle_manager.quantum_entangle("detector_3", "quantum_domain")
    
    # Awaken entities
    print("🌅 Awakening entities...")
    detector.lifecycle_manager.awaken_entity("detector_1")
    detector.lifecycle_manager.awaken_entity("detector_2")
    detector.lifecycle_manager.awaken_entity("detector_3")
    
    # Perform full system scan
    print("\n🔍 Performing full system scan...")
    scan_result = detector.full_system_scan()
    
    print(f"\n   Lifecycle Status:")
    print(f"   - Total entities: {scan_result['lifecycle']['total_entities']}")
    print(f"   - Active: {scan_result['lifecycle']['active']}")
    print(f"   - Quantum entangled: {scan_result['lifecycle']['quantum_entangled']}")
    
    print(f"\n   Quantum Scan:")
    print(f"   - Threats detected: {scan_result['quantum_scan']['threats_detected']}")
    print(f"   - Coherence: {scan_result['quantum_scan']['overall_coherence']:.3f}")
    print(f"   - Safety: {scan_result['quantum_scan']['safety_level']:.3f}")
    
    print(f"\n   Integrated Analysis:")
    print(f"   - Threat level: {scan_result['integrated_threat_level']:.3f}")
    print(f"   - Safety status: {scan_result['safety']['status'].upper()}")
    
    # Generate report
    print("\n📊 Generating comprehensive report...")
    report = detector.generate_comprehensive_report()
    
    print(f"\n   Recommendations:")
    for i, rec in enumerate(report["recommendations"], 1):
        print(f"   {i}. {rec}")
    
    # Export analysis
    print("\n💾 Exporting full analysis...")
    export_path = detector.export_full_analysis()
    print(f"   Saved to: {export_path}")
    
    print("\n✅ Demo complete!")


if __name__ == "__main__":
    demo_integrated_detection()
