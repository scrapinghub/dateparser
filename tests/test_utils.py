import itertools
from tests import BaseTestCase
from nose_parameterized import parameterized, param
from dateparser.utils import find_date_separator


class TestUtils(BaseTestCase):
    def setUp(self):
        super(TestUtils, self).setUp()
        self.date_format = None
        self.result = None

    def given_date_format(self, date_format):
        self.date_format = date_format

    def when_date_seperator_is_parsed(self):
        self.result = find_date_separator(self.date_format)

    def then_date_seperator_is(self, sep):
        self.assertEqual(self.result, sep)

    @parameterized.expand([
        param(date_format=fmt.format(sep=sep), expected_sep=sep)
        for (fmt, sep) in itertools.product(
            ['%d{sep}%m{sep}%Y', '%d{sep}%m{sep}%Y %H:%M'],
            ['/', '.', '-', ':'])
    ])
    def test_separator_extraction(self, date_format, expected_sep):
        self.given_date_format(date_format)
        self.when_date_seperator_is_parsed()
        self.then_date_seperator_is(expected_sep)
