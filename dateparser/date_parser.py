# coding: utf-8
from __future__ import unicode_literals

import re

from datetime import datetime

from dateutil import parser
from dateutil.relativedelta import relativedelta

from dateparser.timezone_parser import pop_tz_offset_from_string, convert_to_local_tz


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


def dateutil_parse(date_string, **kwargs):
    """Wrapper function around dateutil.parser.parse
    """
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    kwargs.update(default=today)
    date_string = re.sub(r'\b(year|month|week|day)\b', '', date_string, re.I)

    # XXX: this is needed because of a bug in dateutil.parser
    # that raises TypeError for an invalid string
    # https://bugs.launchpad.net/dateutil/+bug/1042851
    try:
        return parser.parse(date_string, **kwargs)
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
