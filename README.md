# Bot Discord AFK

Bot en Python que permanece en un canal de voz de Discord, registra tiempo de conexión y responde al comando `!yo` mediante Groq. Es un proyecto personal: revisa el código y las políticas de Discord antes de desplegarlo en un servidor.

## Requisitos

- Python 3.10 o superior, o Docker
- Una aplicación de Discord con token de bot y acceso al servidor
- Una clave de Groq para usar `!yo`

## Instalación local

```bash
git clone https://github.com/Auky216/BotDiscordAFK.git
cd BotDiscordAFK
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edita `.env` con tus identificadores y credenciales. Nunca publiques ese archivo. Activa el intent de contenido de mensajes en el portal de Discord si vas a usar comandos de texto.

```bash
python app.py
```

Los comandos implementados son `!status`, `!health`, `!join`, `!voicetime` (alias `!vt`) y `!yo <mensaje>`. El prefijo es `!`.

## Docker

```bash
mkdir -p data
docker build -t bot-discord-afk .
docker run --rm --env-file .env -v "$PWD/data:/app/data" bot-discord-afk
```

La imagen no contiene `.env`: Docker recibe las variables al iniciar el contenedor. El historial de tiempo se guarda en `data/voice_time_data.json` mediante `VOICE_TIME_FILE`.

## Configuración

Consulta [.env.example](.env.example) para los nombres de variables. `DISCORD_TOKEN` (o `BOT_TOKEN`), `GUILD_ID` y `VOICE_CHANNEL_ID` son necesarios para la conexión. `TEXT_CHANNEL_ID` determina el canal de texto de respaldo. `GROQ_API_KEY` habilita las respuestas de IA.

## Seguridad y contribuciones

No compartas tokens, archivos `.env` ni el historial de voz. Si detectas una vulnerabilidad, sigue [SECURITY.md](SECURITY.md). Se aceptan issues y PRs con una descripción reproducible.

## Licencia

Distribuido bajo la [licencia MIT](LICENSE).
