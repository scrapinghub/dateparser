# -*- coding: utf-8 -*-
import re
from datetime import datetime, timedelta

from dateparser.timezones import timezone_info_list

TIMEZONE_REGEX_PATTERN = r'(\b|\d)%s$'
TIMEZONE_HHMM_PATTERN = re.compile(r'(?<=\d\d:\d\d)([-+])(\d\d)(\d\d)')


def pop_tz_offset_from_string(date_string, as_offset=True):
    for name, info in _tz_offsets.iteritems():
        timezone_re = info['regex']
        if timezone_re.search(date_string):
            # \1 = (\b|\d) in TIMEZONE_REGEX_PATTERN
            date_string = timezone_re.sub(r'\1', date_string)
            return date_string, info['offset'] if as_offset else name
    else:
        for tz_offset in [_get_tz_utc_offset_from_iso_datestamp(date_string)]:
            return date_string, tz_offset if as_offset else None
        else:
            return date_string, None


def _get_tz_utc_offset_from_iso_datestamp(date_string):
    for offset in TIMEZONE_HHMM_PATTERN.findall(date_string):
        sign, hours, minutes = offset
        return timedelta(hours=int('%s%s' % (sign, hours)), minutes=int('%s%s' % (sign, minutes)))


def convert_to_local_tz(datetime_obj, datetime_tz_offset):
    return datetime_obj - datetime_tz_offset + local_tz_offset


def get_tz_offsets():
    return {
        tz_info[0]: {
            'regex': re.compile(TIMEZONE_REGEX_PATTERN % tz_info[0], re.IGNORECASE),
            'offset': timedelta(seconds=tz_info[1]),
        }
        for tz_info in timezone_info_list
    }


def get_local_tz_offset():
    offset = datetime.now() - datetime.utcnow()
    offset = timedelta(days=offset.days, seconds=round(offset.seconds, -1))
    return offset


_tz_offsets = get_tz_offsets()
local_tz_offset = get_local_tz_offset()
