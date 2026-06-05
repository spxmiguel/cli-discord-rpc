"""
CLI Discord Rich Presence Watcher
Roda em background com ícone no system tray (Windows e Mac).
Clique direito no tray → Ativar/Desativar, Sair.
"""

import time
import sys
import os
import random
import threading
import platform
import winreg
from datetime import datetime

try:
    import psutil
except ImportError:
    print("Erro: pip install -r requirements.txt")
    sys.exit(1)

try:
    from pypresence import Presence
except ImportError:
    print("Erro: pip install -r requirements.txt")
    sys.exit(1)

try:
    import pystray
    from PIL import Image, ImageDraw
except ImportError:
    print("Erro: pip install -r requirements.txt")
    sys.exit(1)

# ---------------------------------------------------------------------------
CLIENT_ID = os.environ.get("DISCORD_CLIENT_ID", "1512275140661088417")
# ---------------------------------------------------------------------------

WATCHED = {
    # AI CLIs
    "claude":           ("Claude Code",      "claude"),
    "claude-cli":       ("Claude Code",      "claude"),
    "claude-code":      ("Claude Code",      "claude"),
    "codex":            ("OpenAI Codex",     "codex"),
    "codex-cli":        ("OpenAI Codex",     "codex"),
    "antigravity":      ("Antigravity",      "antigravity"),
    "antigravity-cli":  ("Antigravity",      "antigravity"),
    # Editores
    "code":             ("VS Code",          "vscode"),
    "cursor":           ("Cursor",           "cursor"),
    "windsurf":         ("Windsurf",         "windsurf"),
    "zed":              ("Zed",              "zed"),
    "webstorm":         ("WebStorm",         "jetbrains"),
    "pycharm":          ("PyCharm",          "jetbrains"),
    "idea":             ("IntelliJ IDEA",    "jetbrains"),
    "clion":            ("CLion",            "jetbrains"),
    "goland":           ("GoLand",           "jetbrains"),
    "rider":            ("Rider",            "jetbrains"),
    "fleet":            ("Fleet",            "jetbrains"),
    "sublime_text":     ("Sublime Text",     "sublime"),
    "subl":             ("Sublime Text",     "sublime"),
    "vim":              ("Vim",              "vim"),
    "nvim":             ("Neovim",           "vim"),
    "emacs":            ("Emacs",            "emacs"),
    "atom":             ("Atom",             "atom"),
    # Terminais
    "wt":               ("Windows Terminal", "terminal"),
    "alacritty":        ("Alacritty",        "terminal"),
    "warp":             ("Warp",             "terminal"),
    "iterm2":           ("iTerm2",           "terminal"),
    "kitty":            ("Kitty",            "terminal"),
    # Ferramentas
    "docker":           ("Docker",           "docker"),
    "postman":          ("Postman",          "postman"),
    "insomnia":         ("Insomnia",         "postman"),
    "tableplus":        ("TablePlus",        "database"),
    "dbeaver":          ("DBeaver",          "database"),
    "figma":            ("Figma",            "figma"),
}

CMD_KEYWORDS = {"claude", "codex", "antigravity"}

FUNNY_DETAILS = [
    "Mandando o GPT pra terapia",
    "Deixando a IA fazer o trabalho",
    "Debugando com o poder do panico",
    "Fazendo a IA sofrer por mim",
    "Escrevendo codigo que nem eu entendo",
    "Pedindo pro Claude me salvar",
    "Compilando... (mentira, eh Python)",
    "Vibe coding intenso",
    "Ctrl+C Ctrl+V com estilo",
    "Stack Overflow? Nunca ouvi falar",
    "Produtivo (pelo menos eh o que parece)",
    "Fazendo o Claude fazer o dever de casa",
    "Commit message: 'fix'",
    "Mais um dia salvando o mundo com if/else",
    "git commit -m 'arrumei tudo (mentira)'",
    "Cafe na veia, bug na tela",
    "Indo pra producao na forca bruta",
    "A documentacao? Inventei ela",
    "Testes? Minha fe eh meu teste",
    "Funcionou na minha maquina",
    "O prazo era ontem mas o codigo eh hoje",
    "Deixa eu perguntar pro robozinho...",
    "O codigo ta horrivel mas funciona",
    "Sem bugs (por enquanto)",
    "Quebrando prod em desenvolvimento",
    "Fingindo que entende o output",
    "Juntando tokens desde as 9h",
    "Desenvolvedor por fora, usuario de IA por dentro",
    "Trabalhando duro (ou ficando duro de trabalhar)",
    "Nao eh gambiarra, eh solucao criativa",
]

