====================================================
dateparser -- python parser for human readable dates
====================================================

.. image:: https://img.shields.io/travis/scrapinghub/dateparser/master.svg?style=flat-square
    :target: https://travis-ci.org/scrapinghub/dateparser
    :alt: travis build status

.. image:: https://img.shields.io/pypi/dd/dateparser.svg?style=flat-square
    :target: https://pypi.python.org/pypi/dateparser/
    :alt: pypi downloads per day

.. image:: https://img.shields.io/pypi/v/dateparser.svg?style=flat-square
    :target: https://pypi.python.org/pypi/dateparser
    :alt: pypi version


`dateparser` provides modules to easily parse localized dates in almost
any string formats commonly found on web pages.


Features
--------
* Generic parsing of dates in English, Spanish, Dutch, Russian and several other langauges and formats.
* Generic parsing of relative dates like: ``'1 min ago'``, ``'2 weeks ago'``, ``'3 months, 1 week and 1 day ago'``.
* Generic parsing of dates with time zones abbreviations like: ``'August 14, 2015 EST'``, ``'July 4, 2013 PST'``.
* Extensive test coverage.


Usage
-----
The most straightforward way is to use the :func:`dateparser.parse` function,
that wraps around most of the functionality in the module.

.. automodule:: dateparser
   :members: parse


Popular Formats
+++++++++++++++

    >>> import dateparser
    >>> dateparser.parse('12/12/12')
    datetime.datetime(2012, 12, 12, 0, 0)
    >>> dateparser.parse(u'Fri, 12 Dec 2014 10:55:50')
    datetime.datetime(2014, 12, 12, 10, 55, 50)
    >>> dateparser.parse(u'Martes 21 de Octubre de 2014')  # Spanish (Tuesday 21 October 2014)
    datetime.datetime(2014, 10, 21, 0, 0)
    >>> dateparser.parse(u'Le 11 Décembre 2014 à 09:00')  # French (11 December 2014 at 09:00)
    datetime.datetime(2014, 12, 11, 9, 0)
    >>> dateparser.parse(u'13 января 2015 г. в 13:34')  # Russian (13 January 2015 at 13:34)
    datetime.datetime(2015, 1, 13, 13, 34)
    >>> dateparser.parse(u'1 เดือนตุลาคม 2005, 1:00 AM')  # Thai (1 October 2005, 1:00 AM)
    datetime.datetime(2005, 10, 1, 1, 0)

This will try to parse a date from the given string, attempting to
detect the language each time.

You can specify the language(s), if known, using ``languages`` argument. In this case, given languages are used and language detection is skipped::

    >>> dateparser.parse('2015, Ago 15, 1:08 pm', languages=['pt', 'es'])
    datetime.datetime(2015, 8, 15, 13, 8)

If you know the possible formats that the date will be, you can
use the ``date_formats`` argument::

    >>> dateparser.parse(u'22 Décembre 2010', date_formats=['%d %B %Y'])
    datetime.datetime(2010, 12, 22, 0, 0)


Relative Dates
++++++++++++++

    >>> parse('1 hour ago')
    datetime.datetime(2015, 5, 31, 23, 0)
    >>> parse(u'Il ya 2 heures')  # French (2 hours ago)
    datetime.datetime(2015, 5, 31, 22, 0)
    >>> parse(u'1 anno 2 mesi')  # Italian (1 year 2 months)
    datetime.datetime(2014, 4, 1, 0, 0)
    >>> parse(u'yaklaşık 23 saat önce')  # Turkish (23 hours ago)
    datetime.datetime(2015, 5, 31, 1, 0)
    >>> parse(u'Hace una semana')  # Spanish (a week ago)
    datetime.datetime(2015, 5, 25, 0, 0)
    >>> parse(u'2小时前')  # Chinese (2 hours ago)
    datetime.datetime(2015, 5, 31, 22, 0)

.. note:: Testing above code might return different values for you depending on your environment's current date and time.


Dependencies
------------
`dateparser` translates non-english dates to English and uses dateutil_ module ``'parser'`` to parse the translated date.

Also, it requires PyYAML_ for its language detection module to work.

.. _dateutil: https://pypi.python.org/pypi/python-dateutil
.. _PyYAML: https://pypi.python.org/pypi/PyYAML


Limitations
-----------
`dateparser` at this point does not support generic parsing of dates with fixed UTC offsets. This restricts its ability to reliably parse time zone aware dates since the use of abbreviated time zones as a sole designator of time zones is not recommended.

Read `Wikipedia Time Zone article`_ for more information.

.. _Wikipedia Time Zone Article: https://en.wikipedia.org/wiki/Time_zone#Abbreviations

