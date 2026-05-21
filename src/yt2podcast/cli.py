import argparse
import os
import sys
from dotenv import load_dotenv
import logging
from tglogging import configure_logger, LoggingConfig

from .config import load_app_config
from .stages.update_ytdlp import update_ytdlp
from .stages.process_videos import process_videos
from .stages.generate_feed import generate_feed
from .stages.upload import upload





def main(argv: list = None) -> None:
    load_dotenv()
    parser = argparse.ArgumentParser(description='YT2Podcast command line interface')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable debug output')
    subparsers = parser.add_subparsers(dest='command', required=True)

    subparsers.add_parser('update', help='Update yt-dlp to latest version')
    subparsers.add_parser('process', help='Download and transform videos')
    subparsers.add_parser('generate', help='Generate RSS feed and .htaccess')
    subparsers.add_parser('upload', help='Upload generated files to remote host')
    subparsers.add_parser('run', help='Execute full pipeline')

    args = parser.parse_args(argv)
    cfg = load_app_config()
    # Setup logger using tglogging
    tg_cfg = LoggingConfig(
        log_file_path=cfg.log_file_path,
        telegram_bot_token=cfg.telegram_bot_token,
        level_chat_ids=cfg.level_chat_ids,
    )
    logger = configure_logger('yt2podcast', tg_cfg, verbose=args.verbose)

    if args.command == 'update':
        update_ytdlp(logger)
    elif args.command == 'process':
        process_videos(cfg, logger)
    elif args.command == 'generate':
        generate_feed(cfg, logger)
    elif args.command == 'upload':
        upload(cfg, logger)
    elif args.command == 'run':
        update_ytdlp(logger)
        process_videos(cfg, logger)
        generate_feed(cfg, logger)
        upload(cfg, logger)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
