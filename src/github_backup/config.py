import os
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, ClassVar
from pathlib import Path

def _env(name: str, default: str = "") -> str:
    """Return environment variable value, or default if not set."""
    return os.getenv(name, default)

# Mapping from logging level to its corresponding environment variable name
_LEVEL_CHAT_ENV: ClassVar[Dict[int, str]] = {
    logging.DEBUG:          'TELEGRAM_CHAT_IDS_DEBUG',
    logging.INFO:           'TELEGRAM_CHAT_IDS_INFO',
    logging.PRIORITY_INFO:  'TELEGRAM_CHAT_IDS_PRIORITY_INFO',
    logging.WARNING:        'TELEGRAM_CHAT_IDS_WARNING',
    logging.ERROR:          'TELEGRAM_CHAT_IDS_ERROR',
    logging.CRITICAL:       'TELEGRAM_CHAT_IDS_CRITICAL',
}

def _build_level_chat_ids() -> Dict[int, List[str]]:
    result: Dict[int, List[str]] = {}
    for level, env_var in _LEVEL_CHAT_ENV.items():
        value = _env(env_var, "").strip()
        if value:
            result[level] = [chat_id.strip() for chat_id in value.split(",")]
    return result

@dataclass(frozen=True)
class AppConfig:
    """Configuration holder for the application."""

    # TgLogging
    level_chat_ids: Dict[int, List[str]] = field(default_factory=_build_level_chat_ids)
    log_file_path: str = _env('LOG_FILE') or None
    telegram_bot_token: Optional[str] = _env('TELEGRAM_BOT_TOKEN') or None

    # Backup settings
    backup_dir: str = _env("BACKUP_DIR", None)

    # Auth Security settings
    token_key_file: Optional[str] = _env("TOKEN_KEY_FILE") or None
    token_encrypted_file: str = _env("TOKEN_ENCRYPTED_FILE", "./.tokEncEn")

    @property
    def data_dir(self) -> Path:
        return Path(self.backup_dir)

_cached_config: Optional[AppConfig] = None
def load_app_config() -> AppConfig:
    global _cached_config
    if _cached_config is None:
        _cached_config = AppConfig()
        
        # Validation
        if not _cached_config.token_encrypted_file:
            raise ValueError("TOKEN_ENCRYPTED_FILE environment variable must be set.")
        if not _cached_config.backup_dir:
            raise ValueError("BACKUP_DIR environment variable must be set.")

    return _cached_config
