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


def dateutil_parse(date_string, **kwargs):
    """Wrapper function around dateutil.parser.parse
    """
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    kwargs.update(default=today)

    # XXX: this is needed because of a bug in dateutil.parser
    # that raises TypeError for an invalid string
    # https://bugs.launchpad.net/dateutil/+bug/1042851
    try:
        return parser.parse(date_string, **kwargs)
    except TypeError, e:
        raise ValueError(e, "Invalid date: %s" % date_string)


class DateParser(object):

    def __init__(self, language=None, allow_redetect_language=False):
        if isinstance(language, basestring):
            available_language_map = default_language_loader.get_language_map()
            if language in available_language_map:
                language = available_language_map[language]
            else:
                raise ValueError("Unknown language %r" % language)

        if allow_redetect_language:
            self._parser = AutoDetectLanguage(languages=[language] if language else None, allow_redetection=True)
        elif language:
            self._parser = ExactLanguage(language=language)
        else:
            self._parser = AutoDetectLanguage(languages=None, allow_redetection=False)

    def parse(self, date_string):
        date_string = unicode(date_string)

        if not date_string.strip():
            raise ValueError("Empty string")

        date_string, tz_offset = pop_tz_offset_from_string(date_string)

        for language in self._parser.iterate_applicable_languages(date_string, modify=True):
            translated_date = language.translate(date_string, keep_formatting=True)
            try:
                date_obj = dateutil_parse(translated_date)
            except ValueError:
                continue
            else:
                break
        else:
            raise ValueError(u"Invalid date: %s" % date_string)

        if tz_offset is not None:
            date_obj = convert_to_local_tz(date_obj, tz_offset)

        return date_obj


default_language_loader = LanguageDataLoader()
