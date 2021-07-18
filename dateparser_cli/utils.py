import os


DEFAULT_CACHE_DIR = os.environ.get("DEFAULT_CACHE_DIR", '~/.cache')
DEFAULT_DIR_NAME = os.environ.get("DEFAULT_DIR_NAME", 'date_parser_models')

date_parser_model_home = os.path.expanduser(os.path.join(DEFAULT_CACHE_DIR, DEFAULT_DIR_NAME))

if not os.path.isdir(date_parser_model_home):
    os.mkdir(date_parser_model_home)


def clear_cache(*args):
    from pathlib import Path
    for path in Path(date_parser_model_home).rglob('*.*'):
        os.remove(path)

    print("dateparser-download: All cache deleted")
