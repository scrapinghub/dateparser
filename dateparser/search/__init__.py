# -*- coding: utf-8 -*-
from .search import DateSearchWithDetection

_search_with_detection = DateSearchWithDetection()


def search_dates(text, languages=None, settings=None):
    result = _search_with_detection.search_dates(text=text, languages=languages, settings=settings)
    if result['Dates']:
        return result['Dates']
