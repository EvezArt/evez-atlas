#!/usr/bin/env bash
#
# OpenClaw Unified Startup Script
# Combines the entire OpenClaw swarm startup sequence into one command
#
# Usage: ./scripts/start_openclaw.sh [--dry-run] [--stop]
#

set -euo pipefail

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Parse command line arguments
DRY_RUN=false
STOP_MODE=false

for arg in "$@"; do
    case $arg in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --stop)
            STOP_MODE=true
            shift
            ;;
        *)
            error "Unknown argument: $arg"
            echo "Usage: $0 [--dry-run] [--stop]"
            exit 1
            ;;
    esac
done

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "${SCRIPT_DIR}")"

# Stop mode - teardown
if [ "$STOP_MODE" = true ]; then
    info "Stopping OpenClaw swarm..."
    
    if [ "$DRY_RUN" = true ]; then
        info "[DRY RUN] Would stop Docker containers"
        info "[DRY RUN] Would kill openclaw processes"
        exit 0
    fi
    
    # Stop Docker containers
    JUBILEE_DIR="${ROOT_DIR}/third_party/jubilee-online"
    if [ -d "${JUBILEE_DIR}" ]; then
        step "Stopping Jubilee Docker containers..."
        cd "${JUBILEE_DIR}"
        if docker compose version &> /dev/null; then
            docker compose down 2>/dev/null || true
        else
            docker-compose down 2>/dev/null || true
        fi
        success "Stopped Jubilee containers"
    fi
    
    # Kill openclaw processes
    step "Stopping OpenClaw processes..."
    if [ -f /tmp/openclaw.pid ]; then
        OPENCLAW_PID=$(cat /tmp/openclaw.pid)
        if kill -0 "$OPENCLAW_PID" 2>/dev/null; then
            kill "$OPENCLAW_PID" 2>/dev/null || true
            rm -f /tmp/openclaw.pid
            success "Stopped OpenClaw process (PID: $OPENCLAW_PID)"
        else
            warn "OpenClaw process not running"
            rm -f /tmp/openclaw.pid
        fi
    else
        # Fallback to pkill if PID file doesn't exist
        if pgrep -f "openclaw" > /dev/null 2>&1; then
            pkill -f "openclaw" 2>/dev/null || true
            success "Stopped OpenClaw processes"
        else
            warn "No OpenClaw processes found"
        fi
    fi
    
    success "✓ Teardown complete!"
    exit 0
fi

# Check prerequisites
info "Checking prerequisites..."

check_command() {
    local cmd=$1
    local name=$2
    local min_version=${3:-}
    
    if [ "$DRY_RUN" = true ]; then
        info "[DRY RUN] Would check for $name"
        return 0
    fi
    
    if ! command -v "$cmd" &> /dev/null; then
        error "$name is not installed"
        return 1
    fi
    success "$name is installed"
    
    # Version check if specified
    if [ -n "$min_version" ]; then
        info "  Checking $name version..."
    fi
    
    return 0
}

PREREQ_FAILED=false

# Check Docker
check_command docker "Docker" || PREREQ_FAILED=true

# Check Git
check_command git "Git" || PREREQ_FAILED=true

# Check Node.js
if [ "$DRY_RUN" = false ]; then
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version | sed 's/v//' | cut -d'.' -f1)
        if [ "$NODE_VERSION" -lt 20 ]; then
            error "Node.js version 20+ required (found: $NODE_VERSION)"
            PREREQ_FAILED=true
        else
            success "Node.js $NODE_VERSION is installed"
        fi
    else
        error "Node.js is not installed"
        PREREQ_FAILED=true
    fi
else
    info "[DRY RUN] Would check for Node.js 20+"
fi

# Check Python
if [ "$DRY_RUN" = false ]; then
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}' | cut -d'.' -f1,2)
        PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d'.' -f1)
        PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d'.' -f2)
        
        if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 11 ]); then
            error "Python 3.11+ required (found: $PYTHON_VERSION)"
            PREREQ_FAILED=true
        else
            success "Python $PYTHON_VERSION is installed"
        fi
    else
        error "Python 3 is not installed"
        PREREQ_FAILED=true
    fi
