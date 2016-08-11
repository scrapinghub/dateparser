# coding: utf-8

import regex as re

from datetime import datetime

from umalqurra.hijri_date import HijriDate

from dateparser.calendars import CalendarBase
from dateparser.conf import settings
from dateparser.calendars.hijri_parser import hijri_parser


class HijriCalendar(CalendarBase):

    def get_date(self):
        try:
            date_obj, period =  hijri_parser.parse(self.source, settings)
            return {'date_obj': date_obj, 'period': period}
        except ValueError:
            pass
