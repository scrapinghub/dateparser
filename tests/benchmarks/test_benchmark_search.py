from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from dateparser.search import search_dates, search_first_date

if TYPE_CHECKING:
    from pytest_codspeed import BenchmarkFixture

# The language is given so that language detection, which both functions run
# the same way, does not dilute the difference between them.
LANGUAGES = ["en"]

TEXT = (
    "The first artificial Earth satellite was launched on 4 October 1957. "
    "It orbited for three weeks before its batteries died on 26 October 1957, "
    "and it burned up on re-entry on 4 January 1958. The second one followed "
    "on 3 November 1957, carrying a dog, and the American Explorer 1 reached "
    "orbit on 1 February 1958, after a failed attempt on 6 December 1957."
)

STRATEGIES = pytest.mark.parametrize("strategy", ["split", "ngram"])


@STRATEGIES
def test_search_dates(benchmark: BenchmarkFixture, strategy: str) -> None:
    def run():
        return search_dates(TEXT, languages=LANGUAGES, strategy=strategy)

    # Dates after the first one are what search_first_date() gets to skip.
    # Running the search here also loads the locale data and warms the parser
    # caches outside the measurement.
    assert len(run()) > 1

    benchmark(run)


@STRATEGIES
def test_search_first_date(benchmark: BenchmarkFixture, strategy: str) -> None:
    def run():
        return search_first_date(TEXT, languages=LANGUAGES, strategy=strategy)

    assert run()[0].endswith("4 October 1957")

    benchmark(run)
