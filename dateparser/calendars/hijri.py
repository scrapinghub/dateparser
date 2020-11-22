from dateparser.calendars import CalendarBase
from dateparser.calendars.hijri_parser import hijri_parser


class HijriCalendar(CalendarBase):
    parser = hijri_parser

    def get_date(self):
        try:
            date_data = super().get_date()
        except OverflowError:
            return None
