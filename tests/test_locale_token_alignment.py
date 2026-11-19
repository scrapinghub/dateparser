import datetime
from unittest.mock import patch

from parameterized import param, parameterized

from dateparser.conf import settings
from dateparser.languages import default_loader
from dateparser.languages.locale import Locale
from dateparser.search import search_dates
from tests import BaseTestCase
from tests.linear_time import assert_fast

SETUP = """
from dateparser.conf import settings
from dateparser.languages import default_loader
from dateparser.search import search_dates
locale = default_loader.get_locale("en")
"""

# U+FDFA is four words once normalized; a U+00B4 glued to letters on both
# sides gets a word break after it.
FDFA = "ﷺ"
ACUTE = "´"


def _align_tokens(
    original: list[str], simplified: list[str]
) -> tuple[list[str], list[str]]:
    """Run Locale._simplify_split_align on chosen token lists: the steps that
    turn the text into tokens are replaced by stubs, the alignment is not."""
    calls = iter([original, simplified])
    locale = default_loader.get_locale("en")
    with (
        patch.object(Locale, "_break_standalone_marks", staticmethod(lambda s: s)),
        patch.object(Locale, "_simplify", lambda self, string, settings=None: string),
        patch.object(
            Locale, "_word_split", lambda self, string, settings: list(next(calls))
        ),
    ):
        return locale._simplify_split_align("text", settings)


class TestAlignTokensGolden(BaseTestCase):
    """Results of the alignment of two token lists, which do not depend on how
    the alignment is built."""

    @parameterized.expand(
        [
            param(["a", "b", "c"], ["a", "b", "c"], ["a", "b", "c"], ["a", "b", "c"]),
            param(["a", "c"], ["a", "b", "c"], ["a", "c", ""], ["a", "b", "c"]),
            param(
                ["a", "b"],
                ["a", "x", "y", "b"],
                ["a", "b", "", ""],
                ["a", "x", "y", "b"],
            ),
            param(["a"], ["a", "b", "c", "d"], ["a", "", "", ""], ["a", "b", "c", "d"]),
            param(
                ["A", "B"],
                ["a", "b", "z", "z"],
                ["A", "B", "", ""],
                ["a", "b", "z", "z"],
            ),
            param(
                ["a", "b", "c", "d"],
                ["a", "c"],
                ["a", "b", "c", "d"],
                ["a", "c", "", ""],
            ),
            param(
                ["a", "b", "c", "d", "e"],
                ["a"],
                ["a", "b", "c", "d", "e"],
                ["a", "", "", "", ""],
            ),
            param(["x", "a", "b"], ["a", "b"], ["x", "a", "b"], ["a", "", "b"]),
            param([], ["a", "b"], ["", ""], ["a", "b"]),
            param(["a", "b"], [], ["a", "b"], ["", ""]),
            param(["a", "", "b"], ["a", "b", "c"], ["a", "", "b"], ["a", "b", "c"]),
            param(
                ["p", "q", "r"],
                ["z", "z", "z", "z", "q", "r"],
                ["p", "", "", "", "q", "r"],
                ["z", "z", "z", "z", "q", "r"],
            ),
            param(
                ["a", "b", "c", "d"],
                ["a", "b", "c"],
                ["a", "b", "c", "d"],
                ["a", "b", "c", ""],
            ),
            param(
                ["a", "x", "b", "y", "c"],
                ["a", "b", "c"],
                ["a", "x", "b", "y", "c"],
                ["a", "b", "", "", "c"],
            ),
            param(
                ["É", "b"],
                ["e", "1", "2", "b"],
                ["É", "b", "", ""],
                ["e", "1", "2", "b"],
            ),
            param(
                ["a", "b", "c"],
                ["a", "1", "2", "3", "b", "c", "4"],
                ["a", "b", "", "", "", "c", ""],
                ["a", "1", "2", "3", "b", "c", "4"],
            ),
        ]
    )
    def test_alignment_of_token_lists(
        self,
        original: list[str],
        simplified: list[str],
        expected_original: list[str],
        expected_simplified: list[str],
    ) -> None:
        self.assertEqual(
            (expected_original, expected_simplified),
            _align_tokens(original, simplified),
        )


