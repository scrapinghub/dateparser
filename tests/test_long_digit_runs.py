"""Numbers with more digits than int() accepts, which Python limits by
default, must not make the search functions raise."""

import datetime

from parameterized import param, parameterized

from dateparser.search import search_dates
from tests import BaseTestCase

LONG_NUMBER = "1" * 5000
BASE = datetime.datetime(2026, 11, 3, 12, 0)
TIME_SPAN_SETTINGS = {"RETURN_TIME_SPAN": True, "RELATIVE_BASE": BASE}


class TestLongDigitRuns(BaseTestCase):
    def test_relative_quantity_too_long_for_int_is_not_a_date(self) -> None:
        self.assertIsNone(search_dates(f"in {LONG_NUMBER} days", languages=["en"]))

    def test_trailing_quantity_too_long_for_int_keeps_the_date_before_it(self) -> None:
        result = search_dates(
            f"Sep 15, 2026 10:50 AM {LONG_NUMBER} years after",
            languages=["en"],
            settings={"RELATIVE_BASE": BASE},
        )
        self.assertEqual(result, [("Sep 15", datetime.datetime(2026, 9, 15))])

    @parameterized.expand(
        [
            param("next_days", f"the next {LONG_NUMBER} days"),
            param("past_weeks", f"the past {LONG_NUMBER} weeks"),
            param("too_large_for_a_date", "the next 99999999999 days"),
        ]
    )
    def test_time_span_that_cannot_be_a_date_is_left_out(
        self, label: str, text: str
    ) -> None:
        self.assertIsNone(
            search_dates(text, languages=["en"], settings=TIME_SPAN_SETTINGS)
        )

    def test_time_span_is_still_returned_for_a_normal_number(self) -> None:
        result = search_dates(
            "the next 5 days", languages=["en"], settings=TIME_SPAN_SETTINGS
        )
        assert result is not None
        self.assertEqual(
            result[-2:],
            [
                ("next 5 days (start)", BASE),
                ("next 5 days (end)", BASE + datetime.timedelta(days=5)),
            ],
        )
