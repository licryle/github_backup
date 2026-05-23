FROM python:3.11-slim

# --- system deps (must be root) ---
RUN apt-get update && apt-get install -y \
    git \
    curl \
    gnupg \
    && curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | gpg --dearmor -o /usr/share/keyrings/githubcli-archive-keyring.gpg \
    && chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
    && apt-get update && apt-get install -y gh \
    && rm -rf /var/lib/apt/lists/*

# --- create non-root user ---
RUN useradd -u 1000 -m appuser

WORKDIR /app

# --- Python deps ---
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# --- copy code ---
COPY ./src/github_backup ./github_backup

# --- writable data dir ---
RUN mkdir -p /app/backups && chown -R appuser:appuser /app/backups
RUN mkdir -p /app/secrets && chown -R appuser:appuser /app/secrets

USER appuser

ENV PATH="/home/appuser/.local/bin:${PATH}"

# Default sync interval is one off run
ENV SYNC_INTERVAL=-1

COPY --chmod=755 ./src/run_loop.sh /app/run_loop.sh

CMD ["/app/run_loop.sh"]
