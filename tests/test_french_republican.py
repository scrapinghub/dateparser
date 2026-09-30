import pytest

pytest.importorskip("convertdate")

from datetime import datetime

from parameterized import param, parameterized

from dateparser.calendars.french_republican import (
    FrenchRepublicanCalendar,
    _french_republican_parser,
)
from dateparser.conf import settings
from tests import BaseTestCase


class TestFrenchRepublicanCalendar(BaseTestCase):
    @parameterized.expand(
        [
            param("18 brumaire an VIII", datetime(1799, 11, 9)),
            param("1er Vendémiaire an II", datetime(1793, 9, 22)),
            param("6 jours complémentaires an iii", datetime(1795, 9, 22)),
            param("1 Floréal an. 79", datetime(1871, 4, 21)),
        ]
    )
    def test_dates(self, date_string: str, expected: datetime) -> None:
        date_data = FrenchRepublicanCalendar(date_string).get_date()
        assert date_data is not None
        self.assertEqual(date_data.date_obj, expected)
        self.assertEqual(date_data.period, "day")

    @parameterized.expand(
        [
            param("An XIV", datetime(1805, 9, 23), "year"),
            param("An 3.eme", datetime(1794, 9, 22), "year"),
            param("An IVme.", datetime(1795, 9, 23), "year"),
            param("Sans-culottides an I", datetime(1793, 9, 17), "month"),
        ]
    )
    def test_prefer_first(
        self, date_string: str, expected: datetime, period: str
    ) -> None:
        first = settings.replace(
            PREFER_DAY_OF_MONTH="first", PREFER_MONTH_OF_YEAR="first"
        )
        self.assertEqual(
            _french_republican_parser.parse(date_string, first)[:2], (expected, period)
        )

    def test_prefer_current(self) -> None:
        current = settings.replace(RELATIVE_BASE=datetime(2026, 9, 29))
        self.assertEqual(
            _french_republican_parser.parse("an VIII", current)[:2],
            (datetime(1799, 9, 29), "year"),
        )

    def test_prefer_last(self) -> None:
        last = settings.replace(PREFER_DAY_OF_MONTH="last", PREFER_MONTH_OF_YEAR="last")
        self.assertEqual(
            _french_republican_parser.parse("an III", last)[:2],
            (datetime(1795, 9, 22), "year"),
        )

    @parameterized.expand(
        [
            param("31 brumaire an VIII"),
            param("6 sansculottides an II"),
            param("An 0"),
            param("An"),
            param("An XIIII"),
            param("brumaire"),
            param("18 brumaire 1799"),
        ]
    )
    def test_invalid(self, date_string: str) -> None:
        self.assertIsNone(FrenchRepublicanCalendar(date_string).get_date())
