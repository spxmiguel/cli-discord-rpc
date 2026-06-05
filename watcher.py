"""
CLI Discord Rich Presence Watcher
Detecta Claude, Codex e Antigravity CLI e exibe status divertido no Discord.
"""

import time
import sys
import os
import random

try:
    import psutil
except ImportError:
    print("Erro: psutil nao instalado. Execute: pip install -r requirements.txt")
    sys.exit(1)

try:
    from pypresence import Presence
except ImportError:
    print("Erro: pypresence nao instalado. Execute: pip install -r requirements.txt")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Cole aqui o Client ID do seu app do Discord Developer Portal
# ---------------------------------------------------------------------------
CLIENT_ID = os.environ.get("DISCORD_CLIENT_ID", "YOUR_CLIENT_ID_HERE")

# Mensagens de status que rotacionam a cada ciclo (details = linha de cima)
FUNNY_DETAILS = [
    "Mandando o GPT pra terapia",
    "Deixando a IA fazer o trabalho",
    "Debugando com o poder do panico",
    "Fazendo a IA sofrer por mim",
    "Escrevendo codigo que nem eu entendo",
    "Pedindo pro Claude me salvar",
    "Compilando... (mentira, eh Python)",
    "Vibe coding intenso",
    "Promovendo a preguica intelectual",
    "Conversando com robos desde cedo",
    "Ctrl+C Ctrl+V com estilo",
    "Stack Overflow? Nunca ouvi falar",
    "Produtivo (pelo menos eh o que parece)",
    "Fazendo o Claude fazer o dever de casa",
    "Algoritmo? Deixa o modelo resolver",
    "Fingindo que entende o output",
    "Juntando tokens desde as 9h",
    "Sem bugs (por enquanto)",
    "Quebrando prod em desenvolvimento",
    "Desenvolvedor por fora, usuário de IA por dentro",
]

# Frases de estado (state = linha de baixo)
FUNNY_STATES = {
    "claude":      [
        "com Claude como co-piloto",
        "deixando o Claude pensar",
        "confiando cegamente no Claude",
        "Claude disse que funciona, ta bom",
    ],
    "codex":       [
        "com Codex no volante",
        "deixando o Codex codar",
        "o Codex escreve, eu aprovo",
    ],
    "antigravity": [
        "desafiando a fisica",
        "com Antigravity no comando",
        "gravidade opcional",
    ],
}

WATCHED_PROCESS_NAMES = {
    "claude", "claude-cli", "claude-code",
    "codex", "codex-cli",
    "antigravity", "antigravity-cli",
}

WATCHED_CMD_KEYWORDS = {
    "claude", "codex", "antigravity",
}

LABEL_MAP = {
    "claude":          ("Claude Code",   "claude"),
    "claude-cli":      ("Claude Code",   "claude"),
    "claude-code":     ("Claude Code",   "claude"),
    "codex":           ("OpenAI Codex",  "codex"),
    "codex-cli":       ("OpenAI Codex",  "codex"),
    "antigravity":     ("Antigravity",   "antigravity"),
    "antigravity-cli": ("Antigravity",   "antigravity"),
}

# Troca a mensagem de details a cada N segundos
ROTATE_INTERVAL = 30
POLL_INTERVAL   = 5


def detect_active_cli():
    for proc in psutil.process_iter(["name", "cmdline"]):
        try:
            name    = (proc.info["name"] or "").lower().removesuffix(".exe")
            cmdline = " ".join(proc.info["cmdline"] or []).lower()

            if name in WATCHED_PROCESS_NAMES:
                return name, LABEL_MAP.get(name, (name, "code"))

            for keyword in WATCHED_CMD_KEYWORDS:
                if keyword in cmdline:
                    return keyword, LABEL_MAP.get(keyword, (keyword, "code"))

        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    return None, None


def pick_state(tool_key):
    pool = FUNNY_STATES.get(tool_key, [f"usando {tool_key}"])
    return random.choice(pool)


def main():
    if CLIENT_ID == "YOUR_CLIENT_ID_HERE":
        print(
            "Cole seu CLIENT_ID no watcher.py (linha 16)\n"
            "ou exporte: DISCORD_CLIENT_ID=<id>\n"
            "Crie o app em: https://discord.com/developers/applications\n"
        )
        sys.exit(1)

    print("CLI Discord RPC - iniciando...")
    rpc = Presence(CLIENT_ID)

    try:
        rpc.connect()
        print("Conectado ao Discord.")
    except Exception as e:
        print(f"Nao foi possivel conectar ao Discord: {e}")
        print("  Verifique se o Discord esta aberto.")
        sys.exit(1)

    active          = False
    start_time      = None
    last_rotate     = 0
    current_details = random.choice(FUNNY_DETAILS)
    current_tool    = None

    print(f"Monitorando: {', '.join(sorted(WATCHED_PROCESS_NAMES))}")
    print("Pressione Ctrl+C para encerrar.\n")

    try:
        while True:
            tool_name, label_tuple = detect_active_cli()
            friendly  = label_tuple[0] if label_tuple else None
            tool_key  = tool_name or "claude"
            now       = time.time()

            should_rotate = (now - last_rotate) >= ROTATE_INTERVAL

            if tool_name and not active:
                start_time      = int(now)
                last_rotate     = now
                current_details = random.choice(FUNNY_DETAILS)
                current_tool    = tool_key
                rpc.update(
                    details   = current_details,
                    state     = pick_state(tool_key),
                    start     = start_time,
                    large_image = "https://i.imgur.com/wSTFkRM.png",
                    large_text  = friendly,
                )
                active = True
                print(f"[{_now()}] Ativo — {friendly} | {current_details}")

            elif tool_name and active and should_rotate:
                current_details = random.choice(FUNNY_DETAILS)
                last_rotate     = now
                rpc.update(
                    details   = current_details,
                    state     = pick_state(current_tool),
                    start     = start_time,
                    large_image = "https://i.imgur.com/wSTFkRM.png",
                    large_text  = friendly,
                )
                print(f"[{_now()}] Status: {current_details}")

            elif not tool_name and active:
                rpc.clear()
                active      = False
                start_time  = None
                current_tool = None
                print(f"[{_now()}] Desativado")

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
