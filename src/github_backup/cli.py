import argparse
import sys
import logging
from dotenv import load_dotenv
from tglogging import configure_logger, LoggingConfig

from .config import load_app_config
from .stages.auth import check_auth
from .stages.backup import backup_repos

def main(argv: list = None) -> None:
    load_dotenv()
    parser = argparse.ArgumentParser(description='GitHub Backup CLI')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable debug output')
    subparsers = parser.add_subparsers(dest='command', required=True)

    subparsers.add_parser('auth', help='Check GitHub CLI authentication')
    subparsers.add_parser('backup', help='Run the backup process')
    subparsers.add_parser('run', help='Check auth and run backup')

    args = parser.parse_args(argv)
    cfg = load_app_config()
    
    # Setup logger
    tg_cfg = LoggingConfig(
        log_file_path=cfg.log_file_path,
        telegram_bot_token=cfg.telegram_bot_token,
        level_chat_ids=cfg.level_chat_ids,
    )
    logger = configure_logger('github_backup', tg_cfg, verbose=args.verbose)

    try:
        if args.command == 'auth':
            if not check_auth(cfg, logger):
                sys.exit(1)
        elif args.command == 'backup':
            summary = backup_repos(cfg, logger)
            if summary:
                logger.priority_info(summary)
                if not summary.success:
                    sys.exit(1)
            else:
                sys.exit(1)
        elif args.command == 'run':
            if not check_auth(cfg, logger):
                logger.error("Authentication failed. Cannot proceed with backup.")
                sys.exit(1)
            
            summary = backup_repos(cfg, logger)
            if summary:
                logger.priority_info(summary)
                if not summary.success:
                    sys.exit(1)
            else:
                sys.exit(1)
        else:
            parser.print_help()
    except KeyboardInterrupt:
        logger.warning("Process interrupted by user (Ctrl+C). Exiting...")
        sys.exit(130)  # Standard exit code for SIGINT

if __name__ == '__main__':
    main()
