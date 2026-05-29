#!/bin/sh
# run_loop.sh — runs github_backup with optional sync interval

trap 'echo "Caught SIGINT, exiting"; exit 0' INT

sleep_interruptible() {
    SECONDS_LEFT="$1"

    while [ "$SECONDS_LEFT" -gt 0 ]; do
        sleep 1
        SECONDS_LEFT=$((SECONDS_LEFT - 1))
    done
}

# set environment variables
export BACKUP_DIR=/app/backups
export TOKEN_KEY_FILE=/app/secrets/key
export TOKEN_ENCRYPTED_FILE=/app/secrets/tok

# Read + sanitize once
INTERVAL="${SYNC_INTERVAL:-1}"
INTERVAL=$(printf '%s' "$INTERVAL" | tr -cd '0-9-')

[ -z "$INTERVAL" ] && INTERVAL=-1

while true; do
    python -m github_backup run;

    if [ "$INTERVAL" -lt 0 ]; then
        echo "SYNC_INTERVAL < 0, exiting."
        exit 0
    fi

    echo "Sleeping for $INTERVAL seconds..."
    sleep_interruptible "$INTERVAL"
done