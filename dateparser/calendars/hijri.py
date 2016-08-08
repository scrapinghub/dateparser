from datetime import datetime

from umalqurra.hijri_date import HijriDate
import regex as re

from dateparser.calendars import CalendarBase
from dateparser.conf import settings


class HijriCalendar(CalendarBase):

    def get_date(self):
        from dateparser.calendars.hijri_parser import hijri_parser
        try:
            return hijri_parser.parse(self.source, settings)
        except ValueError, ex:
            raise ex
            pass
