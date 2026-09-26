import pytest


def test_fasttext_is_deprecated() -> None:
    with pytest.warns(DeprecationWarning):
        from dateparser.custom_language_detection import fasttext
    with pytest.raises(ImportError):
        fasttext.detect_languages("14 June 2020", 0.0)
