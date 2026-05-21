#!/usr/bin/env python3
import os
import sys
import json
import urllib.request
import subprocess


from dotenv import load_dotenv
# Load local environment variables if .env exists
load_dotenv()

# System variables
TZ = os.getenv("TZ", "Asia/Tokyo")
PUID = os.getenv("PUID")
PGID = os.getenv("PGID")

# Podcast configuration
PODCAST_TITLE = os.getenv("PODCAST_TITLE", "La parole de Jean-Luc Mélenchon")
PODCAST_DESCRIPTION = os.getenv("PODCAST_DESCRIPTION", "Retrouvez les vidéos, prises de paroles, conférences et notes de blogs de Jean-Luc Mélenchon en version audio.")
PODCAST_NAME = os.getenv("PODCAST_NAME", "jlm-fr")

urls_raw = os.getenv("PODCAST_URLS", "")
PODCAST_URLS = [u.strip() for u in urls_raw.replace(",", " ").split() if u.strip()]
START_DATE = os.getenv("START_DATE", "20250701")
HOSTNAME = os.getenv("HOSTNAME", "")
FTP_LOGIN = os.getenv("FTP_LOGIN", "")
FTP_PASSWORD = os.getenv("FTP_PASSWORD", "")

# Cookies configuration
COOKIES_FILE = os.getenv("COOKIES_FILE", "")

# Directory configurations
DATA_DIR = os.getenv("DATA_DIR", "./src/data")
HTML_DIR = os.path.join(DATA_DIR, "public_html")
CACHE_DIR = os.path.join(DATA_DIR, ".cache")
CACHE_FILE = os.path.join(CACHE_DIR, f"yt-dlp-{PODCAST_NAME}-archive")

def send_telegram(message):
    """
    Sends an HTML-formatted message to a Telegram individual or group chat.
    """
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        print("[CRON_INFO] Telegram notifications not configured.")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }
    
    # Convert chat_id to integer if numeric (supports negative numbers for group chats)
    try:
        if chat_id.startswith("-") and chat_id[1:].isdigit():
            payload["chat_id"] = int(chat_id)
        elif chat_id.isdigit():
            payload["chat_id"] = int(chat_id)
    except Exception:
        pass

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            pass
        print("[CRON_INFO] Telegram notification sent successfully.")
    except Exception as e:
        print(f"[CRON_WARNING] Failed to send Telegram notification: {e}")


def update_ytdlp():
    """
    Updates yt-dlp to the absolute latest pre-release or stable version at runtime.
    """
    print("[CRON_INFO] Checking and updating yt-dlp to the latest version...")
    try:
        env = os.environ.copy()
        env["PIP_BREAK_SYSTEM_PACKAGES"] = "1"
        subprocess.run([sys.executable, "-m", "pip", "install", "-U", "--pre", "yt-dlp"], env=env, check=True)
        print("[CRON_INFO] yt-dlp updated successfully.")
    except Exception as e:
        print(f"[CRON_WARNING] Failed to update yt-dlp at runtime: {e}")


def process_url(url, cache_set):
    """
    Downloads new videos from a channel or playlist that are not already cached.
    """
    print(f"[CRON_INFO] Processing URL: {url}")
    
    # 1. Get flat video IDs list from playlist
    cmd = ["yt-dlp", "--flat-playlist", "--print", "id", url]
    if COOKIES_FILE and os.path.exists(COOKIES_FILE):
        cmd.extend(["--cookies", COOKIES_FILE])
        
    try:
        print(f"[CRON_DEBUG] Running command {' '.join(cmd)}")
        result = subprocess.run(cmd, 
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, text=True, check=False)

        video_ids = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    except Exception as e:
        print(f"[CRON_WARNING] Failed to extract playlist video list from {url}: {e}")
        return

    video_count = len(video_ids)
    print(f"[CRON_INFO] Found {video_count} videos in playlist/channel.")

    # 2. Process each video ID
    for index, video_id in enumerate(video_ids, start=1):
        if not video_id:
            continue
            
        cache_key = f"youtube {video_id}"
        if cache_key in cache_set:
            # Already processed, skip
            continue
            
        print(f"[CRON_INFO] Processing video {index} of {video_count}: {video_id}...")
        
        # Download, convert to mp3, extract audio, write metadata
        download_cmd = [
            "yt-dlp",
            "--format", "bestaudio/best",
            "--js-runtimes", "node",
            "--remote-components", "ejs:github",
            "--extract-audio",
            "--audio-format", "mp3",
            "--output", os.path.join(HTML_DIR, PODCAST_NAME, "%(id)s.%(ext)s"),
            "--write-info-json",
            "--no-clean-info-json",
            "--add-metadata",
            "--embed-chapters",
            "--embed-subs",
            "--mtime",
            "--ignore-errors",
            "--match-filter", "duration > 65",
            "--dateafter", START_DATE,
            f"https://www.youtube.com/watch?v={video_id}"
        ]
        
        if COOKIES_FILE and os.path.exists(COOKIES_FILE):
            download_cmd.extend(["--cookies", COOKIES_FILE])
            
        print(f"[CRON_DEBUG] Running command {' '.join(download_cmd)}")
        res = subprocess.run(download_cmd)
        if res.returncode == 0:
            # Successfully downloaded and converted, save to cache file
            with open(CACHE_FILE, "a", encoding="utf-8") as f:
                f.write(f"{cache_key}\n")
            cache_set.add(cache_key)
                
            print(f"[CRON_INFO] Successfully processed and cached {video_id}")
        else:
            print(f"[CRON_ALERT] Failed to process video {video_id}. Not adding to cache.")


