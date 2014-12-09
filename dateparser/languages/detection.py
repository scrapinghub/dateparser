# -*- coding: utf-8 -*-
import re
from datetime import datetime

from dateutil import parser

from dateparser.languages import LanguageDataLoader

default_language_loader = LanguageDataLoader()


class LanguageWasNotSeenBeforeError(Exception):
    pass


class DateParsingStrategy(object):

    def __init__(self, language=None):
        self.language = language

    def parse(self, date_string, date_format):
        """Attempts to parse a date using the given format
        """
        raise NotImplementedError

    @staticmethod
    def get_language_candidates(date_string, languages=None, exclude_languages=None):
        """Find the languages which have a word matching
        at least one of the given tokens and all tokens are known by this language
        """
        languages = languages if languages else default_language_loader.get_languages()
        if exclude_languages:
            languages = filter(lambda l: l not in exclude_languages, languages)

        candidates = []
        for language in languages:
            if language.is_applicable(date_string):
                candidates.append(language)

        return candidates

    @classmethod
    def parse_using_languages(cls, date_string, date_format, languages):
        """Try parsing date using the given format for each of
        the languages given as argument
        """
        for lang in languages:
            try:
                return cls.parse_with_language_and_format(date_string, lang, date_format)
            except:
                continue
        else:
            raise ValueError("Invalid date: %s" % date_string)

    @classmethod
    def parse_with_language_and_format(cls, date_string, language, date_format):
        date_string = language.translate(date_string, keep_formatting=bool(date_format))

        if date_format:
            date_format = re.sub(r'(?<!%)%b', '%B', date_format)
            return datetime.strptime(date_string, date_format)

        return dateutil_parse(date_string, ignoretz=True)


class AutoDetectLanguage(DateParsingStrategy):
    """Date parser with support for language detection.

    It uses the get_language_candidates() method to get the
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
        candidates = self.get_language_candidates(date_string, self.detected_languages)

        if not candidates and self.detected_languages:
            raise LanguageWasNotSeenBeforeError

        self.detected_languages = candidates

        if len(candidates) == 1:
            self.language = candidates[0]

        return candidates

    def detect_unseen_language(self, date_string):
        return self.get_language_candidates(date_string,
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

        return self.parse_using_languages(date_string, date_format, languages)

    def parse(self, date_string, date_format):
        if self.language:
            try:
                languages = [self.language]
                return self.parse_using_languages(date_string, date_format, languages)
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
        return self.parse_using_languages(date_string, date_format, [self.language])


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


