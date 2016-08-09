# coding: utf-8
from datetime import datetime

from umalqurra.hijri_date import HijriDate
import regex as re

from dateparser.calendars import CalendarBase
from dateparser.conf import settings


class HijriCalendar(CalendarBase):
    _time_conventions = {
        'am': [u"صباحاً"],
        'pm': [u"مساءً"],
    }

    def replace_time_conventions(self, source):
        result = source
        for latin, arabics in self._time_conventions.items():
            for arabic in arabics:
                result = result.replace(arabic, latin)
        return result

    def get_date(self):
        from dateparser.calendars.hijri_parser import hijri_parser
        translated = self.replace_time_conventions(self.source)
        try:
            date_obj, period =  hijri_parser.parse(translated, settings)
            return {'date_obj': date_obj, 'period': period}
        except ValueError:
            pass
