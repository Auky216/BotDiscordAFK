import discord
from discord.ext import commands, tasks
import asyncio
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import json
from groq import Groq

# Cargar variables de entorno
load_dotenv()

# ===== PERSISTENCIA DE DATOS =====
VOICE_TIME_FILE = 'voice_time_data.json'

def load_voice_time_data():
    """Carga los datos de tiempo de voz desde el archivo"""
    try:
        if os.path.exists(VOICE_TIME_FILE):
            with open(VOICE_TIME_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                converted = {}
                for user_id_str, info in data.items():
                    user_id = int(user_id_str)
                    converted[user_id] = {
                        'total_seconds': info.get('total_seconds', 0),
                        'join_time': None,
                        'name': info.get('name', 'Unknown')
                    }
                print(f"✓ Datos cargados: {len(converted)} usuarios")
                return converted
    except Exception as e:
        print(f"✗ Error cargando datos: {e}")
    return {}

def save_voice_time_data():
    """Guarda los datos de tiempo de voz en el archivo"""
    try:
        data_to_save = {}
        for user_id, info in user_voice_time.items():
            total = info['total_seconds']
            if info['join_time']:
                session_time = (datetime.now() - info['join_time']).total_seconds()
                total += session_time
            
            data_to_save[str(user_id)] = {
                'total_seconds': total,
                'name': info['name']
            }
        
        with open(VOICE_TIME_FILE, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, indent=2, ensure_ascii=False)
        print(f"✓ Datos guardados: {len(data_to_save)} usuarios")
    except Exception as e:
        print(f"✗ Error guardando datos: {e}")

# ===== CLASE DE AUDIO SILENCIOSO =====
class SilentAudioSource(discord.AudioSource):
    """Genera audio PCM silencioso de 20ms sin necesidad de FFmpeg"""
    
    def __init__(self, duration_minutes=30):
        self.frame_size = 3840
        self.total_frames = int((duration_minutes * 60) * 50)
        self.current_frame = 0
    
    def read(self):
        if self.current_frame >= self.total_frames:
            return b""
        self.current_frame += 1
        return b"\x00" * self.frame_size
    
    def is_opus(self):
        return False

# ===== CONFIGURACIÓN DEL BOT =====
intents = discord.Intents.default()
intents.voice_states = True
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents, case_insensitive=True)

# Configuración
GUILD_ID = int(os.getenv('GUILD_ID', '0'))
VOICE_CHANNEL_ID = int(os.getenv('VOICE_CHANNEL_ID', '0'))
TEXT_CHANNEL_ID = int(os.getenv('TEXT_CHANNEL_ID', '0'))

# Variables de estado
bot_stats = {
    'connected_at': None,
    'last_heartbeat': None,
    'heartbeat_count': 0,
    'silent_audio_plays': 0,
}

# Cliente Groq
groq_client = Groq(api_key=os.getenv('GROQ_API_KEY'))

# Cargar datos de tiempo de voz
user_voice_time = load_voice_time_data()

# ===== FUNCIONES AUXILIARES =====
def _get_text_channel(ctx=None):
    """Obtiene el canal de texto destino configurado"""
    if TEXT_CHANNEL_ID:
        channel = bot.get_channel(TEXT_CHANNEL_ID)
        if channel:
            return channel
    if ctx and ctx.guild and TEXT_CHANNEL_ID:
        fallback = ctx.guild.get_channel(TEXT_CHANNEL_ID)
        if fallback:
            return fallback
    return ctx.channel if ctx else None

async def send_home(ctx, content=None, embed=None):
    """Envía respuestas al canal configurado"""
    channel = _get_text_channel(ctx)
    if not channel:
        channel = ctx.channel
    await channel.send(content if content else None, embed=embed)

# ===== EVENTOS PRINCIPALES =====
@bot.event
async def on_ready():
    print(f'✓ Bot conectado como {bot.user}')
    print(f'✓ Latencia: {bot.latency * 1000:.2f}ms')
    
    if not check_connection.is_running():
        check_connection.start()
    if not play_silent_audio.is_running():
        play_silent_audio.start()
    if not auto_save_data.is_running():
        auto_save_data.start()
    
    await connect_to_voice()

