import os
import logging, tglogging

from dataclasses import dataclass, field
from typing import Dict, List, Optional, ClassVar
from pathlib import Path


def _env(name: str, default: str = "") -> str:
    """Return environment variable value stripped of comments, or default if not set."""
    return os.getenv(name)

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
        if value:  # only add non-empty
            result[level] = [chat_id.strip() for chat_id in value.split(",")]
    return result

@dataclass(frozen=True)
class AppConfig:
    """Configuration holder for the application.

    Values are read from environment variables once at start‑up,
    with any trailing ``#`` comments stripped. This class is immutable
    to guarantee that the configuration does not change at runtime.
    """

    # TgLogging
    level_chat_ids: Dict[int, List[str]] = field(default_factory=_build_level_chat_ids)
    log_file_path: str = _env('YT2PODCAST_LOG_FILE') or "./data/logs/yt2podcast.log"
    telegram_bot_token: Optional[str] = _env('TELEGRAM_BOT_TOKEN') or ""
    # System variables
    tz: str = _env("TZ", "Asia/Tokyo")
    puid: Optional[str] = _env("PUID")
    pgid: Optional[str] = _env("PGID")
    # Podcast info
    podcast_title: str = _env("PODCAST_TITLE", "La parole de Jean-Luc Mélenchon")
    podcast_description: str = _env("PODCAST_DESCRIPTION", "Retrouvez les vidéos, prises de paroles, conférences et notes de blogs de Jean-Luc Mélenchon en version audio.")
    podcast_name: str = _env("PODCAST_NAME", "jlm-fr")
    podcast_urls: List[str] = field(default_factory=lambda: _env("PODCAST_URLS", "").replace(",", " ").split())
    start_date: str = _env("START_DATE", "20250701")
    hostname: str = _env("HOSTNAME", "")
    # FTP credentials
    ftp_login: str = _env("FTP_LOGIN", "")
    ftp_password: str = _env("FTP_PASSWORD", "")
    ftp_path: str = _env("FTP_PATH", "/public_html")
    # Cookies
    cookies_file: str = _env("COOKIES_FILE", "")
    # Directories
    data_dir: str = _env("DATA_DIR", "./src/data")

    @property
    def html_dir(self) -> Path:
        return Path(self.data_dir) / "public_html"

    @property
    def cache_dir(self) -> Path:
        return Path(self.data_dir) / ".cache"

    @property
    def cache_file(self) -> Path:
        return self.cache_dir / f"yt-dlp-{self.podcast_name}-archive"


_cached_config: Optional[AppConfig] = None
def load_app_config() -> AppConfig:
    """Return a singleton AppConfig instance.

    The first call constructs the configuration by reading environment variables.
    Subsequent calls return the same immutable instance, avoiding repeated work.
    """
    global _cached_config
    if _cached_config is None:
        _cached_config = AppConfig()
    return _cached_config
