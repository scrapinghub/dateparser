# -*- coding: utf-8 -*-
import re
from datetime import datetime, timedelta
from math import ceil


HOUR = 3600

tz_offsets = {
    'CET': +1 * HOUR,
    'EDT': -4 * HOUR,
    'PDT': -7 * HOUR,
    'PST': -8 * HOUR,
}

_tz_offsets = {
    re.compile(r'\b%s$' % timezone): {'name': timezone, 'offset': timedelta(seconds=offset)}
    for timezone, offset in tz_offsets.iteritems()
}


def pop_tz_offset_from_string(date_string, as_offset=True):
    for timezone_re, info in _tz_offsets.iteritems():
        if timezone_re.search(date_string):
            date_string = timezone_re.sub('', date_string)
            return date_string, info['offset'] if as_offset else info['name']
    else:
        return date_string, None


def convert_to_local_tz(datetime_obj, datetime_tz_offset):
    return datetime_obj - datetime_tz_offset + local_tz_offset


def get_local_tz_offset():
    delta = datetime.now() - datetime.utcnow()
    days, seconds, microseconds = delta.days, delta.seconds, delta.microseconds
    return timedelta(seconds=days * 24 * HOUR + seconds + ceil(microseconds / 1000000.0))


local_tz_offset = get_local_tz_offset()
