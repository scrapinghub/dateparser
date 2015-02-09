# coding: utf-8
from __future__ import unicode_literals

import re, sys
from datetime import datetime


from dateutil import parser
from dateutil.relativedelta import relativedelta
from dateparser.timezone_parser import pop_tz_offset_from_string, convert_to_local_tz

from conf import settings

binary_type = bytes if sys.version_info[0] == 3 else str


class new_relativedelta(relativedelta):
    """ dateutil does not check if result of parsing weekday is in the future.
    Although items dates are already in the past, so we need to fix this particular case.
    """

    def __new__(cls, *args, **kwargs):
        if not args and len(kwargs) == 1 and 'weekday' in kwargs:
            return super(new_relativedelta, cls).__new__(cls, *args, **kwargs)
        else:
            # use original class to parse other cases
            return relativedelta(*args, **kwargs)

    def __add__(self, other):
        ret = super(new_relativedelta, self).__add__(other)
        if ret > datetime.utcnow():
            ret -= relativedelta(days=7)
        return ret


parser.relativedelta.relativedelta = new_relativedelta


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
        new_date = new_parser._populate(res, default)

        # Clean hour and minutes, etc in case not defined
        for e in ['hour', 'minute', 'second', 'microsecond']:
            if not getattr(res, e):
                new_date = new_date.replace(**{e: 0})

        return new_date

    @staticmethod
    def _populate(res, default):
        new_date = default

        # Populate all fields
        repl = {}
        for field in ['year', 'month', 'day', 'hour', 'minute', 'second', 'microsecond']:
            value = getattr(res, field)
            if value is not None:
                repl[field] = value
        new_date = new_date.replace(**repl)

        # Fix weekday
        if res.weekday and not res.day:
            new_date = new_date + new_relativedelta(weekday=res.weekday)

        # Correct date and return
        return new_parser._correct(new_date, [key + 's' for key in repl.keys()], default)

    @staticmethod
    def _correct(date, given_fields, default):
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
            corrected_date = new_parser._correct_for_future(date, delta, default)
            corrected_date = new_parser._correct_for_past(corrected_date, delta, default)

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
    except TypeError, e:
        raise ValueError(e, "Invalid date: %s" % date_string)


class DateParser(object):
    def parse(self, date_string):
        date_string = unicode(date_string)

        if not date_string.strip():
            raise ValueError("Empty string")

        date_string, tz_offset = pop_tz_offset_from_string(date_string)

        date_obj = dateutil_parse(date_string)
        if tz_offset is not None:
            date_obj = convert_to_local_tz(date_obj, tz_offset)

        return date_obj


date_parser = DateParser()
