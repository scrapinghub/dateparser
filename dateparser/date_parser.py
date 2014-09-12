# coding: utf-8
from __future__ import unicode_literals

import re
from collections import OrderedDict
from datetime import datetime

from dateutil import parser
from dateutil.relativedelta import relativedelta


DATE_WORDS = 'Year|Month|Week|Day|Hour|Minute|Second'
SPECIAL_CASE_WORDS = 'Today|Yesterday|The day before yesterday'


class es_parserinfo(parser.parserinfo):
    MONTHS = [
        ('enero', 'ene'),
        ('febrero', 'feb'),
        ('marzo', 'mar'),
        ('abril', 'abr'),
        ('mayo', 'may'),
        ('junio', 'jun'),
        ('julio', 'jul'),
        ('agosto', 'ago'),
        ('septiembre', 'setiembre', 'sep', 'set'),
        ('octubre', 'oct'),
        ('noviembre', 'nov'),
        ('diciembre', 'dic'),
    ]


class fr_parserinfo(parser.parserinfo):
    MONTHS = [
        ('janvier', 'janv'),
        ('février', 'févr'),
        ('mars'),
        ('avril'),
        ('mai'),
        ('juin'),
        ('juillet', 'juil'),
        ('août',),
        ('septembre', 'sept'),
        ('octobre', 'oct'),
        ('novembre', 'nov'),
        ('décembre', 'déc'),
    ]


class it_parserinfo(parser.parserinfo):
    MONTHS = [
        ('gennaio', 'gen'),
        ('febbraio', 'feb'),
        ('marzo', 'mar'),
        ('aprile', 'apr'),
        ('maggio', 'mag'),
        ('giugno', 'giu'),
        ('luglio', 'lug'),
        ('agosto', 'ago'),
        ('settembre', 'set'),
        ('ottobre', 'ott'),
        ('novembre', 'nov'),
        ('dicembre', 'dic')
    ]


class pt_parserinfo(parser.parserinfo):
    MONTHS = [
        ('janeiro', u'jan'),
        ('fevereiro', u'fev'),
        ('março', u'mar'),
        ('abril', u'abr'),
        ('maio', u'mai'),
        ('junho', u'jun'),
        ('julho', u'jul'),
        ('agosto', u'ago'),
        ('septembro', u'setembro', u'septemberembro', u'set'),
        ('outubro', u'out'),
        ('novembro', u'nov'),
        ('dezembro', u'dez'),
    ]


class tr_parserinfo(parser.parserinfo):
    MONTHS = [
        ('Ocak',),
        ('Şubat',),
        ('Mart',),
        ('Nisan',),
        ('Mayıs',),
        ('Haziran',),
        ('Temmuz',),
        ('Ağustos',),
        ('Eylül',),
        ('Ekim',),
        ('Kasım',),
        ('Aralık',),
    ]


class ru_parserinfo(parser.parserinfo):
    MONTHS = [
        ('января', 'Января'),
        ('февраля', 'Февраля'),
        ('марта', 'Марта'),
        ('апреля', 'Апреля'),
        ('мая', 'Мая'),
        ('июня', 'Июня'),
        ('июля', 'Июля'),
        ('августа', 'Августа'),
        ('сентября', 'Сентября'),
        ('октября', 'Октября'),
        ('ноября', 'Ноября'),
        ('декабря', 'Декабря'),
    ]


class cz_parserinfo(parser.parserinfo):
    WEEKDAYS = [
        (u'pondělí', u'pon'),
        (u'úterý', u'úte'),
        (u'středa', u'stř'),
        (u'čtvrtek', u'čtv'),
        (u'pátek', u'pát'),
        (u'sobota', u'sob'),
        (u'neděle', u'ned'),
    ]

    MONTHS = [
        (u'leden', u'led'),
        (u'únor', u'úno'),
        (u'březen', u'bře'),
        (u'duben', u'dub'),
        (u'květen', u'kvě'),
        (u'červen', u'čer'),
        (u'červenec', u'črc'),
        (u'srpen', u'srp'),
        (u'září', u'zář'),
        (u'říjen', u'říj'),
        (u'listopad', u'lis'),
        (u'prosinec', u'pro'),
    ]


class de_parserinfo(parser.parserinfo):
    MONTHS = [
        ('Januar', 'Jan'),
        ('Februar', 'Feb'),
        ('März',),
        ('April', 'Apr'),
        ('Mai',),
        ('Juni',),
        ('Juli',),
        ('August', 'Aug'),
        ('September', 'Sept'),
        ('Oktober', 'Okt'),
        ('November', 'Nov'),
        ('Dezember', 'Dez'),
    ]


class ro_parserinfo(parser.parserinfo):
    MONTHS = [
        ('ianuarie', 'ian'),
        ('februarie', 'feb'),
        ('martie', 'mar'),
        ('aprilie', 'apr'),
        ('mai',),
        ('iunie',),
        ('iulie',),
        ('august', 'aug'),
        ('septembrie', 'sept'),
        ('octombrie', 'oct'),
        ('noiembrie', 'noiem'),
        ('decembrie', 'dec'),
    ]


INFOS = OrderedDict([
    ('es', es_parserinfo()),
    ('fr', fr_parserinfo()),
    ('it', it_parserinfo()),
    ('pt', pt_parserinfo()),
    ('tr', tr_parserinfo()),
    ('ru', ru_parserinfo()),
    ('cz', cz_parserinfo()),
    ('de', de_parserinfo()),
    ('ro', ro_parserinfo()),
    ('en', parser.parserinfo()),
])


