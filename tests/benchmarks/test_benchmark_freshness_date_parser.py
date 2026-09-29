r"""Benchmarks for :mod:`dateparser.freshness_date_parser`.

``PATTERN`` matches a number followed by a time unit, and is applied to the whole
input string by ``findall()`` (in ``get_kwargs()``) and by ``sub()`` (in
``_parse_time()``). Until #1335 it spelled the number as the greedy
``\d+[.,]?\d*``, whose adjacent digit quantifiers backtrack without ever
changing the match, so the cost grew superlinearly with the length of a digit
run. #1335 made the quantifiers possessive (``\d++[.,]?\d*+``).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from dateparser.freshness_date_parser import PATTERN, freshness_date_parser
from tests.benchmarks import LONG_DIGIT_RUN, TRANSLATED_RELATIVE_STRINGS

if TYPE_CHECKING:
    from pytest_codspeed import BenchmarkFixture


def test_freshness_pattern_findall(benchmark: BenchmarkFixture) -> None:
    def run():
        for date_string in TRANSLATED_RELATIVE_STRINGS:
            PATTERN.findall(date_string)

    # Guard against measuring a no-op: were PATTERN to stop matching these
    # inputs, the benchmark would get faster instead of failing.
    assert PATTERN.findall(TRANSLATED_RELATIVE_STRINGS[-1]) == [
        ("1", "day"),
        (" 2", "hour"),
        (" 3", "minute"),
        (" 4", "second"),
    ]

    benchmark(run)


def test_freshness_pattern_findall_long_digit_run(benchmark: BenchmarkFixture) -> None:
    assert PATTERN.findall(LONG_DIGIT_RUN) == []

    benchmark(lambda: PATTERN.findall(LONG_DIGIT_RUN))


def test_freshness_pattern_sub_long_digit_run(benchmark: BenchmarkFixture) -> None:
    """``_parse_time()`` runs ``PATTERN.sub()`` over the input as well."""
    assert PATTERN.sub("", LONG_DIGIT_RUN) == LONG_DIGIT_RUN

    benchmark(lambda: PATTERN.sub("", LONG_DIGIT_RUN))


def test_freshness_get_kwargs(benchmark: BenchmarkFixture) -> None:
    def run():
        for date_string in TRANSLATED_RELATIVE_STRINGS:
            freshness_date_parser.get_kwargs(date_string)

    kwargs, _ = freshness_date_parser.get_kwargs(TRANSLATED_RELATIVE_STRINGS[1])
    assert kwargs == {"hours": 2.0, "minutes": 50.0}

    benchmark(run)
