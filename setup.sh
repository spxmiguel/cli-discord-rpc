#!/usr/bin/env bash
set -e

echo "=== CLI Discord RPC - Setup (Mac/Linux) ==="

if ! command -v python3 &>/dev/null; then
    echo "ERRO: python3 não encontrado. Instale via Homebrew: brew install python"
    exit 1
fi

echo "Instalando dependências..."
python3 -m pip install --user -r requirements.txt

echo ""
echo "Pronto! Agora edite o watcher.py e defina seu CLIENT_ID."
echo "Depois execute: python3 watcher.py"