def main():
    print(f"[CRON_INFO] Script started at standard datetime.")
    
    # 1. Update yt-dlp
    update_ytdlp()
    
    # 2. Make sure output directories exist
    os.makedirs(CACHE_DIR, exist_ok=True)
    os.makedirs(os.path.join(HTML_DIR, PODCAST_NAME), exist_ok=True)
    
    # 3. Create .htaccess if not present
    htaccess_path = os.path.join(HTML_DIR, ".htaccess")
    if not os.path.exists(htaccess_path):
        with open(htaccess_path, "w", encoding="utf-8") as f:
            f.write("DirectoryIndex podcast.xml\n")

    # 4. Load cache into memory (O(1) lookups)
    cache_set = set()
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()
                if stripped:
                    cache_set.add(stripped)
    print(f"[CRON_INFO] Loaded {len(cache_set)} entries from cache.")

    # 5. Process all channels/playlists
    for url in PODCAST_URLS:
        process_url(url, cache_set)

    # 6. Generate RSS Feed using generss package directly
    import generss
    print("[CRON_INFO] Generating RSS feed...")
    og_path = os.getcwd()
    try:
        os.chdir(HTML_DIR)
        rss_args = [
            "--metadata",
            "--sort-creation",
            "--host", f"http://{HOSTNAME}/",
            "--dirname", PODCAST_NAME,
            "--out", os.path.join(PODCAST_NAME, "podcast.xml"),
            "--extensions", "mp3",
            "--title", PODCAST_TITLE,
            "--description", PODCAST_DESCRIPTION,
            "--image", f"{PODCAST_NAME}/cover.jpg"
        ]
        ret = generss.main(rss_args)
        if ret != 0 and ret is not None:
            raise Exception(f"generss returned exit code {ret}")
    finally:
        os.chdir(og_path)

    print("[CRON_INFO] RSS feed generated successfully.")

    # 7. Upload to FTP using rclone-python wrapper (best-effort, non-blocking)
    from rclone_python import rclone
    print("[CRON_INFO] Syncing files to remote FTP host...")
    
    try:
        # Obscure the FTP password using rclone
        obs_res = subprocess.run(["rclone", "obscure", FTP_PASSWORD], capture_output=True, text=True, check=True)
        obs_pass = obs_res.stdout.strip()
        print(f"[CRON_WARNING] Obscured FTP password")
    except Exception as e:
        print(f"[CRON_WARNING] Failed to obscure FTP password: {e}")
        print("[CRON_INFO] Continuing without password obscuring...")
        obs_pass = FTP_PASSWORD

    source_path = f"{HTML_DIR}/"
    dest_path = f":ftp:/domains/{HOSTNAME}/public_html/"
    
    extra_args = [
        "--ftp-host", HOSTNAME,
        "--ftp-user", FTP_LOGIN,
        "--ftp-pass", obs_pass,
        "--size-only",
        "--transfers", "1",
        "--checkers", "1",
        "--ftp-concurrency", "1",
        "--buffer-size", "32M",
        "--contimeout", "120s",
        "--timeout", "600s",
        "--retries", "5",
        "--low-level-retries", "10",
        "--stats", "10s",
        "--stats-one-line",
        "--log-level", "INFO"
    ]
    
    try:
        rclone.copy(source_path, dest_path, args=extra_args)
        print("[CRON_INFO] FTP sync completed successfully.")
    except Exception as e:
        # Log the error but don't crash - FTP failures are often transient (network, auth issues)
        error_details = str(e)
        print(f"[CRON_WARNING] FTP Sync failed: {error_details}")
        print("[CRON_INFO] Continuing execution - RSS feed is still available locally.")
    
    print(f"[CRON_INFO] Script finished successfully at standard datetime.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        error_msg = f"<b>🚨 [YT2Podcast] Run Failed!</b>\n\nError details:\n<code>{str(e)}</code>"
        print(f"[CRON_ERROR] Run failed: {e}", file=sys.stderr)
        send_telegram(error_msg)
        sys.exit(1)
