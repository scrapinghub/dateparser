from datetime import datetime, timedelta
from unittest.mock import patch
from zoneinfo import ZoneInfo

import pytest
import pytz

from dateparser import parse


@pytest.mark.parametrize("timezone_factory", [pytz.timezone, ZoneInfo])
@pytest.mark.parametrize("month, offset", [(1, 1), (6, 2)])
@pytest.mark.parametrize("to_timezone", [None, "UTC"])
@pytest.mark.parametrize("aware", [False, True])
def test_local_timezone_offset(timezone_factory, month, offset, to_timezone, aware):
    local_timezone = timezone_factory("Europe/Warsaw")
    settings = {"TIMEZONE": "local", "RETURN_AS_TIMEZONE_AWARE": aware}
    if to_timezone:
        settings["TO_TIMEZONE"] = to_timezone

    with patch("dateparser.date_parser.get_localzone", return_value=local_timezone):
        result = parse(
            f"2024-{month:02}-15 12:00:00", languages=["en"], settings=settings
        )

    expected_hour = 12 - offset if to_timezone else 12
    assert result.replace(tzinfo=None) == datetime(2024, month, 15, expected_hour)
    if aware:
        assert result.utcoffset() == timedelta(hours=0 if to_timezone else offset)
    else:
        assert result.tzinfo is None


def test_modern_local_timezone_does_not_use_legacy_localize():
    class ModernTimezone(ZoneInfo):
        def localize(self, dt):
            raise AssertionError("Modern timezones do not require localize()")

    # Compatibility shims may expose a deprecated localize method even though
    # they implement the modern tzinfo interface.
    local_timezone = ModernTimezone("Europe/Warsaw")
    with patch("dateparser.date_parser.get_localzone", return_value=local_timezone):
        result = parse(
            "2024-06-15 12:00:00",
            languages=["en"],
            settings={"TIMEZONE": "local", "RETURN_AS_TIMEZONE_AWARE": True},
        )

    assert result == datetime(2024, 6, 15, 12, tzinfo=local_timezone)
    assert result.utcoffset() == timedelta(hours=2)
