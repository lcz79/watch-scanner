#!/bin/bash
# Avvia WatchScanner backend — uccide eventuali processi precedenti prima di partire

cd "$(dirname "$0")"

# Libera la porta 8000 se occupata
PID=$(lsof -ti :8000)
if [ -n "$PID" ]; then
    echo "Uccido processo precedente su porta 8000 (PID $PID)..."
    kill -9 $PID 2>/dev/null
    sleep 1
fi

# Attiva venv se presente
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

echo "Avvio WatchScanner API su http://localhost:8000 ..."
exec uvicorn main:app --host 0.0.0.0 --port 8000
