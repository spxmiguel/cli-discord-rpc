# 🎮 CLI Discord Rich Presence

Exibe automaticamente no seu Discord quando você está usando **Claude CLI**, **Codex CLI** ou **Antigravity CLI** — mostrando **"Codando"** como status.

Funciona em **Windows** e **Mac**.

---

## Como fica no Discord

```
🟢 Codando
   Usando Claude Code
   há 42 minutos
```

---

## Pré-requisitos

- **Python 3.8+** — [python.org](https://python.org)
- **Discord** aberto no computador (app desktop, não browser)
- Uma aplicação no Discord Developer Portal (veja abaixo)

---

## 1. Criar o App no Discord Developer Portal

1. Acesse [discord.com/developers/applications](https://discord.com/developers/applications)
2. Clique em **New Application** e dê um nome (ex: `CLI Watcher`)
3. Na sidebar, vá em **OAuth2** e copie o **Client ID**
4. *(Opcional)* Em **Rich Presence → Art Assets**, faça upload de imagens customizadas

---

## 2. Instalar

### Windows

```bat
setup.bat
```

### Mac / Linux

```bash
chmod +x setup.sh && ./setup.sh
```

Ou manualmente:

```bash
pip install -r requirements.txt
```

---

## 3. Configurar o Client ID

Edite o `watcher.py` e substitua `YOUR_CLIENT_ID_HERE` pelo ID copiado:

```python
CLIENT_ID = "123456789012345678"
```

Ou use variável de ambiente (não precisa editar o arquivo):

```bash
# Mac/Linux
export DISCORD_CLIENT_ID=123456789012345678

# Windows (PowerShell)
$env:DISCORD_CLIENT_ID = "123456789012345678"
```

---

## 4. Executar

### Windows

```bat
start.bat
```

Ou:

```powershell
python watcher.py
```

### Mac / Linux

```bash
./start.sh
```

Ou:

```bash
python3 watcher.py
```

---

## CLIs monitoradas

| CLI | Processo detectado |
|-----|-------------------|
| Claude Code / Claude CLI | `claude`, `claude-cli`, `claude-code` |
| OpenAI Codex | `codex`, `codex-cli` |
| Antigravity | `antigravity`, `antigravity-cli` |

Para adicionar mais ferramentas, edite `WATCHED_PROCESS_NAMES` e `WATCHED_CMD_KEYWORDS` no `watcher.py`.

---

## Executar automaticamente na inicialização

### Windows — Agendador de Tarefas

1. Win + R → `taskschd.msc`
2. Criar Tarefa Básica
3. Gatilho: **Ao fazer logon**
4. Ação: `python C:\caminho\para\watcher.py`

### Mac — LaunchAgent

Crie `~/Library/LaunchAgents/com.clirpc.watcher.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.clirpc.watcher</string>
  <key>ProgramArguments</key>
  <array>
    <string>/usr/bin/python3</string>
    <string>/Users/SEU_USUARIO/cli-discord-rpc/watcher.py</string>
  </array>
  <key>RunAtLoad</key>
  <true/>
  <key>EnvironmentVariables</key>
  <dict>
    <key>DISCORD_CLIENT_ID</key>
    <string>123456789012345678</string>
  </dict>
</dict>
</plist>
```

```bash
launchctl load ~/Library/LaunchAgents/com.clirpc.watcher.plist
```

---

## Problemas comuns

| Problema | Solução |
|----------|---------|
| `Não foi possível conectar ao Discord` | Abra o Discord desktop (não o browser) |
| `YOUR_CLIENT_ID_HERE` | Configure o CLIENT_ID (passo 3) |
| Processo não detectado | Adicione o nome do processo em `WATCHED_PROCESS_NAMES` |

---

## Licença

MIT
