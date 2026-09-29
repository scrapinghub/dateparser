import calendar
from datetime import date

from dateparser.calendars import CalendarBase, non_gregorian_parser

_YEAR_OFFSET = 1911


class _minguo:
    @classmethod
    def to_gregorian(cls, year=None, month=None, day=None):
        return year + _YEAR_OFFSET, month, day

    @classmethod
    def from_gregorian(cls, year=None, month=None, day=None):
        return year - _YEAR_OFFSET, month, day

    @classmethod
    def month_length(cls, year, month):
        return calendar.monthrange(year + _YEAR_OFFSET, month)[1]


class _minguo_parser(non_gregorian_parser):
    calendar_converter = _minguo
    default_year = 101
    default_month = 1
    default_day = 1
    non_gregorian_date_cls = date

    def _get_date_obj(self, token, directive):
        if directive == "%Y":
            if not (token.isdigit() and len(token) <= 3 and int(token)):
                raise ValueError
            return date(int(token), self.default_month, self.default_day)
        return super()._get_date_obj(token, directive)

    @classmethod
    def parse(cls, datestring, settings):
        return super(non_gregorian_parser, cls).parse(
            datestring, settings, date_order="YMD"
        )


class MinguoCalendar(CalendarBase):
    """Calendar class for the `Minguo calendar
    <https://en.wikipedia.org/wiki/Republic_of_China_calendar>`_, used in
    Taiwan."""

    parser = _minguo_parser