FUNNY_STATES = {
    "claude":     ["com Claude no co-piloto", "deixando o Claude pensar", "confiando cegamente no Claude", "Claude disse q funciona, ok"],
    "codex":      ["com Codex no volante", "o Codex escreve, eu aprovo", "deixando o Codex codar"],
    "antigravity":["desafiando a fisica", "com Antigravity no comando", "gravidade: opcional"],
    "vscode":     ["no VS Code", "com 47 extensoes instaladas", "cheio de abas abertas", "terminal integrado aberto"],
    "cursor":     ["no Cursor", "deixando o Cursor completar", "autocomplete com esteroides"],
    "windsurf":   ["no Windsurf", "surfando no codigo"],
    "vim":        ["no Vim (sem saber sair)", "preso no Vim desde 2019", "modo: confuso"],
    "jetbrains":  ["com RAM sofrendo", "indexando desde segunda-feira", "numa IDE da JetBrains"],
    "sublime":    ["no Sublime Text", "editor leve na velocidade da luz"],
    "terminal":   ["no terminal parecendo hacker", "digitando comandos aleatorios", "ls -la em loop"],
    "docker":     ["construindo containers", "docker-compose up --pray", "reiniciando o Docker de novo"],
    "postman":    ["testando APIs", "mandando requests no escuro", "esperando o 200 OK"],
    "figma":      ["no Figma fingindo ser designer", "arrastando retangulos", "pixel perfect (quase)"],
    "database":   ["mexendo no banco de dados", "DELETE sem WHERE (quase)", "SELECT * FROM problemas"],
    "emacs":      ["no Emacs (sistema operacional disfarcado)", "configurando o Emacs ha 3 horas"],
    "zed":        ["no Zed", "editor rapido pra dev lento"],
    "atom":       ["no Atom (descanse em paz)", "usando o Atom em 2025, respeito"],
}

ROTATE_INTERVAL = 30
POLL_INTERVAL   = 5


# ---------------------------------------------------------------------------
# Estado global
# ---------------------------------------------------------------------------
state = {
    "enabled":     True,
    "rpc":         None,
    "active":      False,
    "start_time":  None,
    "last_rotate": 0,
    "cur_details": "",
    "cur_key":     None,
    "tray":        None,
}


def detect_active():
    for proc in psutil.process_iter(["name", "cmdline"]):
        try:
            raw     = (proc.info["name"] or "").lower().removesuffix(".exe")
            cmdline = " ".join(proc.info["cmdline"] or []).lower()
            if raw in WATCHED:
                friendly, key = WATCHED[raw]
                return raw, friendly, key
            for kw in CMD_KEYWORDS:
                if kw in cmdline:
                    entry = WATCHED.get(kw)
                    if entry:
                        return kw, entry[0], entry[1]
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return None, None, None


def _update_rpc(details, key, friendly, start):
    states = FUNNY_STATES.get(key, [f"usando {friendly}"])
    try:
        state["rpc"].update(
            details    = details,
            state      = random.choice(states),
            start      = start,
            large_image= "codando",
            large_text = friendly,
        )
    except Exception:
        pass