async def connect_to_voice():
    """Conecta el bot al canal de voz especificado"""
    try:
        guild = bot.get_guild(GUILD_ID)
        if not guild:
            print(f"✗ Servidor {GUILD_ID} no encontrado")
            return
        
        voice_channel = guild.get_channel(VOICE_CHANNEL_ID)
        if not voice_channel:
            print(f"✗ Canal {VOICE_CHANNEL_ID} no encontrado")
            return
        
        if guild.voice_client and guild.voice_client.channel.id == VOICE_CHANNEL_ID:
            print(f"✓ Ya conectado a {voice_channel.name}")
            return
        
        if guild.voice_client:
            await guild.voice_client.disconnect()
        
        await voice_channel.connect()
        bot_stats['connected_at'] = datetime.now()
        print(f"✓ Conectado a {voice_channel.name}")
        
    except Exception as e:
        print(f"✗ Error al conectar: {e}")
        await asyncio.sleep(5)
        await connect_to_voice()

# ===== RASTREO DE TIEMPO EN VOZ =====
@bot.event
async def on_voice_state_update(member, before, after):
    """Detecta desconexión del bot y rastrea tiempo de usuarios"""
    # Detectar desconexión del bot
    if member.id == bot.user.id:
        if after.channel is None or after.channel.id != VOICE_CHANNEL_ID:
            print(f"⚠ Bot fue desconectado del canal")
            await asyncio.sleep(2)
            await connect_to_voice()
            return
    
    # Rastrear tiempo de usuarios
    if member.bot:
        return
    
    user_id = member.id
    
    if user_id not in user_voice_time:
        user_voice_time[user_id] = {
            'total_seconds': 0,
            'join_time': None,
            'name': member.display_name
        }
    
    # Usuario se unió
    if before.channel is None and after.channel is not None:
        user_voice_time[user_id]['join_time'] = datetime.now()
        user_voice_time[user_id]['name'] = member.display_name
        print(f"🟢 {member.display_name} se conectó")
    
    # Usuario salió
    elif before.channel is not None and after.channel is None:
        if user_voice_time[user_id]['join_time']:
            session = (datetime.now() - user_voice_time[user_id]['join_time']).total_seconds()
            user_voice_time[user_id]['total_seconds'] += session
            user_voice_time[user_id]['join_time'] = None
            
            total = user_voice_time[user_id]['total_seconds']
            hours = int(total // 3600)
            minutes = int((total % 3600) // 60)
            print(f"🔴 {member.display_name} se desconectó - Total: {hours}h {minutes}m")

# ===== TAREAS AUTOMÁTICAS =====
@tasks.loop(seconds=30)
async def check_connection():
    """Verifica la conexión cada 30 segundos"""
    guild = bot.get_guild(GUILD_ID)
    if not guild:
        return
    
    bot_stats['last_heartbeat'] = datetime.now()
    bot_stats['heartbeat_count'] += 1
    
    if not guild.voice_client or not guild.voice_client.is_connected():
        print(f"✗ Desconectado, intentando reconectar...")
        await connect_to_voice()
    elif guild.voice_client.channel.id != VOICE_CHANNEL_ID:
        print(f"✗ Canal incorrecto, reconectando...")
        await guild.voice_client.disconnect()
        await connect_to_voice()

@tasks.loop(minutes=25)
async def play_silent_audio():
    """Reproduce audio silencioso cada 25 minutos"""
    guild = bot.get_guild(GUILD_ID)
    if not guild or not guild.voice_client or not guild.voice_client.is_connected():
        return
    
    try:
        if guild.voice_client.is_playing():
            return
        
        silent_source = SilentAudioSource(duration_minutes=30)
        guild.voice_client.play(silent_source, after=lambda e: None)
        
        bot_stats['silent_audio_plays'] += 1
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"♪ Audio silencioso #{bot_stats['silent_audio_plays']} ({timestamp})")
    except Exception as e:
        print(f"✗ Error reproduciendo audio: {e}")

@tasks.loop(minutes=5)
async def auto_save_data():
    """Guarda datos automáticamente cada 5 minutos"""
    save_voice_time_data()

# ===== COMANDOS DE ESTADO =====
@bot.command(name='status')
async def status_command(ctx):
    """Muestra el estado actual del bot"""
    guild = bot.get_guild(GUILD_ID)
    is_connected = guild.voice_client and guild.voice_client.is_connected()
    is_playing = guild.voice_client and guild.voice_client.is_playing()
    
    uptime = "N/A"
    if bot_stats['connected_at']:
        uptime = datetime.now() - bot_stats['connected_at']
        uptime = str(uptime).split('.')[0]
    
    embed = discord.Embed(
        title="🤖 Estado del Bot",
        color=discord.Color.green() if is_connected else discord.Color.red()
    )
    
    embed.add_field(name="✓ Conexión", value="Conectado" if is_connected else "Desconectado", inline=True)
    embed.add_field(name="♪ Reproduciendo", value="Sí" if is_playing else "No", inline=True)
    embed.add_field(name="⏱ Tiempo en línea", value=uptime, inline=True)
    embed.add_field(name="❤️ Latencia", value=f"{bot.latency * 1000:.2f}ms", inline=True)
    embed.add_field(name="📊 Heartbeats", value=str(bot_stats['heartbeat_count']), inline=True)
    embed.add_field(name="♪ Audio silencioso", value=f"{bot_stats['silent_audio_plays']} veces", inline=True)
    
    if is_connected:
        embed.add_field(name="📍 Canal", value=guild.voice_client.channel.mention, inline=False)
    
    embed.set_footer(text=f"Pedido por {ctx.author.name}")
    await send_home(ctx, embed=embed)

@bot.command(name='health')
async def health_check(ctx):
    """Comprobación rápida de salud"""
    guild = bot.get_guild(GUILD_ID)
    is_connected = guild.voice_client and guild.voice_client.is_connected()
    
    status_emoji = "✅" if is_connected else "❌"
    status_text = "BOT ACTIVO" if is_connected else "BOT INACTIVO"
    
    await send_home(ctx, content=f"{status_emoji} **{status_text}** - Latencia: {bot.latency * 1000:.0f}ms")

@bot.command(name='join')
async def join_command(ctx):
    """Conectar manualmente al canal de voz"""
    await connect_to_voice()
    await send_home(ctx, content="✓ Intentando reconectar...")

# ===== COMANDOS CON GROQ =====
@bot.command(name='yo')
async def yo_command(ctx, *, message: str = "que pasa"):
    """Responde con jerga de barrio usando Groq AI"""
    try:
        system_prompt = """Eres un bot de Discord que habla como gente de barrio mexicano/chicano.
Usa jerga urbana mezclando español e inglés: bro, wey, carnal, homie, man, what's good, chale, órale, etc.
Sé breve (máximo 2-3 frases). Responde casual y natural.
NO uses asteriscos ni acciones. Solo texto conversacional."""
        
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.8,
            max_tokens=100
        )
        
        response = chat_completion.choices[0].message.content.strip()
        await ctx.send(response)
        
    except Exception as e:
        await ctx.send(f"Chale bro, algo salió mal: {e}")
        print(f"Error en !yo: {e}")

