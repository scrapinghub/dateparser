"""Benchmarks for the public :func:`dateparser.parse` entry point.

Where the other benchmark modules pin down individual regexes, these cover the
end-to-end cost a caller actually pays, so that a slowdown anywhere in the
parsing pipeline is caught too.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import dateparser

if TYPE_CHECKING:
    from pytest_codspeed import BenchmarkFixture

RELATIVE_DATE_STRINGS = [
    "2 hours ago",
    "3 days ago",
    "in 5 minutes",
    "a week ago",
    "2 months, 3 weeks ago",
]

ABSOLUTE_DATE_STRINGS = [
    "2015-06-01",
    "June 1, 2015",
    "01/06/2015",
    "1st of June 2015",
    "2015-06-01T13:00:00Z",
]


def _benchmark_parse(benchmark: BenchmarkFixture, date_strings: list[str]) -> None:
    def run():
        for date_string in date_strings:
            dateparser.parse(date_string)

    # Load the locale data and warm the parser caches outside the measurement.
    run()

    assert dateparser.parse(date_strings[0]) is not None

    benchmark(run)


def test_parse_relative_date_strings(benchmark: BenchmarkFixture) -> None:
    _benchmark_parse(benchmark, RELATIVE_DATE_STRINGS)


def test_parse_absolute_date_strings(benchmark: BenchmarkFixture) -> None:
    _benchmark_parse(benchmark, ABSOLUTE_DATE_STRINGS)
