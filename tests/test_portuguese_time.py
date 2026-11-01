from datetime import datetime

import pytest

from dateparser import parse

BASE = {"RELATIVE_BASE": datetime(2026, 6, 15)}


@pytest.mark.parametrize(
    "date_string, expected",
    [
        ("14h", datetime(2026, 6, 15, 14, 0)),
        ("14h30", datetime(2026, 6, 15, 14, 30)),
        ("\u00e0s 14h", datetime(2026, 6, 15, 14, 0)),
        ("\u00e0s 14h30", datetime(2026, 6, 15, 14, 30)),
        ("3 de dezembro de 2026 \u00e0s 14h30", datetime(2026, 12, 3, 14, 30)),
        ("22 de dezembro de 2014 \u00e0s 02:38", datetime(2014, 12, 22, 2, 38)),
    ],
)
def test_hour_marker_is_a_time_of_day(date_string, expected):
    assert parse(date_string, languages=["pt"], settings=BASE) == expected


@pytest.mark.parametrize(
    "date_string, expected",
    [
        ("h\u00e1 14h", datetime(2026, 6, 14, 10, 0)),
        ("h\u00e1 2 horas", datetime(2026, 6, 14, 22, 0)),
    ],
)
def test_hour_marker_after_ha_is_still_a_duration(date_string, expected):
    assert parse(date_string, languages=["pt"], settings=BASE) == expected
