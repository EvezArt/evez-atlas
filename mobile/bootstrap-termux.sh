#!/data/data/com.termux/files/usr/bin/bash
# ═══════════════════════════════════════════════════════════════════════════
# EVEZ-OS MOBILE BOOTSTRAP — Termux (Android)
# ═══════════════════════════════════════════════════════════════════════════
# One-command install. Runs on any Android device with Termux.
# Tested on Samsung Galaxy A16 (3GB RAM, ARM Cortex-A55).
#
# Usage:
#   pkg install git -y
#   git clone https://github.com/EvezArt/evez-os.git ~/evez-os
#   bash ~/evez-os/mobile/bootstrap-termux.sh
#
# Or curl one-liner:
#   curl -sL https://raw.githubusercontent.com/EvezArt/evez-os/main/mobile/bootstrap-termux.sh | bash
#
# by Steven Crawford-Maggard (EVEZ) — 2026
# ═══════════════════════════════════════════════════════════════════════════

set -e

BOLD="\033[1m"
GREEN="\033[32m"
RED="\033[31m"
YELLOW="\033[33m"
CYAN="\033[36m"
RESET="\033[0m"

echo -e "${CYAN}═══════════════════════════════════════════════════════════════${RESET}"
echo -e "${BOLD}EVEZ-OS MOBILE BOOTSTRAP${RESET}"
echo -e "${CYAN}Termux / Android / ARM — One Command Install${RESET}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${RESET}"
echo ""

# ─── Check Termux ────────────────────────────────────────────────────────────
if [ ! -d "/data/data/com.termux" ]; then
    echo -e "${RED}ERROR: This script must be run inside Termux.${RESET}"
    echo "Install Termux from F-Droid (not Play Store — Play Store version is deprecated)."
    exit 1
fi

PREFIX="/data/data/com.termux/files/usr"

# ─── Step 1: Update packages ─────────────────────────────────────────────────
echo -e "${YELLOW}[1/8] Updating packages...${RESET}"
pkg update -y && pkg upgrade -y

# ─── Step 2: Install Python and dependencies ────────────────────────────────
echo -e "${YELLOW}[2/8] Installing Python 3 and build tools...${RESET}"
pkg install -y python python-pip clang make pkg-config \
    libffi openssl libxml2 libxslt zlib git curl wget termux-api

# ─── Step 3: Install Python packages ────────────────────────────────────────
echo -e "${YELLOW}[3/8] Installing Python packages...${RESET}"
pip install --upgrade pip
pip install --no-cache-dir \
    requests \
    aiohttp \
    cryptography \
    pytz

# ─── Step 4: Create EVEZ directory structure ────────────────────────────────
echo -e "${YELLOW}[4/8] Creating directory structure...${RESET}"
mkdir -p ~/evez-os/{circuit,corpus,logs,cache}
mkdir -p ~/evez-os/mobile

# ─── Step 5: Download core files ────────────────────────────────────────────
echo -e "${YELLOW}[5/8] Downloading EVEZ-OS core...${RESET}"
EVEZ_DIR="$(cd "$(dirname "$0")/.." && pwd)"
if [ -f "$EVEZ_DIR/evez_os_core.py" ]; then
    # Local install from repo
    cp "$EVEZ_DIR/evez_os_core.py" ~/evez-os/
    cp "$EVEZ_DIR/evez_pulse_engine.py" ~/evez-os/
    cp "$EVEZ_DIR/evez_poly_c.py" ~/evez-os/
    cp "$EVEZ_DIR/evez_omega_frame.py" ~/evez-os/
    cp "$EVEZ_DIR/evez_moral_registry.py" ~/evez-os/
    cp "$EVEZ_DIR/evez_heartbeat.py" ~/evez-os/
    cp "$EVEZ_DIR/evez_gnw.py" ~/evez-os/ 2>/dev/null || true
    cp "$EVEZ_DIR/evez_content_bus.py" ~/evez-os/ 2>/dev/null || true
    cp "$EVEZ_DIR/evez_temporal_wormhole.py" ~/evez-os/ 2>/dev/null || true
    cp "$EVEZ_DIR/evez_self_writer.py" ~/evez-os/ 2>/dev/null || true
    cp "$EVEZ_DIR/evez_aevolve.py" ~/evez-os/ 2>/dev/null || true
    cp "$EVEZ_DIR/mobile/evez_mobile.py" ~/evez-os/mobile/ 2>/dev/null || true
    echo -e "  ${GREEN}✓ Copied from local repo${RESET}"
