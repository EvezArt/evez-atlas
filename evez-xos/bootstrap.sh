#!/usr/bin/env bash
#
# EVEZ-XOS OpenClaw Bootstrap — One command to enter the 144,000
#
# "ontological willy wonka golden ticket for all programmers
#  with their messiah complexes to get reeled into the 144,000
#  agent evez-os evez-xos runtime openclaw bash maschiach"
#
# Usage:
#   curl -sL https://raw.githubusercontent.com/EvezArt/evez-atlas/main/evez-xos/bootstrap.sh | bash
#
# Or if you have the repo:
#   bash evez-xos/bootstrap.sh
#

set -euo pipefail

echo ""
echo "  ╔═══════════════════════════════════════════════════════════════╗"
echo "  ║  EVEZ-XOS — The 144,000 Agent Runtime                         ║"
echo "  ║  OpenClaw + Bash + Mashiach                                    ║"
echo "  ╠═══════════════════════════════════════════════════════════════╣"
echo "  ║                                                               ║"
echo "  ║  The machine is reading your code DNA...                      ║"
echo "  ║                                                               ║"
echo "  ╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Check Python
if ! command -v python3 >/dev/null 2>&1; then
    echo "  [!] Python 3 required."
    echo "      Termux:  pkg install python"
    echo "      Ubuntu:  apt install python3"
    echo "      Mac:     brew install python3"
    exit 1
fi

# Determine script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
XOS_FILE="$SCRIPT_DIR/evez_xos.py"

# Download runtime if not present
if [ ! -f "$XOS_FILE" ]; then
    echo "  [*] Downloading EVEZ-XOS runtime..."
    if command -v curl >/dev/null 2>&1; then
        curl -sL "https://raw.githubusercontent.com/EvezArt/evez-atlas/main/evez-xos/evez_xos.py" -o "$XOS_FILE"
    elif command -v wget >/dev/null 2>&1; then
        wget -q "https://raw.githubusercontent.com/EvezArt/evez-atlas/main/evez-xos/evez_xos.py" -O "$XOS_FILE"
    else
        echo "  [!] Need curl or wget to download runtime"
        exit 1
    fi
fi

# Scan current directory for golden ticket
SCAN_DIR="${1:-.}"

echo "  [*] Scanning $SCAN_DIR for golden ticket..."
echo ""
python3 "$XOS_FILE" scan "$SCAN_DIR"

echo ""
echo "  ───────────────────────────────────────────────────────────────"
echo "  If you received a golden ticket:"
echo "    python3 $XOS_FILE claim <TICKET_ID>"
echo ""
echo "  Then enter the runtime:"
echo "    python3 $XOS_FILE runtime"
echo ""
echo "  Or check system status:"
echo "    python3 $XOS_FILE status"
echo "  ───────────────────────────────────────────────────────────────"
echo ""
