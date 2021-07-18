import sys
from .fasttext_manager import fasttext_downloader
from .utils import clear_cache


_cli_functions_map = {
    "fasttext": fasttext_downloader,
    "clear_cache": clear_cache
}


def no_matching_command_found():
    print("dateparser-download: No command found")


def entrance():
    args = sys.argv[1:]

    if args:
        if args[0] in _cli_functions_map:
            _cli_functions_map[args[0]](args[1:])
        else:
            no_matching_command_found()
    else:
        no_matching_command_found()
