# coding: utf-8
from __future__ import unicode_literals

import re
from collections import OrderedDict
from datetime import datetime

from dateutil import parser
from dateutil.relativedelta import relativedelta

from timezone_parser import pop_tz_offset_from_string, convert_to_local_tz


DATE_WORDS = 'Year|Month|Week|Day|Hour|Minute|Second'
SPECIAL_CASE_WORDS = 'Today|Yesterday|The day before yesterday'


class BaseParserInfo(parser.parserinfo):
    JUMP = [" ", ".", ",", ";", "-", "/", "'", "|", "@", "[", "]"]
    _SPECIAL_TOKENS = [":", ".", " ", "-", "/"]  # Consts used in dateutil.parser._parse

    def __init__(self, dayfirst=False, yearfirst=False):
        super(BaseParserInfo, self).__init__(dayfirst=dayfirst, yearfirst=yearfirst)
        self._known_tokens = set(self._SPECIAL_TOKENS)
        for dct in (self._jump,
                    self._weekdays,
                    self._months,
                    self._hms,
                    self._ampm,
                    self._utczone,
                    self._pertain):
            for token in dct.keys():
                self._known_tokens.add(token)

    def is_token_known(self, name):
        return name.lower() in self._known_tokens

    def weekday(self, name):
        if len(name) >= 2:
            try:
                return self._weekdays[name.lower()]
            except KeyError:
                pass
        return None


class es_parserinfo(BaseParserInfo):
    JUMP = BaseParserInfo.JUMP + ["de", "del"]

    WEEKDAYS = [
        ("Lunes",),
        ("Martes",),
        ("Miércoles",),
        ("Jueves",),
        ("Viernes",),
        ("Sábado",),
        ("Domingo",),
    ]

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

    PERTAIN = ["de", "del"]


class fr_parserinfo(BaseParserInfo):
    JUMP = BaseParserInfo.JUMP + ["le"]

    WEEKDAYS = [
        ("Lundi",),
        ("Mardi",),
        ("Mercredi",),
        ("Jeudi",),
        ("Vendredi",),
        ("Samedi",),
        ("Dimanche",),
    ]

    MONTHS = [
        ('janvier', 'janv', 'jan'),
        ('février', 'févr', 'fév'),
        ('mars', 'mar'),
        ('avril', 'avr'),
        ('mai'),
        ('juin'),
        ('juillet', 'juil'),
        ('août', 'aoû'),
        ('septembre', 'sept', 'sep'),
        ('octobre', 'oct'),
        ('novembre', 'nov'),
        ('décembre', 'déc'),
    ]


class it_parserinfo(BaseParserInfo):
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


class pt_parserinfo(BaseParserInfo):
    JUMP = BaseParserInfo.JUMP + ["de"]

    WEEKDAYS = [
        ("Segunda-feira",),
        ("Terça-feira",),
        ("Quarta-feira",),
        ("Quinta-feira",),
        ("Sexta-feira",),
        ("Sábado",),
        ("Domingo",),
    ]

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

    PERTAIN = ["de"]


class tr_parserinfo(BaseParserInfo):
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


class ru_parserinfo(BaseParserInfo):
    JUMP = BaseParserInfo.JUMP + ["в"]

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


class cz_parserinfo(BaseParserInfo):
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


class de_parserinfo(BaseParserInfo):
    JUMP = BaseParserInfo.JUMP + ["um", "uhr"]

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


class ro_parserinfo(BaseParserInfo):
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


class nl_parserinfo(BaseParserInfo):
    WEEKDAYS = [
        ("Maandag", "ma"),
        ("Dinsdag", "di"),
        ("Woensdag", "wo"),
        ("Donderdag", "do"),
        ("Vrijdag", "vr"),
        ("Zaterdag", "za"),
        ("Zondag", "zo"),
    ]

    MONTHS = [
        ('januari', 'jan'),
        ('februari', 'feb'),
        ('maart', 'mrt'),
        ('april', 'apr'),
        ('mei',),
        ('juni', 'jun'),
        ('juli', 'jul'),
        ('augustus', 'aug'),
        ('september', 'sep'),
        ('oktober', 'okt'),
        ('november', 'nov'),
        ('december', 'dec'),
    ]

class vi_parserinfo(BaseParserInfo):
    JUMP = BaseParserInfo.JUMP + ["lúc"]

    # From http://www.cjvlang.com/Dow/dowviet.html
    WEEKDAYS = [
        ("Thứ hai",),
        ("Thứ ba",),
        ("Thứ tư",),
        ("Thứ năm",),
        ("Thứ sáu",),
        ("Thứ bảy",),
        ("Chủ nhật",)
    ]

    # From http://free.lessons.l-ceps.com/learn-vietnamese-free-lesson-10.html
    MONTHS = [
        ('Tháng một',),
        ('Tháng hai',),
        ('Tháng ba',),
        ('Tháng tư',),
        ('Tháng năm',),
        ('Tháng sáu',),
        ('Tháng bảy',),
        ('Tháng tám',),
        ('Tháng chín',),
        ('Tháng mười',),
        ('Tháng mười một',),
        ('Tháng mười hai',)
    ]

class en_parserinfo(BaseParserInfo):
    JUMP = list(set(BaseParserInfo.JUMP) | set(parser.parserinfo.JUMP))


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
    ('nl', nl_parserinfo()),
    ('vi', vi_parserinfo()),
    ('en', en_parserinfo())
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

    @classmethod
    def split(cls, s):
        s = cls.prepare_string(s)
        return super(new_timelex, cls).split(s)

    @classmethod
    def prepare_string(cls, s):
        # As we added '-' to .wordchars because some weekdays contain it, we would always keep it
        # as part of a word. Therefore in case '-' is clearly a separator (next to number)
        # we should not keep it as part of the word but substitute it with space.
        s = re.sub('(\d)[-]+', r'\1 ', s)
        s = re.sub('[-]+(\d)', r' \1', s)
        return s


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

    return dateutil_parse(date_string, parserinfo=INFOS[language], ignoretz=True)


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


def get_language_candidates(tokens, languages=None, exclude_languages=None):
    """Find the languages which have a word matching
    at least one of the given tokens and all tokens are known by this language
    """
    languages = languages if languages else INFOS.keys()
    if exclude_languages:
        languages = filter(lambda l: l not in exclude_languages, languages)

    candidates = []
    require_fuzzy = False
    for lang in languages:
        should_add = True
        for token in tokens:
            if not token.isdigit() and not INFOS[lang].is_token_known(token):
                require_fuzzy = True
                should_add = False
                break
        if should_add:
            candidates.append(lang)

    if require_fuzzy and not candidates and exclude_languages:
        # Temporary log message to help find those sites relying on fuzzy parsing
        from scrapy import log
        log.msg('REQUIRE FUZZY: %s' % repr(''.join(tokens)), _level=log.CRITICAL)

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
        date_string, tz_offset = pop_tz_offset_from_string(date_string)
        date_obj = self._parser.parse(date_string, date_format)
        if tz_offset is not None:
            date_obj = convert_to_local_tz(date_obj, tz_offset)
        return date_obj
