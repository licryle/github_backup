#!/bin/sh
# run_loop.sh — runs yt2podcast with optional sync interval

trap 'echo "Caught SIGINT, exiting"; exit 0' INT
sleep_interruptible() {
    SECONDS_LEFT="$1"
    while [ "$SECONDS_LEFT" -gt 0 ]; do
        sleep 1
        SECONDS_LEFT=$((SECONDS_LEFT - 1))
    done
}

# set environment variables
export DATA_DIR=/app/data
export CONFIG_DIR=/app/config
export COOKIES_FILE=/app/config/cookies.txt

while true; do
    echo 'exec python -m yt2podcast run';

    if [ "${SYNC_INTERVAL:--1}" -lt 0 ]; then
        echo "SYNC_INTERVAL < 0, exiting."
        exit 0
    fi

    echo "Sleeping for ${SYNC_INTERVAL} seconds..."
    sleep_interruptible "${SYNC_INTERVAL}"
done