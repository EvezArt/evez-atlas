"""
Test script for Visual Dashboard and WiFi Scanner

This script tests the visual dashboard functionality and WiFi scanning capabilities.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.api.wifi_scanner import WiFiScanner


def test_wifi_scanner():
    """Test WiFi scanner functionality."""
    print("=" * 60)
    print("Testing WiFi Scanner")
    print("=" * 60)

    scanner = WiFiScanner()

    # Test 1: Scan networks
    print("\n[1] Testing network scan...")
    networks = scanner.scan_networks()
    assert isinstance(networks, list), "Networks should be a list"
    assert len(networks) > 0, "Should find at least one network"
    print(f"   ✓ Found {len(networks)} networks")

    # Test 2: Check network structure
    print("\n[2] Testing network data structure...")
    for net in networks:
        assert 'ssid' in net, "Network should have SSID"
        assert 'signal_strength' in net, "Network should have signal strength"
        assert 'security' in net, "Network should have security type"
        assert 'mac_address' in net, "Network should have MAC address"
    print("   ✓ All networks have required fields")

    # Test 3: Statistics
    print("\n[3] Testing statistics...")
    stats = scanner.get_network_statistics()
    assert stats['total_networks'] == len(networks), "Total should match scan results"
    assert stats['open_networks'] + stats['secured_networks'] == stats['total_networks']
    print(f"   ✓ Statistics: {stats['total_networks']} total, {stats['open_networks']} open, {stats['secured_networks']} secured")

    # Test 4: Map data
    print("\n[4] Testing map data generation...")
    map_data = scanner.generate_network_map_data()
    assert 'nodes' in map_data, "Map data should have nodes"
    assert 'statistics' in map_data, "Map data should have statistics"
    assert len(map_data['nodes']) == len(networks), "Map nodes should match networks"
    print(f"   ✓ Generated map with {len(map_data['nodes'])} nodes")

    # Test 5: JSON export
    print("\n[5] Testing JSON export...")
    json_str = scanner.export_to_json()
    assert len(json_str) > 0, "JSON export should not be empty"
    assert 'scan_results' in json_str, "JSON should contain scan_results"
    print("   ✓ JSON export successful")

    print("\n" + "=" * 60)
    print("All WiFi Scanner tests passed!")
    print("=" * 60)

    return True


def test_dashboard_files():
    """Test that dashboard files exist."""
    print("\n" + "=" * 60)
    print("Testing Dashboard Files")
    print("=" * 60)

    import os
    from pathlib import Path

    base_dir = Path(__file__).resolve().parents[1]

    # Test 1: Check dashboard HTML exists
    print("\n[1] Checking dashboard HTML file...")
    dashboard_path = base_dir / "src" / "api" / "visual_dashboard.html"
    assert dashboard_path.exists(), f"Dashboard HTML not found at {dashboard_path}"
    print(f"   ✓ Dashboard HTML found at {dashboard_path}")

    # Test 2: Check dashboard HTML contains required elements
    print("\n[2] Checking dashboard HTML content...")
    content = dashboard_path.read_text()
    assert "Evez666 Visual Dashboard" in content, "Dashboard should have title"
    assert "chart.js" in content.lower(), "Dashboard should include Chart.js"
    assert "wifi" in content.lower(), "Dashboard should have WiFi features"
    print("   ✓ Dashboard HTML has required content")

    # Test 3: Check WiFi scanner module
    print("\n[3] Checking WiFi scanner module...")
    scanner_path = base_dir / "src" / "api" / "wifi_scanner.py"
    assert scanner_path.exists(), f"WiFi scanner not found at {scanner_path}"
    print(f"   ✓ WiFi scanner found at {scanner_path}")

    print("\n" + "=" * 60)
    print("All dashboard file tests passed!")
    print("=" * 60)

    return True


def test_api_endpoints():
    """Test API endpoint definitions."""
    print("\n" + "=" * 60)
    print("Testing API Endpoint Definitions")
    print("=" * 60)

    from pathlib import Path

    base_dir = Path(__file__).resolve().parents[1]
    api_server_path = base_dir / "src" / "api" / "causal-chain-server.py"

    print("\n[1] Checking API server file...")
    assert api_server_path.exists(), f"API server not found at {api_server_path}"
    print(f"   ✓ API server found")

    print("\n[2] Checking endpoint definitions...")
    content = api_server_path.read_text()

    endpoints = [
        ("/dashboard", "visual dashboard"),
        ("/api/wifi/scan", "WiFi scan"),
        ("/api/wifi/map", "WiFi map"),
        ("/api/metrics/summary", "metrics summary"),
        ("/api/activity/recent", "recent activity")
    ]

    for endpoint, name in endpoints:
        assert endpoint in content, f"Endpoint {endpoint} not found"
        print(f"   ✓ {name} endpoint defined: {endpoint}")

    print("\n" + "=" * 60)
    print("All API endpoint tests passed!")
    print("=" * 60)

    return True


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print(" " * 15 + "VISUAL DASHBOARD TEST SUITE")
    print("=" * 70)

    all_passed = True

    try:
        test_wifi_scanner()
    except AssertionError as e:
        print(f"\n✗ WiFi Scanner test failed: {e}")
        all_passed = False
    except Exception as e:
        print(f"\n✗ WiFi Scanner test error: {e}")
        all_passed = False

    try:
        test_dashboard_files()
    except AssertionError as e:
        print(f"\n✗ Dashboard Files test failed: {e}")
        all_passed = False
    except Exception as e:
        print(f"\n✗ Dashboard Files test error: {e}")
        all_passed = False

    try:
        test_api_endpoints()
    except AssertionError as e:
        print(f"\n✗ API Endpoints test failed: {e}")
        all_passed = False
    except Exception as e:
        print(f"\n✗ API Endpoints test error: {e}")
        all_passed = False

    print("\n" + "=" * 70)
    if all_passed:
        print(" " * 20 + "ALL TESTS PASSED ✓")
    else:
        print(" " * 20 + "SOME TESTS FAILED ✗")
    print("=" * 70 + "\n")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
