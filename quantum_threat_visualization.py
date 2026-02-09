#!/usr/bin/env python3
"""
Quantum Threat Visualization API

Provides API endpoints and visualization utilities for the quantum threat
detection system. Includes radar-like visualization, real-time monitoring,
and interactive threat maps.
"""

import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import time

from quantum_entanglement_scanner import QuantumEntanglementScanner
from quantum_threat_integration import IntegratedThreatDetector


class ThreatVisualizationAPI:
    """
    API for visualizing and monitoring quantum threats.
    
    Provides:
    - Real-time threat radar visualization
    - 3D threat mapping
    - Historical trend analysis
    - Alert generation
    """
    
    def __init__(self, detector: Optional[IntegratedThreatDetector] = None):
        """
        Initialize visualization API.
        
        Args:
            detector: Integrated threat detector instance
        """
        self.detector = detector or IntegratedThreatDetector()
        self.alert_threshold = 0.7
    
    def get_radar_view(self) -> Dict[str, Any]:
        """
        Get radar-style visualization data.
        
        Returns current threats in a radar format suitable for
        visualization with concentric circles representing threat levels.
        
        Returns:
            Radar view data structure
        """
        # Perform scan
        scan = self.detector.scanner.full_stack_scan()
        threat_map = self.detector.scanner.generate_threat_map()
        
        # Convert to radar format
        radar_data = {
            "timestamp": time.time(),
            "center": {"x": 0, "y": 0, "z": 0},  # Origin
            "scan_radius": self.detector.scanner.scan_radius,
            "threat_rings": self._create_threat_rings(scan["measurements"]),
            "entities": self._format_entities_for_radar(scan["measurements"]),
            "alerts": self._generate_alerts(scan, threat_map),
            "overall_status": self._get_status_color(scan["safety_level"])
        }
        
        return radar_data
    
    def _create_threat_rings(self, measurements: List[Dict]) -> List[Dict]:
        """Create concentric threat rings for radar visualization."""
        rings = [
            {"radius": 0.2, "label": "Core", "color": "#00ff00"},
            {"radius": 0.4, "label": "Inner", "color": "#88ff00"},
            {"radius": 0.6, "label": "Middle", "color": "#ffff00"},
            {"radius": 0.8, "label": "Outer", "color": "#ff8800"},
            {"radius": 1.0, "label": "Edge", "color": "#ff0000"}
        ]
        
        # Count threats in each ring
        for ring in rings:
            ring["threat_count"] = sum(
                1 for m in measurements 
                if self._distance_from_origin(m["location"]) <= ring["radius"] * self.detector.scanner.scan_radius
                and m["threat_level"] > 0.5
            )
        
        return rings
    
    def _distance_from_origin(self, location: List[float]) -> float:
        """Calculate distance from origin."""
        return sum(x**2 for x in location) ** 0.5
    
    def _format_entities_for_radar(self, measurements: List[Dict]) -> List[Dict]:
        """Format entities for radar display."""
        entities = []
        for m in measurements:
            x, y, z = m["location"]
            distance = self._distance_from_origin([x, y, z])
            angle = (time.time() + hash(m["entity_id"])) % 360  # Animated rotation
            
            entities.append({
                "id": m["entity_id"],
                "position": {"x": x, "y": y, "z": z},
                "distance": distance,
                "angle": angle,
                "threat_level": m["threat_level"],
                "status": "critical" if m["threat_level"] > 0.8 else "warning" if m["threat_level"] > 0.5 else "safe",
                "coherence": m["state_coherence"],
                "error_count": m["error_count"]
            })
        
        return entities
    
    def _generate_alerts(self, scan: Dict, threat_map: Dict) -> List[Dict]:
        """Generate active alerts."""
        alerts = []
        
        # High threat entities
        for m in scan["measurements"]:
            if m["threat_level"] > self.alert_threshold:
                alerts.append({
                    "type": "high_threat",
                    "severity": "critical" if m["threat_level"] > 0.9 else "warning",
                    "entity_id": m["entity_id"],
                    "threat_level": m["threat_level"],
                    "message": f"Entity {m['entity_id']} showing threat level {m['threat_level']:.2f}",
                    "timestamp": m["timestamp"]
                })
        
        # Hotspots
        for hotspot in threat_map.get("hotspots", []):
            alerts.append({
                "type": "hotspot",
                "severity": hotspot["priority"],
                "position": hotspot["position"],
                "threat_level": hotspot["threat_level"],
                "message": f"Threat hotspot detected at {hotspot['position']}",
                "timestamp": time.time()
            })
        
        # System-wide issues
        if scan["corrections_needed"] > len(scan["measurements"]) * 0.3:
            alerts.append({
                "type": "system_degradation",
                "severity": "warning",
                "message": f"{scan['corrections_needed']} entities need error correction",
                "timestamp": time.time()
            })
        
        return alerts
    
    def _get_status_color(self, safety_level: float) -> str:
        """Get color code for status."""
        if safety_level >= 0.9:
            return "#00ff00"  # Green
        elif safety_level >= 0.7:
            return "#88ff00"  # Yellow-green
        elif safety_level >= 0.5:
            return "#ffff00"  # Yellow
        elif safety_level >= 0.3:
            return "#ff8800"  # Orange
        else:
            return "#ff0000"  # Red
    
    def get_3d_threat_map(self) -> Dict[str, Any]:
        """
        Get 3D threat map for visualization.
        
        Returns:
            3D map data with threat levels in spatial grid
        """
        threat_map = self.detector.scanner.generate_threat_map()
        
        # Convert to 3D visualization format
        map_3d = {
            "timestamp": time.time(),
            "grid_size": threat_map["grid_resolution"],
            "scan_radius": threat_map["scan_radius"],
            "max_threat": threat_map["max_threat"],
            "voxels": []  # 3D pixels
        }
        
        # Convert grid to voxels
        for pos_str, threat_level in threat_map["threat_map"].items():
            coords = [float(x) for x in pos_str.split(',')]
            map_3d["voxels"].append({
                "position": {"x": coords[0], "y": coords[1], "z": coords[2]},
                "threat_level": threat_level,
                "color": self._threat_to_color(threat_level),
                "size": max(0.5, threat_level)  # Size based on threat
            })
        
        return map_3d
    
    def _threat_to_color(self, threat_level: float) -> str:
        """Convert threat level to color code."""
        if threat_level < 0.3:
            return "#00ff00"  # Green
        elif threat_level < 0.5:
            return "#88ff00"  # Yellow-green
        elif threat_level < 0.7:
            return "#ffff00"  # Yellow
        elif threat_level < 0.85:
            return "#ff8800"  # Orange
        else:
            return "#ff0000"  # Red
    
    def get_historical_trends(self, duration: int = 3600) -> Dict[str, Any]:
        """
        Get historical threat trends.
        
        Args:
            duration: Time period in seconds
            
        Returns:
            Trend data over time
        """
        # Get recent measurements
        cutoff_time = time.time() - duration
        recent = [m for m in self.detector.scanner.measurement_history 
                 if m.timestamp >= cutoff_time]
        
        if not recent:
            return {"message": "No historical data available"}
        
        # Calculate trends
        threats_over_time = []
        coherence_over_time = []
        
        # Group by time buckets (5 minute intervals)
        bucket_size = 300  # 5 minutes
        buckets = {}
        
        for m in recent:
            bucket = int((m.timestamp - cutoff_time) / bucket_size)
            if bucket not in buckets:
                buckets[bucket] = {"threats": [], "coherence": []}
            
            buckets[bucket]["threats"].append(m.threat_level)
            buckets[bucket]["coherence"].append(m.state_coherence)
        
        # Calculate averages per bucket
        for bucket_id in sorted(buckets.keys()):
            data = buckets[bucket_id]
            threats_over_time.append({
                "time": cutoff_time + bucket_id * bucket_size,
                "avg_threat": sum(data["threats"]) / len(data["threats"]),
                "max_threat": max(data["threats"]),
                "sample_count": len(data["threats"])
            })
            coherence_over_time.append({
                "time": cutoff_time + bucket_id * bucket_size,
                "avg_coherence": sum(data["coherence"]) / len(data["coherence"]),
                "min_coherence": min(data["coherence"])
            })
        
        return {
            "duration": duration,
            "start_time": cutoff_time,
            "end_time": time.time(),
            "total_measurements": len(recent),
            "threat_trends": threats_over_time,
            "coherence_trends": coherence_over_time
        }
    
    def generate_dashboard_data(self) -> Dict[str, Any]:
        """
        Generate complete dashboard data.
        
        Returns all data needed for a comprehensive monitoring dashboard.
        
        Returns:
            Complete dashboard data
        """
        # Get all visualization components
        radar = self.get_radar_view()
        map_3d = self.get_3d_threat_map()
        trends = self.get_historical_trends(duration=3600)
        system_status = self.detector.full_system_scan()
        
        return {
            "timestamp": time.time(),
            "dashboard_type": "quantum_threat_monitoring",
            "radar_view": radar,
            "threat_map_3d": map_3d,
            "historical_trends": trends,
            "system_status": system_status,
            "recommendations": self.detector._generate_recommendations(
                system_status,
                self.detector.scanner.generate_threat_map()
            )
        }
    
    def export_dashboard(self, filename: Optional[str] = None) -> str:
        """
        Export dashboard data to file.
        
        Args:
            filename: Output filename
            
        Returns:
            Path to exported file
        """
        if filename is None:
            filename = f"data/threat_scans/dashboard_{int(time.time())}.json"
        
        dashboard = self.generate_dashboard_data()
        
        with open(filename, 'w') as f:
            json.dump(dashboard, f, indent=2)
        
        return filename
    
    def generate_ascii_radar(self, width: int = 60, height: int = 30) -> str:
        """
        Generate ASCII art radar visualization.
        
        Args:
            width: Width of radar display
            height: Height of radar display
            
        Returns:
            ASCII radar string
        """
        radar = self.get_radar_view()
        
        # Create grid
        grid = [[' ' for _ in range(width)] for _ in range(height)]
        
        # Draw center
        center_x, center_y = width // 2, height // 2
        grid[center_y][center_x] = '+'
        
        # Draw rings
        for ring in radar["threat_rings"]:
            radius_pixels = int(ring["radius"] * min(width, height) / 2)
            for angle in range(0, 360, 10):
                x = int(center_x + radius_pixels * (angle / 180 * 3.14159 / 2))
                y = int(center_y + radius_pixels * (angle / 180 * 3.14159 / 2))
                if 0 <= x < width and 0 <= y < height:
                    grid[y][x] = '.'
        
        # Draw entities
        for entity in radar["entities"]:
            x = int(center_x + entity["position"]["x"] / radar["scan_radius"] * width / 2)
            y = int(center_y + entity["position"]["y"] / radar["scan_radius"] * height / 2)
            
            if 0 <= x < width and 0 <= y < height:
                if entity["status"] == "critical":
                    grid[y][x] = 'X'
                elif entity["status"] == "warning":
                    grid[y][x] = '!'
                else:
                    grid[y][x] = 'o'
        
        # Convert to string
        lines = [''.join(row) for row in grid]
        
        # Add legend
        legend = [
            "\nLegend:",
            "  + = Center",
            "  o = Safe entity",
            "  ! = Warning",
            "  X = Critical threat",
            "  . = Scan radius",
            f"\nStatus: {radar['overall_status']}"
        ]
        
        return '\n'.join(lines + legend)


