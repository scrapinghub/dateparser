Using DateDataParser
--------------------

:func:`dateparser.parse` uses a default parser which tries to detect language
every time it is called and is not the most efficient way while parsing dates
from the same source.

:class:`dateparser.date.DateDataParser` provides an alternate and efficient way
to control language detection behavior.

The instance of :class:`dateparser.date.DateDataParser` reduces the number
of applicable languages, until only one or no language is left. It 
assumes the previously detected language for all the next dates and does not try
to execute the language detection again after a language is discarded.

This class wraps around the core :mod:`dateparser` functionality, and by default
assumes that all of the dates fed to it are in the same language.

.. autoclass:: dateparser.date.DateDataParser
   :members: get_date_data

Once initialized, :func:`dateparser.date.DateDataParser.get_date_data` parses date strings::

    >>> from dateparser.date import DateDataParser
    >>> ddp = DateDataParser()
    >>> ddp.get_date_data(u'Martes 21 de Octubre de 2014')  # Spanish
    {'date_obj': datetime.datetime(2014, 10, 21, 0, 0), 'period': u'day'}
    >>> ddp.get_date_data(u'13 Septiembre, 2014')  # Spanish
    {'date_obj': datetime.datetime(2014, 9, 13, 0, 0), 'period': u'day'}

.. warning:: It fails to parse *English* dates in the example below, because *Spanish* was detected and stored with the ``ddp`` instance:

    >>> ddp.get_date_data('11 August 2012')
    {'date_obj': None, 'period': 'day'}


:class:`dateparser.date.DateDataParser` can also be initialized with known languages::

    >>> ddp = DateDataParser(languages=['de', 'nl'])
    >>> ddp.get_date_data(u'vr jan 24, 2014 12:49')
    {'date_obj': datetime.datetime(2014, 1, 24, 12, 49), 'period': u'day'}
    >>> ddp.get_date_data(u'18.10.14 um 22:56 Uhr')
    {'date_obj': datetime.datetime(2014, 10, 18, 22, 56), 'period': u'day'}

