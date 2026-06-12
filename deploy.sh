#!/bin/bash
# ================================================================
# WorkSphere HR - EC2 Deploy Script
# Run as: chmod +x deploy.sh && ./deploy.sh
# ================================================================
set -e

echo "========================================"
echo "  WorkSphere HR - EC2 Deployment"
echo "========================================"

# 1. Check Docker is installed
if ! command -v docker &> /dev/null; then
    echo "[ERROR] Docker not found. Install with:"
    echo "  sudo apt-get update && sudo apt-get install -y docker.io docker-compose-plugin"
    exit 1
fi

# 2. Check .env exists
if [ ! -f .env ]; then
    echo "[ERROR] .env file not found. Copy .env.example to .env and edit it."
    exit 1
fi

# 3. Stop any running containers
echo "[1/5] Stopping existing containers..."
docker compose down --remove-orphans 2>/dev/null || true

# 4. Pull/build images
echo "[2/5] Building images (this takes 2-4 minutes first time)..."
docker compose build --no-cache

# 5. Start everything
echo "[3/5] Starting all services..."
docker compose up -d

# 6. Wait for Django to be healthy
echo "[4/5] Waiting for Django to be ready (up to 120s)..."
for i in $(seq 1 24); do
    if docker exec worksphere_django curl -sf http://localhost:8000/health/ > /dev/null 2>&1; then
        echo "  Django is up!"
        break
    fi
    echo "  Waiting... ($((i*5))s)"
    sleep 5
done

# 7. Show status
echo "[5/5] Service status:"
docker compose ps

EC2_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo "YOUR_EC2_IP")

echo ""
echo "========================================"
echo "  WorkSphere HR is LIVE!"
echo "========================================"
echo "  App:    http://$EC2_IP"
echo "  App:    http://$EC2_IP:8000"
echo "  Admin:  http://$EC2_IP/admin/"
echo "  API:    http://$EC2_IP/api/docs/"
echo "  Flower: http://$EC2_IP:5555  (admin / flower123)"
echo ""
echo "  Demo login: admin / admin123"
echo "========================================"
