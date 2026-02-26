"""
Deprecated fastText language detection module.

This module is deprecated as the fastText library is archived and unmaintained.
Please use langdetect instead.
"""

import warnings

warnings.warn(
    "fastText support is deprecated and will be removed in a future version. "
    "The fastText library is archived and unmaintained. "
    "Please migrate to langdetect: from dateparser.custom_language_detection.langdetect import detect_languages",
    DeprecationWarning,
    stacklevel=2,
)


def detect_languages(text, confidence_threshold):
    """
    Deprecated function. FastText support has been removed.

    Args:
        text: The text to detect languages from (unused)
        confidence_threshold: Minimum confidence threshold (unused)

    Raises:
        ImportError: Always, as fastText is no longer supported.
    """
    raise ImportError(
        "fastText is no longer supported as the library is archived and unmaintained. "
        "Please use langdetect instead:\n"
        "  pip install dateparser[langdetect]\n"
        "  from dateparser.custom_language_detection.langdetect import detect_languages"
    )
