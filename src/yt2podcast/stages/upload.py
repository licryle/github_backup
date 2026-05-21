import logging
import os
from pathlib import Path
from rclone_python import rclone

from ..config import AppConfig


def upload(cfg: AppConfig, logger: logging.Logger) -> None:
    """Sync generated files to remote FTP using rclone.

    The function constructs the source and destination paths and invokes
    ``rclone.copy`` with a set of options that mirror the original script.
    """
    logger.info("Syncing files to remote FTP host.")
    source_path = f"{cfg.html_dir}/"
    dest_path = f"ftp:/{cfg.ftp_path}"
    extra_args = [
        "--ftp-host", cfg.hostname,
        "--ftp-user", cfg.ftp_login,
        "--ftp-pass", cfg.ftp_password,
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
        "--log-level", "INFO",
    ]
    try:
        rclone.copy(source_path, dest_path, args=extra_args)
        logger.info("FTP sync completed successfully.")
    except Exception as e:
        logger.error(f"FTP Sync failed: {e}")