def watcher_loop():
    rpc = Presence(CLIENT_ID)
    try:
        rpc.connect()
        state["rpc"] = rpc
        log("Conectado ao Discord.")
    except Exception as e:
        log(f"Nao conectou ao Discord: {e}")
        return

    state["cur_details"] = random.choice(FUNNY_DETAILS)

    while True:
        time.sleep(POLL_INTERVAL)

        if not state["enabled"]:
            if state["active"]:
                try:
                    rpc.clear()
                except Exception:
                    pass
                state["active"] = False
                log("RPC pausado (desativado pelo tray)")
            _update_tray_title()
            continue

        proc_name, friendly, key = detect_active()
        now = time.time()

        if proc_name and not state["active"]:
            state["start_time"]  = int(now)
            state["last_rotate"] = now
            state["cur_details"] = random.choice(FUNNY_DETAILS)
            state["cur_key"]     = key
            _update_rpc(state["cur_details"], key, friendly, state["start_time"])
            state["active"] = True
            log(f"ON  {friendly} | {state['cur_details']}")

        elif proc_name and state["active"] and (now - state["last_rotate"]) >= ROTATE_INTERVAL:
            state["cur_details"] = random.choice(FUNNY_DETAILS)
            state["last_rotate"] = now
            _update_rpc(state["cur_details"], state["cur_key"], friendly, state["start_time"])
            log(f"--> {state['cur_details']}")

        elif not proc_name and state["active"]:
            try:
                rpc.clear()
            except Exception:
                pass
            state["active"] = False
            log("OFF")

        _update_tray_title()


def _update_tray_title():
    if state["tray"] is None:
        return
    status = "ON" if (state["enabled"] and state["active"]) else ("pausado" if not state["enabled"] else "aguardando")
    state["tray"].title = f"Codando — {status}"


def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


# ---------------------------------------------------------------------------
# Tray
# ---------------------------------------------------------------------------

def make_icon():
    """Gera um ícone simples (círculo colorido) sem arquivo externo."""
    size = 64
    img  = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse([4, 4, size - 4, size - 4], fill="#5865F2")  # roxo Discord
    draw.ellipse([20, 20, size - 20, size - 20], fill="white")
    return img


def tray_toggle(icon, item):
    state["enabled"] = not state["enabled"]
    status = "ativado" if state["enabled"] else "desativado"
    log(f"Rich Presence {status} pelo tray")
    _update_tray_title()
    icon.update_menu()


def tray_quit(icon, item):
    log("Saindo...")
    if state["active"] and state["rpc"]:
        try:
            state["rpc"].clear()
            state["rpc"].close()
        except Exception:
            pass
    icon.stop()
    os._exit(0)


def toggle_label(item):
    return "Desativar" if state["enabled"] else "Ativar"


def main():
    # Inicia o watcher em thread separada
    t = threading.Thread(target=watcher_loop, daemon=True)
    t.start()

    # Cria o ícone do tray
    icon_img = make_icon()
    menu = pystray.Menu(
        pystray.MenuItem(toggle_label, tray_toggle, default=True),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem(autostart_label, tray_autostart_toggle),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Sair", tray_quit),
    )
    tray = pystray.Icon("Codando", icon_img, "Codando — iniciando...", menu)
    state["tray"] = tray

    log("Iniciando no system tray... (clique direito no ícone para controlar)")
    tray.run()  # bloqueia até sair


def set_autostart(enable=True):
    """Adiciona/remove do registro de inicialização do Windows."""
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    app_name = "CLIWatcher"
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
        if enable:
            exe_path = sys.executable if getattr(sys, "frozen", False) else f'"{sys.executable}" "{os.path.abspath(__file__)}"'
            winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, exe_path)
        else:
            try:
                winreg.DeleteValue(key, app_name)
            except FileNotFoundError:
                pass
        winreg.CloseKey(key)
    except Exception as e:
        log(f"autostart: {e}")


def tray_autostart_toggle(icon, item):
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path)
        winreg.QueryValueEx(key, "CLIWatcher")
        winreg.CloseKey(key)
        currently_on = True
    except FileNotFoundError:
        currently_on = False
    set_autostart(not currently_on)
    status = "ativado" if not currently_on else "desativado"
    log(f"Iniciar com Windows: {status}")
    icon.update_menu()


def autostart_label(item):
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path)
        winreg.QueryValueEx(key, "CLIWatcher")
        winreg.CloseKey(key)
        return "Iniciar com Windows: ON"
    except FileNotFoundError:
        return "Iniciar com Windows: OFF"


if __name__ == "__main__":
    # Na primeira vez que roda como .exe, já ativa o autostart
    if getattr(sys, "frozen", False):
        set_autostart(True)
    main()
