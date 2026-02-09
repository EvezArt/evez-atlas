#!/usr/bin/env python3
"""
Comprehensive End-to-End Quantum Threat Detection Demo

Demonstrates the complete threat detection pipeline:
1. Entity creation and entanglement
2. Threat scanning and measurement
3. Error correction
4. Visualization
5. Continuous monitoring
"""

import time
import sys

from quantum_entanglement_scanner import QuantumEntanglementScanner
from quantum_threat_integration import IntegratedThreatDetector
from quantum_threat_visualization import ThreatVisualizationAPI


def print_section(title):
    """Print formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def demo_full_pipeline():
    """Run complete end-to-end demonstration."""
    print_section("QUANTUM THREAT DETECTION - FULL PIPELINE DEMO")
    
    # ========================================================================
    # Phase 1: System Initialization
    # ========================================================================
    print_section("Phase 1: System Initialization")
    
    print("🔧 Initializing integrated threat detector...")
    detector = IntegratedThreatDetector()
    print("   ✓ Detector initialized")
    
    print("🔧 Initializing visualization API...")
    viz_api = ThreatVisualizationAPI(detector)
    print("   ✓ Visualization API ready")
    
    # ========================================================================
    # Phase 2: Entity Creation and Entanglement
    # ========================================================================
    print_section("Phase 2: Entity Creation and Entanglement")
    
    print("📝 Creating quantum entities...")
    entities = []
    for i in range(8):
        entity_id = f"quantum_detector_{i}"
        role = ["scanner", "analyzer", "monitor", "guardian"][i % 4]
        domain = ["quantum_realm", "threat_domain"][i % 2]
        
        detector.lifecycle_manager.create_entity(entity_id, role, domain)
        entities.append(entity_id)
        print(f"   ✓ Created {entity_id} ({role})")
    
    print(f"\n🔗 Establishing quantum entanglement...")
    for entity_id in entities:
        detector.lifecycle_manager.quantum_entangle(entity_id, "unified_quantum_domain")
        print(f"   ✓ Entangled {entity_id}")
    
    print(f"\n🌅 Awakening entities...")
    for entity_id in entities:
        detector.lifecycle_manager.awaken_entity(entity_id)
    print(f"   ✓ All {len(entities)} entities active")
    
    # ========================================================================
    # Phase 3: Initial Threat Scan
    # ========================================================================
    print_section("Phase 3: Initial Threat Scan")
    
    print("🔍 Performing full system scan...")
    scan_result = detector.full_system_scan()
    
    print("\n📊 Scan Results:")
    print(f"   Lifecycle Status:")
    print(f"   - Total entities: {scan_result['lifecycle']['total_entities']}")
    print(f"   - Active: {scan_result['lifecycle']['active']}")
    print(f"   - Quantum entangled: {scan_result['lifecycle']['quantum_entangled']}")
    
    print(f"\n   Quantum Scan:")
    print(f"   - Total scanned: {scan_result['quantum_scan']['total_entities']}")
    print(f"   - Threats detected: {scan_result['quantum_scan']['threats_detected']}")
    print(f"   - Corrections needed: {scan_result['quantum_scan']['corrections_needed']}")
    print(f"   - Overall coherence: {scan_result['quantum_scan']['overall_coherence']:.3f}")
    print(f"   - Safety level: {scan_result['quantum_scan']['safety_level']:.3f}")
    
    print(f"\n   Integrated Analysis:")
    print(f"   - Threat level: {scan_result['integrated_threat_level']:.3f}")
    print(f"   - Status: {scan_result['safety']['status'].upper()}")
    print(f"   - Safety level: {scan_result['safety']['safety_level']:.1%}")
    
    # ========================================================================
    # Phase 4: Visualization
    # ========================================================================
    print_section("Phase 4: Threat Visualization")
    
    print("🎯 Generating radar view...")
    radar = viz_api.get_radar_view()
    print(f"   ✓ Radar generated")
    print(f"   - Entities tracked: {len(radar['entities'])}")
    print(f"   - Active alerts: {len(radar['alerts'])}")
    print(f"   - Threat rings: {len(radar['threat_rings'])}")
    
    print("\n📡 ASCII Radar Display:")
    ascii_radar = viz_api.generate_ascii_radar(width=50, height=15)
    for line in ascii_radar.split('\n'):
        print(f"   {line}")
    
    print("\n🗺️  Generating 3D threat map...")
    map_3d = viz_api.get_3d_threat_map()
    print(f"   ✓ 3D map generated")
    print(f"   - Grid resolution: {map_3d['grid_size']}")
    print(f"   - Voxels: {len(map_3d['voxels'])}")
    print(f"   - Max threat: {map_3d['max_threat']:.3f}")
    print(f"   - Scan radius: {map_3d['scan_radius']}")
    
    # ========================================================================
    # Phase 5: Threat Simulation and Detection
    # ========================================================================
    print_section("Phase 5: Threat Simulation")
    
    print("⚠️  Simulating threat conditions...")
    # Degrade some entities to create threats
    for i, entity_id in enumerate(entities[:3]):
        state = detector.scanner.entangled_entities[entity_id]
        state.entanglement_strength = 0.3  # Low strength
        state.last_measurement = time.time() - 120  # Old measurement
        print(f"   ! Degraded {entity_id}")
    
    print("\n🔍 Re-scanning with threats present...")
    threat_scan = detector.full_system_scan()
    
    print("\n📊 Updated Scan Results:")
    print(f"   - Threats detected: {threat_scan['quantum_scan']['threats_detected']}")
    print(f"   - Corrections needed: {threat_scan['quantum_scan']['corrections_needed']}")
    print(f"   - New threat level: {threat_scan['integrated_threat_level']:.3f}")
    print(f"   - Safety level: {threat_scan['safety']['safety_level']:.1%}")
    
    # ========================================================================
    # Phase 6: Error Correction
    # ========================================================================
    print_section("Phase 6: Error Correction")
    
    if threat_scan['integrated_threat_level'] > 0.3:
        print("🔧 Applying comprehensive error correction...")
        corrections = detector.apply_comprehensive_correction()
        
        print(f"   ✓ Correction complete")
        print(f"   - Lifecycle corrections: {corrections['lifecycle_corrections']}")
        print(f"   - Quantum corrections: {corrections['quantum_corrections']}")
        
        print("\n🔍 Post-correction scan...")
        post_correction = detector.full_system_scan()
        print(f"   - New threat level: {post_correction['integrated_threat_level']:.3f}")
        print(f"   - Threats remaining: {post_correction['quantum_scan']['threats_detected']}")
        print(f"   - Safety restored to: {post_correction['safety']['safety_level']:.1%}")
    
    # ========================================================================
    # Phase 7: Continuous Monitoring
    # ========================================================================
    print_section("Phase 7: Continuous Monitoring")
    
    print("🔄 Running continuous monitoring (10 seconds)...")
    print("   Scanning every 2 seconds...\n")
    
    monitoring_results = detector.continuous_full_monitoring(
        duration=10,
        scan_interval=2
    )
    
    print(f"\n   ✓ Monitoring complete")
    print(f"   - Total scans: {len(monitoring_results)}")
    print(f"   - Average threat: {sum(r['integrated_threat_level'] for r in monitoring_results) / len(monitoring_results):.3f}")
    print(f"   - Max threat seen: {max(r['integrated_threat_level'] for r in monitoring_results):.3f}")
    
    # ========================================================================
    # Phase 8: Comprehensive Report
    # ========================================================================
    print_section("Phase 8: Comprehensive Report Generation")
    
    print("📊 Generating comprehensive report...")
    report = detector.generate_comprehensive_report()
    
    print(f"   ✓ Report generated")
    print(f"\n   Recommendations:")
    for i, rec in enumerate(report['recommendations'], 1):
        print(f"   {i}. {rec}")
    
    print(f"\n   Threat Map:")
    print(f"   - Hotspots identified: {len(report['threat_map']['hotspots'])}")
    print(f"   - Max threat level: {report['threat_map']['max_threat']:.3f}")
    
    # ========================================================================
    # Phase 9: Export and Summary
    # ========================================================================
    print_section("Phase 9: Export and Summary")
    
    print("💾 Exporting analysis...")
    analysis_file = detector.export_full_analysis()
    print(f"   ✓ Analysis saved to: {analysis_file}")
    
    print("\n💾 Exporting dashboard...")
    dashboard_file = viz_api.export_dashboard()
    print(f"   ✓ Dashboard saved to: {dashboard_file}")
    
    print("\n📈 Final System Status:")
    final_status = detector.full_system_scan()
    print(f"   - System health: {final_status['safety']['status'].upper()}")
    print(f"   - Threat level: {final_status['integrated_threat_level']:.3f}")
    print(f"   - Safety level: {final_status['safety']['safety_level']:.1%}")
    print(f"   - Active entities: {final_status['lifecycle']['active']}/{final_status['lifecycle']['total_entities']}")
    print(f"   - Quantum coherence: {final_status['quantum_scan']['overall_coherence']:.3f}")
    
    # ========================================================================
    # Completion
    # ========================================================================
    print_section("DEMO COMPLETE")
    
    print("\n✅ All phases completed successfully!")
    print("\n📁 Output files generated:")
    print(f"   - {analysis_file}")
    print(f"   - {dashboard_file}")
    print("\n🎯 System Features Demonstrated:")
    print("   ✓ Entity lifecycle management")
    print("   ✓ Quantum entanglement")
    print("   ✓ Full-stack threat scanning")
    print("   ✓ Error detection and correction")
    print("   ✓ 3D threat mapping")
    print("   ✓ Radar visualization")
    print("   ✓ Continuous monitoring")
    print("   ✓ Comprehensive reporting")
    print("\n🌟 Quantum threat detection system fully operational!")


if __name__ == "__main__":
    try:
        demo_full_pipeline()
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
