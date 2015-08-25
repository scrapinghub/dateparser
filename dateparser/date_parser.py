# coding: utf-8
from __future__ import unicode_literals

import calendar
import re
import sys
from datetime import datetime
from collections import OrderedDict

import six
from dateutil import parser
from dateutil.relativedelta import relativedelta

from .timezone_parser import pop_tz_offset_from_string, convert_to_local_tz
from .utils import strip_braces
from .conf import settings


binary_type = bytes if sys.version_info[0] == 3 else str


class new_parser(parser.parser):
    """
    Implements an alternate parse method which supports preference to dates in future and past.
    For more see issue #36
    """

    def parse(self, timestr, default=None, ignoretz=False, **kwargs):
        # timestr needs to be a buffer as required by _parse
        if isinstance(timestr, binary_type):
            timestr = timestr.decode()

        # Parse timestr
        res = self._parse(timestr, **kwargs)

        if res is None:
            raise ValueError("unknown string format")

        # Fill in missing date
        new_date = self._populate(res, default)

        # Clean hour and minutes, etc in case not defined
        for e in ['hour', 'minute', 'second', 'microsecond']:
            if not getattr(res, e):
                new_date = new_date.replace(**{e: 0})

        return new_date, self.get_period(res)

    @staticmethod
    def get_period(res):
        periods = OrderedDict([
            ('day', ['day', 'weekday', 'hour', 'minute', 'second', 'microsecond']),
            ('month', ['month']),
            ('year', ['year']),
        ])
        for period, markers in six.iteritems(periods):
            for marker in markers:
                if getattr(res, marker) is not None:
                    return period

    @classmethod
    def _populate(cls, res, default):
        new_date = default

        # Populate all fields
        repl = {}
        for field in ['year', 'month', 'day', 'hour', 'minute', 'second', 'microsecond']:
            value = getattr(res, field)
            if value is not None:
                repl[field] = value

        # Fix day and populate date with result
        repl_copy = repl.copy()
        repl_copy['day'] = cls.get_valid_day(repl, new_date)
        new_date = new_date.replace(**repl_copy)

        # Fix weekday
        if res.weekday is not None and not res.day:
            new_date = new_date + relativedelta(weekday=res.weekday)
            if new_date > datetime.utcnow():
                new_date -= relativedelta(days=7)

        # Correct date and return
        return cls._correct(new_date, [key + 's' for key in repl.keys()], default)

    @staticmethod
    def get_valid_day(res, new_date):
        _, tail = calendar.monthrange(res.get('year', new_date.year),
                                      res.get('month', new_date.month))

        if 'day' in res:
            if res['day'] > tail:
                raise ValueError('Day not in range for month',)
            else:
                return res['day']

        options = {
            'first': 1,
            'last': tail,
            'current': new_date.day if new_date.day <= tail else tail
        }

        return options[settings.PREFER_DAY_OF_MONTH]

    @classmethod
    def _correct(cls, date, given_fields, default):
        if settings.PREFER_DATES_FROM == 'current_period':
            return date

        for field in ['microseconds', 'seconds', 'minutes', 'hours', 'days',
                      'weeks', 'months', 'years']:
            # Can't override a given field
            if field in given_fields:
                continue

            # Try if applying the delta for this field corrects the problem
            delta = relativedelta(**{field: 1})

            # Run through corrections
            corrected_date = cls._correct_for_future(date, delta, default)
            corrected_date = cls._correct_for_past(corrected_date, delta, default)

            # check if changed
            if corrected_date != date:
                date = corrected_date
                break

        return date

    @staticmethod
    def _correct_for_future(date, delta, default):
        if settings.PREFER_DATES_FROM != 'future':
            return date

        if date < default < date + delta:
            date += delta

        return date

    @staticmethod
    def _correct_for_past(date, delta, default):
        if settings.PREFER_DATES_FROM != 'past':
            return date

        if date > default > date - delta:
            date -= delta

        return date


def dateutil_parse(date_string, **kwargs):
    """Wrapper function around dateutil.parser.parse
    """
    today = datetime.utcnow()
    kwargs.update(default=today)
    date_string = re.sub(r'\b(year|month|week|day)\b', '', date_string, re.I)

    # XXX: this is needed because of a bug in dateutil.parser
    # that raises TypeError for an invalid string
    # https://bugs.launchpad.net/dateutil/+bug/1042851
    try:
        return new_parser().parse(date_string, **kwargs)
    except TypeError as e:
        raise ValueError(e, "Invalid date: %s" % date_string)


class DateParser(object):

    def parse(self, date_string):
        date_string = six.text_type(date_string)

        if not date_string.strip():
            raise ValueError("Empty string")

        date_string = strip_braces(date_string)
        date_string, tz_offset = pop_tz_offset_from_string(date_string)

        date_obj, period = dateutil_parse(date_string)

        if tz_offset is not None:
            date_obj = convert_to_local_tz(date_obj, tz_offset)

        return date_obj, period


date_parser = DateParser()