class new_timelex(parser._timelex):

    def __init__(self, *args, **kwargs):
        super(new_timelex, self).__init__(*args, **kwargs)
        for k, info in INFOS.iteritems():
            for days in info.WEEKDAYS:
                self._update_wordchars_for_tokens(days)

            for months in info.MONTHS:
                self._update_wordchars_for_tokens(months)

    def _update_wordchars_for_tokens(self, tokens):
        for token in tokens:
            for char in token:
                if char not in self.wordchars:
                    self.wordchars += char

parser._timelex = new_timelex


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

tokenize_date = lambda s: new_timelex.split(s)


def _build_table(info):
    """Build a table to substitute month names per month numbers"""
    table = {}

    # TODO: weekdays?
    for pos, months in enumerate(info.MONTHS, 1):
        for m in months:
            table[m] = '%02d' % pos

    return table


def translate_words(date_string, language):
    """Translate date words in the given language into its equivalent number
    e.g.:  'January' -> 1 (english), 'Marzo' -> 3 (spanish), ...
    """
    info = INFOS[language]

    table = _build_table(info)

    for word, pos in sorted(table.items(), key=lambda x: len(x[0]), reverse=True):
        date_string = re.sub(word, str(pos), date_string, flags=re.IGNORECASE)

    return date_string


def convert_date_formats_to_numeric(date_format):
    # TODO: weekdays?
    return re.sub(r'(?<!%)%[bB]', '%m', date_format)


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


def parse_with_language_and_format(date_string, language, date_format):
    if date_format:

        date_format = convert_date_formats_to_numeric(date_format)
        date_string = translate_words(date_string, language)

        return datetime.strptime(date_string, date_format)

    return dateutil_parse(date_string, parserinfo=INFOS[language],
                          ignoretz=True, fuzzy=True)


def parse_using_languages(date_string, date_format, languages):
    """Try parsing date using the given format for each of
    the languages given as argument
    """
    for lang in languages:
        try:
            return parse_with_language_and_format(date_string, lang, date_format)
        except:
            continue
    else:
        raise ValueError("Invalid date: %s" % date_string)


def _is_word_in_language(token, language):
    """Check if token is a word in the given language
    """
    # XXX: needed for unclean dates (in URLs) like 14_luglio_2014
    token = token.strip('_')

    return INFOS[language].month(token)


def get_language_candidates(tokens, languages=None, exclude_languages=None):
    """Find the languages which have a word matching
    at least one of the given tokens
    """
    languages = languages if languages else INFOS.keys()
    if exclude_languages:
        languages = filter(lambda l: l not in exclude_languages, languages)

    candidates = []

    for lang in languages:
        for token in tokens:
            if _is_word_in_language(token, lang):
                candidates.append(lang)

    return candidates


class DateParsingStrategy(object):

    def __init__(self, language=None):
        self.language = language

    def parse(self, date_string, date_format):
        """Attempts to parse a date using the given format
        """
        raise NotImplementedError


class LanguageWasNotSeenBeforeError(RuntimeError):
    pass


class AutoDetectLanguage(DateParsingStrategy):
    """Date parser with support for language detection.

    It uses the get_language_candidates() function to get the
    possible languages for each date, keeps track of the
    previously detected languages and uses this information
    to reduce the set of possible languages.
    """
    def __init__(self, language=None, allow_redetection=False, *args, **kwargs):
        super(AutoDetectLanguage, self).__init__(language, *args, **kwargs)
        self.detected_languages = None
        self.allow_redetection = allow_redetection

    def has_found_candidates_previously(self):
        return self.detected_languages is not None

    def detect_language(self, date_string):
        tokens = tokenize_date(date_string)

        candidates = get_language_candidates(tokens, self.detected_languages)

        if not candidates and self.detected_languages:
            raise LanguageWasNotSeenBeforeError

        self.detected_languages = candidates

        if len(candidates) == 1:
            self.language = candidates[0]

        return candidates

    def detect_unseen_language(self, date_string):
        tokens = tokenize_date(date_string)
        return get_language_candidates(tokens,
                                       exclude_languages=self.detected_languages)

    def detect_language_and_parse(self, date_string, date_format):
        """Attempt to detect language and parse date.
        If no language is detected, fallback to vanilla dateutil parser
        """
        try:
            languages = self.detect_language(date_string)
        except LanguageWasNotSeenBeforeError:
            languages = self.detect_unseen_language(date_string)
            if languages and not self.allow_redetection:
                raise

        if not languages:
            return dateutil_parse(date_string)

        return parse_using_languages(date_string, date_format, languages)

    def parse(self, date_string, date_format):
        if self.language:
            try:
                languages = [self.language]
                return parse_using_languages(date_string, date_format, languages)
            except ValueError:
                if self.allow_redetection:
                    return self.detect_language_and_parse(date_string, date_format)
                else:
                    raise

        return self.detect_language_and_parse(date_string, date_format)


class ExactLanguage(DateParsingStrategy):
    """Date parser that works only for a specific language
    """
    def __init__(self, language, *args, **kwargs):
        super(ExactLanguage, self).__init__(language, *args, **kwargs)
        if language is None:
            raise ValueError("language cannot be None for ExactLanguage")

    def parse(self, date_string, date_format):
        return parse_using_languages(date_string, date_format, [self.language])


class DateParser(object):

    def __init__(self, language=None, allow_redetect_language=False):
        parser_cls = ExactLanguage if language else AutoDetectLanguage

        if allow_redetect_language:
            self._parser = AutoDetectLanguage(language, allow_redetection=True)
        else:
            self._parser = parser_cls(language)

    def parse(self, date_string, date_format=None):
        date_string = unicode(date_string)

        if not date_string.strip():
            raise ValueError("Empty string")

        return self._parser.parse(date_string, date_format)