else
    info "[DRY RUN] Would check for Python 3.11+"
fi

# Check pnpm
check_command pnpm "pnpm" || PREREQ_FAILED=true

if [ "$PREREQ_FAILED" = true ]; then
    error "Prerequisites check failed. Please install missing dependencies."
    exit 1
fi

success "✓ All prerequisites satisfied"
echo ""

# Set default environment variables (allow override)
step "Setting up environment variables..."

if [ "$DRY_RUN" = true ]; then
    info "[DRY RUN] Would set JUBILEE_MODE=${JUBILEE_MODE:-qsvc-ibm}"
    info "[DRY RUN] Would set JUBILEE_TOUCH_ID=${JUBILEE_TOUCH_ID:-8e5526c72cebad3c09e4158399eaab06}"
    info "[DRY RUN] Would set JUBILEE_ENDPOINT=${JUBILEE_ENDPOINT:-http://localhost:8000/forgive}"
    if [ -z "${JUBILEE_HMAC_SECRET:-}" ]; then
        info "[DRY RUN] Would generate JUBILEE_HMAC_SECRET via openssl rand -hex 32"
    fi
else
    export JUBILEE_MODE="${JUBILEE_MODE:-qsvc-ibm}"
    export JUBILEE_TOUCH_ID="${JUBILEE_TOUCH_ID:-8e5526c72cebad3c09e4158399eaab06}"
    export JUBILEE_ENDPOINT="${JUBILEE_ENDPOINT:-http://localhost:8000/forgive}"
    
    if [ -z "${JUBILEE_HMAC_SECRET:-}" ]; then
        export JUBILEE_HMAC_SECRET=$(openssl rand -hex 32)
        info "Generated JUBILEE_HMAC_SECRET: ${JUBILEE_HMAC_SECRET:0:8}..."
    else
        info "Using existing JUBILEE_HMAC_SECRET: ${JUBILEE_HMAC_SECRET:0:8}..."
    fi
    
    success "Environment configured:"
    info "  JUBILEE_MODE=$JUBILEE_MODE"
    info "  JUBILEE_TOUCH_ID=$JUBILEE_TOUCH_ID"
    info "  JUBILEE_ENDPOINT=$JUBILEE_ENDPOINT"
fi
echo ""

# Run swarm bootstrap
step "Running swarm bootstrap..."

if [ "$DRY_RUN" = true ]; then
    info "[DRY RUN] Would execute: ${SCRIPT_DIR}/swarm_bootstrap.sh"
else
    if [ -f "${SCRIPT_DIR}/swarm_bootstrap.sh" ]; then
        bash "${SCRIPT_DIR}/swarm_bootstrap.sh"
        success "✓ Swarm bootstrap complete"
    else
        warn "swarm_bootstrap.sh not found, skipping..."
    fi
fi
echo ""

# Start Jubilee service
step "Starting Jubilee service..."

if [ "$DRY_RUN" = true ]; then
    info "[DRY RUN] Would execute: ${SCRIPT_DIR}/jubilee_up.sh"
    info "[DRY RUN] Would wait for health check at http://localhost:8000/healthz"
else
    if [ -f "${SCRIPT_DIR}/jubilee_up.sh" ]; then
        bash "${SCRIPT_DIR}/jubilee_up.sh"
        success "✓ Jubilee service started"
    else
        error "jubilee_up.sh not found"
        exit 1
    fi
fi
echo ""

# Install OpenClaw if needed
step "Checking OpenClaw installation..."

if [ "$DRY_RUN" = true ]; then
    info "[DRY RUN] Would check if openclaw is on PATH"
    info "[DRY RUN] Would install via: curl -sSL https://openclaw.ai/install.sh | bash"
