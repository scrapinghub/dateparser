Using DateDataParser
--------------------

:func:`dateparser.parse` uses a default parser which tries to detect language
every time it is called and is not the most efficient way while parsing dates
from the same source.

:class:`DateDataParser <dateparser.date.DateDataParser>` provides an alternate and efficient way
to control language detection behavior.

The instance of :class:`DateDataParser <dateparser.date.DateDataParser>` reduces the number
of applicable languages, until only one or no language is left. It
assumes the previously detected language for all the subsequent dates supplied.

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

:mod:`dateparser`'s parsing behavior can be configured by supplying settings as a dictionary to `settings` argument in `dateparser.parse` or :class:`DateDataParser <dateparser.date.DateDataParser>` constructor.

All supported `settings` with their usage examples are given below:


Date Order
++++++++++

``DATE_ORDER`` specifies the order in which date components `year`, `month` and `day` are expected while parsing ambiguous dates. It defaults to `MDY` which translates to `month` first, `day` second and `year` last order. Characters `M`, `D` or `Y` can be shuffled to meet required order. For example, `DMY` specifies `day` first, `month` second and `year` last order:

    >>> parse('15-12-18 06:00')  # assumes default order: MDY
    datetime.datetime(2018, 12, 15, 6, 0)  # since 15 is not a valid value for Month, it is swapped with Day's
    >>> parse('15-12-18 06:00', settings={'DATE_ORDER': 'YMD'})
    datetime.datetime(2015, 12, 18, 6, 0)

``PREFER_LANGUAGE_DATE_ORDER`` defaults to `True`. Most languages have a default `DATE_ORDER` specified for them. For example, for French it is `DMY`:

   >>> # parsing ambiguous date
   >>> parse('02-03-2016')  # assumes english language, uses MDY date order
   datetime.datetime(2016, 3, 2, 0, 0)
   >>> parse('le 02-03-2016')  # detects french, hence, uses DMY date order
   datetime.datetime(2016, 3, 2, 0, 0)

.. note:: There's no language level default `DATE_ORDER` associated with `en` language. That's why it assumes `MDY` which is :obj:``settings <dateparser.conf.settings>`` default. If the language has a default `DATE_ORDER` associated, supplying custom date order will not be applied unless we set `PREFER_LANGUAGE_DATE_ORDER` to `False`:

    >>> parse('le 02-03-2016', settings={'DATE_ORDER': 'MDY'})
    datetime.datetime(2016, 3, 2, 0, 0)  # MDY didn't apply

    >>> parse('le 02-03-2016', settings={'DATE_ORDER': 'MDY', 'PREFER_LANGUAGE_DATE_ORDER': False})
    datetime.datetime(2016, 2, 3, 0, 0)  # MDY worked!


Timezone Related Configurations
+++++++++++++++++++++++++++++++


``TIMEZONE`` defaults to local timezone. When specified, resultant :class:`datetime <datetime.datetime>` is localized with the given timezone.

    >>> parse('January 12, 2012 10:00 PM', settings={'TIMEZONE': 'US/Eastern'})
    datetime.datetime(2012, 1, 12, 22, 0)

``TO_TIMEZONE`` defaults to None. When specified, resultant :class:`datetime <datetime.datetime>` converts according to the supplied timezone:

    >>> settings = {'TIMEZONE': 'UTC', 'TO_TIMEZONE': 'US/Eastern'}
    >>> parse('January 12, 2012 10:00 PM', settings=settings)
    datetime.datetime(2012, 1, 12, 17, 0)

``RETURN_AS_TIMEZONE_AWARE`` is a flag to toggle between timezone aware/naive dates:

    >>> parse('30 mins ago', settings={'RETURN_AS_TIMEZONE_AWARE': True})
    datetime.datetime(2017, 3, 13, 1, 43, 10, 243565, tzinfo=<DstTzInfo 'Asia/Karachi' PKT+5:00:00 STD>)

    >>> parse('12 Feb 2015 10:56 PM EST', settings={'RETURN_AS_TIMEZONE_AWARE': False})
    datetime.datetime(2015, 2, 12, 22, 56)



Handling Incomplete Dates
+++++++++++++++++++++++++

``PREFER_DAY_OF_MONTH`` This option comes handy when the date string is missing the day part. It defaults to ``current`` and can have ``first`` and ``last`` denoting first and last day of months respectively as values:

    >>> from dateparser import parse
    >>> parse(u'December 2015')  # default behavior
    datetime.datetime(2015, 12, 16, 0, 0)
    >>> parse(u'December 2015', settings={'PREFER_DAY_OF_MONTH': 'last'})
    datetime.datetime(2015, 12, 31, 0, 0)
    >>> parse(u'December 2015', settings={'PREFER_DAY_OF_MONTH': 'first'})
    datetime.datetime(2015, 12, 1, 0, 0)

``PREFER_DATES_FROM`` defaults to `current_period` and can have `past` and `future` as values.

If date string is missing some part, this option ensures consistent results depending on the `past` or `future` preference, for example, assuming current date is `June 16, 2015`:

    >>> from dateparser import parse
    >>> parse(u'March')
    datetime.datetime(2015, 3, 16, 0, 0)
    >>> parse(u'March', settings={'PREFER_DATES_FROM': 'future'})
    datetime.datetime(2016, 3, 16, 0, 0)
    >>> # parsing with preference set for 'past'
    >>> parse('August', settings={'PREFER_DATES_FROM': 'past'})
    datetime.datetime(2015, 8, 15, 0, 0)

``RELATIVE_BASE`` allows setting the base datetime to use for interpreting partial or relative date strings.
Defaults to the current date and time.

For example, assuming current date is `June 16, 2015`:

    >>> from dateparser import parse
    >>> parse(u'14:30')
    datetime.datetime(2015, 3, 16, 14, 30)
    >>> parse(u'14:30', settings={'RELATIVE_BASE': datetime.datetime(2020, 1, 1)})
    datetime.datetime(2020, 1, 1, 14, 30)
    >>> parse(u'tomorrow', settings={'RELATIVE_BASE': datetime.datetime(2020, 1, 1)})
    datetime.datetime(2020, 1, 2, 0, 0)

``STRICT_PARSING`` defaults to `False`.

When set to `True` if missing any of `day`, `month` or `year` parts, it does not return any result altogether.:

    >>> parse(u'March', settings={'STRICT_PARSING': True})
    None


Language Detection
++++++++++++++++++

``SKIP_TOKENS`` is a ``list`` of tokens to discard while detecting language. Defaults to ``['t']`` which skips T in iso format datetime string .e.g. ``2015-05-02T10:20:19+0000``.:

    >>> from dateparser.date import DateDataParser
    >>> DateDataParser(settings={'SKIP_TOKENS': ['de']}).get_date_data(u'27 Haziran 1981 de')  # Turkish (at 27 June 1981)
    {'date_obj': datetime.datetime(1981, 6, 27, 0, 0), 'period': 'day'}
