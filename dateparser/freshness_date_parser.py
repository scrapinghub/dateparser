# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re
from datetime import datetime

from dateutil.relativedelta import relativedelta

from dateparser.languages import LanguageDataLoader


class FreshnessDateDataParser(object):
    """ Parses date string like "1 year, 2 months ago" and "3 hours, 50 minutes ago" """

    def __init__(self, now=None):
        self.now = now or datetime.utcnow()

    def parse(self, date_string):
        for language in default_language_loader.get_languages():
            if language.is_applicable(date_string):
                break
        else:
            return None, None

        kwargs = self.get_kwargs(date_string, language)
        if not kwargs:
            return None, None

        period = 'day'
        if 'days' not in kwargs:
            for k in ['weeks', 'months', 'years']:
                if k in kwargs:
                    period = k
                    break

        td = relativedelta(**kwargs)
        date = self.now - td
        return date, period

    def apply_replacements(self, date_string, lang):
        if 'word_replacements' in lang:
            for replacement, words in lang['word_replacements']:
                for w in words:
                    date_string = re.sub(ur'\b%s\b' % w, replacement, date_string,
                                         flags=re.IGNORECASE | re.UNICODE)

        return date_string

    def get_kwargs(self, date_string, language):
        date_string = language.translate(date_string)

        m = re.findall(r'(\d+)\s*(year|month|week|day|hour|minute|second)\b', date_string, re.I | re.S | re.U)
        if not m:
            return {}

        kwargs = {}
        for num, unit in m:
            kwargs[unit + 's'] = int(num)

        years = kwargs.get('years', None)
        months = kwargs.get('months', None)

        validate = lambda val, lower, upper: \
            val is None or (lower <= val <= upper)

        if validate(years, 1, 19) and validate(months, 1, 12):
            return kwargs
        else:
            return {}

    def get_date_data(self, date_string):
        date, period = self.parse(date_string)
        return dict(date_obj=date, period=period)

default_language_loader = LanguageDataLoader()
freshness_date_parser = FreshnessDateDataParser()
