#!/bin/bash
# LORD Dashboard Docker Deployment Script
# Part of the Complete LORD Integration Guide

set -e

echo "🚀 Starting LORD Dashboard Deployment..."

# Configuration
export LORD_PORT=${LORD_PORT:-3000}
export LORD_HOST=${LORD_HOST:-0.0.0.0}
export WEBSOCKET_PORT=${WEBSOCKET_PORT:-3001}

# Check Docker installation
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Build Docker image
echo "📦 Building LORD Dashboard image..."
docker build -t lord-dashboard:latest -f - . <<'EOF'
FROM node:18-alpine

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci --only=production

# Copy application files
COPY . .

# Build assets
RUN npm run build

EXPOSE 3000 3001

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD node healthcheck.js || exit 1

CMD ["npm", "start"]
EOF

# Create docker-compose.yml
cat > docker-compose.yml <<'COMPOSE'
version: '3.8'

services:
  lord-dashboard:
    image: lord-dashboard:latest
    container_name: lord-dashboard
    ports:
      - "${LORD_PORT:-3000}:3000"
      - "${WEBSOCKET_PORT:-3001}:3001"
    environment:
      - NODE_ENV=production
      - PORT=3000
      - WEBSOCKET_PORT=3001
    volumes:
      - ./data:/app/data
      - ./config:/app/config
    restart: unless-stopped
    networks:
      - lord-network

  redis:
    image: redis:7-alpine
    container_name: lord-redis
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    restart: unless-stopped
    networks:
      - lord-network

networks:
  lord-network:
    driver: bridge

volumes:
  redis-data:
COMPOSE

# Start services
echo "🎬 Starting LORD Dashboard services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 5

# Check service health
if curl -f http://localhost:${LORD_PORT}/health > /dev/null 2>&1; then
    echo "✅ LORD Dashboard is running!"
    echo ""
    echo "📊 Dashboard URL: http://localhost:${LORD_PORT}"
    echo "🔌 WebSocket URL: ws://localhost:${WEBSOCKET_PORT}"
    echo ""
    echo "📝 View logs: docker-compose logs -f"
    echo "🛑 Stop services: docker-compose down"
else
    echo "⚠️  Services started but health check failed. Check logs with:"
    echo "   docker-compose logs"
fi
