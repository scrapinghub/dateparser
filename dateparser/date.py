# -*- coding: utf-8 -*-
import calendar
import collections
from datetime import datetime, timedelta
from warnings import warn

import six
import regex as re
from dateutil.relativedelta import relativedelta

from dateparser.date_parser import date_parser
from dateparser.parser import parse
from dateparser.freshness_date_parser import freshness_date_parser
from dateparser.languages.loader import LanguageDataLoader
from dateparser.languages.detection import AutoDetectLanguage, ExactLanguages
from dateparser.conf import apply_settings
from dateparser.utils import normalize_unicode


APOSTROPHE_LOOK_ALIKE_CHARS = [
    u'\N{RIGHT SINGLE QUOTATION MARK}',     # u'\u2019'
    u'\N{MODIFIER LETTER APOSTROPHE}',      # u'\u02bc'
    u'\N{MODIFIER LETTER TURNED COMMA}',    # u'\u02bb'
    u'\N{ARMENIAN APOSTROPHE}',             # u'\u055a'
    u'\N{LATIN SMALL LETTER SALTILLO}',     # u'\ua78c'
    u'\N{PRIME}',                           # u'\u2032'
    u'\N{REVERSED PRIME}',                  # u'\u2035'
    u'\N{MODIFIER LETTER PRIME}',           # u'\u02b9'
    u'\N{FULLWIDTH APOSTROPHE}',            # u'\uff07'
]


def sanitize_spaces(html_string):
    html_string = re.sub(u'\xa0', ' ', html_string, flags=re.UNICODE)
    html_string = re.sub(r'\s+', ' ', html_string)
    html_string = re.sub(r'^\s+(\S.*?)\s+$', r'\1', html_string)
    return html_string


def date_range(begin, end, **kwargs):
    dateutil_error_prone_args = ['year', 'month', 'week', 'day', 'hour',
                                 'minute', 'second']
    for arg in dateutil_error_prone_args:
        if arg in kwargs:
            raise ValueError("Invalid argument: %s" % arg)

    step = relativedelta(**kwargs) if kwargs else relativedelta(days=1)

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
        r'\t|\n|\r|\u00bb|,\s\u0432|\u200e|\xb7|\u200f|\u064e|\u064f',
        ' ', date_string, flags=re.M
    )
    date_string = re.sub(r'([\W\d])\u0433\.', r'\1 ', date_string,
                         flags=re.I | re.U)  # remove u'г.' (Russian for year) but not in words
    date_string = sanitize_spaces(date_string)
    date_string = re.sub(r'\b([ap])(\.)?m(\.)?\b', r'\1m', date_string, flags=re.DOTALL | re.I)
    date_string = re.sub(r'^.*?on:\s+(.*)', r'\1', date_string)

    date_string = re.sub(u'|'.join(APOSTROPHE_LOOK_ALIKE_CHARS), u"'", date_string)

    return date_string


def get_date_from_timestamp(date_string):
    if re.search(r'^\d{10}$', date_string):
        return datetime.fromtimestamp(int(date_string[:10]))


def get_last_day_of_month(year, month):
    return calendar.monthrange(year, month)[1]


def parse_with_formats(date_string, date_formats):
    """ Parse with formats and return a dictionary with 'period' and 'obj_date'.

    :returns: :class:`datetime.datetime`, dict or None

    """
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


