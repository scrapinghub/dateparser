from datetime import datetime

from umalqurra.hijri_date import HijriDate
import regex as re

from dateparser.calendars import CalendarBase
from dateparser.date import DateDataParser
from dateparser.languages.loader import default_language_loader
from dateparser.utils import find_date_separator
from dateparser.conf import settings


class HijriGregorianFebruaryMismatch(Exception):
    pass


class HijriCalendar(CalendarBase):

    def get_date(self, date_formats=None, languages=None):
        date_formats = date_formats or ['%d-%m-%Y %I:%M %p', '%d-%m-%Y %I:%M',
                                        '%d-%m-%Y']
        languages = languages or ['ar']
        date_data = self._parser_get_date(self.source, date_formats, languages)
        date_obj = date_data.get('date_obj')
        if date_obj:
            # Convert Hijri to Gregorian
            date_data['date_obj'] = self._hijri_to_gregorian(
                date_obj.year, date_obj.month, date_obj.day, date_obj)
        else:
            try:
                self._detect_parse_error(date_formats, languages)
            except HijriGregorianFebruaryMismatch:
                date_data = self._fix_hijri_gregorian_feb_mismatch(
                    date_formats, languages)
        return date_data

    def _parser_get_date(self, date_string, date_formats, languages):
        parser = DateDataParser(languages)
        return parser.get_date_data(date_string, date_formats)

    def _detect_parse_error(self, date_formats, languages):
        """
        Check following cases:

        * 2nd month in Hijri calendar can be 29 or 30 days whilst this is
        not possible for Gregorian calendar.
        """
        for lang_shortname in languages:
            language = default_language_loader.get_language(lang_shortname)
            translated = language.translate(self.source, settings=settings)
            for date_format in date_formats:
                try:
                    datetime.strptime(date_format, translated)
                except ValueError:
                    sep = find_date_separator(date_format)
                    m = re.search(
                        r'(?<!\d)(?:(?:(0?2){sep}(29|30))|(?:(29|30){sep}(0?2)))'.format(sep=sep),
                        translated)
                    if m:
                        raise HijriGregorianFebruaryMismatch()

    def _fix_hijri_gregorian_feb_mismatch(self, date_formats, languages):
        # Now, search for 29th or 30th day of 2nd month.
        # If found, reduce it by 10 days and use regular parse
        # function again, if succeeds this time, then add 10
        # days to parsed Hijri form.
        for lang_shortname in languages:
            language = default_language_loader.get_language(lang_shortname)
            translated = language.translate(self.source, settings=settings)

            def _sub_fn(m):
                digit = int(m.group(0))
                return '{:02d}'.format(digit - 10)
            fixed_date_string, nreplaced = re.subn(
                r'(?<!\d)(29|30)', _sub_fn, translated, 1)
            if not nreplaced:
                continue

            date_data = self._parser_get_date(fixed_date_string, date_formats, languages)
            date_obj = date_data.get('date_obj')
            if date_obj:
                # Remember that, we have subtracted 10 days.
                date_data['date_obj'] = self._hijri_to_gregorian(
                    date_obj.year, date_obj.month, date_obj.day + 10, date_obj)
                return date_data

    @staticmethod
    def _hijri_to_gregorian(year, month, day, date_obj=None):
        hd = HijriDate(year=year, month=month, day=day)
        year_gr = int(hd.year_gr)
        month_gr = int(hd.month_gr)
        day_gr = int(hd.day_gr)
        if date_obj:
            return date_obj.replace(year=year_gr, month=month_gr, day=day_gr)
        else:
            return datetime(year=year_gr, month=month_gr, day=day_gr)
