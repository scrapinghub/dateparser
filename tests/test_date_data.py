from datetime import datetime

import pytest
from dateutil.relativedelta import relativedelta

from dateparser.date import DateData, DateDataParser


class TestDateData:
    def test_get_item_like_dict(self):
        date = datetime(year=5432, month=3, day=1)
        dd = DateData(date_obj=date, period="day", locale="de")
        assert dd["date_obj"] == date
        assert dd["period"] == "day"
        assert dd["locale"] == "de"

    def test_get_item_like_dict_keyerror(self):
        dd = DateData(date_obj=None, period="day", locale="de")
        with pytest.raises(KeyError) as e:
            date_obj = dd["date"]
            assert e == "date"
            assert not date_obj

    def test_set_item_like_dict(self):
        dd = DateData()
        assert dd.date_obj is None

        date = datetime(year=5432, month=3, day=1)
        dd["date_obj"] = date
        assert dd.date_obj == date

    def test_set_item_like_dict_keyerror(self):
        dd = DateData()
        with pytest.raises(KeyError) as e:
            dd["date"] = datetime(year=5432, month=3, day=1)
            assert e == "date"

    @pytest.mark.parametrize(
        "date,period,locale,expected",
        [
            (
                datetime(year=2020, month=10, day=28),
                "day",
                "en",
                "DateData(date_obj=datetime.datetime(2020, 10, 28, 0, 0), period='day', locale='en')",
            ),
            (
                datetime(year=2014, month=5, day=29, hour=3, minute=2),
                "day",
                "es",
                "DateData(date_obj=datetime.datetime(2014, 5, 29, 3, 2), period='day', locale='es')",
            ),
            (
                datetime(
                    year=2028,
                    month=7,
                    day=31,
                    hour=3,
                    minute=2,
                    second=12,
                    microsecond=601265,
                ),
                "time",
                "fr",
                "DateData(date_obj=datetime.datetime(2028, 7, 31, 3, 2, 12, 601265), period='time', locale='fr')",
            ),
            (
                datetime(year=1994, month=8, day=1),
                "month",
                "ca",
                "DateData(date_obj=datetime.datetime(1994, 8, 1, 0, 0), period='month', locale='ca')",
            ),
            (
                datetime(year=2033, month=10, day=12),
                "month",
                None,
                "DateData(date_obj=datetime.datetime(2033, 10, 12, 0, 0), period='month', locale=None)",
            ),
            (None, "day", None, "DateData(date_obj=None, period='day', locale=None)"),
            (None, "year", "fr", "DateData(date_obj=None, period='year', locale='fr')"),
        ],
    )
    def test_repr(self, date, period, locale, expected):
        dd = DateData(date_obj=date, period=period, locale=locale)
        assert dd.__repr__() == expected

    @pytest.mark.parametrize(
        "date_string,expected",
        [
            ("3 years and 6 months ago", relativedelta(years=-3, months=-6)),
            ("in 5 weeks", relativedelta(weeks=5)),
            ("-5wk", relativedelta(weeks=-5)),
            ("2 decades, +1 year", relativedelta(years=-19)),
            ("hace 2 horas", relativedelta(hours=-2)),
            ("1 may 1990", None),
        ],
    )
    def test_relative_delta(self, date_string, expected):
        parser = DateDataParser(settings={"RELATIVE_BASE": datetime(2000, 1, 1)})
        assert parser.get_date_data(date_string).relative_delta == expected
