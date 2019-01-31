# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from dateparser.search.search import DateSearchWithDetection

_search_with_detection = DateSearchWithDetection()


def search_dates(text, languages=None, settings=None):
    """Find all substrings of the given string which represent date and/or time and parse them.

        :param text:
            A string in a natural language which may contain date and/or time expressions.
        :type text: str|unicode
        :param languages:
            A list of two letters language codes.e.g. ['en', 'es']. If languages are given, it will not attempt
            to detect the language.
        :type languages: list
        :param settings:
               Configure customized behavior using settings defined in :mod:`dateparser.conf.Settings`.
        :type settings: dict


        :return: Returns list of tuples containing pairs:
                 substrings representing date and/or time and corresponding :mod:`datetime.datetime` object.
                 Returns None if no dates that can be parsed are found.
        :rtype: list
        :raises: ValueError - Unknown Language

        >>> search_dates('The first artificial Earth satellite was launched on 4 October 1957.')
        [('on 4 October 1957', datetime.datetime(1957, 10, 4, 0, 0))]

        """
    result = _search_with_detection.search_dates(text=text, languages=languages, settings=settings)
    if result['Dates']:
        return result['Dates']


def search_dates_interval(text, languages=None, settings=None):
    """Find all substrings of the given string which represent date and/or time and parse them. Parsing includes 
    dates and time intervals.

        :param text:
            A string in a natural language which may contain date and/or time expressions.
        :type text: str|unicode
        :param languages:
            A list of two letters language codes.e.g. ['en', 'es']. If languages are given, it will not attempt
            to detect the language.
        :type languages: list
        :param settings:
               Configure customized behavior using settings defined in :mod:`dateparser.conf.Settings`.
        :type settings: dict


        :return: Returns list of tuples containing pairs:
                 substrings representing date and/or time and corresponding dictionary containing:
                    date obj: a datetime object with the parsed date
                    date_begin: a datetime object with the beginning date in case it is a time interval
                    date_end: a datetime object with the end date in case it is a time interval
                    is_range: a boolean that is true when the parsed string contains a time interval
                 Returns None if no dates that can be parsed are found.
        :rtype: list
        :raises: ValueError - Unknown Language

        >>> search_dates_interval('The first artificial Earth satellite was launched on 4 October 1957.')
        [('on 4 October 1957',
            {'date_obj': datetime.datetime(1957, 10, 4, 0, 0),
            'date_begin': None,
            'date_end': None,
            'is_range': False})]

        >>> search_dates_interval('January.')
        [('January 2009',
            {'date_obj': datetime.datetime(2009, 1, 30, 0, 0),
            'date_begin': datetime.datetime(2009, 1, 1, 0, 0),
            'date_end': datetime.datetime(2009, 1, 31, 0, 0),
            'is_range': True})]

        >>> search_dates_interval('2010')
        [('2010',
            {'date_obj': datetime.datetime(2010, 1, 30, 0, 0),
            'date_begin': datetime.datetime(2010, 1, 1, 0, 0),
            'date_end': datetime.datetime(2010, 12, 31, 0, 0),
            'is_range': True})]
        """
    result = _search_with_detection.search_dates_interval(text=text, languages=languages, settings=settings)
    if result['Dates']:
        return result['Dates']
