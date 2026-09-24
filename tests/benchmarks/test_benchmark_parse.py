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

# Dates in languages other than English, so that language autodetection does
# real work before the date is parsed.
AUTODETECTED_DATE_STRINGS = [
    "13 août 2014",
    "Le 11 Décembre 2014 à 09:00",
    "13 Setembro, 2014",
    "1 Ноябрь 2014",
    "2014年04月08日",
    "11 Ağustos, 2014",
    "hace 2 horas",
    "vor 3 Tagen",
]

# Values that a scraped date field carries in practice but that are not dates.
UNPARSEABLE_STRINGS = [
    "—",
    "TBD",
    "Unknown",
    "Out of stock",
    "v2.3.1",
    "Updated regularly, check back soon",
    "2019-11-29 08:08-08",
]


def _benchmark_parse(
    benchmark: BenchmarkFixture, date_strings: list[str], parses: bool = True
) -> None:
    def run():
        for date_string in date_strings:
            dateparser.parse(date_string)

    # Load the locale data and warm the parser caches outside the measurement.
    run()

    for date_string in date_strings:
        assert (dateparser.parse(date_string) is not None) is parses, date_string

    benchmark(run)


def test_parse_relative_date_strings(benchmark: BenchmarkFixture) -> None:
    _benchmark_parse(benchmark, RELATIVE_DATE_STRINGS)


def test_parse_absolute_date_strings(benchmark: BenchmarkFixture) -> None:
    _benchmark_parse(benchmark, ABSOLUTE_DATE_STRINGS)


def test_parse_autodetected_date_strings(benchmark: BenchmarkFixture) -> None:
    _benchmark_parse(benchmark, AUTODETECTED_DATE_STRINGS)


def test_parse_unparseable_strings(benchmark: BenchmarkFixture) -> None:
    _benchmark_parse(benchmark, UNPARSEABLE_STRINGS, parses=False)
