import os
import logging
from pathlib import Path

from ..config import AppConfig


def generate_feed(cfg: AppConfig, logger: logging.Logger) -> None:
    """Generate the RSS feed using generss.

    The function changes the working directory to the HTML output directory,
    constructs the appropriate argument list and invokes ``generss.main``.
    """
    import generss

    logger.info("Generating RSS feed.")
    # Remember original cwd to restore later
    original_cwd = os.getcwd()
    try:
        os.chdir(cfg.html_dir)
        rss_args = [
            "--metadata",
            "--sort-creation",
            "--host",
            f"http://{cfg.hostname}/" if cfg.hostname else "",
            "--dirname",
            cfg.podcast_name,
            "--out",
            os.path.join(cfg.podcast_name, "podcast.xml"),
            "--extensions",
            "mp3",
            "--title",
            cfg.podcast_title,
            "--description",
            cfg.podcast_description,
            "--image",
            f"{cfg.podcast_name}/cover.jpg",
        ]
        ret = generss.main(rss_args)
        if ret not in (0, None):
            raise RuntimeError(f"generss returned exit code {ret}")
        logger.info("RSS feed generated successfully.")
    finally:
        os.chdir(original_cwd)
