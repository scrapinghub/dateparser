from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime, timedelta, tzinfo
from datetime import timezone as dt_timezone
from typing import Any
from unittest.mock import patch

import pytest

from dateparser.search import search_dates

_INSTANT = datetime(2020, 5, 5, 23, 30, tzinfo=dt_timezone.utc)
# A local time zone far from UTC, as a fixed offset that needs no tz database.
_LOCAL_ZONE = dt_timezone(timedelta(hours=14))


class _FrozenDateTime(datetime):
    """Every call to now() sees the same instant, by default 2020-05-05 23:30
    UTC."""

    instant = _INSTANT

    @classmethod
    def now(cls, tz: tzinfo | None = None) -> datetime:  # type: ignore[override]
        if tz is None:
            return cls.instant.replace(tzinfo=None)
        return cls.instant.astimezone(tz)


@contextmanager
def _frozen_clock(instant: datetime = _INSTANT) -> Iterator[None]:
    # The base date comes from _now() in dateparser.utils. Before the fix,
    # dateparser.search.search read the system clock itself, so both names
    # are patched: the old code then gives the same instant as the new one.
    with (
        patch.object(_FrozenDateTime, "instant", instant),
        patch("dateparser.utils.datetime", _FrozenDateTime),
        patch("dateparser.search.search.datetime", _FrozenDateTime),
    ):
        yield


def _time_span(
    text: str, strategy: str = "split", instant: datetime = _INSTANT, **settings: Any
) -> dict[str, datetime]:
    with _frozen_clock(instant):
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


def _as_text(dates: dict[str, datetime]) -> dict[str, str]:
    # Aware datetimes in different time zones compare equal when they are the
    # same instant, so compare their text, which also shows the offset.
    return {name: date.isoformat() for name, date in dates.items()}


@pytest.mark.parametrize("strategy", ["split", "ngram"])
def test_time_span_is_aware_with_return_as_timezone_aware(strategy: str) -> None:
    assert _as_text(
        _time_span(
            "see you past 1 day",
            strategy,
            TIMEZONE="Pacific/Kiritimati",
            RETURN_AS_TIMEZONE_AWARE=True,
        )
    ) == {
        "past 1 day (start)": "2020-05-05T13:30:00+14:00",
        "past 1 day (end)": "2020-05-06T13:30:00+14:00",
    }


@pytest.mark.parametrize("strategy", ["split", "ngram"])
@pytest.mark.parametrize(
    ("aware", "start", "end"),
    [
        (False, "2020-05-04T23:30:00", "2020-05-05T23:30:00"),
        (True, "2020-05-04T23:30:00+00:00", "2020-05-05T23:30:00+00:00"),
    ],
)
def test_time_span_is_converted_to_to_timezone(
    strategy: str, aware: bool, start: str, end: str
) -> None:
    assert _as_text(
        _time_span(
            "see you past 1 day",
            strategy,
            TIMEZONE="Pacific/Kiritimati",
            TO_TIMEZONE="UTC",
            RETURN_AS_TIMEZONE_AWARE=aware,
        )
    ) == {"past 1 day (start)": start, "past 1 day (end)": end}


_AWARE_BASE = datetime(2019, 1, 10, 12, 0, tzinfo=dt_timezone.utc)

# 2020-10-25 00:30 UTC is 02:30 CEST in Berlin, the first of the two 02:30s of
# that night: the offset of the time cannot be told from its wall clock.
_REPEATED_HOUR = datetime(2020, 10, 25, 0, 30, tzinfo=dt_timezone.utc)


def test_time_span_from_an_aware_relative_base_is_naive_when_asked() -> None:
    assert _as_text(_time_span("see you past 1 day", RELATIVE_BASE=_AWARE_BASE)) == {
        "past 1 day (start)": "2019-01-09T12:00:00",
        "past 1 day (end)": "2019-01-10T12:00:00",
    }


@pytest.mark.parametrize("strategy", ["split", "ngram"])
@pytest.mark.parametrize(
    ("to_timezone", "start", "end"),
    [
        (None, "2019-01-09T12:00:00+00:00", "2019-01-10T12:00:00+00:00"),
        ("Pacific/Honolulu", "2019-01-09T02:00:00-10:00", "2019-01-10T02:00:00-10:00"),
    ],
)
def test_time_span_from_an_aware_relative_base_stays_aware_by_default(
    strategy: str, to_timezone: str | None, start: str, end: str
) -> None:
    # As before the time zone settings applied to spans, although a relative
    # date such as "1 day" is naive here.
    result = search_dates(
        "see you past 1 day",
        languages=["en"],
        settings={
            "RETURN_TIME_SPAN": True,
            "RELATIVE_BASE": _AWARE_BASE,
            **({"TO_TIMEZONE": to_timezone} if to_timezone else {}),
        },
        strategy=strategy,
    )
    assert result is not None
    assert _as_text({item[0]: item[1] for item in result if "(" in item[0]}) == {
        "past 1 day (start)": start,
        "past 1 day (end)": end,
    }


def test_time_span_past_the_year_9999_in_to_timezone_is_not_returned() -> None:
    assert (
        _time_span(
            "see you past 1 day",
            RELATIVE_BASE=datetime(9999, 12, 31, 20, 0),
            TIMEZONE="UTC",
            TO_TIMEZONE="Pacific/Kiritimati",
            RETURN_AS_TIMEZONE_AWARE=True,
        )
        == {}
    )


