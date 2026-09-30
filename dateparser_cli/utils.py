import sys
from pathlib import Path

DEFAULT_DIR_NAME = "dateparser_models"
DEFAULT_UNIX_CACHE_DIR = "~/.cache"

DEFAULT_WINDOWS_CACHE_DIR = Path.home() / "AppData" / "Roaming"


if sys.platform.startswith("win"):
    # For Windows:
    _cache_dir = DEFAULT_WINDOWS_CACHE_DIR
else:
    # UNIX & OS X:
    _cache_dir = DEFAULT_UNIX_CACHE_DIR

dateparser_model_home = (Path(_cache_dir) / DEFAULT_DIR_NAME).expanduser()


def clear_cache(*args):
    for path in dateparser_model_home.rglob("*.*"):
        path.unlink()