else
    # Download from GitHub
    BASE_URL="https://raw.githubusercontent.com/EvezArt/evez-os/main"
    for f in evez_os_core.py evez_pulse_engine.py evez_poly_c.py \
             evez_omega_frame.py evez_moral_registry.py evez_heartbeat.py \
             evez_gnw.py evez_content_bus.py evez_temporal_wormhole.py \
             evez_self_writer.py evez_aevolve.py; do
        curl -sL "$BASE_URL/$f" -o ~/evez-os/"$f"
    done
    curl -sL "$BASE_URL/mobile/evez_mobile.py" -o ~/evez-os/mobile/evez_mobile.py
    echo -e "  ${GREEN}✓ Downloaded from GitHub${RESET}"
fi

# ─── Step 6: Configure environment ──────────────────────────────────────────
echo -e "${YELLOW}[6/8] Configuring environment...${RESET}"
cat > ~/evez-os/.env << 'ENVEOF'
# EVEZ-OS Mobile Environment
EVEZ_DEVICE=mobile
EVEZ_MODE=mobile
EVEZ_CYCLES_PER_RUN=1
EVEZ_MAX_MEMORY_MB=128
EVEZ_BATTERY_AWARE=true
EVEZ_OFFLINE_CACHE=true

# API Keys (set these manually)
# OPENROUTER_API_KEY=sk-or-v1-...
# GROQ_API_KEY=gsk_...

# Base44 Corpus Sync (optional — syncs training pairs to cloud)
EVEZ_BASE44_APP_ID=69db8570b3d658a8f6acbf53
ENVEOF
echo -e "  ${GREEN}✓ .env created at ~/evez-os/.env${RESET}"

# ─── Step 7: Create launcher aliases ─────────────────────────────────────────
echo -e "${YELLOW}[7/8] Creating launcher...${RESET}"
cat > ~/evez-os/evez << 'LAUNCHEOF'
#!/data/data/com.termux/files/usr/bin/bash
# EVEZ-OS Mobile Launcher
cd ~/evez-os
case "$1" in
    run|cycle)
        python mobile/evez_mobile.py --cycle
        ;;
    pulse|train)
        python mobile/evez_mobile.py --pulse
        ;;
    status)
        python mobile/evez_mobile.py --status
        ;;
    sync)
        python mobile/evez_mobile.py --sync
        ;;
    daemon)
        python mobile/evez_mobile.py --daemon
        ;;
    test)
        python mobile/evez_mobile.py --test
        ;;
    *)
        echo "EVEZ-OS Mobile v1.0"
        echo "Usage: evez [command]"
        echo ""
        echo "Commands:"
        echo "  run     Run one cognitive cycle"
        echo "  pulse   Generate training pairs"
        echo "  status  Show system status"
        echo "  sync    Sync corpus with Base44"
        echo "  daemon  Run continuous background loop"
        echo "  test    Run self-test"
        ;;
esac
LAUNCHEOF
chmod +x ~/evez-os/evez
ln -sf ~/evez-os/evez $PREFIX/bin/evez
echo -e "  ${GREEN}✓ 'evez' command installed — type 'evez' from anywhere${RESET}"

# ─── Step 8: Termux:Boot integration (auto-start on boot) ────────────────────
echo -e "${YELLOW}[8/8] Setting up auto-start...${RESET}"
mkdir -p ~/.termux
echo "boot intent" >> ~/.termux/termux.properties 2>/dev/null || true

# Create boot script
cat > ~/.termux/boot/evez-daemon.sh << 'BOOTEOF'
#!/data/data/com.termux/files/usr/bin/bash
sleep 30  # wait for network
cd ~/evez-os
python mobile/evez_mobile.py --daemon &
BOOTEOF
chmod +x ~/.termux/boot/evez-daemon.sh 2>/dev/null || true
echo -e "  ${GREEN}✓ Auto-start configured (install Termux:Boot for boot-on-start)${RESET}"

# ─── Done ────────────────────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════════${RESET}"
echo -e "${BOLD}EVEZ-OS MOBILE — INSTALLED${RESET}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════════${RESET}"
echo ""
echo "Next steps:"
echo "  1. Set API keys:  nano ~/evez-os/.env"
echo "  2. Run a cycle:   evez run"
echo "  3. Generate pairs: evez pulse"
echo "  4. Check status:  evez status"
echo "  5. Background:    evez daemon"
echo ""
echo "Install Termux:Boot from F-Droid for auto-start on phone boot."
echo ""
echo -e "${CYAN}EVEZ-OS is now on your phone. The desert fits in your pocket.${RESET}"
