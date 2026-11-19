import datetime
from collections.abc import Set as AbstractSet
from itertools import product
from time import process_time
from typing import Any
from unittest.mock import patch

from parameterized import param, parameterized

import dateparser.languages.locale as locale_module
from dateparser.conf import settings as default_settings
from dateparser.languages.loader import default_loader
from dateparser.search import search_dates
from dateparser.search.search import _clean_substring
from tests import BaseTestCase

relative_base = datetime.datetime(2020, 2, 13, 20, 7, 6)


class TestLongRunsOfBrackets(BaseTestCase):
    """Long runs of brackets: the work is counted, instead of timed, as the
    number of times a token is looked at."""

    def setUp(self) -> None:
        super().setUp()
        self.locale = default_loader.get_locale("en")

    def count_enclosed_time_checks(self, text: str) -> int:
        """Return how many times the tokens of *text* are looked at to find
        out whether they belong to a group of brackets."""
        calls = 0
        enclosed_time = locale_module._ENCLOSED_TIME

        class CountingPattern:
            @staticmethod
            def fullmatch(token: str) -> Any:
                nonlocal calls
                calls += 1
                return enclosed_time.fullmatch(token)

        with patch.object(locale_module, "_ENCLOSED_TIME", CountingPattern):
            self.locale.translate_search(text, settings=default_settings)
        return calls

    @parameterized.expand([("(UTC ",), ("[UTC ",), ("(12:00 ",), ("(1 ",), ("(Mon ",)])
    def test_groups_are_scanned_once(self, unit: str) -> None:
        # Each group was scanned up to the end of the text, to find out where
        # it closes: about 125 000 checks for 500 groups.
        groups = 500
        self.assertLessEqual(self.count_enclosed_time_checks(unit * groups), 4 * groups)

    def test_weekdays_before_a_group_are_checked_once(self) -> None:
        # Every group looked again at all the tokens before it, to find out
        # whether they are only weekdays: about 250 000 checks for 500 groups.
        # A check strips PUNCTUATION + " " from a token, so those are counted.
        calls = 0

        class CountingPunctuation(str):
            __slots__ = ()

            def __add__(self, other: str) -> str:
                nonlocal calls
                calls += 1
                return str.__add__(self, other)

        groups = 500
        with patch.object(
            locale_module, "PUNCTUATION", CountingPunctuation(locale_module.PUNCTUATION)
        ):
            self.locale.translate_search("(Mon " * groups, settings=default_settings)
        self.assertLessEqual(calls, 4 * groups)

    @parameterized.expand(
        [
            param(
                text="(UTC (UTC (UTC",
                expected=(["(UTC", "(UTC", "(UTC"], ["(UTC", "(UTC", "(UTC"]),
            ),
            param(
                text="8 May 2020 (UTC) (Mon) (UTC",
                expected=(
                    ["8 may 2020 (UTC) (monday)", "(UTC"],
                    ["8 May 2020 (UTC) (Mon)", "(UTC"],
                ),
            ),
            param(
                text="8 May 2020 (Mon (UTC 5pm) (1 Jan 2021)",
                expected=(
                    ["8 may 2020 (monday (UTC 5pm)", "(1 january 2021)"],
                    ["8 May 2020 (Mon (UTC 5pm)", "(1 Jan 2021)"],
                ),
            ),
            param(
                text="8 May 2020 (Mon (UTC) 5pm) (Tue",
                expected=(
                    ["8 may 2020 (monday (UTC) 5pm)", "(tuesday"],
                    ["8 May 2020 (Mon (UTC) 5pm)", "(Tue"],
                ),
            ),
            param(
                text="),on  (, / (UTC ",
                expected=(["", "/", "(UTC"], ["),on", "/", "(UTC"]),
            ),
            param(
                text='UTC, pm) (+02:00, (UTC,  ", (am)), ] UTC)',
                expected=(
                    ["UTC, pm)", "(+02:00, (UTC,", "(am)),", "UTC)"],
                    ["UTC, pm)", "(+02:00, (UTC,", "(am)), ]", "UTC)"],
                ),
            ),
            param(
                text="on, (am, in [UTC] ",
                expected=(["(am, [UTC]"], ["on, (am, in [UTC]"]),
            ),
            param(
                text="8 May 2020 (Mon) (am) (UTC",
                expected=(
                    ["8 may 2020 (monday) (am)", "(UTC"],
                    ["8 May 2020 (Mon) (am)", "(UTC"],
                ),
            ),
            param(
                text="Thu (12 Feb 2016) (UTC+1)",
                expected=(
                    ["thursday (12 february 2016)", "(utc+1)"],
                    ["Thu (12 Feb 2016)", "(UTC+1)"],
                ),
            ),
        ]
    )
    def test_translate_search_of_groups(
        self, text: str, expected: tuple[list[str], list[str]]
    ) -> None:
        translated, original = self.locale.translate_search(
            text, settings=default_settings
        )
        self.assertEqual((translated, original), expected)

    def test_search_dates_of_unclosed_groups(self) -> None:
        self.assertIsNone(search_dates("(UTC " * 300, languages=["en"]))
        self.assertEqual(
            search_dates(
                "8 May 2020 (16:05) " + "(UTC " * 300,
                languages=["en"],
                settings={"RELATIVE_BASE": relative_base},
            ),
            [("8 May 2020 (16:05)", datetime.datetime(2020, 5, 8, 16, 5))],
        )


