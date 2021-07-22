import argparse

from .fasttext_manager import fasttext_downloader
from .utils import clear_cache
from .exceptions import CommandNotFound


_cli_functions_map = {
    "fasttext": fasttext_downloader,
    "clear_cache": clear_cache
}


def no_matching_command_found(msg=None):
    msg = msg or "No matching command found"
    raise CommandNotFound(msg)


def entrance():
    dateparser_argparse = argparse.ArgumentParser(
        description='dateparser-download menager.', usage="dateparser-download [-h] [--fasttext] [--clear-cache]"
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
        _cli_functions_map["fasttext"](args.fasttext)
    elif args.clear:
        _cli_functions_map["clear_cache"]()
    else:
        no_matching_command_found(msg="To use dateparser-download you have to specify the integration and the model")