@pytest.mark.parametrize(
    ("settings", "start", "end"),
    [
        (
            {"RETURN_AS_TIMEZONE_AWARE": True},
            "2020-05-05T13:30:00+14:00",
            "2020-05-06T13:30:00+14:00",
        ),
        (
            {
                "RELATIVE_BASE": datetime(2019, 1, 10, 12, 0),
                "TO_TIMEZONE": "UTC",
                "RETURN_AS_TIMEZONE_AWARE": True,
            },
            "2019-01-08T22:00:00+00:00",
            "2019-01-09T22:00:00+00:00",
        ),
    ],
)
def test_time_span_in_the_local_time_zone(
    settings: dict[str, Any], start: str, end: str
) -> None:
    # The local time zone is set to one far from UTC, so that the test tells
    # it from UTC on any machine.
    with patch("dateparser.search.search._get_localzone", lambda: _LOCAL_ZONE):
        dates = _time_span("see you past 1 day", TIMEZONE="local", **settings)
    assert _as_text(dates) == {"past 1 day (start)": start, "past 1 day (end)": end}


@pytest.mark.parametrize("strategy", ["split", "ngram"])
def test_time_span_in_the_repeated_hour_keeps_the_offset_of_the_time(
    strategy: str,
) -> None:
    assert _as_text(
        _time_span(
            "see you past 1 day",
            strategy,
            instant=_REPEATED_HOUR,
            TIMEZONE="Europe/Berlin",
            RETURN_AS_TIMEZONE_AWARE=True,
        )
    ) == {
        "past 1 day (start)": "2020-10-24T02:30:00+02:00",
        "past 1 day (end)": "2020-10-25T02:30:00+02:00",
    }


@pytest.mark.parametrize("strategy", ["split", "ngram"])
@pytest.mark.parametrize(
    ("settings", "instant"),
    [
        pytest.param({"TIMEZONE": "Pacific/Kiritimati"}, _INSTANT, id="tz"),
        pytest.param(
            {"TIMEZONE": "Pacific/Kiritimati", "RETURN_AS_TIMEZONE_AWARE": True},
            _INSTANT,
            id="tz-aware",
        ),
        pytest.param(
            {"TIMEZONE": "Pacific/Kiritimati", "TO_TIMEZONE": "UTC"},
            _INSTANT,
            id="tz-to",
        ),
        pytest.param(
            {
                "TIMEZONE": "Pacific/Kiritimati",
                "TO_TIMEZONE": "UTC",
                "RETURN_AS_TIMEZONE_AWARE": True,
            },
            _INSTANT,
            id="tz-to-aware",
        ),
        # CET is in the tz database and in dateparser's own abbreviations, with
        # different offsets in summer.
        pytest.param(
            {"TIMEZONE": "CET", "RETURN_AS_TIMEZONE_AWARE": True},
            _INSTANT,
            id="abbreviation-aware",
        ),
        pytest.param(
            {"TIMEZONE": "CET", "TO_TIMEZONE": "UTC"}, _INSTANT, id="abbreviation-to"
        ),
        pytest.param(
            {"TIMEZONE": "local", "RETURN_AS_TIMEZONE_AWARE": True},
            _INSTANT,
            id="local-aware",
        ),
        pytest.param(
            {
                "TIMEZONE": "local",
                "TO_TIMEZONE": "UTC",
                "RETURN_AS_TIMEZONE_AWARE": True,
            },
            _INSTANT,
            id="local-to-aware",
        ),
        pytest.param(
            {
                "TIMEZONE": "local",
                "RELATIVE_BASE": datetime(2019, 1, 10, 12, 0),
                "TO_TIMEZONE": "UTC",
                "RETURN_AS_TIMEZONE_AWARE": True,
            },
            _INSTANT,
            id="local-naive-base",
        ),
        pytest.param(
            {
                "TIMEZONE": "Europe/Berlin",
                "TO_TIMEZONE": "UTC",
                "RETURN_AS_TIMEZONE_AWARE": True,
            },
            _REPEATED_HOUR,
            id="repeated-hour",
        ),
        pytest.param(
            {
                "TIMEZONE": "Pacific/Honolulu",
                "RELATIVE_BASE": datetime(2019, 1, 10, 12, 0),
                "TO_TIMEZONE": "Pacific/Kiritimati",
                "RETURN_AS_TIMEZONE_AWARE": True,
            },
            _INSTANT,
            id="naive-base",
        ),
        pytest.param(
            {"RELATIVE_BASE": _AWARE_BASE, "RETURN_AS_TIMEZONE_AWARE": False},
            _INSTANT,
            id="aware-base-naive",
        ),
        pytest.param(
            {
                "RELATIVE_BASE": _AWARE_BASE,
                "TO_TIMEZONE": "Pacific/Honolulu",
                "RETURN_AS_TIMEZONE_AWARE": True,
            },
            _INSTANT,
            id="aware-base-to-aware",
        ),
    ],
)
def test_time_span_starts_at_the_date_found_for_its_quantity(
    strategy: str, settings: dict[str, Any], instant: datetime
) -> None:
    """Test that "past 1 day" starts at the date that the same call returns
    for "1 day", whatever the time zone settings are."""
    # The local time zone is set to one far from UTC in the two modules that
    # read it for these texts, so that the cases with TIMEZONE="local" tell it
    # from UTC on any machine; test_time_span_in_the_local_time_zone checks
    # that the span really uses it.
    with (
        _frozen_clock(instant),
        patch("dateparser.freshness_date_parser.datetime", _FrozenDateTime),
        patch("dateparser.search.search._get_localzone", lambda: _LOCAL_ZONE),
        patch("dateparser.freshness_date_parser._get_localzone", lambda: _LOCAL_ZONE),
    ):
        result = search_dates(
            "see you past 1 day",
            languages=["en"],
            settings={"RETURN_TIME_SPAN": True, **settings},
            strategy=strategy,
        )
    assert result is not None
    dates = {item[0]: item[1].isoformat() for item in result}
    assert dates["past 1 day (start)"] == dates["1 day"]