def _clean_substring_by_cutting(substring: str, skip: AbstractSet[str]) -> str:
    """The straightforward version of _clean_substring: it cuts the text, and
    counts its brackets, again for every closing bracket or skipped word."""
    while True:
        substring = substring.strip(" .,:：-'\"").lstrip("([")
        closing = substring[-1:]
        if closing in {")", "]"} and substring.count(closing) > substring.count(
            "(" if closing == ")" else "["
        ):
            substring = substring[:-1]
            continue
        first, _, rest = substring.partition(" ")
        if rest and first in skip and not any(char.isalnum() for char in first):
            substring = rest
            continue
        rest, _, last = substring.rpartition(" ")
        if rest and last in skip and not any(char.isalnum() for char in last):
            substring = rest
            continue
        return substring


class TestCleanSubstring(BaseTestCase):
    @parameterized.expand(
        [
            param(text="May 5", expected="May 5"),
            param(text=" (May 5) ", expected="May 5"),
            param(text="May 5 (5pm)", expected="May 5 (5pm)"),
            param(text="May 5 (5pm))", expected="May 5 (5pm)"),
            param(text="May 5 (5pm]", expected="May 5 (5pm"),
            param(text="May 5 [5pm])]", expected="May 5 [5pm]"),
            param(text="May 5 ) ] ).", expected="May 5"),
            param(text="/ May 5 / /", expected="May 5"),
            param(text="/ ) / May 5 ) /", expected=") / May 5"),
            param(text="( May 5", expected=" May 5"),
            param(text="", expected=""),
            param(text=")))", expected=""),
        ]
    )
    def test_clean_substring(self, text: str, expected: str) -> None:
        self.assertEqual(_clean_substring(text, {"/"}), expected)

    @parameterized.expand(
        [
            param(skip={"/"}),
            param(skip={"(", ")"}),
            param(skip={"/)", "(/", "]", "[/"}),
        ]
    )
    def test_short_texts_like_cutting_the_text(self, skip: set[str]) -> None:
        # Skipped words may hold brackets: they are not counted any more
        # once they are dropped.
        for length in range(7):
            for chars in product(" ()[]/a", repeat=length):
                text = "".join(chars)
                self.assertEqual(
                    _clean_substring(text, skip),
                    _clean_substring_by_cutting(text, skip),
                    (text, skip),
                )

    @parameterized.expand([(")",), (")]",), (" )",), ("]) ",)])
    def test_many_unbalanced_closing_brackets(self, closing: str) -> None:
        # Every closing bracket was dropped on its own, counting the brackets
        # of the whole text: several seconds of CPU time for 200 000 of them,
        # against less than 0.05 s now. The bound is about 10 times away from
        # both.
        text = "Jan 5" + closing * (200_000 // len(closing))
        start = process_time()
        self.assertEqual(_clean_substring(text, set()), "Jan 5")
        self.assertLess(process_time() - start, 0.5)

    def test_long_word_is_looked_up_once(self) -> None:
        # The first word was looked up in *skip* again for each word dropped
        # at the end: 2000 times the length of the word, about 20 million.
        class MeasuringSet(set[str]):
            looked_up = 0

            def __contains__(self, word: object) -> bool:
                self.looked_up += len(str(word))
                return super().__contains__(word)

        word = "x" * 10_000
        skip = MeasuringSet({"/"})
        self.assertEqual(_clean_substring(word + " /" * 2000, skip), word)
        self.assertLessEqual(skip.looked_up, 2 * len(word))

    def test_search_dates_with_many_closing_brackets(self) -> None:
        self.assertEqual(
            search_dates(
                "Jan 5" + ")" * 20_000,
                languages=["en"],
                settings={"RELATIVE_BASE": relative_base},
            ),
            [("Jan 5", datetime.datetime(2020, 1, 5))],
        )
