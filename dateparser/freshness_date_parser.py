# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import regex as re
import calendar as cal
from datetime import datetime
from datetime import time
from tzlocal import get_localzone

from dateutil.relativedelta import relativedelta

from dateparser.utils import apply_timezone, localize_timezone, strip_braces
from .parser import time_parser
from .timezone_parser import pop_tz_offset_from_string


_UNITS = r'year|month|week|day|hour|minute|second'
PATTERN = re.compile(r'(\d+)\s*(%s)\b' % _UNITS, re.I | re.S | re.U)
_WEEKDAYS = r'monday|tuesday|wednesday|thursday|friday|saturday|sunday'


class FreshnessDateDataParser(object):
    """ Parses date string like "1 year, 2 months ago" and "3 hours, 50 minutes ago" """
    def __init__(self):
        self.now = None

    def _are_all_words_units(self, date_string):
        skip = [_UNITS,
                r'ago|in|next|after|\d+',
                r':|[ap]m']

        date_string = re.sub(r'\s+', ' ', date_string.strip())

        words = filter(lambda x: x if x else False, re.split(r'\W', date_string))
        words = filter(lambda x: not re.match(r'%s' % '|'.join(skip), x), words)
        return not list(words)

    def _parse_time(self, date_string, settings):
        """Attempts to parse time part of date strings like '1 day ago, 2 PM' """
        date_string = PATTERN.sub('', date_string)
        date_string = re.sub(r'\b(?:ago|in|next|after)\b', '', date_string)
        try:
            return time_parser(date_string)
        except:
            pass

    def get_local_tz(self):
        return get_localzone()

    def parse(self, date_string, settings):

        _time = self._parse_time(date_string, settings)

        date_string = strip_braces(date_string)
        date_string, ptz = pop_tz_offset_from_string(date_string)

        _settings_tz = settings.TIMEZONE.lower()

        def apply_time(dateobj, timeobj):
            if not isinstance(_time, time):
                return dateobj

            return dateobj.replace(
                hour=timeobj.hour, minute=timeobj.minute,
                second=timeobj.second, microsecond=timeobj.microsecond
            )

        if settings.RELATIVE_BASE:
            self.now = settings.RELATIVE_BASE

            if 'local' not in _settings_tz:
                self.now = localize_timezone(self.now, settings.TIMEZONE)

            if ptz:
                if self.now.tzinfo:
                    self.now = self.now.astimezone(ptz)
                else:
                    self.now = ptz.localize(self.now)

            if not self.now.tzinfo:
                self.now = self.get_local_tz().localize(self.now)

        elif ptz:
            _now = datetime.now(ptz)

            if 'local' in _settings_tz:
                self.now = _now
            else:
                self.now = apply_timezone(_now, settings.TIMEZONE)

        else:
            if 'local' not in _settings_tz:
                utc_dt = datetime.utcnow()
                self.now = apply_timezone(utc_dt, settings.TIMEZONE)
            else:
                self.now = datetime.now(self.get_local_tz())

        date, period = self._parse_date(date_string, settings.PREFER_DATES_FROM)

        if date:
            date = apply_time(date, _time)
            if settings.TO_TIMEZONE:
                date = apply_timezone(date, settings.TO_TIMEZONE)

            if (
                not settings.RETURN_AS_TIMEZONE_AWARE or
                (settings.RETURN_AS_TIMEZONE_AWARE and
                 'default' == settings.RETURN_AS_TIMEZONE_AWARE and not ptz)
            ):
                date = date.replace(tzinfo=None)

        self.now = None
        return date, period

    def _parse_date(self, date_string, prefer_dates_from):

        _weekday = self.get_weekday_data(date_string)

        if not self._are_all_words_units(date_string) and not _weekday:
            return None, None

        kwargs = self.get_kwargs(date_string)

        if not kwargs and not _weekday:
            return None, None

        period = 'day'
        if _weekday:
            day = getattr(cal, _weekday.upper())
            day_ahead = day - self.now.weekday()
            if day_ahead <= 0:
                day_ahead += 7

            td = relativedelta(days=day_ahead)

        else:
            if 'days' not in kwargs:
                for k in ['weeks', 'months', 'years']:
                    if k in kwargs:
                        period = k[:-1]
                        break

            td = relativedelta(**kwargs)
        if (
            re.search(r'\bin\b', date_string) or
            re.search(r'\bnext\b', date_string) or
            re.search(r'\bafter\b', date_string) or
            ('future' in prefer_dates_from and
             not re.search(r'\bago\b', date_string))
        ):
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

    def get_weekday_data(self, date_string):
        words = re.split(r"\s+", date_string)
        for word in words:
            if re.search(r'\b'+word, _WEEKDAYS) and 'next' in date_string:
                return word

        else:
            return None


freshness_date_parser = FreshnessDateDataParser()
