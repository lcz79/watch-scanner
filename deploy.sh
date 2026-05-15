#!/bin/bash
# deploy.sh — Deploya WatchScanner su DigitalOcean Droplet
# Uso: ./deploy.sh <IP_DROPLET>
# Es:  ./deploy.sh 167.99.123.45

set -e

DROPLET_IP="${1}"
REMOTE_DIR="/opt/watch-scanner"
SSH="ssh -o StrictHostKeyChecking=no root@${DROPLET_IP}"

if [ -z "$DROPLET_IP" ]; then
  echo "Uso: ./deploy.sh <IP_DROPLET>"
  exit 1
fi

echo "▶ Deploy su $DROPLET_IP..."

# 1. Setup server (idempotente — skip se già fatto)
$SSH << 'SETUP'
  # Installa Docker se non presente
  if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com | sh
    systemctl enable docker
  fi
  mkdir -p /opt/watch-scanner
SETUP

# 2. Copia il progetto (escludi venv, node_modules, dati locali)
echo "▶ Sincronizzazione file..."
rsync -az --delete \
  --exclude='backend/venv' \
  --exclude='backend/__pycache__' \
  --exclude='backend/data' \
  --exclude='frontend/node_modules' \
  --exclude='frontend/dist' \
  --exclude='.git' \
  ./ root@${DROPLET_IP}:${REMOTE_DIR}/

# 3. Copia auth Instagram (se esiste)
if [ -f "backend/data/ig_browser_auth.json" ]; then
  echo "▶ Copia sessione Instagram..."
  $SSH "mkdir -p /opt/watch-scanner-data"
  scp backend/data/ig_browser_auth.json root@${DROPLET_IP}:/opt/watch-scanner-data/
fi

# 4. Build e avvio
echo "▶ Build Docker e avvio..."
$SSH << REMOTE
  cd ${REMOTE_DIR}
  
  # Monta i dati persistenti nella directory corretta
  mkdir -p /opt/watch-scanner-data
  
  # Ricrea il volume Docker con i dati esistenti (se primo deploy)
  docker compose down --remove-orphans 2>/dev/null || true
  docker compose build --no-cache
  docker compose up -d
  
  echo "✅ Deploy completato!"
  docker compose ps
REMOTE

echo ""
echo "✅ WatchScanner online su http://${DROPLET_IP}"
echo "   Logs backend: ssh root@${DROPLET_IP} 'docker compose -f /opt/watch-scanner/docker-compose.yml logs -f backend'"
