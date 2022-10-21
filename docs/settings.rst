.. _settings:

Settings
========

`dateparser`'s parsing behavior can be configured by supplying settings as a dictionary to `settings` argument in :func:`dateparser.parse` or :class:`DateDataParser <dateparser.date.DateDataParser>` constructor.

.. note:: From `dateparser 1.0.0` when a setting with a wrong value is provided, a ``SettingValidationError`` is raised.


All supported `settings` with their usage examples are given below:


Date Order
++++++++++

``DATE_ORDER``: specifies the order in which date components `year`, `month` and `day` are expected while parsing ambiguous dates. It defaults to ``MDY`` which translates to `month` first, `day` second and `year` last order. Characters `M`, `D` or `Y` can be shuffled to meet required order. For example, ``DMY`` specifies `day` first, `month` second and `year` last order:

    >>> parse('15-12-18 06:00')  # assumes default order: MDY
    datetime.datetime(2018, 12, 15, 6, 0)  # since 15 is not a valid value for Month, it is swapped with Day's
    >>> parse('15-12-18 06:00', settings={'DATE_ORDER': 'YMD'})
    datetime.datetime(2015, 12, 18, 6, 0)

``PREFER_LOCALE_DATE_ORDER``: defaults to ``True``. Most languages have a default ``DATE_ORDER`` specified for them. For example, for French it is ``DMY``:

   >>> # parsing ambiguous date
   >>> parse('02-03-2016')  # assumes english language, uses MDY date order
   datetime.datetime(2016, 2, 3, 0, 0)
   >>> parse('le 02-03-2016')  # detects french, hence, uses DMY date order
   datetime.datetime(2016, 3, 2, 0, 0)

.. note:: There's no language level default ``DATE_ORDER`` associated with `en` language. That's why it assumes ``MDY`` which is :obj:``settings <dateparser.conf.settings>`` default. If the language has a default ``DATE_ORDER`` associated, supplying custom date order will not be applied unless we set ``PREFER_LOCALE_DATE_ORDER`` to ``False``:

    >>> parse('le 02-03-2016', settings={'DATE_ORDER': 'MDY'})
    datetime.datetime(2016, 3, 2, 0, 0)  # MDY didn't apply

    >>> parse('le 02-03-2016', settings={'DATE_ORDER': 'MDY', 'PREFER_LOCALE_DATE_ORDER': False})
    datetime.datetime(2016, 2, 3, 0, 0)  # MDY worked!


Timezone Related Configurations
+++++++++++++++++++++++++++++++

``TIMEZONE``: defaults to local timezone. When specified, resultant :class:`datetime <datetime.datetime>` is localized with the given timezone. Can be timezone abbreviation or any of `tz database name as given here <https://en.wikipedia.org/wiki/List_of_tz_database_time_zones>`_.

    >>> parse('January 12, 2012 10:00 PM', settings={'TIMEZONE': 'US/Eastern'})
    datetime.datetime(2012, 1, 12, 22, 0)

``TO_TIMEZONE``: defaults to None. When specified, resultant :class:`datetime <datetime.datetime>` converts according to the supplied timezone:

    >>> settings = {'TIMEZONE': 'UTC', 'TO_TIMEZONE': 'US/Eastern'}
    >>> parse('January 12, 2012 10:00 PM', settings=settings)
    datetime.datetime(2012, 1, 12, 17, 0)

``RETURN_AS_TIMEZONE_AWARE``: if ``True`` returns tz aware datetime objects in case timezone is detected in the date string.

    >>> parse('30 mins ago', settings={'RETURN_AS_TIMEZONE_AWARE': True})
    datetime.datetime(2017, 3, 13, 1, 43, 10, 243565, tzinfo=<DstTzInfo 'Asia/Karachi' PKT+5:00:00 STD>)

    >>> parse('12 Feb 2015 10:56 PM EST', settings={'RETURN_AS_TIMEZONE_AWARE': False})
    datetime.datetime(2015, 2, 12, 22, 56)


Handling Incomplete Dates
+++++++++++++++++++++++++

``PREFER_DAY_OF_MONTH``: it comes handy when the date string is missing the day part. It defaults to ``current`` and can be ``first`` and ``last`` denoting first and last day of months respectively as values:

    >>> from dateparser import parse
    >>> parse('December 2015')  # default behavior
    datetime.datetime(2015, 12, 16, 0, 0)
    >>> parse('December 2015', settings={'PREFER_DAY_OF_MONTH': 'last'})
    datetime.datetime(2015, 12, 31, 0, 0)
    >>> parse('December 2015', settings={'PREFER_DAY_OF_MONTH': 'first'})
    datetime.datetime(2015, 12, 1, 0, 0)

``PREFER_DATES_FROM``: defaults to ``current_period`` and can have ``past`` and ``future`` as values.

If date string is missing some part, this option ensures consistent results depending on the ``past`` or ``future`` preference, for example, assuming current date is `June 16, 2015`:

    >>> from dateparser import parse
    >>> parse('March')
    datetime.datetime(2015, 3, 16, 0, 0)
    >>> parse('March', settings={'PREFER_DATES_FROM': 'future'})
    datetime.datetime(2016, 3, 16, 0, 0)
    >>> # parsing with preference set for 'past'
    >>> parse('August', settings={'PREFER_DATES_FROM': 'past'})
    datetime.datetime(2015, 8, 15, 0, 0)

``RELATIVE_BASE``: allows setting the base datetime to use for interpreting partial or relative date strings.
Defaults to the current date and time.

