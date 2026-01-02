# Dockerfile
FROM python:3.10-slim

# Establecer directorio de trabajo
WORKDIR /app

# Copiar archivos de requirements
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código del bot
COPY app.py .
COPY .env .

# Crear directorio para datos persistentes
RUN mkdir -p /app/data

# Variable de entorno para el archivo de datos
ENV VOICE_TIME_FILE=/app/data/voice_time_data.json

# Comando para ejecutar el bot
CMD ["python", "-u", "app.py"]