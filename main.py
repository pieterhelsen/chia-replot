# std
import logging
import subprocess

from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import Tuple

# project
from src.config import Config
from src.path import PathManager


def parse_arguments() -> Tuple[ArgumentParser, Namespace]:
    parser = ArgumentParser(
        description="chia-replot: Make room for plotman to do its thang."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--config', type=str, help="path to config.yaml")
    group.add_argument('--version', action='store_true')
    return parser, parser.parse_args()


def get_log_level(log_level: str) -> int:
    if log_level == "CRITICAL":
        return logging.CRITICAL
    if log_level == "ERROR":
        return logging.ERROR
    if log_level == "WARNING":
        return logging.WARNING
    if log_level == "INFO":
        return logging.INFO
    if log_level == "DEBUG":
        return logging.DEBUG

    logging.warning(f"Unsupported log level: {log_level}. Fallback to INFO level.")
    return logging.INFO


def init(config: Config):
    log_level = get_log_level(config.raw.get('log_level'))
    logging.basicConfig(
        format='[%(asctime)s] [%(levelname)8s] --- %(message)s (%(filename)s:%(lineno)s)',
        level=log_level,
        datefmt='%Y-%m-%d %H:%M:%S',
        filename=config.raw.get('log_file'),
    )

    logging.info(f"Starting chia-replot ({version()})")

    manager = PathManager(config)
    manager.start_loop()


def version():
    try:
        command_args = ["git", "describe", "--tags"]
        f = subprocess.Popen(command_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = f.communicate()
        return stdout.decode(encoding="utf-8").rstrip()
    except:
        return "unknown"


if __name__ == "__main__":
    # Parse config and configure logger
    argparse, args = parse_arguments()

    if args.config:
        conf = Config(Path(args.config))
        init(conf)
    elif args.version:
        print(version())