class TestAlignTextGolden(BaseTestCase):
    @parameterized.expand(
        [
            param(
                "en",
                f"a {FDFA} b",
                ["a", "", "", "", FDFA, "b"],
                ["1", "صلى", "الله", "عليه", "وسلم", "b"],
            ),
            param("en", f"a{ACUTE}b 5", [f"a{ACUTE}", "b", "5"], ["1", "b", "5"]),
            param("en", f"C{ACUTE}1997", [f"C{ACUTE}", "1997"], ["c", "1997"]),
            param(
                "en",
                f"Sep 15 {FDFA} 2026",
                ["Sep", "15", FDFA, "", "", "", "2026"],
                ["sep", "15", "صلى", "الله", "عليه", "وسلم", "2026"],
            ),
            param(
                "en",
                f"{FDFA} {FDFA} x",
                [FDFA, "", "", "", "", "", "", FDFA, "x"],
                ["صلى", "الله", "عليه", "وسلم", "صلى", "الله", "عليه", "وسلم", "x"],
            ),
            param(
                "en",
                f"x {ACUTE} y {ACUTE}z",
                ["x", ACUTE, "y", f"{ACUTE}z"],
                ["x", "y", "", "z"],
            ),
            param(
                "en",
                "Ⅻ № 5 ½ x",
                ["Ⅻ", "№", "5", "½", "x"],
                ["xii", "no", "5", "1⁄2", "x"],
            ),
            param(
                "ja",
                f"2020年5月{FDFA}3日 {ACUTE} a{ACUTE}b",
                [
                    "2020",
                    "年",
                    "5",
                    "月",
                    FDFA,
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "3",
                    "日",
                    " ",
                    ACUTE,
                    " ",
                    f"a{ACUTE}",
                    " ",
                    "b",
                ],
                [
                    "2020",
                    "年",
                    "5",
                    "月",
                    "صلى",
                    " ",
                    "الله",
                    " ",
                    "عليه",
                    " ",
                    "وسلم",
                    "3",
                    "日",
                    " ",
                    " ",
                    " ",
                    "a",
                    " ",
                    "b",
                ],
            ),
            param(
                "ar",
                f"{FDFA} 5 مايو",
                [FDFA, "", "", "", "5", "مايو"],
                ["صلى", "الله", "عليه", "وسلم", "5", "مايو"],
            ),
            param(
                "vi",
                f"năm 2020 {FDFA}",
                ["năm", "", "", "2020", FDFA],
                ["2020", "صلى", "الله", "عليه", "وسلم"],
            ),
            param(
                "de",
                f"3. März {ACUTE}2020",
                ["3.", "März", f"{ACUTE}2020"],
                ["3.", "marz", "2020"],
            ),
            param(
                "ru",
                f"5 мая {ACUTE} {FDFA}",
                ["5", "мая", ACUTE, "", "", FDFA],
                ["5", "мая", "صلى", "الله", "عليه", "وسلم"],
            ),
        ]
    )
    def test_simplify_split_align(
        self, language: str, text: str, original: list[str], simplified: list[str]
    ) -> None:
        locale = default_loader.get_locale(language)
        self.assertEqual(
            (original, simplified), locale._simplify_split_align(text, settings)
        )

    @parameterized.expand(
        [
            param("", ""),
            param(ACUTE, ACUTE),
            param(f"a{ACUTE}", f"a{ACUTE}"),
            param(f"{ACUTE}a", f"{ACUTE}a"),
            param(f"a{ACUTE}b", f"a{ACUTE} b"),
            param(f"a{ACUTE}{ACUTE}b", f"a{ACUTE} {ACUTE} b"),
            param(f"a {ACUTE}b", f"a {ACUTE}b"),
            param(f"a{ACUTE} b", f"a{ACUTE} b"),
            param(f"C{ACUTE}1997", f"C{ACUTE} 1997"),
            param(f"x{ACUTE}y{ACUTE}z", f"x{ACUTE} y{ACUTE} z"),
            param(f"{ACUTE}{ACUTE}{ACUTE}", f"{ACUTE}{ACUTE} {ACUTE}"),
            param(f"j{ACUTE * 4}", f"j{ACUTE} {ACUTE} {ACUTE} {ACUTE}"),
            param("５月３日´１０時", "５月３日´ １０時"),
        ]
    )
    def test_break_standalone_marks(self, text: str, expected: str) -> None:
        self.assertEqual(expected, Locale._break_standalone_marks(text))

    @parameterized.expand(
        [
            param(
                "Sep 15 2026 ﷺ 3 July 2021",
                "en",
                [
                    ("Sep 15 2026", datetime.datetime(2026, 9, 15)),
                    ("3 July 2021", datetime.datetime(2021, 7, 3)),
                ],
            ),
            param(
                "on 15 September 2026 ﷺ ﷺ and 3 July 2021",
                "en",
                [
                    ("on 15 September 2026", datetime.datetime(2026, 9, 15)),
                    ("and 3 July 2021", datetime.datetime(2021, 7, 3)),
                ],
            ),
            param(
                "meeting C´1997 on 5 May 2020",
                "en",
                [
                    ("1997", datetime.datetime(1997, 6, 15)),
                    ("on 5 May 2020", datetime.datetime(2020, 5, 5)),
                ],
            ),
            param(
                "Call me on 5 May 2020´ or 7 June 2021",
                "en",
                [
                    ("on 5 May 2020´", datetime.datetime(2020, 5, 5)),
                    ("7 June 2021", datetime.datetime(2021, 6, 7)),
                ],
            ),
            param(
                "5 мая 2020 ﷺ 7 июня 2021",
                "ru",
                [
                    ("5 мая 2020", datetime.datetime(2020, 5, 5)),
                    ("7 июня 2021", datetime.datetime(2021, 6, 7)),
                ],
            ),
        ]
    )
    def test_search_dates(
        self,
        text: str,
        language: str,
        expected: list[tuple[str, datetime.datetime]],
    ) -> None:
        self.assertEqual(
            expected,
            search_dates(
                text,
                languages=[language],
                settings={"RELATIVE_BASE": datetime.datetime(2020, 6, 15, 12)},
            ),
        )


