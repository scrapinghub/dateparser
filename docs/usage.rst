Using DateDataParser
--------------------

:func:`dateparser.parse` uses a default parser which tries to detect language
every time it is called and is not the most efficient way while parsing dates
from the same source.

:class:`DateDataParser <dateparser.date.DateDataParser>` provides an alternate and efficient way
to control language detection behavior.

The instance of :class:`DateDataParser <dateparser.date.DateDataParser>` reduces the number
of applicable languages, until only one or no language is left. It 
assumes the previously detected language for all the subsequent dates supplied and does not try
to execute the language detection again after a language is discarded.

This class wraps around the core :mod:`dateparser` functionality, and by default
assumes that all of the dates fed to it are in the same language.

.. autoclass:: dateparser.date.DateDataParser
   :members: get_date_data

.. warning:: It fails to parse *English* dates in the example below, because *Spanish* was detected and stored with the ``ddp`` instance:

    >>> ddp.get_date_data('11 August 2012')
    {'date_obj': None, 'period': 'day'}


:class:`dateparser.date.DateDataParser` can also be initialized with known languages:

    >>> ddp = DateDataParser(languages=['de', 'nl'])
    >>> ddp.get_date_data(u'vr jan 24, 2014 12:49')
    {'date_obj': datetime.datetime(2014, 1, 24, 12, 49), 'period': u'day'}
    >>> ddp.get_date_data(u'18.10.14 um 22:56 Uhr')
    {'date_obj': datetime.datetime(2014, 10, 18, 22, 56), 'period': u'day'}


Settings
========

:mod:`dateparser`'s parsing behavior can be configured like below:

``TIMEZONE`` defaults to `UTC`. All dates, complete or relative, are assumed to be in `UTC`. When specified, resultant :class:`datetime <datetime.datetime>` converts according to the supplied timezone:

    >>> parse('January 12, 2012 10:00 PM')
    datetime.datetime(2012, 1, 12, 22, 0)

    >>> parse('January 12, 2012 10:00 PM', settings={'TIMEZONE': 'US/Eastern'})
    datetime.datetime(2012, 1, 12, 17, 0)

``PREFER_DAY_OF_MONTH`` defaults to ``current`` and can have ``first`` and ``last`` as values:

    >>> from dateparser import parse
    >>> parse(u'December 2015')  # default behavior
    datetime.datetime(2015, 12, 16, 0, 0)
    >>> parse(u'December 2015', settings={'PREFER_DAY_OF_MONTH': 'last'})
    datetime.datetime(2015, 12, 31, 0, 0)
    >>> parse(u'December 2015', settings={'PREFER_DAY_OF_MONTH': 'first'})
    datetime.datetime(2015, 12, 1, 0, 0)

``PREFER_DATES_FROM`` defaults to ``current_period`` and can have ``past`` and ``future`` as values.
Assuming current date is June 16, 2015:

    >>> from dateparser import parse
    >>> parse(u'March')
    datetime.datetime(2015, 3, 16, 0, 0)
    >>> parse(u'March', settings={'PREFER_DATES_FROM': 'future'})
    datetime.datetime(2016, 3, 16, 0, 0)

``SKIP_TOKENS`` is a ``list`` of tokens to discard while detecting language. Defaults to ``['t']`` which skips T in iso format datetime string .e.g. ``2015-05-02T10:20:19+0000``.:

    >>> from dateparser.date import DateDataParser
    >>> DateDataParser(settings={'SKIP_TOKENS': ['de']}).get_date_data(u'27 Haziran 1981 de')  # Turkish (at 27 June 1981)
    {'date_obj': datetime.datetime(1981, 6, 27, 0, 0), 'period': 'day'}

``RETURN_AS_TIMEZONE_AWARE`` is a flag to turn on timezone aware dates if timezone is detected or specified.:

    >>> parse('12 Feb 2015 10:56 PM EST', settings={'RETURN_AS_TIMEZONE_AWARE': True})
    datetime.datetime(2015, 2, 13, 3, 56, tzinfo=<StaticTzInfo 'UTC'>)

    >>> parse('12 Feb 2015 10:56 PM EST', settings={'RETURN_AS_TIMEZONE_AWARE': True, 'TIMEZONE': 'EST'})
    datetime.datetime(2015, 2, 12, 22, 56, tzinfo=<StaticTzInfo 'EST'>)

If ``RETURN_AS_TIMEZONE_AWARE`` is set to ``True``, and ``TIMEZONE`` is ``None``, a timezone aware date is only returned if the input string explicitly specifies the time zone, otherwise an unaware date is returned:

    >>> parse('12 Feb 2015 10:56 PM', settings={'RETURN_AS_TIMEZONE_AWARE': True, 'TIMEZONE': None})
    datetime.datetime(2015, 2, 12, 22, 56)

    >>> parse('12 Feb 2015 10:56 PM EST', settings={'RETURN_AS_TIMEZONE_AWARE': True, 'TIMEZONE': None})
    datetime.datetime(2015, 2, 12, 22, 56, tzinfo=<StaticTzInfo 'EST'>)
