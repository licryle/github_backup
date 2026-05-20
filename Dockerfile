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
COPY . .

# --- optional writable data dir ---
RUN mkdir -p /data && chown -R appuser:appuser /data /app

USER appuser

ENV PATH="/home/appuser/.local/bin:${PATH}"

CMD ["python", "-u", "src/yt2podcast/yt2podcast.py"]