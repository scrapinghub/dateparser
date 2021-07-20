import sys
import logging

from .fasttext_manager import fasttext_downloader
from .utils import clear_cache


_cli_functions_map = {
    "fasttext": fasttext_downloader,
    "clear_cache": clear_cache
}


def no_matching_command_found(msg=None):
    msg = msg or "No matching command found"
    logging.error("dateparser-download: {}".format(msg))


def entrance():
    args = sys.argv[1:]
    if args:
        if args[0] in _cli_functions_map:
            _cli_functions_map[args[0]](args[1:])
        else:
            no_matching_command_found()
    else:
        no_matching_command_found(msg="To use dateparser-download you have to specify the integration and the model")
