from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime, tzinfo
from datetime import timezone as dt_timezone
from typing import Any
from unittest.mock import patch

import pytest

from dateparser.search import search_dates


class _FrozenDateTime(datetime):
    """Every call to now() sees the same instant, 2020-05-05 23:30 UTC."""

    @classmethod
    def now(cls, tz: tzinfo | None = None) -> datetime:  # type: ignore[override]
        instant = datetime(2020, 5, 5, 23, 30, tzinfo=dt_timezone.utc)
        if tz is None:
            return instant.replace(tzinfo=None)
        return instant.astimezone(tz)


@contextmanager
def _frozen_clock() -> Iterator[None]:
    # The base date comes from _now() in dateparser.utils. Before the fix,
    # dateparser.search.search read the system clock itself, so both names
    # are patched: the old code then gives the same instant as the new one.
    with (
        patch("dateparser.utils.datetime", _FrozenDateTime),
        patch("dateparser.search.search.datetime", _FrozenDateTime),
    ):
        yield


def _time_span(
    text: str, strategy: str = "split", **settings: Any
) -> dict[str, datetime]:
    with _frozen_clock():
        result = search_dates(
            text,
            languages=["en"],
            settings={
                "RETURN_TIME_SPAN": True,
                "RETURN_AS_TIMEZONE_AWARE": False,
                **settings,
            },
            strategy=strategy,
        )
    assert result is not None
    return {item[0]: item[1] for item in result if "(" in item[0]}


@pytest.mark.parametrize("strategy", ["split", "ngram"])
@pytest.mark.parametrize(
    ("zone", "start", "end"),
    [
        # In Pacific/Kiritimati (UTC+14) it is already 6 May 2020, 13:30.
        (
            "Pacific/Kiritimati",
            datetime(2020, 5, 5, 13, 30),
            datetime(2020, 5, 6, 13, 30),
        ),
        # In Pacific/Honolulu (UTC-10) it is still 5 May 2020, 13:30.
        (
            "Pacific/Honolulu",
            datetime(2020, 5, 4, 13, 30),
            datetime(2020, 5, 5, 13, 30),
        ),
    ],
)
def test_time_span_is_relative_to_the_timezone_setting(
    strategy: str, zone: str, start: datetime, end: datetime
) -> None:
    assert _time_span("see you past 1 day", strategy, TIMEZONE=zone) == {
        "past 1 day (start)": start,
        "past 1 day (end)": end,
    }


def test_relative_base_takes_precedence_over_the_timezone_setting() -> None:
    assert _time_span(
        "see you past 1 day",
        TIMEZONE="Pacific/Kiritimati",
        RELATIVE_BASE=datetime(2019, 1, 10, 12, 0),
    ) == {
        "past 1 day (start)": datetime(2019, 1, 9, 12, 0),
        "past 1 day (end)": datetime(2019, 1, 10, 12, 0),
    }


def test_local_timezone_keeps_the_system_clock() -> None:
    assert _time_span("see you past 1 day", TIMEZONE="local") == {
        "past 1 day (start)": datetime(2020, 5, 4, 23, 30),
        "past 1 day (end)": datetime(2020, 5, 5, 23, 30),
    }
