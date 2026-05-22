import logging
import os
from pathlib import Path
import subprocess

from ..config import AppConfig

def rclone_obscure(plain_password):
    # Run the rclone obscure command
    result = subprocess.run(
        ["rclone", "obscure", plain_password], 
        capture_output=True, 
        text=True, 
        check=True
    )
    return result.stdout.strip()

def upload(cfg: AppConfig, logger: logging.Logger) -> None:
    """Sync generated files to remote FTP using rclone.

    The function constructs the source and destination paths and invokes
    ``rclone.copy`` with a set of options that mirror the original script.
    """
    logger.info("Syncing files to remote FTP host.")
    

    try:
        obs_pass = rclone_obscure(cfg.ftp_password)
        
        # Construct the rclone command
        cmd = [
            "rclone",
            "copy",
            f"{cfg.html_dir}/",
            f":ftp:/domains/{cfg.hostname}/public_html/",
            f"--ftp-host={cfg.hostname}",
            f"--ftp-user={cfg.ftp_login}",
            f"--ftp-pass={obs_pass}",
            "--progress"
        ]

        logger.info("Starting FTP sync.")
        process = subprocess.run(cmd, capture_output=False)

        if process.returncode == 0:
            logger.info("FTP sync completed successfully.")
        else:
            logger.error(f"Rclone failed with exit code {process.returncode}, error {process.stderr}")
    except Exception as e:
        logger.error(f"FTP Sync failed: {e}")
