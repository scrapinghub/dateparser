# -*- coding: utf-8 -*-
import re
from datetime import datetime, timedelta

from .timezones import timezone_info_list


def pop_tz_offset_from_string(date_string, as_offset=True):
    for name, info in _tz_offsets:
        timezone_re = info['regex']
        if timezone_re.search(date_string):
            date_string = timezone_re.sub(r'\1', date_string)
            return date_string, info['offset'] if as_offset else name
    else:
        return date_string, None


def convert_to_local_tz(datetime_obj, datetime_tz_offset):
    return datetime_obj - datetime_tz_offset + local_tz_offset


def get_tz_offsets():

    def get_offset(tz_obj, regex, repl='', replw=''):
        return (
            tz_obj[0],
            {
                'regex': re.compile(re.sub(repl, replw, regex % tz_obj[0]), re.IGNORECASE),
                'offset': timedelta(seconds=tz_obj[1])
            }
        )

    for tz_info in timezone_info_list:
        for regex in tz_info['regex_patterns']:
            for tz_obj in tz_info['timezones']:
                yield get_offset(tz_obj, regex)

            # alternate patterns
            for replace, replacewith in tz_info.get('replace', []):
                for tz_obj in tz_info['timezones']:
                    yield get_offset(tz_obj, regex, repl=replace, replw=replacewith)


def get_local_tz_offset():
    offset = datetime.now() - datetime.utcnow()
    offset = timedelta(days=offset.days, seconds=round(offset.seconds, -1))
    return offset


_tz_offsets = list(get_tz_offsets())
local_tz_offset = get_local_tz_offset()
