"""Locale.translate removes the skip words between separators in linear time."""

import datetime

import pytest

import dateparser
from dateparser.conf import settings
from dateparser.languages import default_loader
from tests.linear_time import assert_fast

SETUP = """
import dateparser
from dateparser.conf import settings
from dateparser.date import sanitize_date
from dateparser.languages import default_loader

locale = default_loader.get_locale("en")
locale.translate("1 of 2", settings=settings)
"""

# 12,000 to 48,000 separators for translate and 6,000 to 24,000 for parse()
# followed by a third as many skip words.
PAYLOADS = [
    "'1' + ' !' * {k} + 'of!' * ({k} // 3)",
    "'1' + ' !' * {k} + ' of!' * ({k} // 3)",
    "'1' + ' ;' * {k} + 'at;' * ({k} // 3)",
]


@pytest.mark.parametrize(
    "payload", PAYLOADS, ids=["bang", "spaced-skip-word", "semicolon"]
)
def test_translate_run_of_separators_then_skip_words_is_linear(payload: str) -> None:
    assert_fast(
        SETUP,
        [
            f"locale.translate(sanitize_date({payload.format(k=k)}), settings=settings)"
            for k in (12_000, 24_000, 48_000)
        ],
        limit=1.5,
    )


@pytest.mark.parametrize("payload", PAYLOADS[:1], ids=["bang"])
def test_parse_run_of_separators_then_skip_words_is_linear(payload: str) -> None:
    assert_fast(
        SETUP,
        [f"dateparser.parse({payload.format(k=k)})" for k in (6_000, 12_000, 24_000)],
        limit=1.5,
    )


@pytest.mark.parametrize(
    ("date_string", "keep_formatting", "expected"),
    [
        ("1 ! ! !of!of!of!", False, "1   "),
        ("1 ! ! !of!of!of!", True, "1 ! ! !!!!"),
        ("1 of 2", False, "1 2"),
        ("1 ! ! ! of ! 2", False, "1   2"),
        ("1 ! ! ! of ! 2", True, "1 ! ! !  ! 2"),
        ("1 ! ! of ! ! ! 5", False, "1    5"),
        ("1 ! ! of ! ! ! 5", True, "1 ! !  ! ! ! 5"),
        ("5 ! of ! ! ! of ! !", False, "5   "),
        ("5 ! of ! ! ! of ! !", True, "5 !  ! ! !  ! !"),
        ("1!!!of!", False, "1"),
        ("jan ! ! of ! ! ! ! of 5", False, "january    5"),
        ("jan ! ! of ! ! ! ! of 5", True, "january ! !  ! ! ! !  5"),
        ("of ! ! 5", False, "   5"),
        ("5 ! ! of", True, "5 ! ! "),
        ("1 ,, of ,, ,, 2", True, "1 ,, ,, ,, 2"),
        ("1 -- of -- -- 5", False, "1 -- -- -- 5"),
        ("at ! ! of ! 5", False, "  5"),
        ("1" + " !" * 50 + "of!" * 10, False, "1" + " " * 50),
        ("1" + " !" * 5 + " of!" * 10, False, "1" + " " * 5),
    ],
)
def test_translate_keeps_the_longer_run_of_separators_around_a_skip_word(
    date_string: str, keep_formatting: bool, expected: str
) -> None:
    locale = default_loader.get_locale("en")
    assert (
        locale.translate(
            date_string, settings=settings, keep_formatting=keep_formatting
        )
        == expected
    )


@pytest.mark.parametrize(
    ("date_string", "expected"),
    [
        ("5 ! ! of ! ! ! may ! of 2021", datetime.datetime(2021, 5, 5)),
        ("jan ! ! of ! ! ! ! of 5", datetime.datetime(2020, 1, 5)),
        (
            "15 ! ! at ! ! ! ! of may 2021 ! !of ! 10:30",
            datetime.datetime(2021, 5, 15, 10, 30),
        ),
        ("in ! ! of ! ! 3 ! of ! ! days", datetime.datetime(2020, 6, 18, 12)),
    ],
)
def test_parse_with_runs_of_separators_and_skip_words(
    date_string: str, expected: datetime.datetime
) -> None:
    result = dateparser.parse(
        date_string, settings={"RELATIVE_BASE": datetime.datetime(2020, 6, 15, 12)}
    )
    assert result == expected
