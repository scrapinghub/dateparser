from __future__ import annotations

import re
from typing import TYPE_CHECKING

from dateparser.timezone_parser import _build_tz_regexes, pop_tz_offset_from_string

if TYPE_CHECKING:
    from pytest_codspeed import BenchmarkFixture


def test_timezone_regexes_first_use(benchmark: BenchmarkFixture) -> None:
    def first_use() -> tuple[str, str | None]:
        _build_tz_regexes.cache_clear()
        # re caches compiled patterns, which would otherwise turn every
        # compilation after the first one into a lookup.
        re.purge()
        return pop_tz_offset_from_string("10 Jan 2020 10:00 EST", as_offset=False)

    assert first_use() == ("10 Jan 2020 10:00 ", "EST")

    benchmark(first_use)