class TestAlignmentLinearTime:
    """A text whose normalized form has many more words than the text itself
    (U+FDFA is four words) is aligned with the words of the text; the time of
    that must grow in proportion to the length of the text."""

    def test_align_words_added_by_normalization(self) -> None:
        assert_fast(
            SETUP,
            [
                f"locale._simplify_split_align('j ' + {FDFA + ' '!r} * {n}, settings)"
                for n in (6_000, 12_000, 24_000)
            ],
        )

    def test_search_dates_words_added_by_normalization(self) -> None:
        assert_fast(
            SETUP,
            [
                f"search_dates('j ' + {FDFA + ' '!r} * {n}, languages=['en'])"
                for n in (6_000, 12_000, 24_000)
            ],
            limit=2.5,
            deadline=30.0,
        )

    def test_break_standalone_marks(self) -> None:
        assert_fast(
            SETUP,
            [
                f"locale._break_standalone_marks('j' + {ACUTE!r} * {n})"
                for n in (50_000, 100_000, 200_000)
            ],
        )

    def test_align_words_added_by_breaking_marks(self) -> None:
        # The other direction: the text has more words than its normalized
        # form, because every U+00B4 glued to the letters gets a break after it
        # while the normalization drops it, so the simplified words are padded.
        assert_fast(
            SETUP,
            [
                f"locale._simplify_split_align('j' + {ACUTE!r} * {n}, settings)"
                for n in (50_000, 100_000, 200_000)
            ],
        )

    def test_search_dates_words_added_by_breaking_marks(self) -> None:
        assert_fast(
            SETUP,
            [
                f"search_dates('j' + {ACUTE!r} * {n}, languages=['en'])"
                for n in (48_000, 96_000, 192_000)
            ],
            limit=2.5,
            deadline=30.0,
        )
