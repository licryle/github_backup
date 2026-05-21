import os
import logging, tglogging

from dataclasses import dataclass, field
from typing import Dict, List, Optional
def _clean_value(value: str) -> str:
    """Return the env var value without any trailing comment.

    Example: "path/to/file # comment" -> "path/to/file"
    """
    cleaned = value.split('#', 1)[0].strip()
    return cleaned

def _parse_chat_ids(env_name: str) -> List[str]:
    raw = os.getenv(env_name)
    if not raw:
        return []
    return [cid.strip() for cid in raw.split(',') if cid.strip()]

# Mapping from logging level to its corresponding environment variable name
_LEVEL_CHAT_ENV: Dict[int, str] = {
    logging.DEBUG:          'TELEGRAM_CHAT_IDS_DEBUG',
    logging.INFO:           'TELEGRAM_CHAT_IDS_INFO',
    logging.PRIORITY_INFO:  'TELEGRAM_CHAT_IDS_PRIORITY_INFO',
    logging.WARNING:        'TELEGRAM_CHAT_IDS_WARNING',
    logging.ERROR:          'TELEGRAM_CHAT_IDS_ERROR',
    logging.CRITICAL:       'TELEGRAM_CHAT_IDS_CRITICAL',
}

@dataclass(frozen=True)
class AppConfig:
    """Configuration holder for the application.

    Values are read from environment variables once at start‑up, with any trailing
    ``#`` comments stripped. This class is immutable to guarantee that the
    configuration does not change at runtime (one‑time load as requested).
    """
    log_file_path: str = "./data/logs/yt2podcast.log"
    telegram_bot_token: Optional[str] = None
    level_chat_ids: Dict[int, List[str]] = field(default_factory=dict)

def load_app_config() -> AppConfig:
    """Load configuration from environment variables, cleaning values.

    Returns:
        AppConfig: Instance with all required settings.
    """
    raw_log_path = os.getenv('YT2PODCAST_LOG_FILE')
    log_file_path = _clean_value(raw_log_path) if raw_log_path else "./data/logs/yt2podcast.log"
    raw_token = os.getenv('TELEGRAM_BOT_TOKEN')
    telegram_bot_token = _clean_value(raw_token) if raw_token else None
    level_chat_ids = {level: _parse_chat_ids(env) for level, env in _LEVEL_CHAT_ENV.items()}
    return AppConfig(
        log_file_path=log_file_path,
        telegram_bot_token=telegram_bot_token,
        level_chat_ids=level_chat_ids,
    )
