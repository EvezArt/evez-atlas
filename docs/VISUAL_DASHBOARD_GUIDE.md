# Visual Dashboard & Network Mapping - Quick Reference

This document provides a quick reference for using the visual dashboard and network mapping features in Evez666.

## Overview

The visual dashboard provides a comprehensive web-based interface for monitoring system status, visualizing data, and managing WiFi network scanning.

## Quick Start

### Launch the Dashboard

```bash
# Start the API server (includes dashboard)
python src/api/causal-chain-server.py

# Access in browser
# Navigate to: http://localhost:8000/dashboard
```

### Direct File Access

```bash
# Open dashboard HTML directly (limited functionality without API)
open src/api/visual_dashboard.html
```

## Dashboard Features

### 1. System Status Panel
- **API Server**: Server running status
- **Quantum Backend**: Quantum system status
- **Swarm Director**: Entity orchestration status
- **Jubilee Service**: Debt forgiveness service status

### 2. Real-time Metrics
- **Threats Detected**: Count of detected threats (updates every 5 seconds)
- **Active Entities**: Number of spawned and active entities

### 3. Interactive Charts

#### Threat Detection Timeline
- Line chart showing threat detection over time
- Last 10 time periods displayed
- Updates dynamically

#### Entity Activity
- Bar chart showing entity counts by state
- Categories: Spawned, Active, Hibernating, Molted

#### Quantum Metrics
- Radar chart showing quantum system performance
- Metrics: Kernel, Entanglement, Coherence, Fidelity, Gates

#### System Performance Overview
- Multi-line chart showing CPU, Memory, and Network I/O
- 20 time periods displayed
- Real-time updates

### 4. WiFi Network Mapping

#### Scan Networks
1. Click "Scan WiFi" button
2. Dashboard discovers nearby networks
3. Networks displayed visually on map
4. Hover over nodes for details

#### Network Map Features
- Interactive node visualization
- Color-coded by security status
- Signal strength indicated by position
- Click nodes for detailed information

#### Network Statistics
- **Total Networks**: Count of discovered networks
- **Open Networks**: Unsecured networks
- **Secured Networks**: Password-protected networks
- **Average Signal**: Mean signal strength percentage

### 5. Action Panels

| Button | Action |
|--------|--------|
| Refresh | Update all dashboard data |
| Scan WiFi | Discover nearby WiFi networks |
| Run Demo | Execute quantum threat detection demo |
| Spawn Entity | Create new swarm entity |
| View Logs | Open detailed navigation logs |
| Export Data | Download dashboard data as JSON |

### 6. Activity Log
- Real-time activity stream
- Timestamps for all events
- Last 20 entries displayed
- Auto-scrolls to newest entries

## WiFi Scanner Module

### Standalone Usage

```bash
# Run WiFi scanner
python src/api/wifi_scanner.py
```

### Programmatic Usage

```python
from src.api.wifi_scanner import WiFiScanner

# Create scanner instance
scanner = WiFiScanner()

# Scan for networks
networks = scanner.scan_networks()
print(f"Found {len(networks)} networks")

# Get statistics
stats = scanner.get_network_statistics()
print(f"Open: {stats['open_networks']}, Secured: {stats['secured_networks']}")

# Generate map data
map_data = scanner.generate_network_map_data()

# Export to JSON
json_output = scanner.export_to_json()
scanner.export_to_json('networks.json')  # Save to file
```

### Network Data Structure

Each network object contains:
- `ssid`: Network name
- `signal_strength`: Signal strength (0-100%)
- `frequency`: Frequency in MHz
- `security`: Security type (WPA2, WPA3, Open, etc.)
- `mac_address`: BSSID/MAC address
- `channel`: WiFi channel number

## API Endpoints

### Dashboard Endpoints

```bash
# Get dashboard HTML
GET http://localhost:8000/dashboard

# Scan WiFi networks
GET http://localhost:8000/api/wifi/scan

# Get network map data
GET http://localhost:8000/api/wifi/map

# Get system metrics
GET http://localhost:8000/api/metrics/summary

# Get recent activity
GET http://localhost:8000/api/activity/recent?limit=20
```

### Example API Calls

```bash
# Scan WiFi networks
curl http://localhost:8000/api/wifi/scan | jq

# Get metrics
curl http://localhost:8000/api/metrics/summary | jq

# Get activity log
curl http://localhost:8000/api/activity/recent | jq
```

## Testing

### Run All Tests

```bash
# Run visual dashboard test suite
PYTHONPATH=$PWD python tests/test_visual_dashboard.py
```

### Test Components

1. **WiFi Scanner Tests**
   - Network scanning
   - Data structure validation
   - Statistics calculation
   - Map data generation
   - JSON export

2. **Dashboard File Tests**
   - HTML file existence
   - Content validation
   - Required elements check

3. **API Endpoint Tests**
   - Endpoint definitions
   - Route verification

## Platform Support

### WiFi Scanning

| Platform | Method | Support |
|----------|--------|---------|
| Linux | `nmcli` | Full |
| macOS | `airport` utility | Full |
| Windows | `netsh` | Full |
| Other | Simulated data | Fallback |

### Network Requirements

- No special permissions required for scanning
- Simulated data provided if scanning fails
- Works offline with simulated networks

## Troubleshooting

### Dashboard Not Loading
```bash
# Check if API server is running
curl http://localhost:8000/swarm-status

# Restart server
python src/api/causal-chain-server.py
```

### WiFi Scan Returns Empty
- Check platform-specific tools are installed
- Scanner falls back to simulated data automatically
- No action needed for development/testing

### Charts Not Rendering
- Ensure internet connection for Chart.js CDN
- Check browser console for errors
- Try refreshing the page

## Advanced Usage

### Custom Network Visualization

```python
from src.api.wifi_scanner import WiFiScanner
import json

scanner = WiFiScanner()
networks = scanner.scan_networks()

# Filter by security type
secure_networks = [n for n in networks if n['security'] != 'Open']

# Sort by signal strength
sorted_networks = sorted(networks, key=lambda x: x['signal_strength'], reverse=True)

# Export filtered data
data = {'networks': secure_networks}
with open('secure_networks.json', 'w') as f:
    json.dump(data, f, indent=2)
```

### Integrate with Existing Systems

```python
# Add to your monitoring system
from src.api.wifi_scanner import WiFiScanner

def check_network_security():
    scanner = WiFiScanner()
    scanner.scan_networks()
    stats = scanner.get_network_statistics()

    if stats['open_networks'] > 0:
        print(f"WARNING: {stats['open_networks']} unsecured networks detected!")

    return stats
```

## Browser Compatibility

- **Chrome/Edge**: Full support
- **Firefox**: Full support
- **Safari**: Full support
- **Mobile browsers**: Responsive design supported

## Performance Notes

- Dashboard updates metrics every 5 seconds
- WiFi scans take 2-10 seconds depending on platform
- Charts are rendered client-side (no server load)
- Network map supports up to 50 nodes efficiently

## Security Considerations

- WiFi scanning is read-only (no network modification)
- No credentials are stored or transmitted
- Dashboard requires API key for production use
- All data stays local (no external reporting)

## Further Reading

- [Main README](../README.md)
- [API Server Documentation](causal-chain-server.py)
- [Swarm Setup Guide](../docs/swarm-setup.md)
- [Quantum Navigation UI](http://localhost:8000/navigation-ui)
