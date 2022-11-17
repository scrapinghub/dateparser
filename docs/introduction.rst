==========================
Introduction to dateparser
==========================


Features
========

* Generic parsing of dates in over 200 language locales plus numerous formats in a language agnostic fashion.
* Generic parsing of relative dates like: ``'1 min ago'``, ``'2 weeks ago'``, ``'3 months, 1 week and 1 day ago'``, ``'in 2 days'``, ``'tomorrow'``.
* Generic parsing of dates with time zones abbreviations or UTC offsets like: ``'August 14, 2015 EST'``, ``'July 4, 2013 PST'``, ``'21 July 2013 10:15 pm +0500'``.
* Date lookup in longer texts.
* Support for non-Gregorian calendar systems. See `Supported Calendars`_.
* Extensive test coverage.


Basic Usage
===========

The most straightforward way is to use the `dateparser.parse <#dateparser.parse>`_ function,
that wraps around most of the functionality in the module.

.. automodule:: dateparser
   :members: parse
   :noindex:


Popular Formats
---------------

    >>> import dateparser
    >>> dateparser.parse('12/12/12')
    datetime.datetime(2012, 12, 12, 0, 0)
    >>> dateparser.parse('Fri, 12 Dec 2014 10:55:50')
    datetime.datetime(2014, 12, 12, 10, 55, 50)
    >>> dateparser.parse('Martes 21 de Octubre de 2014')  # Spanish (Tuesday 21 October 2014)
    datetime.datetime(2014, 10, 21, 0, 0)
    >>> dateparser.parse('Le 11 Décembre 2014 à 09:00')  # French (11 December 2014 at 09:00)
    datetime.datetime(2014, 12, 11, 9, 0)
    >>> dateparser.parse('13 января 2015 г. в 13:34')  # Russian (13 January 2015 at 13:34)
    datetime.datetime(2015, 1, 13, 13, 34)
    >>> dateparser.parse('1 เดือนตุลาคม 2005, 1:00 AM')  # Thai (1 October 2005, 1:00 AM)
    datetime.datetime(2005, 10, 1, 1, 0)

This will try to parse a date from the given string, attempting to
detect the language each time.

You can specify the language(s), if known, using ``languages`` argument. In this case, given languages are used and language detection is skipped:

    >>> dateparser.parse('2015, Ago 15, 1:08 pm', languages=['pt', 'es'])
    datetime.datetime(2015, 8, 15, 13, 8)

If you know the possible formats of the dates, you can
use the ``date_formats`` argument:

    >>> dateparser.parse('22 Décembre 2010', date_formats=['%d %B %Y'])
    datetime.datetime(2010, 12, 22, 0, 0)


Relative Dates
--------------

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

.. note:: Testing above code might return different values for you depending on your environment's current date and time.

.. note:: For `Finnish` language, please specify ``settings={'SKIP_TOKENS': []}`` to correctly parse relative dates.

OOTB Language Based Date Order Preference
-----------------------------------------

   >>> # parsing ambiguous date
   >>> parse('02-03-2016')  # assumes english language, uses MDY date order
   datetime.datetime(2016, 2, 3, 0, 0)
   >>> parse('le 02-03-2016')  # detects french, uses DMY date order
   datetime.datetime(2016, 3, 2, 0, 0)

.. note:: Ordering is not locale based, that's why do not expect `DMY` order for UK/Australia English. You can specify date order in that case as follows using :ref:`settings`:

    >>> parse('18-12-15 06:00', settings={'DATE_ORDER': 'DMY'})
    datetime.datetime(2015, 12, 18, 6, 0)

For more on date order, please look at :ref:`settings`.


Timezone and UTC Offset
-----------------------

By default, `dateparser` returns tzaware `datetime` if timezone is present in date string. Otherwise, it returns a naive `datetime` object.

    >>> parse('January 12, 2012 10:00 PM EST')
    datetime.datetime(2012, 1, 12, 22, 0, tzinfo=<StaticTzInfo 'EST'>)

    >>> parse('January 12, 2012 10:00 PM -0500')
    datetime.datetime(2012, 1, 12, 22, 0, tzinfo=<StaticTzInfo 'UTC\-05:00'>)

    >>> parse('2 hours ago EST')
    datetime.datetime(2017, 3, 10, 15, 55, 39, 579667, tzinfo=<StaticTzInfo 'EST'>)

    >>> parse('2 hours ago -0500')
    datetime.datetime(2017, 3, 10, 15, 59, 30, 193431, tzinfo=<StaticTzInfo 'UTC\-05:00'>)

 If date has no timezone name/abbreviation or offset, you can specify it using `TIMEZONE` setting.

    >>> parse('January 12, 2012 10:00 PM', settings={'TIMEZONE': 'US/Eastern'})
    datetime.datetime(2012, 1, 12, 22, 0)

    >>> parse('January 12, 2012 10:00 PM', settings={'TIMEZONE': '+0500'})
    datetime.datetime(2012, 1, 12, 22, 0)

``TIMEZONE`` option may not be useful alone as it only attaches given timezone to
resultant ``datetime`` object. But can be useful in cases where you want conversions from and to different
timezones or when simply want a tzaware date with given timezone info attached.

    >>> parse('January 12, 2012 10:00 PM', settings={'TIMEZONE': 'US/Eastern', 'RETURN_AS_TIMEZONE_AWARE': True})
    datetime.datetime(2012, 1, 12, 22, 0, tzinfo=<DstTzInfo 'US/Eastern' EST-1 day, 19:00:00 STD>)


    >>> parse('10:00 am', settings={'TIMEZONE': 'EST', 'TO_TIMEZONE': 'EDT'})
    datetime.datetime(2016, 9, 25, 11, 0)

