====================================================
dateparser -- python parser for human readable dates
====================================================

.. image:: https://img.shields.io/travis/scrapinghub/dateparser/master.svg?style=flat-square
    :target: https://travis-ci.org/scrapinghub/dateparser
    :alt: travis build status

.. image:: https://img.shields.io/pypi/v/dateparser.svg?style=flat-square
    :target: https://pypi.python.org/pypi/dateparser
    :alt: pypi version

.. image:: https://readthedocs.org/projects/dateparser/badge/?version=latest
    :target: http://dateparser.readthedocs.org/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://codecov.io/gh/scrapinghub/dateparser/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/scrapinghub/dateparser
   :alt: Code Coverage

.. image:: https://badges.gitter.im/scrapinghub/dateparser.svg
   :alt: Join the chat at https://gitter.im/scrapinghub/dateparser
   :target: https://gitter.im/scrapinghub/dateparser?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge


`dateparser` provides modules to easily parse localized dates in almost
any string formats commonly found on web pages.


Documentation
=============

Documentation is built automatically and can be found on
`Read the Docs <https://dateparser.readthedocs.org/en/latest/>`_.


Features
========

* Generic parsing of dates in English, Spanish, Dutch, Russian and over 20 other languages plus numerous formats in a language agnostic fashion.
* Generic parsing of relative dates like: ``'1 min ago'``, ``'2 weeks ago'``, ``'3 months, 1 week and 1 day ago'``, ``'in 2 days'``, ``'tomorrow'``.
* Generic parsing of dates with time zones abbreviations or UTC offsets like: ``'August 14, 2015 EST'``, ``'July 4, 2013 PST'``, ``'21 July 2013 10:15 pm +0500'``.
* Support for non-Gregorian calendar systems. See `Supported Calendars`_.
* Extensive test coverage.


Usage
=====

The most straightforward way is to use the `dateparser.parse <#dateparser.parse>`_ function,
that wraps around most of the functionality in the module.

.. automodule:: dateparser
   :members: parse


Popular Formats
---------------

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

You can specify the language(s), if known, using ``languages`` argument. In this case, given languages are used and language detection is skipped:

    >>> dateparser.parse('2015, Ago 15, 1:08 pm', languages=['pt', 'es'])
    datetime.datetime(2015, 8, 15, 13, 8)

If you know the possible formats of the dates, you can
use the ``date_formats`` argument:

    >>> dateparser.parse(u'22 Décembre 2010', date_formats=['%d %B %Y'])
    datetime.datetime(2010, 12, 22, 0, 0)


Relative Dates
--------------

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

.. note:: Support for relative dates in future needs a lot of improvement, we look forward to community's contribution to get better on that part. See `Contributing`_.


OOTB Language Based Date Order Preference
-----------------------------------------

   >>> # parsing ambiguous date
   >>> parse('02-03-2016')  # assumes english language, uses MDY date order 
   datetime.datetime(2016, 3, 2, 0, 0)
   >>> parse('le 02-03-2016')  # detects french, uses DMY date order
   datetime.datetime(2016, 3, 2, 0, 0)

.. note:: Ordering is not locale based, that's why do not expect `DMY` order for UK/Australia English. You can specify date order in that case as follows usings `Settings`_:

    >>> parse('18-12-15 06:00', settings={'DATE_ORDER': 'DMY'})
    datetime.datetime(2015, 12, 18, 6, 0)

For more on date order, please look at `Settings`_.


Timezone and UTC Offset 
-----------------------

Dateparser assumes all dates to be in UTC if no timezone is specified in the string. To convert the resultant `datetime` object to required timezone. You can do the following:

    >>> parse('January 12, 2012 10:00 PM', settings={'TIMEZONE': 'US/Eastern'})
    datetime.datetime(2012, 1, 12, 17, 0)

Support for tzaware objects:

    >>> parse('12 Feb 2015 10:56 PM EST', settings={'RETURN_AS_TIMEZONE_AWARE': True})
    datetime.datetime(2015, 2, 13, 3, 56, tzinfo=<StaticTzInfo 'UTC'>)

    >>> parse('12 Feb 2015 10:56 PM EST', settings={'RETURN_AS_TIMEZONE_AWARE': True, 'TIMEZONE': None}) 
    datetime.datetime(2015, 2, 12, 22, 56, tzinfo=<StaticTzInfo 'EST'>)

For more on timezones, please look at `Settings`_.


Incomplete Dates
----------------

    >>> from dateparser import parse
    >>> parse(u'December 2015')  # default behavior
    datetime.datetime(2015, 12, 16, 0, 0)
    >>> parse(u'December 2015', settings={'PREFER_DAY_OF_MONTH': 'last'})
    datetime.datetime(2015, 12, 31, 0, 0)
    >>> parse(u'December 2015', settings={'PREFER_DAY_OF_MONTH': 'first'})
    datetime.datetime(2015, 12, 1, 0, 0)

    >>> parse(u'March')
    datetime.datetime(2015, 3, 16, 0, 0)
    >>> parse(u'March', settings={'PREFER_DATES_FROM': 'future'})
    datetime.datetime(2016, 3, 16, 0, 0)
    >>> # parsing with preference set for 'past'
    >>> parse('August', settings={'PREFER_DATES_FROM': 'past'})
    datetime.datetime(2015, 8, 15, 0, 0)

You can also ignore parsing incomplete dates altogether by setting `STRICT_PARSING` flag as follows:

    >>> parse(u'December 2015', settings={'STRICT_PARSING': True})
    None

For more on handling incomplete dates, please look at `Settings`_.


Dependencies
============

`dateparser` relies on following libraries in some ways:

  * dateutil_'s module ``relativedelta`` for its freshness parser.
  * ruamel.yaml_ for reading language and configuration files.
  * jdatetime_ to convert *Jalali* dates to *Gregorian*.
  * umalqurra_ to convert *Hijri* dates to *Gregorian*.

.. _dateutil: https://pypi.python.org/pypi/python-dateutil
.. _ruamel.yaml: https://pypi.python.org/pypi/ruamel.yaml
.. _jdatetime: https://pypi.python.org/pypi/jdatetime
.. _umalqurra: https://pypi.python.org/pypi/umalqurra/


Supported languages
===================

* Arabic
* Belarusian
* Chinese
* Czech
* Danish
* Dutch
* English
* Tagalog/Filipino
* Finnish
* French
* German
* Indonesian
* Italian
* Japanese
* Persian
* Polish
* Portuguese
* Romanian
* Russian
* Spanish
* Thai
* Turkish
* Ukrainian
* Vietnamese


Supported Calendars
===================
* Gregorian calendar.

* Persian Jalali calendar. For more information, refer to `Persian Jalali Calendar <https://en.wikipedia.org/wiki/Iranian_calendars#Zoroastrian_calendar>`_.

* Hijri/Islamic Calendar. For more information, refer to `Hijri Calendar <https://en.wikipedia.org/wiki/Islamic_calendar>`_.

	>>> from dateparser.calendars.jalali import JalaliParser
	>>> JalaliParser(u'جمعه سی ام اسفند ۱۳۸۷').get_date()
	datetime.datetime(2009, 3, 20, 0, 0)

        >>> from dateparser.calendars.hijri import HijriCalendar
        >>> HijriCalendar(u'17-01-1437 هـ 08:30 مساءً').get_date()
        {'date_obj': datetime.datetime(2015, 10, 30, 20, 30), 'period': 'day'}

.. note:: `HijriCalendar` has some limitations with Python 3.
.. note:: For `Finnish` language, please specify `settings={'SKIP_TOKENS': []}` to correctly parse freshness dates.

