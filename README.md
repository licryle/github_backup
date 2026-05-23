# GitHub Backup 🛡️

A Python automation tool to back up all your GitHub repositories, keeping them synced with a "hard reset" to the remote HEAD. It features secure token storage and Telegram notifications.

Warning: the script does use the "repo" scope which includes the write permission, but also that means the token is stored locally.
This is a big security risk. Make sure to only run on a machine you fully trust.

---

## 🎯 What It Does

- **Authenticates** securely using GitHub's Device Flow (no manual token pasting).
- **Encrypts** your access token locally using Fernet (AES-128).
- **Discovers** all repositories owned by your GitHub account.
- **Clones & Updates** repositories to a local backup directory.
- **Hard Sync**: Automatically resets local copies to match the remote `HEAD`, ensuring a clean backup.
- **Notifies** via Telegram about backup status and errors using `tglogging`.

Intended for automated, secure backups of your entire GitHub profile!

---

## 🚀 Quick Start

### Nix Development Environment (Recommended) ⭐

This project uses **Nix** for reproducible development environments. The `flake.nix` defines a devShell with all dependencies:

```bash
# Enter the Nix dev shell (installs Python, git, etc.), and the first time
direnv allow

# Or with nix-shell
nix-shell
```

### ⚙️ Manual setup (no Nix)
- Python 3.8+
- `git` CLI installed
- `pip`

```bash
# Create virtual environment
python -m venv env
# Windows: env\Scripts\activate
source env/bin/activate
# Install deps
pip install -r requirements.txt
```

### 🗝️ Configuration
Create a `.env` in the project root:
```env
BACKUP_DIR="./backups"
TOKEN_KEY_FILE="./.secrets/github-backup.key"
TOKEN_ENCRYPTED_FILE="./.tokEncEn" (optional default)

# (optional – remove token to suppress)
TELEGRAM_BOT_TOKEN="..."
TELEGRAM_CHAT_IDS_INFO="123456"
TELEGRAM_CHAT_IDS_ERROR="123456"
TELEGRAM_CHAT_IDS_DEBUG=
TELEGRAM_CHAT_IDS_PRIORITY_INFO=
TELEGRAM_CHAT_IDS_WARNING=
TELEGRAM_CHAT_IDS_CRITICAL=

# (optional – remove to suppress)
LOG_FILE="backup.log"
```
---

## ▶️ Running the Script

### Initial Config
The first time you run it, you want to create a key to encrypt the token.
```bash
mkdir -p .secrets/ && python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())' > .secrets/github-backup.key

```
Follow the URL and enter the code shown in your terminal or Telegram.

### Direct execution
```bash
python -m github_backup run
```

### Cron (Linux/macOS)
```cron
0 3 * * * cd /path/to/github_backup && ./env/bin/python -m github_backup run >> logs/cron.log 2>&1
```

---

## 🛠️ Development Workflow

### Project layout
```
github_backup/
├── src/
│   └── github_backup/
│       ├── stages/
│       │   ├── auth.py     # Device Flow & Encryption
│       │   └── backup.py   # Cloning & Updating logic
│       ├── cli.py          # CLI Entrypoint
│       └── config.py       # Env-based config
├── requirements.txt
├── Dockerfile
└── README.md
```

### Common commands
```bash
# Run backup only (assumes already authenticated)
python -m github_backup backup

# Enable debug logging
python -m github_backup -v run
```

---

## 🐳 Docker / Podman support
```bash
# Build image
podman build -t github_backup .

# Run container (mounting the key and backup directory)
podman run --rm \
  --env-file .env \
  -v "$PWD/.secrets/github-backup.key:/app/secrets/key:ro" \
  -v "$PWD/backups:/app/backups" \
  github_backup
```

---

## ⚙️ Configuration Options

| Variable | Default | Description                                                                 |
|----------|---------|-----------------------------------------------------------------------------|
| `BACKUP_DIR` | (required) | (not used in Docker, set via Volume) Path where repositories will be cloned |
| `TOKEN_KEY_FILE` | (required) | (not used in Docker, set via Volume) Path to the Fernet encryption key file |
| `TOKEN_ENCRYPTED_FILE`| `./.tokEncEn` | (not used in Docker) Path to store the encrypted GitHub token               |
| `TELEGRAM_BOT_TOKEN` | (optional) | Telegram bot token for notifications                                        |
| `TELEGRAM_CHAT_IDS_*` | (optional) | Comma-separated chat IDs for different log levels                           |
| `LOG_FILE` | (optional) | Path to a file for logging output                                           |

---

## 🛡️ Security Features
Warning: the script does use the "repo" scope which includes the write permission, but also that means the token is stored locally.
This is a big security risk. **Make sure to only run on a machine you fully trust.**

- **Fernet Encryption**: Your GitHub token is never stored in plain text. It is encrypted using a key you generate and store separately.
- **Device Flow**: No need to create Personal Access Tokens manually; the app uses GitHub's official OAuth device flow.
- **Token Scrubbing**: Error messages and logs are automatically scrubbed to remove any sensitive token information before logging or sending to Telegram.

---

## 📝 Logging

The script uses `tglogging` to provide structured logs to both console/files and Telegram.

Example log output:
```
[INFO] Authenticated as: your-username
[INFO] Fetching owned repositories for user: your-username
[INFO] Cloning owner/repo-a.
[INFO] ✅ Successfully cloned owner/repo-a
[INFO] Fetching and updating owner/repo-b.
[INFO] ✅ Successfully updated and reset owner/repo-b
[PRIORITY_INFO] Backup Summary: 2 repos found, 1 cloned, 1 updated, 0 failed.
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
