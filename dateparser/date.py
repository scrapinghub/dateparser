# -*- coding: utf-8 -*-
import calendar
import collections
import re
from datetime import datetime, timedelta
from functools import wraps
from types import NoneType
from warnings import warn

from dateutil.relativedelta import relativedelta

from dateparser.date_parser import date_parser
from dateparser.freshness_date_parser import freshness_date_parser
from dateparser.languages import LanguageDataLoader
from dateparser.languages.detection import AutoDetectLanguage, ExactLanguages


def sanitize_spaces(html_string):
    html_string = re.sub(u'\xa0', ' ', html_string, flags=re.UNICODE)
    html_string = re.sub(r'\s+', ' ', html_string)
    html_string = re.sub(r'^\s+(\S.*?)\s+$', r'\1', html_string)
    return html_string


def date_range(begin, end, **kwargs):
    step = relativedelta(**kwargs) if kwargs else relativedelta(days=1)

    dateutil_error_prone_args = ['year', 'month', 'week', 'day', 'hour',
                                 'minute', 'second']
    for arg in dateutil_error_prone_args:
        if arg in kwargs:
            raise ValueError("Invalid argument: %s" % arg)

    date = begin
    while date < end:
        yield date
        date += step

    # handles edge-case when iterating months and last interval is < 30 days
    if kwargs.get('months', 0) > 0 and (date.year, date.month) == (end.year, end.month):
        yield end


def get_intersecting_periods(low, high, period='day'):
    if period not in ['year', 'month', 'week', 'day', 'hour', 'minute', 'second', 'microsecond']:
        raise ValueError("Invalid period: {}".format(period))

    if high <= low:
        return

    step = relativedelta(**{period + 's': 1})

    current_period_start = low
    if isinstance(current_period_start, datetime):
        reset_arguments = {}
        for test_period in ['microsecond', 'second', 'minute', 'hour']:
            if test_period == period:
                break
            else:
                reset_arguments[test_period] = 0
        current_period_start = current_period_start.replace(**reset_arguments)

    if period == 'week':
        current_period_start \
            = current_period_start - timedelta(days=current_period_start.weekday())
    elif period == 'month':
        current_period_start = current_period_start.replace(day=1)
    elif period == 'year':
        current_period_start = current_period_start.replace(month=1, day=1)

    while current_period_start < high:
        yield current_period_start
        current_period_start += step


def sanitize_date(date_string):
    date_string = re.sub(
        r'\t|\n|\r|\u00bb|,\s\u0432|\u0433\.|\u200e|\xb7|\u200f|\u064e|\u064f',
        ' ', date_string, flags=re.M
    )
    date_string = sanitize_spaces(date_string)
    date_string = re.sub(r'\b([ap])(\.)?m(\.)?\b', r'\1m', date_string, flags=re.DOTALL | re.I)
    date_string = re.sub(r'^.*?on:\s+(.*)', r'\1', date_string)

    return date_string


def get_date_from_timestamp(date_string):
    if re.search(r'^\d{10}', date_string):
        return datetime.fromtimestamp(int(date_string[:10]))


def get_last_day_of_month(year, month):
    return calendar.monthrange(year, month)[1]


def parse_with_formats(date_string, date_formats):
    """ Parse with formats and return a dictionary with 'period' and 'obj_date'.

    :returns: :class:`datetime.datetime`, dict or None

    """
    # Encode to support locale setting in spiders
    if isinstance(date_string, unicode):
        date_string = date_string.encode('utf-8')

    period = 'day'
    for date_format in date_formats:
        try:
            date_obj = datetime.strptime(date_string, date_format)
        except ValueError:
            continue
        else:
            # If format does not include the day, use last day of the month
            # instead of first, because the first is usually out of range.
            if '%d' not in date_format:
                period = 'month'
                date_obj = date_obj.replace(
                    day=get_last_day_of_month(date_obj.year, date_obj.month))

            if not ('%y' in date_format or '%Y' in date_format):
                today = datetime.today()
                date_obj = date_obj.replace(year=today.year)

            return {'date_obj': date_obj, 'period': period}
    else:
        return {'date_obj': None, 'period': period}


def same_for_all_languages(method):
    @wraps(method)
    def wrapped(self, language):
        control_attribute = '__{}_executed'.format(method.func_name)
        if getattr(self, control_attribute, False):
            return
        result = method(self, language)
        setattr(self, control_attribute, True)
        return result
    return wrapped


