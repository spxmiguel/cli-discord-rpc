"""
CLI Discord Rich Presence Watcher
Detecta Claude, Codex e Antigravity CLI e exibe status no Discord.
"""

import time
import sys
import os

try:
    import psutil
except ImportError:
    print("Erro: psutil não instalado. Execute: pip install -r requirements.txt")
    sys.exit(1)

try:
    from pypresence import Presence
except ImportError:
    print("Erro: pypresence não instalado. Execute: pip install -r requirements.txt")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Configure o CLIENT_ID com o ID do seu app no Discord Developer Portal:
# https://discord.com/developers/applications
# ---------------------------------------------------------------------------
CLIENT_ID = os.environ.get("DISCORD_CLIENT_ID", "YOUR_CLIENT_ID_HERE")

# Nomes de processo a monitorar (sem extensão)
WATCHED_PROCESS_NAMES = {
    "claude", "claude-cli", "claude-code",
    "codex", "codex-cli",
    "antigravity", "antigravity-cli",
}

# Palavras-chave na linha de comando (para CLIs rodando via node/python)
WATCHED_CMD_KEYWORDS = {
    "claude", "codex", "antigravity",
}

# Mapeamento de nome detectado → label amigável
LABEL_MAP = {
    "claude":       ("Claude Code", "claude"),
    "claude-cli":   ("Claude Code", "claude"),
    "claude-code":  ("Claude Code", "claude"),
    "codex":        ("OpenAI Codex", "codex"),
    "codex-cli":    ("OpenAI Codex", "codex"),
    "antigravity":  ("Antigravity", "antigravity"),
    "antigravity-cli": ("Antigravity", "antigravity"),
}

POLL_INTERVAL = 5  # segundos entre verificações


def detect_active_cli():
    """Retorna (tool_name, label) se algum CLI monitorado estiver rodando, ou (None, None)."""
    for proc in psutil.process_iter(["name", "cmdline"]):
        try:
            name = (proc.info["name"] or "").lower().removesuffix(".exe")
            cmdline = " ".join(proc.info["cmdline"] or []).lower()

            if name in WATCHED_PROCESS_NAMES:
                label = LABEL_MAP.get(name, (name, "code"))
                return name, label

            for keyword in WATCHED_CMD_KEYWORDS:
                if keyword in cmdline:
                    label = LABEL_MAP.get(keyword, (keyword, "code"))
                    return keyword, label

        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    return None, None


def main():
    if CLIENT_ID == "YOUR_CLIENT_ID_HERE":
        print(
            "⚠  Defina seu CLIENT_ID!\n"
            "   Edite watcher.py ou exporte: DISCORD_CLIENT_ID=<id>\n"
            "   Crie um app em: https://discord.com/developers/applications\n"
        )
        sys.exit(1)

    print("🎮 CLI Discord RPC — iniciando...")
    rpc = Presence(CLIENT_ID)

    try:
        rpc.connect()
        print("✓ Conectado ao Discord.")
    except Exception as e:
        print(f"✗ Não foi possível conectar ao Discord: {e}")
        print("  Verifique se o Discord está aberto.")
        sys.exit(1)

    active = False
    start_time = None

    print(f"👀 Monitorando: {', '.join(sorted(WATCHED_PROCESS_NAMES))}")
    print("   Pressione Ctrl+C para encerrar.\n")

    try:
        while True:
            tool_name, label_tuple = detect_active_cli()
            if label_tuple:
                friendly, img_key = label_tuple
            else:
                friendly, img_key = None, None

            if tool_name and not active:
                start_time = int(time.time())
                rpc.update(
                    details="Codando",
                    state=f"Usando {friendly}",
                    start=start_time,
                    large_image="https://i.imgur.com/wSTFkRM.png",
                    large_text=friendly,
                    small_image="https://i.imgur.com/wSTFkRM.png",
                    small_text="CLI ativa",
                )
                active = True
                print(f"[{_now()}] ▶ Rich Presence ativado — {friendly}")

            elif not tool_name and active:
                rpc.clear()
                active = False
                start_time = None
                print(f"[{_now()}] ■ Rich Presence desativado")

            time.sleep(POLL_INTERVAL)

    except KeyboardInterrupt:
        print("\nEncerrando...")
    finally:
        if active:
            rpc.clear()
        rpc.close()


def _now():
    from datetime import datetime
    return datetime.now().strftime("%H:%M:%S")


if __name__ == "__main__":
    main()