def demo_visualization():
    """Demonstrate visualization API."""
    print("=" * 70)
    print("Quantum Threat Visualization API - Demo")
    print("=" * 70)
    
    # Initialize
    detector = IntegratedThreatDetector()
    api = ThreatVisualizationAPI(detector)
    
    # Create test scenario
    print("\n📝 Setting up test scenario...")
    for i in range(5):
        detector.lifecycle_manager.create_entity(f"monitor_{i}", "scanner", "quantum")
        detector.lifecycle_manager.quantum_entangle(f"monitor_{i}", "quantum_domain")
        detector.lifecycle_manager.awaken_entity(f"monitor_{i}")
    
    # Get radar view
    print("\n🎯 Generating radar view...")
    radar = api.get_radar_view()
    print(f"   Entities detected: {len(radar['entities'])}")
    print(f"   Active alerts: {len(radar['alerts'])}")
    print(f"   Status: {radar['overall_status']}")
    
    # Show ASCII radar
    print("\n📡 ASCII Radar View:")
    print(api.generate_ascii_radar(width=60, height=20))
    
    # Get 3D map
    print("\n🗺️  3D Threat Map:")
    map_3d = api.get_3d_threat_map()
    print(f"   Grid size: {map_3d['grid_size']}")
    print(f"   Voxels: {len(map_3d['voxels'])}")
    print(f"   Max threat: {map_3d['max_threat']:.3f}")
    
    # Export dashboard
    print("\n💾 Exporting dashboard...")
    dashboard_file = api.export_dashboard()
    print(f"   Saved to: {dashboard_file}")
    
    print("\n✅ Visualization demo complete!")


if __name__ == "__main__":
    demo_visualization()