class _DateLanguageParser(object):
    DATE_FORMATS_ERROR_MESSAGE = "Date formats should be list, tuple or set of strings"
    HARDCODED_DATE_FORMATS = [
        '%B %d, %Y, %I:%M:%S %p',
        '%b %d, %Y at %I:%M %p',
        '%d %B %Y %H:%M:%S',
        '%A, %B %d, %Y',
    ]

    def __init__(self, language_iterator, date_string, date_formats):
        if isinstance(date_formats, basestring):
            warn(self.DATE_FORMATS_ERROR_MESSAGE, FutureWarning)
            date_formats = [date_formats]
        elif not isinstance(date_formats, (list, tuple, collections.Set, NoneType)):
            raise TypeError(self.DATE_FORMATS_ERROR_MESSAGE)

        self.language_iterator = language_iterator
        self.date_string = date_string
        self.date_formats = date_formats
        self._translations_cache = {}

    @classmethod
    def parse(cls, language_iterator, date_string, date_formats=None):
        instance = cls(language_iterator, date_string, date_formats)
        return instance._parse()

    def _parse(self):
        for language in self.language_iterator:
            date_obj = self._parse_for_language(language)
            if date_obj is not None:
                return date_obj
        else:
            return {'date_obj': None, 'period': 'day'}

    def _parse_for_language(self, language):
        for parser in (
            self._try_timestamp,
            self._try_freshness_parser,
            self._try_untranslated_with_given_formats,
            self._try_given_formats,
            self._try_dateutil_parser,
            self._try_untranslated_with_hardcoded_formats,
            self._try_hardcoded_formats,
        ):
            date_obj = parser(language)
            if self._is_valid_date_obj(date_obj):
                return date_obj
        else:
            return None

    @same_for_all_languages
    def _try_timestamp(self, language):
        return {
            'date_obj': get_date_from_timestamp(self.date_string),
            'period': 'day',
        }

    def _try_freshness_parser(self, language):
        return freshness_date_parser.get_date_data(self._get_translated_date(language))

    def _try_dateutil_parser(self, language):
        try:
            date_obj = date_parser.parse(self._get_translated_date(language))
            return {
                'date_obj': date_obj,
                'period': 'day',
            }
        except ValueError:
            return None

    def _try_given_formats(self, language):
        if not self.date_formats:
            return

        return parse_with_formats(self._get_translated_date_with_formatting(language), self.date_formats)

    @same_for_all_languages
    def _try_untranslated_with_given_formats(self, language):
        # TODO: When tests are unified we should add test to parse '02/12/2014 at 15:08' string
        # with ['%d/%m/%Y at %H:%M'] formats
        if not self.date_formats:
            return

        return parse_with_formats(self.date_string, self.date_formats)

    def _try_hardcoded_formats(self, language):
        return parse_with_formats(self._get_translated_date_with_formatting(language), self.HARDCODED_DATE_FORMATS)

    @same_for_all_languages
    def _try_untranslated_with_hardcoded_formats(self, language):
        return parse_with_formats(self.date_string, self.HARDCODED_DATE_FORMATS)

    def _get_translated_date(self, language):
        return self._get_translation(language, keep_formatting=False)

    def _get_translated_date_with_formatting(self, language):
        return self._get_translation(language, keep_formatting=True)

    def _get_translation(self, language, keep_formatting):
        if (language.shortname, keep_formatting) not in self._translations_cache:
            translation = language.translate(self.date_string, keep_formatting)
            self._translations_cache[language.shortname, keep_formatting] = translation
        return self._translations_cache[language.shortname, keep_formatting]

    def _is_valid_date_obj(self, date_obj):
        if not isinstance(date_obj, dict):
            return False
        if len(date_obj) != 2:
            return False
        if 'date_obj' not in date_obj or 'period' not in date_obj:
            return False
        if not date_obj['date_obj']:
            return False
        if date_obj['period'] not in ('day', 'week', 'month', 'year'):
            return False

        return True


class DateDataParser(object):

    def __init__(self, languages=None, allow_redetect_language=False):
        if isinstance(languages, (list, tuple, collections.Set)):
            available_language_map = default_language_loader.get_language_map()

            if all([language in available_language_map for language in languages]):
                languages = [available_language_map[language] for language in languages]
            else:
                unsupported_languages = set(languages) - set(available_language_map.keys())
                raise ValueError("Unknown language(s) %r" % ', '.join(unsupported_languages))
        elif languages is not None:
            raise TypeError("languages argument must be a list (%r given)"  % type(languages))

        if allow_redetect_language:
            self.language_detector = AutoDetectLanguage(languages=languages if languages else None,
                                                        allow_redetection=True)
        elif languages:
            self.language_detector = ExactLanguages(languages=languages)
        else:
            self.language_detector = AutoDetectLanguage(languages=None, allow_redetection=False)

    def get_date_data(self, date_string, date_formats=None):
        """ Return a dictionary with a date object and a period.
        Period values can be a 'day' (default), 'week', 'month', 'year'.
        It aims to solve the following issue:
        In example, a forum could displays "2 weeks ago" in the thread list
        (in the thread itself there's the right date) so the engine
        will translate "2 weeks ago" to a certain date.
        The next thread summary displays "3 weeks ago" which is translated
        to a other date seven days before first date.
        A valid date_string between both dates won't be scraped because
        it's not an exact date match. The period field helps to build
        better date range detection.

        TODO: Timezone issues

        """
        date_string = date_string.strip()
        date_string = sanitize_date(date_string)

        language_iterator = self.language_detector.iterate_applicable_languages(date_string, modify=True)
        return _DateLanguageParser.parse(language_iterator, date_string, date_formats)


default_language_loader = LanguageDataLoader()
