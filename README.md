# YT2Podcast 🎙️

A Python automation tool converting YouTube videos into an audio podcast, publishing via RSS to an FTP server.

---

## 🎯 What It Does

- **Discovers** new videos from configured YouTube channels/playlists
- **Downloads & converts** them to MP3
- **Generates** a podcast RSS feed (`geneRSS`)
- **Uploads** to a remote FTP server

Perfect for creating podcasts from YouTube content without manual intervention!

---

## 🚀 Quick Start

### Nix Development Environment (Recommended) ⭐

This project uses **Nix** for reproducible development environments. The `flake.nix` defines a devShell with all dependencies pre-configured:

```bash
# Enter the Nix dev shell (installs Python, pip, virtualenv, ffmpeg, rclone, podman)
nix develop

# Or with nix-shell
nix-shell
```
The devShell automatically creates and activates a virtual environment and installs `requirements.txt` on first use.

### ⚙️ Manual setup (no Nix)
- Python 3.8+
- `pip`
- `yt-dlp` (auto‑installed)
- `rclone` (for FTP)

```bash
# Create virtual environment
python -m venv env
# Windows: env\\Scripts\\activate
source env/bin/activate
# Install deps
pip install -r requirements.txt
```

### 🗝️ Configuration
Create a `.env` in the project root:
```env
PODCAST_TITLE="La parole de Jean‑Luc Mélenchon"
PODCAST_DESCRIPTION="Audio versions of JLM's videos."
PODCAST_NAME="jlm-fr"

PODCAST_URLS="https://www.youtube.com/watch?v=y-tgVrngjf0&list=PLtXUQ5t979ibdVm5jqS5JsBZOVniVgh0D&ab_channel=LFI-Monde https://www.youtube.com/@JLMelenchon/ https://www.youtube.com/playlist?list=PLnAm9o_Xn_3DIOQdk_pb96lMZL4dWXsBt"

START_DATE="20250701"
HOSTNAME="podcast.lfi-monde.org"
FTP_LOGIN="lfimonde"
FTP_PASSWORD="your‑ftp‑password"
TELEGRAM_BOT_TOKEN="..."

# (optional – leave empty to suppress DEBUG)
TELEGRAM_CHAT_IDS_DEBUG= 
TELEGRAM_CHAT_IDS_INFO=0000_0
TELEGRAM_CHAT_IDS_PRIORITY_INFO=000_0,111
TELEGRAM_CHAT_IDS_WARNING=000_0
# send ERROR to two chats, either topics in groups or direct chats.
TELEGRAM_CHAT_IDS_ERROR=000_0,111
TELEGRAM_CHAT_IDS_CRITICAL=000_0,111

# The docker image is designed to run continously and sleep in between sync_interval-s. By default, it's -1 meaning exit after 1 run.
SYNC_INTERVAL=
```

---

## ▶️ Running the Script

### Direct execution
```bash
python -m yt2podcast run
```

### Cron (Linux/macOS)
```cron
0 2 * * * cd /path/to/YT2Podcast && source env/bin/activate && python src/yt2podcast/yt2podcast.py >> logs/cron.log 2>&1
```

### Windows Task Scheduler
```cmd
env\\Scripts\\activate.bat && python src\\yt2podcast\\yt2podcast.py
```

---

## 🛠️ Development Workflow

### Project layout
```
YT2Podcast/
├── src/                # Python package
│   └── yt2podcast/
│       └── yt2podcast.py
├── requirements.txt
├── Dockerfile
├── .envrc   # direnv template
└── README.md
```

### Common commands
```bash
# Activate venv (Linux/macOS)
source env/bin/activate
# Activate venv (Windows)
env\\Scripts\\activate.bat

# Install / upgrade deps
pip install -r requirements.txt
pip install -U --pre yt-dlp

# Run once (test)
python src/yt2podcast/yt2podcast.py

# Verbose debug
python src/yt2podcast/yt2podcast.py 2>&1 | tee run.log
```

---

## 🐳 Docker support
```bash
# Build image
podman build -t yt2podcast .
# Run container
podman run --rm \
  -v "$PWD/src/data:/app/data" \
  -v "$PWD/cookies.txt:/app/config/cookies.txt" \
  --env-file .env \
  yt2podcast
```

---

## ⚙️ Configuration Options

| Variable | Default | Description |
|----------|---------|-------------|
| `PODCAST_TITLE` | "La parole de Jean-Luc Mélenchon" | Podcast RSS title |
| `PODCAST_DESCRIPTION` | See above | Podcast description |
| `PODCAST_NAME` | "jlm-fr" | Podcast folder name |
| `PODCAST_URLS` | 3 default URLs | Comma/space-separated YouTube URLs |
| `START_DATE` | "20250701" | Filter videos after this date (YYYYMMDD) |
| `HOSTNAME` | "podcast.lfi-monde.org" | FTP hostname |
| `FTP_LOGIN` | "lfimonde" | FTP username |
| `FTP_PASSWORD` | See above | FTP password |
| `TELEGRAM_BOT_TOKEN` | (empty) | Telegram bot token for notifications |
| `TELEGRAM_CHAT_ID` | (empty) | Telegram chat/group ID |
| `DATA_DIR` | "./src/data" | Base data directory |
| `TZ` | "Asia/Tokyo" | Timezone for logging |

---

## 📁 Output Structure

```
public_html/
└── jlm-fr/
    ├── [video_id].mp3          # Converted audio files
    ├── [video_id].info.json     # Metadata files
    ├── podcast.xml              # Generated RSS feed
    └── cover.jpg                # Podcast artwork
```

---

## 🔔 Telegram Notifications

When configured, the script sends HTML-formatted messages to your Telegram chat:

- ✅ **Success**: New episodes published
- ❌ **Failure**: Error details with troubleshooting info

---

## 🛡️ Safety Features

- **Cache-based deduplication**: Only processes new videos
- **Error handling**: Graceful failure with logging
- **Duration filter**: Minimum 65 seconds per video
- **Date filtering**: Respects `START_DATE` constraint
- **Auto-update**: yt-dlp updates to latest version on each run

---

## 📝 Logging

The script uses `[CRON_INFO]`, `[CRON_DEBUG]`, `[CRON_WARNING]`, and `[CRON_ERROR]` prefixes for easy log parsing.

Example log output:
```
[CRON_INFO] Script started at standard datetime.
[CRON_INFO] Checking and updating yt-dlp to the latest version...
[CRON_INFO] Processing URL: https://www.youtube.com/@JLMelenchon/
[CRON_INFO] Successfully processed and cached 1234567890
[CRON_INFO] RSS feed generated successfully.
[CRON_INFO] FTP sync completed successfully.
```

---

## 🐳 Docker Support

A `Dockerfile` is included for containerized deployment:

```bash
podman build -t yt2podcast .
podman run --rm \
    -v "$PWD/src/data:/app/data" \
    -v "$PWD/cookies.txt:/app/config/cookies.txt" \
    --env-file .env \
    yt2podcast
```

---

## 📄 License
MIT – feel free to use & modify!

---

## 🤝 Contributing
1. Fork the repo
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📞 Support
Open an issue or join the discussion on GitHub.