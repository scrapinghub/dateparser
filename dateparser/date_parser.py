# coding: utf-8
from __future__ import unicode_literals

import re
from cStringIO import StringIO

from datetime import datetime, time
import collections

from dateutil import parser
from dateutil.relativedelta import relativedelta
from dateutil import tz
from six import text_type, binary_type, integer_types
from dateparser.timezone_parser import pop_tz_offset_from_string, convert_to_local_tz

from conf import settings

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

    def parse(self, timestr, default=None, ignoretz=False, prefer_future=None, **kwargs):
        # timestr needs to be a buffer as required by _parse
        timestr = timestr if not isinstance(timestr, str) else StringIO(timestr)

        # Set right prefer_future var
        prefer_future = prefer_future if prefer_future is not None else settings.PREFER_DATES_FROM_FUTURE

        # Parse timestr
        res = self._parse(timestr, **kwargs)

        if res is None:
            raise ValueError("unknown string format")

        # Fill in missing date
        given_fields = []  # fields set by
        new_date = default

        for field in ['year', 'month', 'day', 'hour', 'minute', 'second', 'microsecond']:
            value = getattr(res, field)
            if value is not None:
                new_date = new_date.replace(**{field: value})
                given_fields.append(field + 's')
        if res.weekday and not res.day:
            new_date = new_date + new_relativedelta(weekday=res.weekday)

        # Correct date to if prefer in future of past
        if prefer_future is not None:
            for field in ['microseconds', 'seconds', 'minutes', 'hours', 'days', 'weeks', 'months', 'years']:
                # Can't override given field
                if field in given_fields:
                    continue

                delta = relativedelta(**{field: 1})

                if (prefer_future == False and new_date >= default and new_date - delta < default)\
                    or (prefer_future == True and new_date <= default and new_date + delta > default):

                    new_date = new_date - delta if prefer_future == False else new_date + delta
                    break

        # Clean hour and minutes, etc in case not defined
        if not res.hour and not res.minute and not res.second and not res.microsecond:
            new_date = new_date.replace(hour=0, minute=0, second=0, microsecond=0)

        return new_date

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
