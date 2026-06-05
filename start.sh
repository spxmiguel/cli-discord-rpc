#!/usr/bin/env bash
# Inicia em background sem terminal
python3 watcher.py &
disown
echo "CLI Watcher iniciado em background. Procure o ícone no tray."
