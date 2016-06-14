# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import regex as re
from datetime import datetime
from datetime import time

from dateutil.relativedelta import relativedelta

from dateparser.utils import apply_timezone
from .parser import time_parser


_UNITS = r'year|month|week|day|hour|minute|second'
PATTERN = re.compile(r'(\d+)\s*(%s)\b' % _UNITS, re.I | re.S | re.U)


class FreshnessDateDataParser(object):
    """ Parses date string like "1 year, 2 months ago" and "3 hours, 50 minutes ago" """
    def __init__(self):
        self._now = None

    @property
    def now(self):
        return self._now if self._now else datetime.utcnow()

    @now.setter
    def now(self, value):
        self._now = value

    def _are_all_words_units(self, date_string):
        skip = [_UNITS,
                r'ago|in|\d+',
                r':|[ap]m']

        date_string = re.sub(r'\s+', ' ', date_string.strip())

        words = filter(lambda x: x if x else False, re.split(r'\W', date_string))
        words = filter(lambda x: not re.match(r'%s' % '|'.join(skip), x), words)
        return not list(words)

    def _parse_time(self, date_string, settings):
        """Attemps to parse time part of date strings like '1 day ago, 2 PM' """
        date_string = PATTERN.sub('', date_string)
        date_string = re.sub(r'\b(?:ago|in)\b', '', date_string)
        try:
            return time_parser(date_string)
        except:
            pass

    def parse(self, date_string, settings):
        if settings.RELATIVE_BASE:
            self.now = settings.RELATIVE_BASE

        date, period = self._parse(date_string)

        if date:
            _time = self._parse_time(date_string, settings)
            if isinstance(_time, time):
                date = date.replace(hour=_time.hour, minute=_time.minute,
                                    second=_time.second, microsecond=_time.microsecond)
            else:
                # No timezone shift takes place if time is given in the string.
                # e.g. `2 days ago at 1 PM`
                if settings.TIMEZONE:
                    date = apply_timezone(date, settings.TIMEZONE)

            if not settings.RETURN_AS_TIMEZONE_AWARE:
                date = date.replace(tzinfo=None)
        self.now = None
        return date, period

    def _parse(self, date_string):
        if not self._are_all_words_units(date_string):
            return None, None

        kwargs = self.get_kwargs(date_string)
        if not kwargs:
            return None, None

        period = 'day'
        if 'days' not in kwargs:
            for k in ['weeks', 'months', 'years']:
                if k in kwargs:
                    period = k[:-1]
                    break

        td = relativedelta(**kwargs)
        if re.search(r'\bin\b', date_string):
            date = self.now + td
        else:
            date = self.now - td
        return date, period

    def get_kwargs(self, date_string):
        m = PATTERN.findall(date_string)
        if not m:
            return {}

        kwargs = {}
        for num, unit in m:
            kwargs[unit + 's'] = int(num)

        return kwargs

    def get_date_data(self, date_string, settings=None):
        date, period = self.parse(date_string, settings)
        return dict(date_obj=date, period=period)

freshness_date_parser = FreshnessDateDataParser()
