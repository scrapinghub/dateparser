
__version__ = '0.1.0'


from dateparser.date import DateDataParser

_default_parser = DateDataParser(allow_redetect_language=True)


def parse(date_string, date_formats=None, language=None):
    """Parse date and time from given date string.

    If language is given, it will not attempt to detect the language.

    A list of formats can also be provided, in which case
    it will attempt to use the formats one by one, taking
    into account the detected language.

    Returns a datetime.datetime() if successful, else returns None
    """
    parser = _default_parser

    if language:
        parser = DateDataParser(language=language)

    data = parser.get_date_data(date_string, date_formats)

    if data:
        return data['date_obj']
