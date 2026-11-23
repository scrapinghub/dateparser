import datetime
import inspect
import sys
from typing import Any
from unittest.mock import patch

from parameterized import param, parameterized

from dateparser.date import DateDataParser
from dateparser.search import search_dates
from dateparser.search.search import _ExactLanguageSearch
from tests import BaseTestCase

DATE = "Sep 15, 2026 10:50 AM "
QUANTITY = "Fifty years after "


class TestSearchDatesManyQuantitiesAfterADate(BaseTestCase):
    def test_search_dates_nests_no_deeper_with_more_quantities(self) -> None:
        """Splitting a quantity off the end of a chunk parses the rest of the
        chunk with a nested call, so the depth of the calls must not grow with
        the number of quantities."""
        depth = deepest = 0
        parse_found_objects = _ExactLanguageSearch.parse_found_objects

        def counting_parse_found_objects(
            search: _ExactLanguageSearch, *args: Any, **kwargs: Any
        ) -> Any:
            nonlocal depth, deepest
            depth += 1
            deepest = max(deepest, depth)
            try:
                return parse_found_objects(search, *args, **kwargs)
            finally:
                depth -= 1

        def deepest_for(quantities: int) -> int:
            nonlocal deepest
            deepest = 0
            with patch.object(
                _ExactLanguageSearch,
                "parse_found_objects",
                counting_parse_found_objects,
            ):
                search_dates(DATE + QUANTITY * quantities, languages=["en"])
            return deepest

        # The call for the chunk, and a nested call for each of the 8 quantities
        # that are split off its end.
        self.assertEqual(deepest_for(40), 9)
        self.assertEqual(deepest_for(80), 9)

    def test_search_dates_work_does_not_grow_with_the_square_of_the_quantities(
        self,
    ) -> None:
        """Doubling the quantities after a date must not much more than double
        the work. The work is counted, instead of timed, as the number of
        characters that are parsed."""
        characters = 0
        get_date_data = DateDataParser.get_date_data

        def counting_get_date_data(
            parser: DateDataParser, date_string: str, *args: Any, **kwargs: Any
        ) -> Any:
            nonlocal characters
            characters += len(date_string)
            return get_date_data(parser, date_string, *args, **kwargs)

        def count_characters(quantities: int) -> int:
            nonlocal characters
            characters = 0
            with patch.object(DateDataParser, "get_date_data", counting_get_date_data):
                search_dates(DATE + QUANTITY * quantities, languages=["en"])
            return characters

        self.assertLess(count_characters(100), 2.5 * count_characters(50))

    def test_search_dates_does_not_exhaust_the_recursion_limit(self) -> None:
        limit = sys.getrecursionlimit()
        # Enough for a search of a few quantities, but not for a nested call
        # for each of two hundred.
        sys.setrecursionlimit(len(inspect.stack(0)) + 120)
        try:
            result = search_dates(DATE + QUANTITY * 200, languages=["en"])
        finally:
            sys.setrecursionlimit(limit)
        self.assertTrue(result)

    @parameterized.expand([param(1), param(3), param(8)])
    def test_search_dates_splits_every_quantity_up_to_the_limit(
        self, quantities: int
    ) -> None:
        result = search_dates(
            DATE + QUANTITY * quantities,
            languages=["en"],
            settings={"RELATIVE_BASE": datetime.datetime(2020, 6, 15, 12)},
        )
        assert result is not None
        self.assertEqual(
            result[0], ("Sep 15, 2026 10:50 AM", datetime.datetime(2026, 9, 15, 10, 50))
        )
        self.assertEqual(len(result), quantities + 1)
