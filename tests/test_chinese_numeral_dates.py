from datetime import datetime

from parameterized import param, parameterized

import dateparser
from tests import BaseTestCase


class TestChineseNumeralDates(BaseTestCase):
    @parameterized.expand(
        [
            param(language, date_string, expected)
            for language in ("zh", "zh-Hans", "zh-Hant")
            for date_string, expected in (
                ("二〇一七年三月二十四日", datetime(2017, 3, 24)),
                ("一九九八年六月十五日", datetime(1998, 6, 15)),
                ("二零一零年十二月三十一日", datetime(2010, 12, 31)),
                ("二〇〇〇年一月一日", datetime(2000, 1, 1)),
                ("二〇一七年十月一日", datetime(2017, 10, 1)),
                ("一九八九年十二月三十一日", datetime(1989, 12, 31)),
            )
        ]
    )
    def test_chinese_numeral_dates(
        self, language: str, date_string: str, expected: datetime
    ) -> None:
        self.assertEqual(dateparser.parse(date_string, languages=[language]), expected)

    @parameterized.expand(
        [
            param(language, "2017年3月24日", datetime(2017, 3, 24))
            for language in ("zh", "zh-Hans", "zh-Hant")
        ]
    )
    def test_arabic_numeral_dates_unchanged(
        self, language: str, date_string: str, expected: datetime
    ) -> None:
        self.assertEqual(dateparser.parse(date_string, languages=[language]), expected)

    @parameterized.expand([param("zh"), param("zh-Hans")])
    def test_month_names_keep_working(self, language: str) -> None:
        self.assertIsNotNone(dateparser.parse("三月", languages=[language]))
