# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re
from datetime import datetime

from dateutil.relativedelta import relativedelta

from dateparser.utils import wrap_replacement_for_regex


class FreshnessDateDataParser(object):
    """ Parses date string like "1 year, 2 months ago" and "3 hours, 50 minutes ago" """

    def __init__(self, now=None):
        self.now = now or datetime.utcnow()

    def parse(self, date_string):
        kwargs = self.get_kwargs(date_string)
        if not kwargs:
            return None, None

        period = 'day'
        if 'days' not in kwargs:
            for k in ['weeks', 'months', 'years']:
                if k in kwargs:
                    period = k[:-1]
                    break

        td = relativedelta(**kwargs)
        date = self.now - td
        return date, period

    def apply_replacements(self, date_string, lang):
        if 'word_replacements' in lang:
            for replacement, words in lang['word_replacements']:
                for w in words:
                    wrapped_replacement = wrap_replacement_for_regex(replacement, w)
                    w = ur'(\A|\d|_|\W)%s(\d|_|\W|\Z)' % w
                    date_string = re.sub(w, wrapped_replacement, date_string, flags=re.IGNORECASE | re.UNICODE)
        return date_string

    def get_kwargs(self, date_string):
        m = re.findall(r'(\d+)\s*(year|month|week|day|hour|minute|second)\b', date_string, re.I | re.S | re.U)
        if not m:
            return {}

        kwargs = {}
        for num, unit in m:
            kwargs[unit + 's'] = int(num)

        return kwargs

    def get_date_data(self, date_string):
        date, period = self.parse(date_string)
        return dict(date_obj=date, period=period)

freshness_date_parser = FreshnessDateDataParser()
