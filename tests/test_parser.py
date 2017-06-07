from datetime import datetime, time

from nose_parameterized import parameterized, param
from tests import BaseTestCase

from dateparser.parser import tokenizer
from dateparser.parser import _no_spaces_parser
from dateparser.parser import _parser
from dateparser.parser import time_parser
from dateparser.conf import apply_settings


class TestTokenizer(BaseTestCase):

    @parameterized.expand([
        param(
            date_string=u"11 april 2010",
            expected_tokens=['11', ' ', 'april', ' ', '2010'],
            expected_types=[0, 2, 1, 2, 0],
        ),
        param(
            date_string=u"Tuesday 11 april 2010",
            expected_tokens=['Tuesday', ' ', '11', ' ', 'april', ' ', '2010'],
            expected_types=[1, 2, 0, 2, 1, 2, 0],
        ),
        param(
            date_string=u"11/12-2013",
            expected_tokens=['11', '/', '12', '-', '2013'],
            expected_types=[0, 2, 0, 2, 0],
        ),
        param(
            date_string=u"11/12-2013",
            expected_tokens=['11', '/', '12', '-', '2013'],
            expected_types=[0, 2, 0, 2, 0],
        ),
        param(
            date_string=u"10:30:35 PM",
            expected_tokens=['10:30:35', ' ', 'PM'],
            expected_types=[0, 2, 1],
        ),
        param(
            date_string=u"18:50",
            expected_tokens=['18:50'],
            expected_types=[0],
        ),
        param(
            date_string=u"December 23, 2010, 16:50 pm",
            expected_tokens=['December', ' ', '23', ', ', '2010', ', ', '16:50', ' ', 'pm'],
            expected_types=[1, 2, 0, 2, 0, 2, 0, 2, 1],
        ),
        param(
            date_string=tokenizer.digits,
            expected_tokens=[tokenizer.digits],
            expected_types=[0],
        ),
        param(
            date_string=tokenizer.letters,
            expected_tokens=[tokenizer.letters],
            expected_types=[1],
        ),
        param(
            date_string=tokenizer.nonwords,
            expected_tokens=[tokenizer.nonwords],
            expected_types=[2],
        ),
    ])
    def test_tokenization(self, date_string, expected_tokens, expected_types):
        self.given_tokenizer(date_string)
        self.when_tokenized()
        self.then_tokens_were(expected_tokens)
        self.then_token_types_were(expected_types)

    def given_tokenizer(self, date_string):
        self.tokenizer = tokenizer(date_string)

    def when_tokenized(self):
        self.result = list(self.tokenizer.tokenize())

    def then_tokens_were(self, expected_tokens):
        self.assertEqual([l[0] for l in self.result], expected_tokens)

    def then_token_types_were(self, expected_types):
        self.assertEqual([l[1] for l in self.result], expected_types)


