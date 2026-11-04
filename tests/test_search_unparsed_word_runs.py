import datetime
from typing import Any
from unittest.mock import patch

from parameterized import param, parameterized

from dateparser.date import DateData
from dateparser.search import search_dates
from tests import BaseTestCase


class TestSearchDatesRunsOfWordsThatDoNotParse(BaseTestCase):
    @parameterized.expand(
        [
            param("hour ", "en"),
            param("ngày ", "vi"),
        ]
    )
    def test_search_dates_work_per_word_does_not_grow_with_the_run(
        self, word: str, language: str
    ) -> None:
        """Doubling a run of words that do not parse on their own must not
        much more than double the work. The work is counted, instead of timed,
        as the number of times a DateData is read."""
        reads = 0
        date_data_getitem = DateData.__getitem__

        def counting_getitem(date_data: DateData, key: str) -> Any:
            nonlocal reads
            reads += 1
            return date_data_getitem(date_data, key)

        def count_reads(words: int) -> int:
            nonlocal reads
            reads = 0
            with patch.object(DateData, "__getitem__", counting_getitem):
                search_dates(word * words, languages=[language])
            return reads

        short_run, long_run = count_reads(200), count_reads(400)
        self.assertGreater(short_run, 0)
        self.assertLess(long_run, 2.5 * short_run)

    @parameterized.expand(
        [
            param(
                "5 May 2020, in 2 days, hour hour hour, in 3 days",
                [
                    ("5 May 2020", datetime.datetime(2020, 5, 5)),
                    ("in 2 days", datetime.datetime(2020, 5, 7)),
                    ("in 3 days", datetime.datetime(2020, 5, 8)),
                ],
            ),
            param(
                "5 May 2020, tomorrow, in 3 days, 7 June 2021, in 3 days",
                [
                    ("5 May 2020", datetime.datetime(2020, 5, 5)),
                    ("tomorrow", datetime.datetime(2020, 5, 6)),
                    ("in 3 days", datetime.datetime(2020, 5, 8)),
                    ("7 June 2021", datetime.datetime(2021, 6, 7)),
                    ("in 3 days", datetime.datetime(2021, 6, 10)),
                ],
            ),
            param(
                "On 5 May 2020 he left; 2 days later he came back; in 3 days he left",
                [
                    ("On 5 May 2020", datetime.datetime(2020, 5, 5)),
                    ("2 days later", datetime.datetime(2020, 5, 7)),
                    ("in 3 days", datetime.datetime(2020, 5, 8)),
                ],
            ),
            param(
                "On 5 May 2020, Fifty years after. Then in 3 days",
                [
                    ("On 5 May 2020", datetime.datetime(2020, 5, 5)),
                    ("Fifty years after", datetime.datetime(2070, 5, 5)),
                    ("in 3 days", datetime.datetime(2020, 5, 8)),
                ],
            ),
        ]
    )
    def test_search_dates_relative_to_the_last_date_that_is_not_relative(
        self, text: str, expected: list[tuple[str, datetime.datetime]]
    ) -> None:
        self.assertEqual(search_dates(text, languages=["en"]), expected)

    def test_search_dates_relative_to_a_date_before_many_words_that_do_not_parse(
        self,
    ) -> None:
        result = search_dates(
            "5 May 2020. 7 June 2021, " + "hour, " * 300 + "2 days ago",
            languages=["en"],
        )
        assert result is not None
        self.assertEqual(
            [item[1] for item in result],
            [
                datetime.datetime(2020, 5, 5),
                datetime.datetime(2021, 6, 7),
                datetime.datetime(2021, 6, 5),
            ],
        )
