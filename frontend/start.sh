#!/bin/bash
# Avvia WatchScanner frontend — uccide processi Vite precedenti prima di partire

cd "$(dirname "$0")"

# Libera le porte 5173-5175
for PORT in 5173 5174 5175; do
    PID=$(lsof -ti :$PORT)
    if [ -n "$PID" ]; then
        echo "Uccido processo su porta $PORT (PID $PID)..."
        kill -9 $PID 2>/dev/null
    fi
done

# Uccidi anche per nome
pkill -9 -f "vite" 2>/dev/null
sleep 1

echo "Avvio WatchScanner Frontend su http://localhost:5173 ..."
exec npm run dev
