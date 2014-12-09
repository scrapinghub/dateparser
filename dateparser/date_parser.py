# coding: utf-8
from __future__ import unicode_literals

from datetime import datetime

from dateutil import parser
from dateutil.relativedelta import relativedelta

from dateparser.languages import LanguageDataLoader
from dateparser.languages.detection import ExactLanguage, AutoDetectLanguage
from dateparser.timezones import pop_tz_offset_from_string, convert_to_local_tz


class new_relativedelta(relativedelta):
    """ dateutil does not check if result of parsing weekday is in the future.
    Although items dates are already in the past, so we need to fix this particular case.
    """

    def __new__(cls, *args, **kwargs):
        if not args and len(kwargs) == 1 and 'weekday' in kwargs:
            return super(new_relativedelta, cls).__new__(cls, *args, **kwargs)
        else:
            # use original class to parse other cases
            return relativedelta(*args, **kwargs)

    def __add__(self, other):
        ret = super(new_relativedelta, self).__add__(other)
        if ret > datetime.utcnow():
            ret -= relativedelta(days=7)
        return ret

parser.relativedelta.relativedelta = new_relativedelta


class DateParser(object):

    def __init__(self, language=None, allow_redetect_language=False):
        parser_cls = ExactLanguage if language else AutoDetectLanguage

        if isinstance(language, basestring):
            available_language_map = default_language_loader.get_language_map()
            if language in available_language_map:
                language = available_language_map[language]
            else:
                raise ValueError("Unknown language %r" % language)

        if allow_redetect_language:
            self._parser = AutoDetectLanguage(language, allow_redetection=True)
        else:
            self._parser = parser_cls(language)

    def parse(self, date_string, date_format=None):
        date_string = unicode(date_string)

        if not date_string.strip():
            raise ValueError("Empty string")
        date_string, tz_offset = pop_tz_offset_from_string(date_string)
        date_obj = self._parser.parse(date_string, date_format)
        if tz_offset is not None:
            date_obj = convert_to_local_tz(date_obj, tz_offset)
        return date_obj


default_language_loader = LanguageDataLoader()
