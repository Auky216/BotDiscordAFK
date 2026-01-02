# 🤖 Bot Discord AFK 24/7

Bot de Discord que se mantiene conectado permanentemente a un canal de voz, rastrea el tiempo que los usuarios pasan en voz y responde con IA usando Groq.

## ✨ Características

### 🎙️ Conexión Persistente 24/7
- Se conecta automáticamente a un canal de voz específico
- Reconexión automática cada 30 segundos si se desconecta
- Reproduce audio silencioso cada 25 minutos para evitar desconexiones por inactividad
- Detecta si es movido o expulsado y se reconecta automáticamente

### ⏱️ Rastreo de Tiempo en Voz
- Registra cuánto tiempo cada usuario pasa en canales de voz
- Muestra estadísticas con horas y minutos acumulados
- Datos persistentes guardados en JSON (no se pierden al reiniciar)
- Autoguardado cada 5 minutos
- Indica usuarios actualmente conectados con 🟢

### 🤖 Chat con IA (Groq)
- Responde mensajes usando Llama 3.3 70B
- Estilo conversacional de barrio/urbano
- Respuestas naturales y casuales

### 📊 Monitoreo y Estado
- Comandos para verificar estado del bot
- Logs detallados de conexiones/desconexiones
- Estadísticas de uptime y latencia

## 📋 Requisitos

- Python 3.10+
- Cuenta de Discord Developer
- API Key de Groq (gratuita en [console.groq.com](https://console.groq.com))
- Docker (opcional, para deployment)

## 🚀 Instalación

### Opción 1: Local

```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/discord-bot-afk.git
cd discord-bot-afk

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus tokens

# Ejecutar bot
python app.py
```

### Opción 2: Docker

```bash
# Construir y ejecutar
docker-compose up -d

# Ver logs
docker-compose logs -f

# Detener
docker-compose down
```

## ⚙️ Configuración

Crea un archivo `.env` con:

```env
DISCORD_TOKEN=tu_token_de_discord
GUILD_ID=id_de_tu_servidor
VOICE_CHANNEL_ID=id_del_canal_de_voz
TEXT_CHANNEL_ID=id_del_canal_de_texto
GROQ_API_KEY=tu_api_key_de_groq
```

### Obtener IDs de Discord

1. Habilita el **Modo Desarrollador** en Discord:
   - Configuración → Avanzado → Modo Desarrollador ✅

2. **Guild ID**: Click derecho en el servidor → "Copiar ID"
3. **Channel IDs**: Click derecho en el canal → "Copiar ID"

### Obtener Token del Bot

1. Ve a [Discord Developer Portal](https://discord.com/developers/applications)
2. Crea una nueva aplicación o selecciona una existente
3. Ve a **Bot** → **Reset Token** → Copia el token
4. Habilita estos **Privileged Gateway Intents**:
   - ❌ Presence Intent (desactivado)
   - ❌ Server Members Intent (desactivado)
   - ✅ Message Content Intent (activado)

### Obtener Groq API Key

1. Regístrate en [console.groq.com](https://console.groq.com)
2. Ve a API Keys
3. Crea una nueva API key
4. Cópiala a tu `.env`

## 📝 Comandos

### Estado del Bot
- `!status` - Muestra estado completo del bot (conexión, uptime, latencia)
- `!health` - Verificación rápida de salud
- `!join` - Reconectar manualmente al canal de voz
- `!leave` - Desconectar del canal de voz

### Tiempo en Voz
- `!voicetime` o `!vt` - Muestra ranking de usuarios por tiempo en voz
- `!resettime` - Resetea todos los datos de tiempo (cuidado!)
- `!savetime` - Guarda manualmente los datos

### IA / Chat
- `!yo [mensaje]` - Chatea con el bot usando IA de Groq
  - Ejemplo: `!yo que onda bro`
  - Responde con jerga urbana/de barrio

### Testing
- `!test_audio` - Reproduce audio silencioso de prueba (5 minutos)
- `!info` - Información técnica del bot

## 📊 Ejemplo de Uso

```
Usuario: !voicetime

Bot:
🎙️ Tiempo en 🔈Sala de chupapis

1. 🟢 Antonio
   34h 5m

2. 🟢 vainillita  
   12h 47m

3. ⚫ Milanes1n
   8h 23m

4. ⚫ TaRik Ver(JASR)
   5h 12m
```

```
Usuario: !yo que pasa carnal

Bot: Órale wey, aquí todo tranqui homie. ¿Qué onda contigo bro?
```

## 🐳 Deployment en AWS EC2

```bash
# Conectar a EC2
ssh -i tu-key.pem ec2-user@tu-ip-ec2

# Instalar Docker
sudo yum update -y
sudo yum install -y docker
sudo service docker start
sudo usermod -a -G docker ec2-user

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Subir archivos y ejecutar
docker-compose up -d
```

## 📁 Estructura del Proyecto

```
discord-bot-afk/
├── app.py                  # Código principal del bot
├── requirements.txt        # Dependencias Python
├── .env                    # Variables de entorno (no incluir en git)
├── .env.example           # Ejemplo de configuración
├── .gitignore             # Archivos a ignorar en git
├── Dockerfile             # Imagen Docker
├── docker-compose.yml     # Orquestación Docker
├── README.md              # Este archivo
└── data/
    └── voice_time_data.json  # Datos persistentes (generado automáticamente)
```

## 🔧 Tecnologías

- **discord.py** - Librería para interactuar con Discord API
- **Groq** - IA conversacional con Llama 3.3 70B
- **Docker** - Containerización
- **Python 3.10** - Lenguaje de programación

## 🛡️ Características de Seguridad

- ✅ Datos sensibles en `.env` (no en código)
- ✅ `.gitignore` configurado para proteger tokens
- ✅ Permisos mínimos necesarios en Discord
- ✅ Logs sin información sensible
- ✅ Validación de entradas en comandos

## 📈 Persistencia de Datos

Los datos de tiempo en voz se guardan en `voice_time_data.json`:

- **Autoguardado** cada 5 minutos
- **Guardado al salir/desconectar** usuarios
- **Carga automática** al iniciar el bot
- **Formato JSON** fácil de leer y editar

## 🐛 Troubleshooting

### Bot no se conecta
- Verifica que el token en `.env` sea correcto
- Confirma que los IDs de servidor y canal sean correctos
- Revisa que el bot tenga permisos de "Connect" y "Speak"

### Comando !yo no funciona
- Verifica que `GROQ_API_KEY` esté en `.env`
- Confirma que tengas créditos en tu cuenta de Groq
- Revisa los logs para ver errores específicos

### Datos de tiempo no se guardan
- Verifica que la carpeta `data/` exista
- Confirma permisos de escritura
- Revisa los logs para errores de guardado

## 📄 Licencia

MIT License - Siéntete libre de usar y modificar

## 👨‍💻 Autor

Creado para mantener presencia 24/7 en canales de Discord

## 🤝 Contribuciones

Las contribuciones son bienvenidas! Siéntete libre de abrir issues o pull requests.

## 📞 Soporte

Si tienes problemas:
1. Revisa la sección de Troubleshooting
2. Verifica los logs: `docker-compose logs -f`
3. Abre un issue en GitHub

---

⭐ Si te gusta este proyecto, dale una estrella en GitHub!