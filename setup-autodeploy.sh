#!/bin/bash
set -e

echo "=== WatchScanner — Setup Auto-Deploy ==="

# Installa git se mancante
if ! command -v git &>/dev/null; then
  echo "[1/4] Installazione git..."
  apt-get update -qq && apt-get install -y -qq git
fi

# Inizializza git in /opt/watch-scanner
echo "[2/4] Inizializzazione repository..."
cd /opt/watch-scanner
if [ ! -d ".git" ]; then
  git init
  git remote add origin https://github.com/lcz79/watch-scanner.git
fi
git fetch origin main
git reset --hard origin/main
echo "     Codice aggiornato all'ultimo commit."

# Crea lo script di deploy
echo "[3/4] Creazione script di deploy..."
cat > /opt/deploy-watchscanner.sh << 'DEPLOY'
#!/bin/bash
cd /opt/watch-scanner
git fetch origin main --quiet
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main)
if [ "$LOCAL" != "$REMOTE" ]; then
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] Nuovo commit rilevato — deploy in corso..."
  git reset --hard origin/main
  docker compose up -d --build
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] Deploy completato!"
else
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] Nessun aggiornamento."
fi
DEPLOY
chmod +x /opt/deploy-watchscanner.sh

# Aggiunge cron job ogni 5 minuti
echo "[4/4] Configurazione cron job (ogni 5 minuti)..."
(crontab -l 2>/dev/null | grep -v deploy-watchscanner; \
 echo "*/5 * * * * /opt/deploy-watchscanner.sh >> /var/log/watchscanner-deploy.log 2>&1") | crontab -

echo ""
echo "=== Setup completato! ==="
echo "  Il server controllerà GitHub ogni 5 minuti."
echo "  Log deploy: tail -f /var/log/watchscanner-deploy.log"
