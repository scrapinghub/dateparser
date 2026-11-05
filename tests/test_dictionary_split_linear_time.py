from typing import Any
from unittest.mock import patch

import pytest

from dateparser.conf import settings
from dateparser.languages import default_loader
from dateparser.languages.dictionary import Dictionary


class MatchSpy:
    """Wraps the compiled regular expression that finds the next known word."""

    def __init__(self, pattern: Any) -> None:
        self.pattern = pattern
        self.strings: list[str] = []
        self.starts: list[int] = []

    def match(self, string: str, pos: int = 0, *args: Any, **kwargs: Any) -> Any:
        self.strings.append(string)
        self.starts.append(pos)
        return self.pattern.match(string, pos, *args, **kwargs)


@pytest.mark.parametrize(
    ("shortname", "text"),
    [
        ("en", "Jan " * 200 + "x"),
        ("en", "Jan\n" * 200),
        ("en", "Jan1" * 200),
        ("ja", "月曜日" * 200),
        ("ja", "月曜日\n" * 200 + "x"),
        ("zh", "1月" * 200),
    ],
)
def test_known_words_are_found_in_place(shortname: str, text: str) -> None:
    # Cutting the text that was not matched yet off the string after each known
    # word copies it every time, which takes quadratic time on a long string.
    dictionary = Dictionary(default_loader.get_locale(shortname).info, settings)
    spy = MatchSpy(dictionary._get_split_regex_cache())

    with patch.object(Dictionary, "_get_split_regex_cache", return_value=spy):
        tokens = dictionary.split(text, keep_formatting=True)

    assert "".join(tokens) == text
    assert len(spy.starts) > 100
    assert all(string is text for string in spy.strings)
    assert spy.starts == sorted(spy.starts)
    assert len(set(spy.starts)) == len(spy.starts)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        (" x", [" x"]),
        ("Janx", ["Janx"]),
        ("xJan", ["xJan"]),
        ("Jan1", ["Jan", "1"]),
        ("Jan, Feb", ["Jan", ",", " ", "Feb"]),
        (",,\n", [",", ",", "\n"]),
        ("Jan,\nFeb", ["Jan", ",", "\n", "Feb"]),
        ("Jan\n\nFeb", ["Jan", "\n\n", "Feb"]),
    ],
)
def test_split_keeps_formatting(text: str, expected: list[str]) -> None:
    dictionary = Dictionary(default_loader.get_locale("en").info, settings)
    assert dictionary.split(text, keep_formatting=True) == expected
