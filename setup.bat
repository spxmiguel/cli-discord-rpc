@echo off
echo === CLI Discord RPC - Setup (Windows) ===

where python >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: Python nao encontrado. Instale em https://python.org
    pause
    exit /b 1
)

echo Instalando dependencias...
pip install -r requirements.txt

echo.
echo Pronto! Agora edite o watcher.py e defina seu CLIENT_ID.
echo Depois execute: python watcher.py
echo.
pause