class TestNoSpaceParser(BaseTestCase):

    def test_date_with_spaces_is_not_parsed(self):
        self.given_parser()
        self.given_settings()
        self.when_date_is_parsed('2013 25 12')
        self.then_date_is_not_parsed()

    def test_date_with_alphabets_is_not_parsed(self):
        self.given_parser()
        self.given_settings()
        self.when_date_is_parsed('12AUG2015')
        self.then_date_is_not_parsed()

    @parameterized.expand([
        param(
            date_string=u"201115",
            expected_date=datetime(2015, 11, 20),
            date_order='DMY',
            expected_period='day',
        ),
        param(
            date_string=u"20201511",
            expected_date=datetime(2015, 11, 20),
            date_order='DYM',
            expected_period='day',
        ),
        param(
            date_string=u"112015",
            expected_date=datetime(2015, 1, 1),
            date_order='MDY',
            expected_period='day',
        ),
        param(
            date_string=u"11012015",
            expected_date=datetime(2015, 11, 1),
            date_order='MDY',
            expected_period='day',
        ),
        param(
            date_string=u"12201511",
            expected_date=datetime(2015, 12, 11),
            date_order='MYD',
            expected_period='day',
        ),
        param(
            date_string=u"20151211",
            expected_date=datetime(2015, 12, 11),
            date_order='YMD',
            expected_period='day',
        ),
        param(
            date_string=u"20153011",
            expected_date=datetime(2015, 11, 30),
            date_order='YDM',
            expected_period='day',
        ),
    ])
    def test_date_are_parsed_in_order_supplied(self, date_string, expected_date, expected_period, date_order):
        self.given_parser()
        self.given_settings(settings={'DATE_ORDER': date_order})
        self.when_date_is_parsed(date_string)
        self.then_date_exactly_is(expected_date)
        self.then_period_exactly_is(expected_period)

    def given_parser(self):
        self.parser = _no_spaces_parser

    @apply_settings
    def given_settings(self, settings=None):
        self.settings = settings

    def when_date_is_parsed(self, date_string):
        self.result = self.parser.parse(date_string, self.settings)

    def then_date_exactly_is(self, expected_date):
        self.assertEqual(self.result[0], expected_date)

    def then_period_exactly_is(self, expected_period):
        self.assertEqual(self.result[1], expected_period)

    def then_date_is_not_parsed(self):
        self.assertIsNone(self.result)


class TestParser(BaseTestCase):

    @parameterized.expand([
        param(date_string=u"april 2010"),
        param(date_string=u"11 March"),
        param(date_string=u"March"),
        param(date_string=u"31 2010"),
        param(date_string=u"31/2010"),
    ])
    def test_error_is_raised_when_incomplete_dates_given(self, date_string):
        self.given_parser()
        self.given_settings(settings={'STRICT_PARSING': True})
        self.then_error_is_raised_when_date_is_parsed(date_string)

    @parameterized.expand([
    param(date_string=u"@@@##$@!@!"),
    param(date_string=u"@-@-@"),
    param(date_string=u"@@-#$##"),
    ])
    def test_completely_invalid_dates_are_not_parsed(self, date_string):
        self.given_parser()
        self.when_date_is_parsed(date_string)
        self.then_date_is_not_parsed()

    def given_parser(self):
        self.parser = _parser

    @apply_settings
    def given_settings(self, settings=None):
        self.settings = settings

    def then_error_is_raised_when_date_is_parsed(self, date_string):
        with self.assertRaises(ValueError):
            self.parser.parse(date_string, self.settings)

    @apply_settings
    def when_date_is_parsed(self, date_string, settings = None):
        self.result = self.parser.parse(date_string, settings)

    def then_date_is_not_parsed(self):
        self.assertIsNone(self.result[0])


class TestTimeParser(BaseTestCase):

    @parameterized.expand([
        param(date_string=u"11:30:14", timeobj=time(11, 30, 14)),
        param(date_string=u"11:30", timeobj=time(11, 30)),
        param(date_string=u"11:30 PM", timeobj=time(23, 30)),
        param(date_string=u"1:30 AM", timeobj=time(1, 30)),
        param(date_string=u"1:30:15.330 AM", timeobj=time(1, 30, 15, 330000)),
        param(date_string=u"1:30:15.330 PM", timeobj=time(13, 30, 15, 330000)),
        param(date_string=u"1:30:15.3301 PM", timeobj=time(13, 30, 15, 330100)),
        param(date_string=u"14:30:15.330100", timeobj=time(14, 30, 15, 330100)),
    ])
    def test_time_is_parsed(self, date_string, timeobj):
        self.given_parser()
        self.when_time_is_parsed(date_string)
        self.then_time_exactly_is(timeobj)

    def given_parser(self):
        self.parser = time_parser

    def when_time_is_parsed(self, datestring):
        self.result = self.parser(datestring)

    def then_time_exactly_is(self, timeobj):
        self.assertEqual(self.result, timeobj)