else
    if command -v openclaw &> /dev/null; then
        success "OpenClaw is already installed"
    else
        info "Installing OpenClaw..."
        if curl -sSL https://openclaw.ai/install.sh | bash; then
            success "✓ OpenClaw installed"
        else
            warn "OpenClaw installation failed or skipped"
            warn "You can install manually: curl -sSL https://openclaw.ai/install.sh | bash"
        fi
    fi
fi
echo ""

# Launch swarm agents
step "Launching OpenClaw swarm agents..."

if [ "$DRY_RUN" = true ]; then
    info "[DRY RUN] Would execute: openclaw --soul SOUL.md --skills jubilee,molt_post"
    info "[DRY RUN] This would run in the background"
else
    cd "${ROOT_DIR}"
    
    if [ ! -f "SOUL.md" ]; then
        error "SOUL.md not found in ${ROOT_DIR}"
        exit 1
    fi
    
    # Ensure data directory exists
    mkdir -p data
    
    # Launch openclaw in the background
    info "Starting: openclaw --soul SOUL.md --skills jubilee,molt_post"
    info "This will run in the background. Check logs in data/ directory"
    
    # Note: In a real environment, openclaw would be installed and available
    # For now, we'll just indicate what would happen
    if command -v openclaw &> /dev/null; then
        nohup openclaw --soul SOUL.md --skills jubilee,molt_post > data/openclaw.log 2>&1 &
        OPENCLAW_PID=$!
        echo $OPENCLAW_PID > /tmp/openclaw.pid
        success "✓ OpenClaw agents launched (PID: $OPENCLAW_PID)"
    else
        warn "openclaw command not found in PATH"
        warn "Please install OpenClaw: curl -sSL https://openclaw.ai/install.sh | bash"
        warn "Then run: openclaw --soul SOUL.md --skills jubilee,molt_post"
    fi
fi
echo ""

# Run verification checks
step "Running verification checks..."
echo ""

if [ "$DRY_RUN" = true ]; then
    info "[DRY RUN] Would verify:"
    info "  - Docker containers are running"
    info "  - Jubilee health endpoint responds"
    info "  - OpenClaw agents are healthy"
else
    # Check Docker containers
    info "Checking Docker containers..."
    JUBILEE_DIR="${ROOT_DIR}/third_party/jubilee-online"
    if [ -d "${JUBILEE_DIR}" ]; then
        cd "${JUBILEE_DIR}"
        if docker compose ps 2>/dev/null | grep -q "Up" || docker-compose ps 2>/dev/null | grep -q "Up"; then
            success "✓ Docker containers are running"
        else
            warn "⚠ Docker containers may not be running"
        fi
    fi
    
    # Check Jubilee health endpoint
    info "Checking Jubilee health endpoint..."
    if curl -s http://localhost:8000/healthz > /dev/null 2>&1; then
        success "✓ Jubilee health endpoint responds"
    else
        warn "⚠ Jubilee health endpoint not responding"
    fi
    
    # Check OpenClaw processes
    info "Checking OpenClaw processes..."
    if pgrep -f "openclaw" > /dev/null 2>&1; then
        success "✓ OpenClaw agents are running"
    else
        warn "⚠ No OpenClaw processes found"
    fi
fi
echo ""

# Final success message
success "═══════════════════════════════════════════════════════"
success "  OpenClaw Swarm Startup Complete!"
success "═══════════════════════════════════════════════════════"
echo ""
info "Service endpoints:"
info "  Jubilee Health:  http://localhost:8000/healthz"
info "  Jubilee Forgive: http://localhost:8000/forgive"
info "  Swarm Status:    http://localhost:8000/swarm-status"
echo ""
info "Monitoring:"
info "  Event logs:      tail -f data/events.jsonl"
info "  OpenClaw logs:   tail -f data/openclaw.log"
info "  Molt posts:      tail -f data/molt_posts.jsonl"
echo ""
info "To stop the swarm:"
info "  ${SCRIPT_DIR}/start_openclaw.sh --stop"
echo ""
success "Happy swarming! 🦞✨"
