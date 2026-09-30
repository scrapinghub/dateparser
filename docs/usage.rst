.. _using-datedataparser:


Using DateDataParser
--------------------

:func:`dateparser.parse` uses a default parser which tries to detect language
every time it is called and is not the most efficient way while parsing dates
from the same source.

:class:`DateDataParser <dateparser.date.DateDataParser>` provides an alternate and efficient way
to control language detection behavior.

See :ref:`performance` for ways to make parsing faster.

:class:`dateparser.date.DateDataParser` can also be initialized with known languages:

    >>> ddp = DateDataParser(languages=['de', 'nl'])
    >>> ddp.get_date_data('vr jan 24, 2014 12:49')
    DateData(date_obj=datetime.datetime(2014, 1, 24, 12, 49), period='day', locale='nl', date_format=None)
    >>> ddp.get_date_data('18.10.14 um 22:56 Uhr')
    DateData(date_obj=datetime.datetime(2014, 10, 18, 22, 56), period='day', locale='de', date_format=None)
    >>> ddp.get_date_data('11 July 2012')
    DateData(date_obj=None, period='day', locale=None, date_format=None)


Getting the date format
+++++++++++++++++++++++

The ``date_format`` attribute of the returned ``DateData`` object is a format
that, passed in *date_formats* to the same parser, parses the same string into
the same date, or ``None`` if dateparser cannot provide one, e.g. for relative
dates or, for now, dates with a time or a time zone.

.. versionadded:: VERSION

For example:

    >>> ddp = DateDataParser(languages=['es'])
    >>> ddp.get_date_data('5 de julio de 2017').date_format
    '%d %B %Y'
