import sys
from .fasttext_manager import fasttext_downloader

_cli_functions_map = {
    "fasttext": fasttext_downloader
}


def no_matching_command_found():
    print("No dateparser-download command found")


def entrance():
    args = sys.argv[1:]

    if args:
        if args[0] in _cli_functions_map:
            _cli_functions_map[args[0]](args[1:])
        else:
            no_matching_command_found()
    else:
        no_matching_command_found()
