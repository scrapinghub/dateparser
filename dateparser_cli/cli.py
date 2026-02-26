import argparse
import logging
import warnings

from .utils import clear_cache


def entrance():
    dateparser_argparse = argparse.ArgumentParser(
        description="dateparser download manager."
    )
    dateparser_argparse.add_argument(
        "--fasttext",
        type=str,
        help="[DEPRECATED] fastText is no longer supported. Please use langdetect instead.",
    )
    dateparser_argparse.add_argument(
        "--clear",
        "--clear-cache",
        help="To clear all cached models",
        action="store_true",
    )

    args = dateparser_argparse.parse_args()

    if args.clear:
        clear_cache()
        logging.info("dateparser-download: All cache deleted")

    if args.fasttext:
        warnings.warn(
            "fastText support has been removed as the library is archived and unmaintained. "
            "Please migrate to langdetect. Install with: pip install dateparser[langdetect]",
            DeprecationWarning,
            stacklevel=2,
        )
        dateparser_argparse.error(
            "fastText is no longer supported. Please use langdetect for language detection."
        )

    if not (args.clear or args.fasttext):
        dateparser_argparse.error(
            "dateparser-download: You need to specify the command (i.e.: --clear)"
        )
