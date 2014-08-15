# coding: utf-8
from __future__ import unicode_literals

import re
from collections import OrderedDict
from datetime import datetime

from dateutil import parser


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
        ('Şubat'),
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


INFOS = OrderedDict([
    ('es', es_parserinfo()),
    ('fr', fr_parserinfo()),
    ('it', it_parserinfo()),
    ('pt', pt_parserinfo()),
    ('tr', tr_parserinfo()),
    ('ru', ru_parserinfo()),
    ('cz', cz_parserinfo()),
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


class DateParser(object):

    def __init__(self, language=None):
        self.language = language
        self.detected_languages = None

    def parse(self, date_string, date_format=None):
        date_string = unicode(date_string)

        if not date_string.strip():
            raise ValueError("Empty string")

        if self.language is None:
            languages = self.detect_language(date_string)
            l = len(languages)
            if l > 1:
                for lang in languages:
                    try:
                        return self._parse(date_string, lang, date_format)
                    except:
                        continue
                else:
                    raise ValueError("Invalid date: %s" % date_string)
            else:
                if l == 1:
                    self.language = languages[0]
                    return self._parse(date_string, self.language, date_format)
                else:
                    return self.parser_parse(date_string)
        else:
            return self._parse(date_string, self.language, date_format)

    def _build_table(self, info):
        """Build a table to substitute month names per month numbers"""
        table = {}

        # TODO: weekdays?
        for pos, months in enumerate(info.MONTHS, 1):
            for m in months:
                table[m] = '%02d' % pos

        return table

    def translate_words(self, date_string, language):
        info = INFOS[language]

        table = self._build_table(info)

        for word, pos in sorted(table.items(), key=lambda x: len(x[0]), reverse=True):
            date_string = re.sub(word, str(pos), date_string, flags=re.IGNORECASE)

        return date_string

    def translate_format(self, date_format):
        # TODO: weekdays?
        return date_format.replace('%b', '%m').replace('%B', '%m')

    def _parse(self, date_string, language, date_format):
        if date_format:

            date_format = self.translate_format(date_format)
            date_string = self.translate_words(date_string, language)

            return datetime.strptime(date_string, date_format)

        return self.parser_parse(date_string, parserinfo=INFOS[language],
                                 ignoretz=True, fuzzy=True)

    def parser_parse(self, date_string, **kwargs):
        # XXX: this is needed because of a bug in dateutil.parser
        # that raises TypeError for an invalid string
        # https://bugs.launchpad.net/dateutil/+bug/1042851
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        kwargs.update(default=today)
        try:
            return parser.parse(date_string, **kwargs)
        except TypeError, e:
            raise ValueError(e, "Invalid date: %s" % date_string)

    def has_found_candidates_previously(self):
        return self.detected_languages is not None

    def is_word_in_language(self, token, language):
        """Check if token is a word in the given language
        """
        return INFOS[language].month(token)

    def get_candidates_for_tokens(self, tokens, languages):
        """Find the languages which have a word matching
        at least one of the given tokens
        """
        candidates = []

        for lang in languages:
            for token in tokens:
                if self.is_word_in_language(token, lang):
                    candidates.append(lang)

        return candidates

    def tokenize(self, date_string):
        return new_timelex.split(date_string)

    def detect_language(self, date_string):
        if self.has_found_candidates_previously():
            known_languages = self.detected_languages
        else:
            known_languages = list(INFOS.keys())

        tokens = self.tokenize(date_string)

        candidate_langs = self.get_candidates_for_tokens(tokens, known_languages)

        # we want to avoid setting detected_languages earlier, because dates like
        # "01/01/1970" should not limit the languages to try for the next date
        if candidate_langs:
            self.detected_languages = candidate_langs

        return candidate_langs
