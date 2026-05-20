FROM python:3.11-slim

# --- system deps (must be root) ---
RUN apt-get update && apt-get install -y \
    ffmpeg \
    rclone \
    nodejs \
    && rm -rf /var/lib/apt/lists/*

# --- create non-root user ---
RUN useradd -u 1000 -m appuser

WORKDIR /app

# --- Python deps ---
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# --- copy code ---
COPY ./src/yt2podcast ./yt2podcast

# --- optional writable data dir ---
RUN mkdir -p /app/data && chown -R appuser:appuser /app/data
RUN mkdir -p /app/config && chown -R appuser:appuser /app/config

USER appuser

ENV PATH="/home/appuser/.local/bin:${PATH}"

CMD ["env", \
     "DATA_DIR=/app/data", \
     "CONFIG_DIR=/app/config", \
     "COOKIES_FILE=/app/config/cookies.txt", \
     "python", "-u", "/app/yt2podcast/yt2podcast.py"]