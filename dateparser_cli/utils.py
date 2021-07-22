import os
from pathlib import Path
import logging

DEFAULT_CACHE_DIR = os.environ.get("DEFAULT_CACHE_DIR", '~/.cache')
DEFAULT_DIR_NAME = os.environ.get("DEFAULT_DIR_NAME", 'date_parser_models')

date_parser_model_home = os.path.expanduser(os.path.join(DEFAULT_CACHE_DIR, DEFAULT_DIR_NAME))


def check_data_model_home_existance():
    if not os.path.isdir(date_parser_model_home):
        os.mkdir(date_parser_model_home)


def clear_cache(*args):
    for path in Path(date_parser_model_home).rglob('*.*'):
        os.remove(path)

    logging.info("dateparser-download: All cache deleted")
