# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from mock import Mock, patch
from nose_parameterized import parameterized, param

import dateparser.timezone_parser
from dateparser.timezone_parser import pop_tz_offset_from_string, get_local_tz_offset
from tests import BaseTestCase


class TestTZPopping(BaseTestCase):
    def setUp(self):
        super(TestTZPopping, self).setUp()
        self.initial_string = self.datetime_string = self.timezone_offset = NotImplemented

    @parameterized.expand([
        param('Sep 03 2014 | 4:32 pm EDT', -4),
        param('17th October, 2034 @ 01:08 am PDT', -7),
        param('17th October, 2034 @ 01:08 am (PDT)', -7),
        param('October 17, 2014 at 7:30 am PST', -8),
        param('20 Oct 2014 13:08 CET', +1),
        param('20 Oct 2014 13:08cet', +1),
        param('Nov 25 2014 | 10:17 pm EST', -5),
        param('Nov 25 2014 | 10:17 pm +0600', +6),
        param('Nov 25 2014 | 10:17 pm -0930', -9.5),
        param('20 Oct 2014 | 05:17 am -1200', -12),
        param('20 Oct 2014 | 05:17 am +0000', 0),
        param('15 May 2004', None),
        param('Wed Aug 05 12:00:00 EDTERR 2015', None),
        param('Wed Aug 05 12:00:00 EDT 2015', -4),
    ])
    def test_extracting_valid_offset(self, initial_string, expected_offset):
        self.given_string(initial_string)
        self.when_offset_popped_from_string()
        self.then_offset_is(expected_offset)

    @parameterized.expand([
        param('Sep 03 2014 | 4:32 pm EDT', 'Sep 03 2014 | 4:32 pm '),
        param('17th October, 2034 @ 01:08 am PDT', '17th October, 2034 @ 01:08 am '),
        param('October 17, 2014 at 7:30 am PST', 'October 17, 2014 at 7:30 am '),
        param('20 Oct 2014 13:08 CET', '20 Oct 2014 13:08 '),
        param('20 Oct 2014 13:08cet', '20 Oct 2014 13:08'),
        param('Nov 25 2014 | 10:17 pm EST', 'Nov 25 2014 | 10:17 pm '),
        param('17th October, 2034 @ 01:08 am +0700', '17th October, 2034 @ 01:08 am '),
        param('Sep 03 2014 4:32 pm +0630', 'Sep 03 2014 4:32 pm '),
    ])
    def test_timezone_deleted_from_string(self, initial_string, result_string):
        self.given_string(initial_string)
        self.when_offset_popped_from_string()
        self.then_string_modified_to(result_string)

    def test_string_not_changed_if_no_timezone(self):
        self.given_string('15 May 2004')
        self.when_offset_popped_from_string()
        self.then_string_modified_to('15 May 2004')

    def given_string(self, string_):
        self.initial_string = string_

    def when_offset_popped_from_string(self):
        self.datetime_string, self.timezone_offset = pop_tz_offset_from_string(self.initial_string)

    def then_string_modified_to(self, expected_string):
        self.assertEqual(expected_string, self.datetime_string)

    def then_offset_is(self, expected_offset):
        delta = timedelta(hours=expected_offset) if expected_offset is not None else None
        self.assertEqual(delta, self.timezone_offset)


class TestLocalTZOffset(BaseTestCase):
    def setUp(self):
        super(TestLocalTZOffset, self).setUp()
        self.timezone_offset = NotImplemented

    @parameterized.expand([
        param(utc='2014-08-20 4:32', local='2014-08-20 8:32', offset=+4),
        param(utc='2052-01-02 11:07', local='2052-01-02 10:07', offset=-1),
        param(utc='2013-12-31 23:59', local='2014-01-01 00:29', offset=+0.5),
        param(utc='2011-07-14 11:59', local='2011-07-13 23:59', offset=-12),
        param(utc='2014-10-18 17:41', local='2014-10-18 17:41', offset=0),
    ])
    def test_timezone_offset_calculation(self, utc, local, offset):
        self.given_utc_time(utc)
        self.given_local_time(local)
        self.when_offset_popped_from_string()
        self.then_offset_is(offset)

    def given_utc_time(self, datetime_string):
        self._given_time(datetime_string, 'utcnow')

    def given_local_time(self, datetime_string):
        self._given_time(datetime_string, 'now')

    def when_offset_popped_from_string(self):
        self.timezone_offset = get_local_tz_offset()

    def then_offset_is(self, expected_offset):
        delta = timedelta(seconds=3600 * expected_offset) if expected_offset is not None else None
        self.assertEqual(delta, self.timezone_offset)

    def _given_time(self, datetime_string, getter_name):
        datetime_cls = dateparser.timezone_parser.datetime
        if not isinstance(datetime_cls, Mock):
            datetime_cls = Mock(wraps=datetime)
        datetime_obj = datetime.strptime(datetime_string, '%Y-%m-%d %H:%M')
        setattr(datetime_cls, getter_name, Mock(return_value=datetime_obj))
        self.add_patch(
            patch('dateparser.timezone_parser.datetime', new=datetime_cls)
        )