Some more use cases for conversion of timezones.

    >>> parse('10:00 am EST', settings={'TO_TIMEZONE': 'EDT'})  # date string has timezone info
    datetime.datetime(2017, 3, 12, 11, 0, tzinfo=<StaticTzInfo 'EDT'>)

    >>> parse('now EST', settings={'TO_TIMEZONE': 'UTC'})  # relative dates
    datetime.datetime(2017, 3, 10, 23, 24, 47, 371823, tzinfo=<StaticTzInfo 'UTC'>)

In case, no timezone is present in date string or defined in :ref:`settings`. You can still
return tzaware ``datetime``. It is especially useful in case of relative dates when uncertain
what timezone is relative base.

    >>> parse('2 minutes ago', settings={'RETURN_AS_TIMEZONE_AWARE': True})
    datetime.datetime(2017, 3, 11, 4, 25, 24, 152670, tzinfo=<DstTzInfo 'Asia/Karachi' PKT+5:00:00 STD>)

In case, you want to compute relative dates in UTC instead of default system's local timezone, you can use `TIMEZONE` setting.

    >>> parse('4 minutes ago', settings={'TIMEZONE': 'UTC'})
    datetime.datetime(2017, 3, 10, 23, 27, 59, 647248, tzinfo=<StaticTzInfo 'UTC'>)

.. note:: In case, when timezone is present both in string and also specified using :ref:`settings`, string is parsed into tzaware representation and then converted to timezone specified in :ref:`settings`.

   >>> parse('10:40 pm PKT', settings={'TIMEZONE': 'UTC'})
   datetime.datetime(2017, 3, 12, 17, 40, tzinfo=<StaticTzInfo 'UTC'>)

   >>> parse('20 mins ago EST', settings={'TIMEZONE': 'UTC'})
   datetime.datetime(2017, 3, 12, 21, 16, 0, 885091, tzinfo=<StaticTzInfo 'UTC'>)

For more on timezones, please look at :ref:`settings`.


Incomplete Dates
----------------

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
    >>> # parsing with preference set for 'past'
    >>> parse('August', settings={'PREFER_DATES_FROM': 'past'})
    datetime.datetime(2015, 8, 15, 0, 0)

You can also ignore parsing incomplete dates altogether by setting `STRICT_PARSING` flag as follows:

    >>> parse('December 2015', settings={'STRICT_PARSING': True})
    None

For more on handling incomplete dates, please look at :ref:`settings`.


Search for Dates in Longer Chunks of Text
-----------------------------------------

.. warning:: Support for searching dates is really limited and needs a lot of improvement, we look forward to community's contribution to get better on that part. See ":ref:`contributing`".


You can extract dates from longer strings of text. They are returned as list of tuples with text chunk containing the date and parsed datetime object.


.. automodule:: dateparser.search
   :members: search_dates
   :noindex:

Advanced Usage
==============
If you need more control over what is being parser check the :ref:`settings` section as well as the :ref:`using-datedataparser` section.


Dependencies
============

`dateparser` relies on following libraries in some ways:

  * dateutil_'s module ``relativedelta`` for its freshness parser.
  * convertdate_ to convert *Jalali* dates to *Gregorian*.
  * hijri-converter_ to convert *Hijri* dates to *Gregorian*.
  * tzlocal_ to reliably get local timezone.
  * ruamel.yaml_ (optional) for operations on language files.

.. _dateutil: https://pypi.python.org/pypi/python-dateutil
.. _convertdate: https://pypi.python.org/pypi/convertdate
.. _hijri-converter: https://pypi.python.org/pypi/hijri-converter
.. _tzlocal: https://pypi.python.org/pypi/tzlocal
.. _ruamel.yaml: https://pypi.python.org/pypi/ruamel.yaml

Supported languages and locales
===============================
You can check the supported locales by visiting the ":ref:`supported-locales`" section.


Supported Calendars
===================

Apart from the Georgian calendar, `dateparser` supports the `Persian Jalali calendar` and the `Hijri/Islami calendar`

To be able to use them you need to install the `calendar` extra by typing:

    pip install dateparser[calendars]


* Example using the `Persian Jalali calendar`. For more information, refer to `Persian Jalali Calendar <https://en.wikipedia.org/wiki/Iranian_calendars#Zoroastrian_calendar>`_.

    >>> from dateparser.calendars.jalali import JalaliCalendar
    >>> JalaliCalendar('جمعه سی ام اسفند ۱۳۸۷').get_date()
    DateData(date_obj=datetime.datetime(2009, 3, 20, 0, 0), period='day', locale=None)


* Example using the `Hijri/Islamic Calendar`. For more information, refer to `Hijri Calendar <https://en.wikipedia.org/wiki/Islamic_calendar>`_.

    >>> from dateparser.calendars.hijri import HijriCalendar
    >>> HijriCalendar('17-01-1437 هـ 08:30 مساءً').get_date()
    DateData(date_obj=datetime.datetime(2015, 10, 30, 20, 30), period='day', locale=None)

.. note:: `HijriCalendar` only works with Python ≥ 3.6.
