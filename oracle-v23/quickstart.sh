#!/bin/bash
# Oracle v2.3 Quick Start Script

echo "╔════════════════════════════════════════════╗"
echo "║   Oracle v2.3 Deployment System           ║"
echo "║   Quick Start Launcher                    ║"
echo "╚════════════════════════════════════════════╝"
echo ""

# Check for required tools
command -v python3 >/dev/null 2>&1 || { 
    echo "❌ Python 3 not found. Please install Python 3.7+"; exit 1; 
}

echo "✓ Python 3 detected"
echo ""
echo "Choose deployment method:"
echo "  [1] Direct Browser (default)"
echo "  [2] Python HTTP Server"
echo "  [3] Docker Container"
echo ""
read -p "Selection [1-3]: " choice

case $choice in
    1|"")
        echo ""
        echo "Opening in browser..."
        if command -v xdg-open >/dev/null; then
            xdg-open index.html
        elif command -v open >/dev/null; then
            open index.html
        elif command -v start >/dev/null; then
            start index.html
        else
            echo "Please manually open: index.html"
        fi
        ;;
    2)
        echo ""
        echo "Starting Python server..."
        python3 server.py
        ;;
    3)
        if ! command -v docker >/dev/null; then
            echo "❌ Docker not found. Please install Docker first."
            exit 1
        fi
        echo ""
        echo "Building and starting Docker container..."
        docker-compose up -d
        echo ""
        echo "✓ Container started"
        echo "→ Visit: http://localhost:8080"
        echo ""
        echo "To view logs: docker-compose logs -f"
        echo "To stop: docker-compose down"
        ;;
    *)
        echo "Invalid selection"
        exit 1
        ;;
esac
