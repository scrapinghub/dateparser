.. Note that we use raw HTML in the header section because centering images and paragraphs is not supported in Github (https://github.com/github/markup/issues/163)

.. raw:: html

    <h1 align="center">
        <br/>
        <a href="https://github.com/scrapinghub/dateparser">
            <img src="artwork/dateparser-logo.png" alt="Dateparser" width="500">
        </a>
        <br/>
    </h1>

    <h3 align="center">Python parser for human readable dates</h4>

    <p align="center">
        <a href="https://pypi.python.org/pypi/dateparser">
            <img src="https://img.shields.io/pypi/dm/dateparser.svg" alt="PyPI - Downloads">
        </a>
        <a href="https://pypi.python.org/pypi/dateparser">
            <img src="https://img.shields.io/pypi/v/dateparser.svg" alt="PypI - Version">
        </a>
        <a href="https://codecov.io/gh/scrapinghub/dateparser">
            <img src="https://codecov.io/gh/scrapinghub/dateparser/branch/master/graph/badge.svg" alt="Code Coverage">
        </a>
        <a href="https://github.com/scrapinghub/dateparser/actions">
            <img src="https://github.com/scrapinghub/dateparser/workflows/Build/badge.svg" alt="Github - Build">
        </a>
        <a href="https://dateparser.readthedocs.org/en/latest/?badge=latest">
            <img src="https://readthedocs.org/projects/dateparser/badge/?version=latest" alt="Readthedocs - Docs">
        </a>
    </p>

    <p align="center">
        <a href="#key-features">Key Features</a> •
        <a href="#how-to-use">How To Use</a> •
        <a href="#installation">Installation</a> •
        <a href="#common-use-cases">Common use cases</a> •
        <a href="#you-may-also-like">You may also like...</a> •
        <a href="#license">License</a>
    </p>


Key Features
------------

-  Support for almost every existing date format: absolute dates,
   relative dates (``"two weeks ago"`` or ``"tomorrow"``), timestamps,
   etc.
-  Support for more than `200 language
   locales <https://dateparser.readthedocs.io/en/latest/supported_locales.html>`__.
-  Language autodetection
-  Customizable behavior through
   `settings <https://dateparser.readthedocs.io/en/latest/settings.html>`__.
-  Support for `non-Gregorian calendar
   systems <#supported-calendars>`__.
-  Support for dates with timezones abbreviations or UTC offsets
   (``"August 14, 2015 EST"``, ``"21 July 2013 10:15 pm +0500"``...)
-  `Search dates <#search-for-dates-in-longer-chunks-of-text>`__
   in longer texts.
-  Time span detection for expressions like "past month", "last week".

Online demo
-----------

Do you want to try it out without installing any dependency? Now you can test
it quickly by visiting `this online demo <https://gnyman.github.io/dateparser-demo-app/>`__!



How To Use
----------

The most straightforward way to parse dates with **dateparser** is to
use the ``dateparser.parse()`` function, that wraps around most of the
functionality of the module.

.. code:: python

    >>> import dateparser

    >>> dateparser.parse('Fri, 12 Dec 2014 10:55:50')
    datetime.datetime(2014, 12, 12, 10, 55, 50)

    >>> dateparser.parse('1991-05-17')
    datetime.datetime(1991, 5, 17, 0, 0)

    >>> dateparser.parse('In two months')  # today is 1st Aug 2020
    datetime.datetime(2020, 10, 1, 11, 12, 27, 764201)

    >>> dateparser.parse('1484823450')  # timestamp
    datetime.datetime(2017, 1, 19, 10, 57, 30)

    >>> dateparser.parse('January 12, 2012 10:00 PM EST')
    datetime.datetime(2012, 1, 12, 22, 0, tzinfo=<StaticTzInfo 'EST'>)

**dateparser** also works with strings in different languages:

.. code:: python

    >>> dateparser.parse('Martes 21 de Octubre de 2014')  # Spanish (Tuesday 21 October 2014)
    datetime.datetime(2014, 10, 21, 0, 0)

    >>> dateparser.parse('Le 11 Décembre 2014 à 09:00')  # French (11 December 2014 at 09:00)
    datetime.datetime(2014, 12, 11, 9, 0)

    >>> dateparser.parse('13 января 2015 г. в 13:34')  # Russian (13 January 2015 at 13:34)
    datetime.datetime(2015, 1, 13, 13, 34)

    >>> dateparser.parse('1 เดือนตุลาคม 2005, 1:00 AM')  # Thai (1 October 2005, 1:00 AM)
    datetime.datetime(2005, 10, 1, 1, 0)

    >>> dateparser.parse('yaklaşık 23 saat önce')  # Turkish (23 hours ago), current time: 12:46
    datetime.datetime(2019, 9, 7, 13, 46)

    >>> dateparser.parse('2小时前')  # Chinese (2 hours ago), current time: 22:30
    datetime.datetime(2018, 5, 31, 20, 30)

You can specify the language(s), if known, using the ``languages`` argument.
In this case, given languages are used and language detection is skipped:

.. code:: python

    >>> dateparser.parse('2015, Ago 15, 1:08 pm', languages=['pt', 'es'])
    datetime.datetime(2015, 8, 15, 13, 8)

If you know the possible formats of the dates, you can use the
``date_formats`` argument:

.. code:: python

    >>> dateparser.parse('22 Décembre 2010', date_formats=['%d %B %Y'])
    datetime.datetime(2010, 12, 22, 0, 0)

Relative Dates
^^^^^^^^^^^^^^

.. code:: python

    >>> from dateparser import parse
    >>> parse('1 hour ago')
    datetime.datetime(2015, 5, 31, 23, 0)
    >>> parse('Il ya 2 heures')  # French (2 hours ago)
    datetime.datetime(2015, 5, 31, 22, 0)
    >>> parse('1 anno 2 mesi')  # Italian (1 year 2 months)
    datetime.datetime(2014, 4, 1, 0, 0)
    >>> parse('yaklaşık 23 saat önce')  # Turkish (23 hours ago)
    datetime.datetime(2015, 5, 31, 1, 0)
    >>> parse('Hace una semana')  # Spanish (a week ago)
    datetime.datetime(2015, 5, 25, 0, 0)
    >>> parse('2小时前')  # Chinese (2 hours ago)
    datetime.datetime(2015, 5, 31, 22, 0)

.. note:: Testing above code might return different values depending on your environment's current date and time.

.. note:: For the ``Finnish`` language, please specify ``settings={'SKIP_TOKENS': []}`` to correctly parse relative dates.

Date Order
^^^^^^^^^^

.. code:: python

    >>> # parsing ambiguous date
    >>> parse('02-03-2016')  # assumes english language, uses MDY date order
    datetime.datetime(2016, 2, 3, 0, 0)
    >>> parse('le 02-03-2016')  # detects french, uses DMY date order
    datetime.datetime(2016, 3, 2, 0, 0)

.. note:: Ordering is not locale-based — do not expect ``DMY`` order for UK/Australia English.
   You can specify date order explicitly:

   .. code:: python

       >>> parse('18-12-15 06:00', settings={'DATE_ORDER': 'DMY'})
       datetime.datetime(2015, 12, 18, 6, 0)

For more on date order, see the `settings documentation <https://dateparser.readthedocs.io/en/latest/settings.html>`__.

Timezone and UTC Offset
^^^^^^^^^^^^^^^^^^^^^^^

By default, `dateparser` returns a timezone-aware ``datetime`` if a timezone is
present in the date string. Otherwise it returns a naive ``datetime`` object.

.. code:: python

    >>> parse('January 12, 2012 10:00 PM EST')
    datetime.datetime(2012, 1, 12, 22, 0, tzinfo=<StaticTzInfo 'EST'>)

    >>> parse('January 12, 2012 10:00 PM -0500')
    datetime.datetime(2012, 1, 12, 22, 0, tzinfo=<StaticTzInfo 'UTC\-05:00'>)

    >>> parse('2 hours ago EST')
    datetime.datetime(2017, 3, 10, 15, 55, 39, 579667, tzinfo=<StaticTzInfo 'EST'>)

If the date has no timezone name/abbreviation or offset, you can specify it
using the ``TIMEZONE`` setting:

.. code:: python

    >>> parse('January 12, 2012 10:00 PM', settings={'TIMEZONE': 'US/Eastern'})
    datetime.datetime(2012, 1, 12, 22, 0)

    >>> parse('January 12, 2012 10:00 PM', settings={'TIMEZONE': 'US/Eastern', 'RETURN_AS_TIMEZONE_AWARE': True})
    datetime.datetime(2012, 1, 12, 22, 0, tzinfo=<DstTzInfo 'US/Eastern' EST-1 day, 19:00:00 STD>)

    >>> parse('10:00 am', settings={'TIMEZONE': 'EST', 'TO_TIMEZONE': 'EDT'})
    datetime.datetime(2016, 9, 25, 11, 0)

    >>> parse('10:00 am EST', settings={'TO_TIMEZONE': 'EDT'})
    datetime.datetime(2017, 3, 12, 11, 0, tzinfo=<StaticTzInfo 'EDT'>)

For more on timezones, see the `settings documentation <https://dateparser.readthedocs.io/en/latest/settings.html>`__.

Incomplete Dates
^^^^^^^^^^^^^^^^

.. code:: python

    >>> from dateparser import parse
    >>> parse('December 2015')  # default behavior
    datetime.datetime(2015, 12, 16, 0, 0)
    >>> parse('December 2015', settings={'PREFER_DAY_OF_MONTH': 'last'})
    datetime.datetime(2015, 12, 31, 0, 0)
    >>> parse('December 2015', settings={'PREFER_DAY_OF_MONTH': 'first'})
    datetime.datetime(2015, 12, 1, 0, 0)

    >>> parse('March')
    datetime.datetime(2015, 3, 16, 0, 0)
    >>> parse('March', settings={'PREFER_DATES_FROM': 'future'})
    datetime.datetime(2016, 3, 16, 0, 0)

    >>> import dateparser
    >>> dateparser.parse("2015")  # default behavior
    datetime.datetime(2015, 3, 27, 0, 0)
    >>> dateparser.parse("2015", settings={"PREFER_MONTH_OF_YEAR": "last"})
    datetime.datetime(2015, 12, 27, 0, 0)
    >>> dateparser.parse("2015", settings={"PREFER_MONTH_OF_YEAR": "current"})
    datetime.datetime(2015, 3, 27, 0, 0)

You can also ignore incomplete dates by setting the ``STRICT_PARSING`` flag:

.. code:: python

    >>> parse('December 2015', settings={'STRICT_PARSING': True})
    None

For more on handling incomplete dates, see the `settings documentation <https://dateparser.readthedocs.io/en/latest/settings.html>`__.

Search for Dates in Longer Chunks of Text
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. warning:: Support for date searching is limited and needs improvement.
   Contributions are welcome — see `contributing <https://dateparser.readthedocs.io/en/latest/contributing.html>`__.

You can extract dates from longer strings of text. Results are returned as a
list of ``(substring, datetime)`` tuples:

.. code:: python

    >>> from dateparser.search import search_dates
    >>> search_dates('Today is 25 of October 2017, so the 27th is in 2 days.')
    [('25 of October 2017', datetime.datetime(2017, 10, 25, 0, 0)), ('the 27th is in 2 days', datetime.datetime(2017, 10, 27, 0, 0))]

Time Span Detection
^^^^^^^^^^^^^^^^^^^

The ``search_dates`` function can also detect time spans such as
"past month" or "last week". When ``RETURN_TIME_SPAN`` is enabled it
returns start and end dates for the detected period:

.. code:: python

    >>> search_dates("Messages from the past month", settings={'RETURN_TIME_SPAN': True})
    [('past month (start)', datetime.datetime(2024, 11, 7, 0, 0)),
     ('past month (end)', datetime.datetime(2024, 12, 7, 23, 59, 59, 999999))]

Settings
^^^^^^^^

You can control multiple behaviors by using the ``settings`` parameter:

.. code:: python

    >>> dateparser.parse('2014-10-12', settings={'DATE_ORDER': 'YMD'})
    datetime.datetime(2014, 10, 12, 0, 0)

    >>> dateparser.parse('2014-10-12', settings={'DATE_ORDER': 'YDM'})
    datetime.datetime(2014, 12, 10, 0, 0)

    >>> dateparser.parse('1 year', settings={'PREFER_DATES_FROM': 'future'})  # Today is 2020-09-23
    datetime.datetime(2021, 9, 23, 0, 0)

    >>> dateparser.parse('tomorrow', settings={'RELATIVE_BASE': datetime.datetime(1992, 1, 1)})
    datetime.datetime(1992, 1, 2, 0, 0)

To see all available settings, check the `settings
documentation <https://dateparser.readthedocs.io/en/latest/settings.html>`__.

False positives
^^^^^^^^^^^^^^^

**dateparser** will do its best to return a date, dealing with multiple formats and different locales.
For that reason it is important that the input is a valid date, otherwise it could return false positives.

To reduce the possibility of receiving false positives, make sure that:

- The input string is a valid date and doesn't contain any other words or numbers.
- If you know the language or languages beforehand, you add them through the ``languages`` or ``locales`` properties.


On the other hand, if you want to exclude any of the default parsers
(``timestamp``, ``relative-time``...) or change the order in which they
are executed, you can do so through the
`settings PARSERS <https://dateparser.readthedocs.io/en/latest/usage.html#handling-incomplete-dates>`_.

Installation
------------

Dateparser supports Python 3.10+. You can install it by doing:

::

    $ pip install dateparser

If you want to use the jalali or hijri calendar, you need to install the
``calendars`` extra:

::

    $ pip install dateparser[calendars]

Supported Calendars
-------------------

Apart from the Gregorian calendar, `dateparser` supports the
`Persian Jalali calendar` and the `Hijri/Islamic calendar`.
To use them, install the ``calendars`` extra (see `Installation`_).

Example using the `Persian Jalali calendar
<https://en.wikipedia.org/wiki/Iranian_calendars#Zoroastrian_calendar>`_:

.. code:: python

    >>> from dateparser.calendars.jalali import JalaliCalendar
    >>> JalaliCalendar('جمعه سی ام اسفند ۱۳۸۷').get_date()
    DateData(date_obj=datetime.datetime(2009, 3, 20, 0, 0), period='day', locale=None)

Example using the `Hijri/Islamic calendar
<https://en.wikipedia.org/wiki/Islamic_calendar>`_:

.. code:: python

    >>> from dateparser.calendars.hijri import HijriCalendar
    >>> HijriCalendar('17-01-1437 هـ 08:30 مساءً').get_date()
    DateData(date_obj=datetime.datetime(2015, 10, 30, 20, 30), period='day', locale=None)

Dependencies
------------

`dateparser` relies on the following libraries:

* dateutil_'s module ``relativedelta`` for its freshness parser.
* convertdate_ to convert *Jalali* dates to *Gregorian*.
* hijridate_ to convert *Hijri* dates to *Gregorian*.
* tzlocal_ to reliably get local timezone.
* ruamel.yaml_ (optional) for operations on language files.

.. _dateutil: https://pypi.python.org/pypi/python-dateutil
.. _convertdate: https://pypi.python.org/pypi/convertdate
.. _hijridate: https://pypi.python.org/pypi/hijridate
.. _tzlocal: https://pypi.python.org/pypi/tzlocal
.. _ruamel.yaml: https://pypi.python.org/pypi/ruamel.yaml

Common use cases
----------------

**dateparser** can be used for a wide variety of purposes,
but it stands out when it comes to:

Consuming data from different sources:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

-  **Scraping**: extract dates from different places with several
   different formats and languages
-  **IoT**: consuming data coming from different sources with different
   date formats
-  **Tooling**: consuming dates from different logs / sources
-  **Format transformations**: when transforming dates coming from
   different files (PDF, CSV, etc.) to other formats (database, etc).

Offering natural interaction with users:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

-  **Tooling and CLI**: allow users to write “3 days ago” to retrieve
   information.
-  **Search engine**: allow people to search by date in an easy /
   natural format.
-  **Bots**: allow users to interact with a bot easily

You may also like...
--------------------

-  `price-parser <https://github.com/scrapinghub/price-parser/>`__ - A
   small library for extracting price and currency from raw text
   strings.
-  `number-parser <https://github.com/scrapinghub/number-parser/>`__ -
   Library to convert numbers written in the natural language to it's
   equivalent numeric forms.
-  `Scrapy <https://github.com/scrapy/scrapy/>`__ - Web crawling and web
   scraping framework

License
-------

`BSD3-Clause <https://github.com/scrapinghub/dateparser/blob/master/LICENSE>`__
