from collections.abc import Callable
from datetime import datetime, timedelta, tzinfo
from unittest.mock import patch
from zoneinfo import ZoneInfo

import pytest
import pytz

from dateparser import parse


class ModernTimezone(ZoneInfo):
    def localize(self, dt: datetime) -> datetime:
        raise AssertionError("Modern timezones do not require localize()")


@pytest.mark.parametrize("timezone_factory", [pytz.timezone, ZoneInfo])
@pytest.mark.parametrize(("month", "offset"), [(1, 1), (6, 2)])
@pytest.mark.parametrize("to_timezone", [None, "UTC"])
@pytest.mark.parametrize("aware", [False, True])
def test_local_timezone_offset(
    timezone_factory: Callable[[str], tzinfo],
    month: int,
    offset: int,
    to_timezone: str | None,
    aware: bool,
) -> None:
    local_timezone = timezone_factory("Europe/Warsaw")
    settings = {"TIMEZONE": "local", "RETURN_AS_TIMEZONE_AWARE": aware}
    if to_timezone:
        settings["TO_TIMEZONE"] = to_timezone

    with patch("dateparser.date_parser._get_localzone", return_value=local_timezone):
        result = parse(
            f"2024-{month:02}-15 12:00:00", languages=["en"], settings=settings
        )

    assert result is not None
    expected_hour = 12 - offset if to_timezone else 12
    assert result.replace(tzinfo=None) == datetime(2024, month, 15, expected_hour)
    if aware:
        assert result.utcoffset() == timedelta(hours=0 if to_timezone else offset)
    else:
        assert result.tzinfo is None


def test_modern_local_timezone_does_not_use_legacy_localize() -> None:
    # Compatibility shims may expose a deprecated localize method even though
    # they implement the modern tzinfo interface.
    local_timezone = ModernTimezone("Europe/Warsaw")
    with patch("dateparser.date_parser._get_localzone", return_value=local_timezone):
        result = parse(
            "2024-06-15 12:00:00",
            languages=["en"],
            settings={"TIMEZONE": "local", "RETURN_AS_TIMEZONE_AWARE": True},
        )

    assert result is not None
    assert result == datetime(2024, 6, 15, 12, tzinfo=local_timezone)
    assert result.utcoffset() == timedelta(hours=2)


@pytest.mark.parametrize("timezone_factory", [pytz.timezone, ZoneInfo, ModernTimezone])
@pytest.mark.parametrize(("month", "offset"), [(1, 1), (6, 2)])
@pytest.mark.parametrize("aware_base", [False, True])
@pytest.mark.parametrize("to_timezone", [None, "UTC"])
def test_relative_local_timezone_offset(
    timezone_factory: Callable[[str], tzinfo],
    month: int,
    offset: int,
    aware_base: bool,
    to_timezone: str | None,
) -> None:
    local_timezone = timezone_factory("Europe/Warsaw")
    base = datetime(2024, month, 15, 12)
    if aware_base:
        # Construct the input independently of dateparser's localization helper.
        base = pytz.timezone("Europe/Warsaw").localize(base)
    settings = {
        "TIMEZONE": "local",
        "RELATIVE_BASE": base,
        "RETURN_AS_TIMEZONE_AWARE": True,
    }
    if to_timezone:
        settings["TO_TIMEZONE"] = to_timezone

    with patch(
        "dateparser.freshness_date_parser._get_localzone", return_value=local_timezone
    ):
        result = parse("1 hour ago", languages=["en"], settings=settings)

    assert result is not None
    expected_hour = 11 - offset if to_timezone else 11
    assert result.replace(tzinfo=None) == datetime(2024, month, 15, expected_hour)
    assert result.utcoffset() == timedelta(hours=0 if to_timezone else offset)


@pytest.mark.parametrize("timezone_factory", [pytz.timezone, ZoneInfo, ModernTimezone])
@pytest.mark.parametrize(
    ("month", "timestamp", "offset"), [(1, "1705312800", 1), (6, "1718445600", 2)]
)
@pytest.mark.parametrize("to_timezone", [None, "UTC"])
def test_timestamp_local_timezone_offset(
    timezone_factory: Callable[[str], tzinfo],
    month: int,
    timestamp: str,
    offset: int,
    to_timezone: str | None,
) -> None:
    local_timezone = timezone_factory("Europe/Warsaw")
    settings = {"TIMEZONE": "local", "RETURN_AS_TIMEZONE_AWARE": True}
    if to_timezone:
        settings["TO_TIMEZONE"] = to_timezone

    with (
        patch("dateparser.date._get_localzone", return_value=local_timezone),
        patch("dateparser.utils._get_localzone", return_value=local_timezone),
    ):
        result = parse(timestamp, languages=["en"], settings=settings)

    assert result is not None
    expected_hour = 10 if to_timezone else 10 + offset
    assert result.replace(tzinfo=None) == datetime(2024, month, 15, expected_hour)
    assert result.utcoffset() == timedelta(hours=0 if to_timezone else offset)
