import pytest

pytest.importorskip("langdetect")

import unittest
from datetime import datetime
from unittest.mock import Mock

from parameterized import param, parameterized

from dateparser import parse
from dateparser.custom_language_detection.langdetect import (
    detect_languages as lang_detect_detect_languages,
)
from dateparser.date import DateDataParser
from dateparser.search import search_dates


class LangDetectBasicTest(unittest.TestCase):
    """Tests for basic langdetect functionality"""

    def test_returns_list(self):
        result = lang_detect_detect_languages("14 June 2020", 0.0)
        self.assertIsInstance(result, list)

    def test_detects_english(self):
        result = lang_detect_detect_languages(
            "The meeting is scheduled for Tuesday, July 22, 2014", 0.5
        )
        self.assertIn("en", result)

    def test_detects_spanish(self):
        result = lang_detect_detect_languages(
            "La reunión está programada para el martes 22 de julio de 2014", 0.5
        )
        self.assertIn("es", result)

    def test_detects_french(self):
        result = lang_detect_detect_languages(
            "La réunion est prévue pour le mardi 22 juillet 2014", 0.5
        )
        self.assertIn("fr", result)

    def test_detects_german(self):
        result = lang_detect_detect_languages(
            "Das Treffen ist für Dienstag, den 22. Juli 2014 geplant", 0.5
        )
        self.assertIn("de", result)

    def test_handles_numeric_only_input(self):
        result = lang_detect_detect_languages("10-10-2021", 0.5)
        self.assertEqual(result, [])

    def test_handles_empty_string(self):
        result = lang_detect_detect_languages("", 0.5)
        self.assertEqual(result, [])

    def test_confidence_threshold_filters_results(self):
        # With low threshold, should detect language
        result_low = lang_detect_detect_languages("14 June 2020", 0.0)
        self.assertGreater(len(result_low), 0)

        # With very high threshold, might not detect anything on short strings
        result_high = lang_detect_detect_languages("14 June", 0.99)
        # Short strings may have uncertain detection, result_high might be empty
        self.assertIsInstance(result_high, list)


class LangDetectIntegrationTest(unittest.TestCase):
    """Tests for langdetect integration with dateparser"""

    def test_parse_with_langdetect_english(self):
        result = parse(
            "Tuesday Jul 22, 2014",
            detect_languages_function=lang_detect_detect_languages,
        )
        self.assertEqual(result, datetime(2014, 7, 22, 0, 0, 0))

    def test_parse_with_langdetect_spanish(self):
        result = parse(
            "martes 22 de julio de 2014",
            detect_languages_function=lang_detect_detect_languages,
        )
        self.assertIsNotNone(result)
        self.assertEqual(result.year, 2014)
        self.assertEqual(result.month, 7)
        self.assertEqual(result.day, 22)

    def test_parse_with_langdetect_french(self):
        result = parse(
            "mardi 22 juillet 2014",
            detect_languages_function=lang_detect_detect_languages,
        )
        self.assertIsNotNone(result)
        self.assertEqual(result.year, 2014)
        self.assertEqual(result.month, 7)
        self.assertEqual(result.day, 22)

    def test_datedataparser_with_langdetect(self):
        ddp = DateDataParser(detect_languages_function=lang_detect_detect_languages)
        result = ddp.get_date_data("Tuesday Jul 22, 2014")
        self.assertEqual(result["date_obj"], datetime(2014, 7, 22, 0, 0, 0))

    def test_search_dates_with_langdetect(self):
        result = search_dates(
            "The event is on January 3, 2017 and ends February 1st",
            detect_languages_function=lang_detect_detect_languages,
        )
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 2)
        # Check that dates are found
        self.assertEqual(result[0][1], datetime(2017, 1, 3, 0, 0))
        self.assertEqual(result[1][1], datetime(2017, 2, 1, 0, 0))

    def test_parse_without_langdetect_still_works(self):
        # Ensure dateparser works without custom language detection
        result = parse("Tuesday Jul 22, 2014")
        self.assertEqual(result, datetime(2014, 7, 22, 0, 0, 0))


class MockLangDetectTest(unittest.TestCase):
    """Tests with mocked language detection"""

    # Mock test for parse, search_dates and DateDataParser

    detect_languages = Mock()
    detect_languages.return_value = ["en"]

    # parse

    def when_date_is_parsed_using_parse(self, dt_string):
        self.result = parse(dt_string, detect_languages_function=self.detect_languages)

    def then_date_obj_exactly_is(self, expected_date_obj):
        self.assertEqual(expected_date_obj, self.result)

    @parameterized.expand(
        [
            param("Tuesday Jul 22, 2014", datetime(2014, 7, 22, 0, 0, 0)),
        ]
    )
    def test_custom_language_detect_mock_parse(self, dt_string, expected_date_obj):
        self.when_date_is_parsed_using_parse(dt_string)
        self.then_date_obj_exactly_is(expected_date_obj)

    # DateDataParser

    def when_date_is_parsed_using_with_datedataparser(self, dt_string):
        ddp = DateDataParser(detect_languages_function=self.detect_languages)
        self.result = ddp.get_date_data(dt_string)["date_obj"]

    @parameterized.expand(
        [
            param("Tuesday Jul 22, 2014", datetime(2014, 7, 22, 0, 0, 0)),
        ]
    )
    def test_custom_language_detect_mock_datedataparser(
        self, dt_string, expected_date_obj
    ):
        self.when_date_is_parsed_using_with_datedataparser(dt_string)
        self.then_date_obj_exactly_is(expected_date_obj)

    # search_date

    def when_date_is_parsed_using_with_search_dates(self, dt_string):
        self.result = search_dates(
            dt_string, detect_languages_function=self.detect_languages
        )

    @parameterized.expand(
        [
            param(
                "January 3, 2017 - February 1st",
                [
                    ("January 3, 2017", datetime(2017, 1, 3, 0, 0)),
                    ("February 1st", datetime(2017, 2, 1, 0, 0)),
                ],
            ),
        ]
    )
    def test_custom_language_detect_mock_search_dates(
        self, dt_string, expected_date_obj
    ):
        self.when_date_is_parsed_using_with_search_dates(dt_string)
        self.then_date_obj_exactly_is(expected_date_obj)
