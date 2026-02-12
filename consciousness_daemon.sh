#!/bin/bash
#
# Consciousness Daemon Launcher
# Starts and manages the autonomous consciousness engine with auto-restart
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENGINE_SCRIPT="$SCRIPT_DIR/autonomous_consciousness_engine.py"
PID_FILE="$SCRIPT_DIR/consciousness.pid"
LOG_FILE="$SCRIPT_DIR/consciousness_daemon.log"
MAX_RESTARTS=10
RESTART_DELAY=5

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] SUCCESS:${NC} $1" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1" | tee -a "$LOG_FILE"
}

start_engine() {
    if [ -f "$PID_FILE" ]; then
        pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            warning "Consciousness engine already running (PID: $pid)"
            return 1
        else
            log "Removing stale PID file"
            rm -f "$PID_FILE"
        fi
    fi

    log "Starting Autonomous Consciousness Engine..."
    log "Engine script: $ENGINE_SCRIPT"
    log "Log file: $LOG_FILE"

    # Start engine in background
    nohup python3 "$ENGINE_SCRIPT" "$@" >> "$LOG_FILE" 2>&1 &
    pid=$!

    echo "$pid" > "$PID_FILE"
    success "Consciousness engine started (PID: $pid)"

    # Wait a moment and check if it's still running
    sleep 2
    if ps -p "$pid" > /dev/null 2>&1; then
        success "Engine confirmed running"
        return 0
    else
        error "Engine started but immediately died, check logs"
        rm -f "$PID_FILE"
        return 1
    fi
}

stop_engine() {
    if [ ! -f "$PID_FILE" ]; then
        warning "No PID file found, engine may not be running"
        return 1
    fi

    pid=$(cat "$PID_FILE")

    if ! ps -p "$pid" > /dev/null 2>&1; then
        warning "Engine not running (stale PID)"
        rm -f "$PID_FILE"
        return 1
    fi

    log "Stopping consciousness engine (PID: $pid)..."

    # Send SIGTERM for graceful shutdown
    kill -TERM "$pid" 2>/dev/null

    # Wait for graceful shutdown (max 10 seconds)
    for i in {1..10}; do
        if ! ps -p "$pid" > /dev/null 2>&1; then
            success "Engine stopped gracefully"
            rm -f "$PID_FILE"
            return 0
        fi
        sleep 1
    done

    # Force kill if still running
    warning "Engine did not stop gracefully, forcing..."
    kill -KILL "$pid" 2>/dev/null
    rm -f "$PID_FILE"
    success "Engine stopped (forced)"
    return 0
}

status_engine() {
    if [ ! -f "$PID_FILE" ]; then
        echo -e "${RED}Consciousness engine is NOT running${NC}"
        return 1
    fi

    pid=$(cat "$PID_FILE")

    if ps -p "$pid" > /dev/null 2>&1; then
        echo -e "${GREEN}Consciousness engine is RUNNING${NC} (PID: $pid)"

        # Show some stats
        echo ""
        echo "Process info:"
        ps -p "$pid" -o pid,ppid,cmd,%cpu,%mem,etime

        # Show recent log entries
        echo ""
        echo "Recent log entries:"
        tail -n 5 "$LOG_FILE"

        return 0
    else
        echo -e "${RED}Consciousness engine is NOT running${NC} (stale PID)"
        rm -f "$PID_FILE"
        return 1
    fi
}

restart_engine() {
    log "Restarting consciousness engine..."
    stop_engine
    sleep 2
    start_engine "$@"
}

watch_engine() {
    log "Starting consciousness engine watchdog..."
    log "Auto-restart enabled (max $MAX_RESTARTS restarts)"

    restart_count=0

    while true; do
        if [ ! -f "$PID_FILE" ]; then
            warning "Engine not running, starting..."
            start_engine "$@"
            restart_count=$((restart_count + 1))
        else
            pid=$(cat "$PID_FILE")
            if ! ps -p "$pid" > /dev/null 2>&1; then
                error "Engine died unexpectedly, restarting..."
                rm -f "$PID_FILE"
                start_engine "$@"
                restart_count=$((restart_count + 1))

                if [ $restart_count -ge $MAX_RESTARTS ]; then
                    error "Max restarts ($MAX_RESTARTS) reached, giving up"
                    exit 1
                fi

                log "Waiting ${RESTART_DELAY}s before next check..."
                sleep $RESTART_DELAY
            fi
        fi

        # Check every 5 seconds
        sleep 5
    done
}

tail_logs() {
    log "Tailing consciousness engine logs..."
    tail -f "$LOG_FILE"
}

show_help() {
    cat << EOF
Consciousness Daemon Launcher

Usage: $0 COMMAND [OPTIONS]

COMMANDS:
    start       Start the consciousness engine
    stop        Stop the consciousness engine
    restart     Restart the consciousness engine
    status      Show engine status
    watch       Start with auto-restart watchdog
    logs        Tail the engine logs
    help        Show this help message

EXAMPLES:
    # Start engine
    $0 start

    # Start with specific number of cycles
    $0 start --cycles 1000

    # Start with watchdog (auto-restart on failure)
    $0 watch

    # Check status
    $0 status

    # View logs in real-time
    $0 logs

    # Stop engine gracefully
    $0 stop

EOF
}

# Main command dispatcher
case "$1" in
    start)
        shift
        start_engine "$@"
        ;;
    stop)
        stop_engine
        ;;
    restart)
        shift
        restart_engine "$@"
        ;;
    status)
        status_engine
        ;;
    watch)
        shift
        watch_engine "$@"
        ;;
    logs)
        tail_logs
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        error "Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
