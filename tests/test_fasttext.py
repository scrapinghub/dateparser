import pytest


def test_fasttext_is_deprecated() -> None:
    with pytest.warns(DeprecationWarning, match="fastText support is deprecated"):
        from dateparser.custom_language_detection import fasttext  # noqa: PLC0415
    with pytest.raises(ImportError):
        fasttext.detect_languages("14 June 2020", 0.0)
