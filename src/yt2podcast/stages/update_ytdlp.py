import subprocess
import sys
import logging
import os

def update_ytdlp(logger: logging.Logger) -> None:
    """Update yt-dlp to the latest version using pip.

    Args:
        logger: Logger instance for output.
    """
    logger.info("Checking and updating yt-dlp to the latest version.")
    try:
        env = os.environ.copy()
        env["PIP_BREAK_SYSTEM_PACKAGES"] = "1"
        subprocess.run([sys.executable, "-m", "pip", "install", "-U", "--pre", "yt-dlp"], env=env, check=True)
        logger.info("yt-dlp updated successfully.")
    except Exception as e:
        logger.warning(f"Failed to update yt-dlp at runtime: {e}")
