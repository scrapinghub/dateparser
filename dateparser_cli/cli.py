import argparse
import logging

from .fasttext_manager import fasttext_downloader
from .utils import clear_cache


def entrance():
    dateparser_argparse = argparse.ArgumentParser(
        description='dateparser download manager.'"
    )
    dateparser_argparse.add_argument(
        '--fasttext',
        type=str,
        help='To download a fasttext language detection models. Supported models are "small" and "large"'
    )
    dateparser_argparse.add_argument(
        '--clear',
        '--clear-cache',
        help='To clear all cached models',
        action='store_true'
    )

    args = dateparser_argparse.parse_args()

    if args.fasttext:
        fasttext_downloader(args.fasttext)
    if args.clear:
        clear_cache()
        dateparser_argparse.error("dateparser-download: All cache deleted")