For example, assuming current date is `June 16, 2015`:

    >>> from dateparser import parse
    >>> parse('14:30')
    datetime.datetime(2015, 6, 16, 14, 30)
    >>> parse('14:30', settings={'RELATIVE_BASE': datetime.datetime(2020, 1, 1)})
    datetime.datetime(2020, 1, 1, 14, 30)
    >>> parse('tomorrow', settings={'RELATIVE_BASE': datetime.datetime(2020, 1, 1)})
    datetime.datetime(2020, 1, 2, 0, 0)

``STRICT_PARSING``: defaults to ``False``.

When set to ``True`` if missing any of ``day``, ``month`` or ``year`` parts, it does not return any result altogether.:

    >>> parse('March', settings={'STRICT_PARSING': True})
    None

``REQUIRE_PARTS``: ensures results are dates that have all specified parts. It defaults to ``[]`` and can include ``day``, ``month`` and/or ``year``.

For example, assuming current date is `June 16, 2019`:

    >>> parse('2012') # default behavior
    datetime.datetime(2012, 6, 16, 0, 0)
    >>> parse('2012', settings={'REQUIRE_PARTS': ['month']})
    None
    >>> parse('March 2012', settings={'REQUIRE_PARTS': ['day']})
    None
    >>> parse('March 12, 2012', settings={'REQUIRE_PARTS': ['day']})
    datetime.datetime(2012, 3, 12, 0, 0)
    >>> parse('March 12, 2012', settings={'REQUIRE_PARTS': ['day', 'month', 'year']})
    datetime.datetime(2012, 3, 12, 0, 0)


Language Detection
++++++++++++++++++

``SKIP_TOKENS``: it is a ``list`` of tokens to discard while detecting language. Defaults to ``['t']`` which skips T in iso format datetime string .e.g. ``2015-05-02T10:20:19+0000``.:

    >>> from dateparser.date import DateDataParser
    >>> DateDataParser(settings={'SKIP_TOKENS': ['de']}).get_date_data(u'27 Haziran 1981 de')  # Turkish (at 27 June 1981)
    DateData(date_obj=datetime.datetime(1981, 6, 27, 0, 0), period='day', locale='tr')

``NORMALIZE``: applies unicode normalization (removing accents, diacritics...) when parsing the words. Defaults to True.

    >>> dateparser.parse('4 decembre 2015', settings={'NORMALIZE': False})
    # It doesn't work as the expected input should be '4 décembre 2015'

    >>> dateparser.parse('4 decembre 2015', settings={'NORMALIZE': True})
    datetime.datetime(2015, 12, 4, 0, 0)


Default Languages
+++++++++++++++++

``DEFAULT_LANGUAGES``: It is a ``list`` of language codes in ISO 639 that will be used as default
languages for parsing when language detection fails. eg. ["en", "fr"]:

    >>> from dateparser import parse
    >>> parse('3 de marzo de 2020', settings={'DEFAULT_LANGUAGES': ["es"]})

.. note:: When using this setting, these languages will be tried after trying with the detected languages with no success. It is especially useful when using the ``detect_languages_function`.

Optional language detection
+++++++++++++++++++++++++++

``LANGUAGE_DETECTION_CONFIDENCE_THRESHOLD``: defaults to ``0.5``. It is a ``float`` of minimum required confidence for the custom language detection:

    >>> from dateparser import parse
    >>> parse('3 de marzo de 2020', settings={'LANGUAGE_DETECTION_CONFIDENCE_THRESHOLD': 0.5}, detect_languages_function=detect_languages)


Other settings
++++++++++++++

``RETURN_TIME_AS_PERIOD``: returns ``time`` as period in date object, if time component is present in date string.
Defaults to ``False``.

    >>> ddp = DateDataParser(settings={'RETURN_TIME_AS_PERIOD': True})
    >>> ddp.get_date_data('vr jan 24, 2014 12:49')
    DateData(date_obj=datetime.datetime(2014, 1, 24, 12, 49), period='time', locale='nl')

``PARSERS``: it is a list of names of parsers to try, allowing to customize which
parsers are tried against the input date string, and in which order they are
tried.

The following parsers exist:

-   ``'timestamp'``: If the input string starts with 10 digits, optionally
    followed by additional digits or a period (``.``), those first 10 digits
    are interpreted as `Unix time <https://en.wikipedia.org/wiki/Unix_time>`_.

-    ``'negative-timestamp'``: ``'timestamp'`` for negative timestamps. For
    example, parses ``-186454800000`` as ``1964-02-03T23:00:00``.

-   ``'relative-time'``: Parses dates and times expressed in relation to the
    current date and time (e.g. “1 day ago”, “in 2 weeks”).

-   ``'custom-formats'``: Parses dates that match one of the date formats in
    the list of the ``date_formats`` parameter of :func:`dateparser.parse` or
    :meth:`DateDataParser.get_date_data
    <dateparser.date.DateDataParser.get_date_data>`.

-   ``'absolute-time'``: Parses dates and times expressed in absolute form
    (e.g. “May 4th”, “1991-05-17”). It takes into account settings such as
    ``DATE_ORDER`` or ``PREFER_LOCALE_DATE_ORDER``.

-   ``'no-spaces-time'``: Parses dates and times that consist in only digits or
    a combination of digits and non-digits where the first non-digit it's a colon
    (e.g. “121994”, “11:052020”). It's not included in the default parsers and it
    can produce false positives frequently.


:data:`dateparser.settings.default_parsers` contains the default value of
``PARSERS`` (the list above, in that order) and can be used to write code that
changes the parsers to try without skipping parsers that may be added to
Dateparser in the future. For example, to ignore relative times:

    >>> from dateparser_data.settings import default_parsers
    >>> parsers = [parser for parser in default_parsers if parser != 'relative-time']
    >>> parse('today', settings={'PARSERS': parsers})
