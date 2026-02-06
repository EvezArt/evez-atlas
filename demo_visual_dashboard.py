#!/usr/bin/env python3
"""
Visual Dashboard Demo Script

This script demonstrates the visual dashboard and WiFi scanning capabilities.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.api.wifi_scanner import WiFiScanner
import json


def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def demo_wifi_scanner():
    """Demonstrate WiFi scanning capabilities."""
    print_header("WiFi Network Scanner Demo")

    scanner = WiFiScanner()

    print("📡 Scanning for WiFi networks...")
    networks = scanner.scan_networks()

    print(f"\n✓ Discovered {len(networks)} networks:\n")

    for i, net in enumerate(networks, 1):
        security_icon = "🔒" if net['security'] != 'Open' else "🔓"
        signal_bars = "▮" * (net['signal_strength'] // 20)

        print(f"{i:2d}. {security_icon} {net['ssid']:<25} {signal_bars:<5} {net['signal_strength']:3d}%")
        print(f"     Security: {net['security']:<15} Channel: {net['channel']:3d}   MAC: {net['mac_address']}")

    return scanner


def demo_statistics(scanner):
    """Demonstrate statistics calculation."""
    print_header("Network Statistics")

    stats = scanner.get_network_statistics()

    print(f"📊 Network Overview:\n")
    print(f"   Total Networks:     {stats['total_networks']}")
    print(f"   Open Networks:      {stats['open_networks']} ⚠️")
    print(f"   Secured Networks:   {stats['secured_networks']} ✓")
    print(f"   Average Signal:     {stats['average_signal']:.1f}%")
    print(f"   Strongest Network:  {stats['strongest_network']}")

    print(f"\n📡 Channel Distribution:")
    for channel, count in sorted(stats['channel_distribution'].items()):
        bars = "▮" * count
        print(f"   Channel {channel:3d}: {bars} ({count})")


def demo_map_visualization(scanner):
    """Demonstrate map data generation."""
    print_header("Network Map Visualization")

    print("🗺️  Generating network map data...\n")

    map_data = scanner.generate_network_map_data()

    print(f"✓ Map generated with {len(map_data['nodes'])} nodes\n")
    print("   Node positions (for visualization):\n")

    for i, node in enumerate(map_data['nodes'][:5], 1):  # Show first 5
        print(f"   {i}. {node['ssid']:<25} Position: ({node['x']:.1f}, {node['y']:.1f})")

    if len(map_data['nodes']) > 5:
        print(f"   ... and {len(map_data['nodes']) - 5} more")


def demo_json_export(scanner):
    """Demonstrate JSON export."""
    print_header("JSON Export")

    print("💾 Exporting scan results to JSON...\n")

    json_data = scanner.export_to_json()
    data_obj = json.loads(json_data)

    print("✓ Export complete!")
    print(f"\n   Networks exported:  {len(data_obj['scan_results'])}")
    print(f"   Data size:          {len(json_data)} bytes")
    print(f"\n   Sample JSON structure:")
    print(json.dumps(data_obj['scan_results'][0] if data_obj['scan_results'] else {}, indent=4)[:300])


def demo_dashboard_info():
    """Display dashboard access information."""
    print_header("Visual Dashboard Access")

    print("🖥️  The visual dashboard provides:\n")
    print("   ✓ Interactive charts and graphs")
    print("   ✓ Real-time system metrics")
    print("   ✓ WiFi network visualization")
    print("   ✓ Action panels for system control")
    print("   ✓ Activity logging")
    print("   ✓ Data export capabilities")

    print("\n📍 Access Methods:\n")
    print("   1. Start API server:")
    print("      $ python src/api/causal-chain-server.py")
    print("      Then visit: http://localhost:8000/dashboard")

    print("\n   2. Open HTML directly:")
    print("      $ open src/api/visual_dashboard.html")

    print("\n🔗 Available API Endpoints:\n")
    endpoints = [
        ("/dashboard", "Visual dashboard interface"),
        ("/api/wifi/scan", "Scan WiFi networks"),
        ("/api/wifi/map", "Get network map data"),
        ("/api/metrics/summary", "System metrics"),
        ("/api/activity/recent", "Recent activity log"),
    ]

    for endpoint, description in endpoints:
        print(f"   GET {endpoint:<25} - {description}")


def main():
    """Run the complete demo."""
    print("\n" + "=" * 70)
    print("  EVEZ666 VISUAL DASHBOARD & WIFI SCANNER DEMO")
    print("=" * 70)

    try:
        # Run WiFi scanner demo
        scanner = demo_wifi_scanner()

        # Show statistics
        demo_statistics(scanner)

        # Show map visualization
        demo_map_visualization(scanner)

        # Show JSON export
        demo_json_export(scanner)

        # Show dashboard info
        demo_dashboard_info()

        print_header("Demo Complete")
        print("✅ All features demonstrated successfully!")
        print("\n💡 Tip: Run 'python src/api/causal-chain-server.py' to start the server")
        print("   Then visit http://localhost:8000/dashboard for the full experience\n")

        return 0

    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
        return 1
    except Exception as e:
        print(f"\n\n❌ Error during demo: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
