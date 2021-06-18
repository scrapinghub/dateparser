from parameterized import parameterized, param
from datetime import datetime

from tests import BaseTestCase

from dateparser.custom_lang_detect.fast_text import detect_languages as fast_text_detect_languages
from dateparser.custom_lang_detect.lang_detect import detect_languages as lang_detect_detect_languages
from dateparser import parse
from dateparser.date import DateDataParser
from dateparser.search import search_dates

class CustomLangDetectParser(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.result = NotImplemented
        self.date_string = NotImplemented
        self.parser = NotImplemented
        self.translated = NotImplemented

    def check_is_returned_list(self):
        self.assertEqual(type(self.result), list)

    @parameterized.expand([
        param(dt_string="14 June 2020"),
    ])
    def test_custom_language_detect_fast_text(self, dt_string):
        self.result = fast_text_detect_languages(dt_string)
        self.check_is_returned_list()

    @parameterized.expand([
        param(dt_string="14 June 2020"),
    ])
    def test_custom_language_detect_lang_detect(self, dt_string):
        self.result = lang_detect_detect_languages(dt_string)
        self.check_is_returned_list()

    # Mock test for parse, search_dates and DateDataParser

    # parse

    def when_date_is_parsed_using_fast_text_parse(self, dt_string):
        self.result = parse(dt_string, detect_languages_func=fast_text_detect_languages)

    def then_date_obj_exactly_is(self, expected_date_obj):
        self.assertEqual(expected_date_obj, self.result)

    @parameterized.expand([
        param("Tuesday Jul 22, 2014", datetime(2014, 7, 22, 0, 0, 0)),
    ])
    def test_custom_language_detect_mock_fast_text_parse(self, dt_string, expected_date_obj):
        self.when_date_is_parsed_using_fast_text_parse(dt_string)
        self.then_date_obj_exactly_is(expected_date_obj)


    # DateDataParser

    def when_date_is_parsed_using_fast_text_with_datedataparser(self, dt_string):
        ddp = DateDataParser(detect_languages_func=fast_text_detect_languages)
        self.result = ddp.get_date_data(dt_string)["date_obj"]

    @parameterized.expand([
        param("Tuesday Jul 22, 2014", datetime(2014, 7, 22, 0, 0, 0)),
    ])
    def test_custom_language_detect_mock_fast_text_datedataparser(self, dt_string, expected_date_obj):
        self.when_date_is_parsed_using_fast_text_with_datedataparser(dt_string)
        self.then_date_obj_exactly_is(expected_date_obj)

    # search_date

    # FAST TEXT

    def when_date_is_parsed_using_fast_text_with_search_dates(self, dt_string):
        self.result = search_dates(dt_string, detect_languages_func=fast_text_detect_languages)

    @parameterized.expand([
        param('January 3, 2017 - February 1st',
              [('January 3, 2017', datetime(2017, 1, 3, 0, 0)),
               ('February 1st', datetime(2017, 2, 1, 0, 0))]),
    ])
    def test_custom_language_detect_mock_fast_text_search_dates(self, dt_string, expected_date_obj):
        self.when_date_is_parsed_using_fast_text_with_search_dates(dt_string)
        self.then_date_obj_exactly_is(expected_date_obj)