class _DateLanguageParser(object):
    DATE_FORMATS_ERROR_MESSAGE = "Date formats should be list, tuple or set of strings"

    def __init__(self, language, date_string, date_formats, settings=None):
        self._settings = settings
        if isinstance(date_formats, six.string_types):
            warn(self.DATE_FORMATS_ERROR_MESSAGE, FutureWarning)
            date_formats = [date_formats]
        elif not (date_formats is None or isinstance(date_formats, (list, tuple, collections.Set))):
            raise TypeError(self.DATE_FORMATS_ERROR_MESSAGE)

        self.language = language
        self.date_string = date_string
        self.date_formats = date_formats
        self._translated_date = None
        self._translated_date_with_formatting = None

    @classmethod
    def parse(cls, language, date_string, date_formats=None, settings=None):
        instance = cls(language, date_string, date_formats, settings)
        return instance._parse()

    def _parse(self):
        for parser in (
            self._try_timestamp,
            self._try_freshness_parser,
            self._try_given_formats,
            self._try_parser,
            self._try_hardcoded_formats,
        ):
            date_obj = parser()
            if self._is_valid_date_obj(date_obj):
                return date_obj
        else:
            return None

    def _try_timestamp(self):
        return {
            'date_obj': get_date_from_timestamp(self.date_string),
            'period': 'day',
        }

    def _try_freshness_parser(self):
        return freshness_date_parser.get_date_data(self._get_translated_date(), self._settings)

    def _try_parser(self):
        _order = self._settings.DATE_ORDER 
        try:
            if self._settings.PREFER_LANGUAGE_DATE_ORDER:
                self._settings.DATE_ORDER = self.language.info.get('dateorder', _order)
            date_obj, period = date_parser.parse(
                self._get_translated_date(), settings=self._settings)
            self._settings.DATE_ORDER = _order
            return {
                'date_obj': date_obj,
                'period': period,
            }
        except ValueError:
            self._settings.DATE_ORDER = _order
            return None

    def _try_given_formats(self):
        if not self.date_formats:
            return

        return parse_with_formats(self._get_translated_date_with_formatting(), self.date_formats)

    def _try_hardcoded_formats(self):
        hardcoded_date_formats = [
            '%B %d, %Y, %I:%M:%S %p',
            '%b %d, %Y at %I:%M %p',
            '%d %B %Y %H:%M:%S',
            '%A, %B %d, %Y',
        ]
        try:
            return parse_with_formats(
                self._get_translated_date_with_formatting(), hardcoded_date_formats)
        except TypeError:
            return None

    def _get_translated_date(self):
        if self._translated_date is None:
            self._translated_date = self.language.translate(
                self.date_string, keep_formatting=False, settings=self._settings)
        return self._translated_date

    def _get_translated_date_with_formatting(self):
        if self._translated_date_with_formatting is None:
            self._translated_date_with_formatting = self.language.translate(
                self.date_string, keep_formatting=True, settings=self._settings)
        return self._translated_date_with_formatting

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
    """
    Class which handles language detection, translation and subsequent generic parsing of
    string representing date and/or time.

    :param languages:
            A list of two letters language codes, e.g. ['en', 'es'].
            If languages are given, it will not attempt to detect the language.
    :type languages: list

    :param allow_redetect_language:
            Enables/disables language re-detection.
    :type allow_redetect_language: bool

    :param settings:
           Configure customized behavior using settings defined in :mod:`dateparser.conf.Settings`.
    :type settings: dict

    :return: A parser instance

    :raises:
            ValueError - Unknown Language, TypeError - Languages argument must be a list
    """
    language_loader = None

    @apply_settings
    def __init__(self, languages=None, allow_redetect_language=False, settings=None):
        self._settings = settings
        available_language_map = self._get_language_loader().get_language_map()

        if isinstance(languages, (list, tuple, collections.Set)):

            if all([language in available_language_map for language in languages]):
                languages = [available_language_map[language] for language in languages]
            else:
                unsupported_languages = set(languages) - set(available_language_map.keys())
                raise ValueError(
                    "Unknown language(s): %s" % ', '.join(map(repr, unsupported_languages)))
        elif languages is not None:
            raise TypeError("languages argument must be a list (%r given)" % type(languages))

        if allow_redetect_language:
            self.language_detector = AutoDetectLanguage(
                languages if languages else list(available_language_map.values()),
                allow_redetection=True)
        elif languages:
            self.language_detector = ExactLanguages(languages=languages)
        else:
            self.language_detector = AutoDetectLanguage(
                list(available_language_map.values()), allow_redetection=False)

    def get_date_data(self, date_string, date_formats=None):
        """
        Parse string representing date and/or time in recognizable localized formats.
        Supports parsing multiple languages and timezones.

        :param date_string:
            A string representing date and/or time in a recognizably valid format.
        :type date_string: str|unicode
        :param date_formats:
            A list of format strings using directives as given
            `here <https://docs.python.org/2/library/datetime.html#strftime-and-strptime-behavior>`_.
            The parser applies formats one by one, taking into account the detected languages.
        :type date_formats: list

        :return: a dict mapping keys to :mod:`datetime.datetime` object and *period*. For example:
            {'date_obj': datetime.datetime(2015, 6, 1, 0, 0), 'period': u'day'}

        :raises: ValueError - Unknown Language

        .. note:: *Period* values can be a 'day' (default), 'week', 'month', 'year'.

        *Period* represents the granularity of date parsed from the given string.

        In the example below, since no day information is present, the day is assumed to be current
        day ``16`` from *current date* (which is June 16, 2015, at the moment of writing this).
        Hence, the level of precision is ``month``:

            >>> DateDataParser().get_date_data(u'March 2015')
            {'date_obj': datetime.datetime(2015, 3, 16, 0, 0), 'period': u'month'}

        Similarly, for date strings with no day and month information present, level of precision
        is ``year`` and day ``16`` and month ``6`` are from *current_date*.

            >>> DateDataParser().get_date_data(u'2014')
            {'date_obj': datetime.datetime(2014, 6, 16, 0, 0), 'period': u'year'}

        Dates with time zone indications or UTC offsets are returned in UTC time unless
        specified using `Settings`_.

            >>> DateDataParser().get_date_data(u'23 March 2000, 1:21 PM CET')
            {'date_obj': datetime.datetime(2000, 3, 23, 14, 21), 'period': 'day'}

        """
        if not(isinstance(date_string, six.text_type) or isinstance(date_string, six.string_types)):
            raise TypeError('Input type must be str or unicode')

        res = parse_with_formats(date_string, date_formats or [])
        if res['date_obj']:
            return res

        if self._settings.NORMALIZE:
           date_string = normalize_unicode(date_string)

        date_string = sanitize_date(date_string)

        for language in self.language_detector.iterate_applicable_languages(
                date_string, modify=True, settings=self._settings):
            parsed_date = _DateLanguageParser.parse(
                language, date_string, date_formats, settings=self._settings)
            if parsed_date:
                return parsed_date
        else:
            return {'date_obj': None, 'period': 'day'}

    def get_date_tuple(self, *args, **kwargs):
        date_tuple = collections.namedtuple('DateData', 'date_obj period')
        date_data = self.get_date_data(*args, **kwargs)
        return date_tuple(**date_data)

    @classmethod
    def _get_language_loader(cls):
        if not cls.language_loader:
            cls.language_loader = LanguageDataLoader()
        return cls.language_loader
