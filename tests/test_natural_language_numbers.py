import unittest
from datetime import datetime, timedelta
from functools import wraps

from mock import patch, Mock
from parameterized import parameterized, param

import dateparser.timezone_parser
from dateparser.date import DateDataParser, date_parser
from dateparser.date_parser import DateParser

from tests import BaseTestCase


class TestNaturalLanguageParser(BaseTestCase):
    def setUp(self):
        super(TestNaturalLanguageParser, self).setUp()
        self.parser = NotImplemented
        self.result = NotImplemented
        self.date_parser = NotImplemented
        self.date_result = NotImplemented

    @parameterized.expand([
        # English dates
        param('November Nineteen, Two thousand and fourteen at noon', datetime(2014, 11, 19, 12, 0)),
        param('December thirteen two thousand at midnight', datetime(2000, 12, 13, 0, 0)),
        param('The first of January 2020.', datetime(2020, 1, 1, 0, 0)),
        param('nineteen hundred', datetime(1900, 11, 13, 0, 0)),
        param('twenty seventh of June', datetime(2012, 6, 27, 0, 0)),
        param('Twenty three January 1997 11:08', datetime(1997, 1, 23, 11, 8)),
        # Spanish dates
        # There does seem to be a preceeding 'el' in dates which has been removed for time-being.
        param('ocho de febrero del mil novecientos ochenta y nueve', datetime(1989, 2, 8)),
        param('quince de abril', datetime(2012, 4, 15)),
        param('dieciocho de febrero del mil novecientos noventa y cinco', datetime(1995, 2, 18)),
        param('Dos mil diecisiete', datetime(2017, 11, 13)),
        # Russian dates
        param('две тысячи девять', datetime(2009, 11, 13)),
        # Hindi dates
        param('ग्यारह जुलाई 1994', datetime(1994, 7, 11,)),
        param('21 अक्टूबर दो हज़ार अठारह', datetime(2018, 10, 21, 0, 0)),
        param('तेरह जनवरी 1997 11:08', datetime(1997, 1, 13, 11, 8))
    ])
    def test_dates_parsing(self, date_string, expected):
        self.given_parser(settings={'NORMALIZE': False,
                                    'RELATIVE_BASE': datetime(2012, 11, 13)})
        self.when_date_is_parsed(date_string)
        self.then_date_was_parsed_by_date_parser()
        self.then_date_obj_exactly_is(expected)

    def given_local_tz_offset(self, offset):
        self.add_patch(
            patch.object(dateparser.timezone_parser,
                         'local_tz_offset',
                         new=timedelta(seconds=3600 * offset))
        )

    def given_parser(self, *args, **kwds):
        def collecting_get_date_data(parse):
            @wraps(parse)
            def wrapped(*args, **kwargs):
                self.date_result = parse(*args, **kwargs)
                return self.date_result
            return wrapped

        self.add_patch(patch.object(date_parser,
                                    'parse',
                                    collecting_get_date_data(date_parser.parse)))

        self.date_parser = Mock(wraps=date_parser)
        self.add_patch(patch('dateparser.date.date_parser', new=self.date_parser))
        self.parser = DateDataParser(*args, **kwds)

    def when_date_is_parsed(self, date_string):
        self.result = self.parser.get_date_data(date_string)

    def when_date_is_parsed_by_date_parser(self, date_string):
        try:
            self.result = DateParser().parse(date_string)
        except Exception as error:
            self.error = error

    def then_period_is(self, period):
        assert period == self.result['period']

    def then_date_obj_exactly_is(self, expected):
        assert expected == self.result['date_obj']

    def then_date_was_parsed_by_date_parser(self):
        print(self.result['date_obj'])
        assert self.result['date_obj'] == self.date_result[0]

    def then_timezone_parsed_is(self, tzstr):
        assert tzstr in repr(self.result['date_obj'].tzinfo)
        self.result['date_obj'] = self.result['date_obj'].replace(tzinfo=None)


if __name__ == '__main__':
    unittest.main()
