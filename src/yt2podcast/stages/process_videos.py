import subprocess
import os
from pathlib import Path
import logging
from typing import Set

from ..config import AppConfig


def _ensure_directories(cfg: AppConfig) -> None:
    cfg.cache_dir.mkdir(parents=True, exist_ok=True)
    (cfg.html_dir / cfg.podcast_name).mkdir(parents=True, exist_ok=True)
    # Ensure .htaccess exists
    htaccess_path = cfg.html_dir / ".htaccess"
    if not htaccess_path.exists():
        htaccess_path.write_text("DirectoryIndex podcast.xml\n", encoding="utf-8")


def _load_cache(cfg: AppConfig) -> Set[str]:
    cache_set: Set[str] = set()
    if cfg.cache_file.exists():
        for line in cfg.cache_file.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if stripped:
                cache_set.add(stripped)
    return cache_set


def _save_cache_entry(cfg: AppConfig, entry: str) -> None:
    cfg.cache_file.parent.mkdir(parents=True, exist_ok=True)
    with cfg.cache_file.open("a", encoding="utf-8") as f:
        f.write(f"{entry}\n")


def _process_video(url: str, cfg: AppConfig, logger: logging.Logger, cache_set: Set[str]) -> None:
    logger.info(f"Processing Video: {url}")
    # Get flat video IDs list from playlist
    cmd = ["yt-dlp", "--flat-playlist", "--print", "id", url]
    if cfg.cookies_file:
        cmd.extend(["--cookies", cfg.cookies_file])
    try:
        logger.debug(f"Running command {' '.join(cmd)}")
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )
        video_ids = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    except Exception as e:
        logger.warning(f"Failed to extract playlist video list from {url}: {e}")
        return

    video_count = len(video_ids)
    cached_count = sum(1 for x in video_ids if f"youtube {x}" in cache_set)
    logger.info(
        f"Found {video_count} videos in playlist/channel. {cached_count} already cached. {video_count-cached_count} to process."
    )
    for index, video_id in enumerate(video_ids, start=1):
        if not video_id:
            continue
        cache_key = f"youtube {video_id}"
        if cache_key in cache_set:
            continue
        logger.info(f"Processing video {index} of {video_count}: {video_id}...")
        download_cmd = [
            "yt-dlp",
            "--format", "bestaudio/best",
            "--js-runtimes", "node",
            "--remote-components", "ejs:github",
            "--extract-audio",
            "--audio-format", "mp3",
            "--output", os.path.join(cfg.html_dir, cfg.podcast_name, "%(id)s.%(ext)s"),
            "--write-info-json",
            "--no-clean-info-json",
            "--add-metadata",
            "--embed-chapters",
            "--embed-subs",
            "--mtime",
            "--ignore-errors",
            "--match-filter", "duration > 65",
            "--dateafter", cfg.start_date,
            f"https://www.youtube.com/watch?v={video_id}",
        ]
        if cfg.cookies_file:
            download_cmd.extend(["--cookies", cfg.cookies_file])
        logger.debug(f"Running command {' '.join(download_cmd)}")
        res = subprocess.run(download_cmd, capture_output=True, text=True)
        if res.returncode == 0:
            _save_cache_entry(cfg, cache_key)
            cache_set.add(cache_key)
            logger.info(f"Successfully processed and cached {video_id}")
        else:
            if "video is private" in (res.stdout + res.stderr):
                logger.warning(f"Cannot process video https://www.youtube.com/watch?v={video_id}. Video is private. Not adding to cache.")
            else:
                logger.error(f"Failed to process video https://www.youtube.com/watch?v={video_id}. Not adding to cache.")


def process_videos(cfg: AppConfig, logger: logging.Logger) -> None:
    """Main entry for the video processing stage.

    It ensures directories exist, loads the cache, and processes all URLs defined in the configuration.
    """
    logger.info("Starting video processing stage.")
    _ensure_directories(cfg)
    cache_set = _load_cache(cfg)
    logger.info(f"Loaded {len(cache_set)} entries from cache.")
    for url in cfg.podcast_urls:
        _process_video(url, cfg, logger, cache_set)
    logger.info("Video processing stage completed.")
