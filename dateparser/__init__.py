# -*- coding: utf-8 -*-
__version__ = '0.1.0'

from date import DateDataParser

_default_parser = DateDataParser(allow_redetect_language=True)


def parse(date_string, date_formats=None, languages=None):
    """Parse date and time from given date string.

    :param date_string:
            A string representing date and/or time in a recognizably valid format.
    :param date_formats:
            A list of format strings using directives as given here_.
            The parser applies formats one by one, taking into account the detected
            languages.

    .. _here: https://docs.python.org/2/library/datetime.html#strftime-and-strptime-behavior
    :param date_languages:
            A list of two letters language codes.e.g. ['en', 'es'].
            If languages are given, it will not attempt to detect the language.
        
    :return: 
            Returns a :mod:`datetime.datetime` if successful, else returns None
    """
    parser = _default_parser

    if languages:
        parser = DateDataParser(languages=languages)

    data = parser.get_date_data(date_string, date_formats)

    if data:
        return data['date_obj']