# ===== COMANDOS DE TIEMPO EN VOZ =====
@bot.command(name='voicetime', aliases=['vt'])
async def voice_time_command(ctx):
    """Muestra horas totales en voz"""
    voice_channel = bot.get_channel(VOICE_CHANNEL_ID)
    
    if not voice_channel:
        await ctx.send("❌ Canal no encontrado")
        return
    
    embed = discord.Embed(
        title=f"🎙️ Tiempo en {voice_channel.name}",
        color=discord.Color.purple()
    )
    
    sorted_users = sorted(
        user_voice_time.items(),
        key=lambda x: x[1]['total_seconds'],
        reverse=True
    )
    
    if not sorted_users:
        embed.add_field(name="Sin datos", value="No hay registro aún", inline=False)
    else:
        for i, (user_id, data) in enumerate(sorted_users[:10], 1):
            total = data['total_seconds']
            if data['join_time']:
                total += (datetime.now() - data['join_time']).total_seconds()
            
            hours = int(total // 3600)
            minutes = int((total % 3600) // 60)
            
            member = ctx.guild.get_member(user_id)
            name = member.display_name if member else data.get('name', f'Usuario {user_id}')
            status = "🟢" if data['join_time'] else "⚫"
            
            embed.add_field(
                name=f"{i}. {status} {name}",
                value=f"**{hours}h {minutes}m**",
                inline=True
            )
    
    embed.set_footer(text=f"Pedido por {ctx.author.name}")
    await ctx.send(embed=embed)

# ===== INICIAR BOT =====
if __name__ == "__main__":
    TOKEN = os.getenv('DISCORD_TOKEN') or os.getenv('BOT_TOKEN')
    if not TOKEN:
        raise ValueError("Falta DISCORD_TOKEN o BOT_TOKEN en .env")
    
    print("=" * 50)
    print("🚀 INICIANDO BOT DE VOZ PERSISTENTE")
    print("=" * 50)
    print(f"Guild ID: {GUILD_ID}")
    print(f"Voice Channel ID: {VOICE_CHANNEL_ID}")
    print(f"Text Channel ID: {TEXT_CHANNEL_ID if TEXT_CHANNEL_ID else 'No configurado'}")
    print("=" * 50)
    
    try:
        bot.run(TOKEN)
    finally:
        print("\n🛑 Bot detenido, guardando datos...")
        save_voice_time_data()