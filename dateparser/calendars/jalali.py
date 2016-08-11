# coding: utf-8
from __future__ import unicode_literals

import regex as re

from . import CalendarBase
from dateparser.calendars.jalali_parser import jalali_parser


def validate_time(string):
    if string.find(':') != -1:
        return string

    persian_time_map = [
        (u'\u0633\u0627\u0639\u062a', 'hour'),
        (u'\u062f\u0642\u06cc\u0642\u0647', 'minute'),
        (u'\u062b\u0627\u0646\u06cc\u0647', 'second')
    ]

    result_dict = {}
    template = '%(hour)s:%(minute)s:%(second)s'
    string = string.replace(u'و', '').strip()

    for persian, latin in persian_time_map:
        cursor = string.find(persian)
        if cursor == -1:
            result_dict[latin] = '00'
            continue
        elif cursor > 0:
            cursor_back = cursor - 3
            if cursor_back == -1:
                cursor_back = 0
            result = string[cursor_back: cursor]
        else:
            cursor += len(persian)
            result = string[cursor: cursor+3]

        result_dict[latin] = result.strip()

    return template % result_dict


class JalaliCalendar(CalendarBase):
    """Calendar class for Jalali calendar."""

    parser = jalali_parser
