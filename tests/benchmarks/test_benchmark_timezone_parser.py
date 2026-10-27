from __future__ import annotations

import re
from typing import TYPE_CHECKING

from dateparser.timezone_parser import _build_tz_regexes, pop_tz_offset_from_string

if TYPE_CHECKING:
    from pytest_codspeed import BenchmarkFixture

# A long run of timezone names. pop_tz_offset_from_string used to strip
# equivalent tokens in a loop that rescanned the whole string once per token,
# and each scan read the matched name out of groupdict(), which builds an entry
# for every timezone name on every match, so the cost grew quadratically with
# the number of tokens. 100 tokens takes ~370ms that way against under 1ms now:
# a regression shows up as a ~400x jump while still finishing under CodSpeed.
LONG_TIMEZONE_RUN = "1 Jan 2020 10:00 " + "UTC " * 100


def test_timezone_regexes_first_use(benchmark: BenchmarkFixture) -> None:
    def first_use() -> tuple[str, str | None]:
        _build_tz_regexes.cache_clear()
        # re caches compiled patterns, which would otherwise turn every
        # compilation after the first one into a lookup.
        re.purge()
        return pop_tz_offset_from_string("10 Jan 2020 10:00 EST", as_offset=False)

    assert first_use() == ("10 Jan 2020 10:00 ", "EST")

    benchmark(first_use)


def test_pop_tz_offset_long_timezone_run(benchmark: BenchmarkFixture) -> None:
    date_string, name = pop_tz_offset_from_string(LONG_TIMEZONE_RUN, as_offset=False)
    assert name == "UTC"
    # The first token and one redundant, equivalent one are removed.
    assert date_string.count("UTC") == LONG_TIMEZONE_RUN.count("UTC") - 2

    benchmark(lambda: pop_tz_offset_from_string(LONG_TIMEZONE_RUN, as_offset=False))
