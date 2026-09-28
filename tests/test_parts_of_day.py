from datetime import datetime, time

import pytest

from dateparser import PartOfDay, PartsOfDay, parse
from dateparser.conf import SettingValidationError
from dateparser.date import DateDataParser
from dateparser.search import search_dates

BASE = datetime(2026, 9, 28, 15, 0)


@pytest.mark.parametrize(
    ("date_string", "languages", "expected"),
    [
        ("tonight", ["en"], datetime(2026, 9, 28, 20, 0)),
        ("last night", ["en"], datetime(2026, 9, 27, 20, 0)),
        ("this morning", ["en"], datetime(2026, 9, 28, 9, 0)),
        ("tomorrow in the afternoon", ["en"], datetime(2026, 9, 29, 15, 0)),
        ("monday evening", ["en"], datetime(2026, 9, 28, 18, 0)),
        ("yesterday in the small hours", ["en"], datetime(2026, 9, 27, 3, 0)),
        ("Sunday, January 4, 2026 at night", ["en"], datetime(2026, 1, 4, 20, 0)),
        ("tonight at 11pm", ["en"], datetime(2026, 9, 28, 23, 0)),
        ("8 in the evening", ["en"], datetime(2026, 9, 28, 20, 0)),
        ("tomorrow at 7:30 in the morning", ["en"], datetime(2026, 9, 29, 7, 30)),
        ("12 at night", ["en"], datetime(2026, 9, 28, 0, 0)),
        ("2 at night", ["en"], datetime(2026, 9, 28, 2, 0)),
        ("January 8 in the evening", ["en"], datetime(2026, 1, 8, 18, 0)),
        ("January 8 at 9 in the evening", ["en"], datetime(2026, 1, 8, 21, 0)),
        ("2026-01-05 at night", ["en"], datetime(2026, 1, 5, 20, 0)),
        ("3 de mayo a las 5 de la madrugada", ["es"], datetime(2026, 5, 3, 5, 0)),
        ("esta madrugada", ["es"], datetime(2026, 9, 28, 3, 0)),
        ("mañana de madrugada", ["es"], datetime(2026, 9, 29, 3, 0)),
        ("ontem de madrugada", ["pt"], datetime(2026, 9, 27, 3, 0)),
        ("onte pola madrugada", ["gl"], datetime(2026, 9, 27, 3, 0)),
        ("night", ["en"], None),
        ("17 in the afternoon", ["en"], None),
    ],
)
def test_parse(date_string, languages, expected):
    settings = {"RELATIVE_BASE": BASE}
    assert parse(date_string, languages=languages, settings=settings) == expected


@pytest.mark.parametrize(
    ("date_string", "return_time_as_period", "period"),
    [
        ("tonight", True, "part_of_day"),
        ("tonight", False, "day"),
        ("tonight at 11pm", True, "time"),
    ],
)
def test_date_data(date_string, return_time_as_period, period):
    parser = DateDataParser(
        settings={"RELATIVE_BASE": BASE, "RETURN_TIME_AS_PERIOD": return_time_as_period}
    )
    date_data = parser.get_date_data(date_string)
    assert date_data.period == period
    assert date_data.part_of_day is PartOfDay.NIGHT


def test_date_data_without_part_of_day():
    date_data = DateDataParser().get_date_data("today")
    assert date_data.part_of_day is None
    assert "part_of_day" not in repr(date_data)


def test_setting():
    settings = {"RELATIVE_BASE": BASE, "PARTS_OF_DAY": PartsOfDay(night=time(22, 30))}
    assert parse("tonight", settings=settings) == datetime(2026, 9, 28, 22, 30)


def test_setting_validation():
    with pytest.raises(SettingValidationError):
        parse("tonight", settings={"PARTS_OF_DAY": {"night": time(22)}})
    with pytest.raises(TypeError):
        PartsOfDay(night="22:00")


def test_search_dates():
    assert search_dates(
        "There is a party tonight. It was a dark night.",
        languages=["en"],
        settings={"RELATIVE_BASE": BASE},
    ) == [("tonight", datetime(2026, 9, 28, 20, 0))]
    assert search_dates(
        "Llegó a las 5 de la madrugada del 3 de mayo",
        languages=["es"],
        settings={"RELATIVE_BASE": BASE},
    ) == [("a las 5 de la madrugada del 3 de mayo", datetime(2026, 5, 3, 5, 0))]
