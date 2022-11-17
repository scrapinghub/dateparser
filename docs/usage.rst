.. _using-datedataparser:


Using DateDataParser
--------------------

:func:`dateparser.parse` uses a default parser which tries to detect language
every time it is called and is not the most efficient way while parsing dates
from the same source.

:class:`DateDataParser <dateparser.date.DateDataParser>` provides an alternate and efficient way
to control language detection behavior.

The instance of :class:`DateDataParser <dateparser.date.DateDataParser>` caches the found
languages and will prioritize them when trying to parse the next string.

:class:`dateparser.date.DateDataParser` can also be initialized with known languages:

    >>> ddp = DateDataParser(languages=['de', 'nl'])
    >>> ddp.get_date_data('vr jan 24, 2014 12:49')
    DateData(date_obj=datetime.datetime(2014, 1, 24, 12, 49), period='day', locale='nl')
    >>> ddp.get_date_data('18.10.14 um 22:56 Uhr')
    DateData(date_obj=datetime.datetime(2014, 10, 18, 22, 56), period='day', locale='de')
    >>> ddp.get_date_data('11 July 2012')
    DateData(date_obj=None, period='day', locale=None)
