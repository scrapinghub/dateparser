.. _performance:

===========
Performance
===========

Limit the languages
-------------------

By default, the language of each input string is detected among all supported
languages. If you know which languages your input can be in, pass them through
the ``languages`` or ``locales`` parameter:

    >>> import dateparser
    >>> dateparser.parse('12 de marzo de 2020', languages=['es'])
    datetime.datetime(2020, 3, 12, 0, 0)

Reuse a parser
--------------

:func:`dateparser.parse` creates a new :class:`DateDataParser
<dateparser.date.DateDataParser>` on every call that sets any parameter or
setting. To parse many strings with the same parameters and settings, create a
:class:`DateDataParser <dateparser.date.DateDataParser>` once and reuse it:

    >>> from dateparser.date import DateDataParser
    >>> ddp = DateDataParser(languages=['es'], settings={'PARSERS': ['absolute-time']})
    >>> ddp.get_date_data('12 de marzo de 2020')
    DateData(date_obj=datetime.datetime(2020, 3, 12, 0, 0), period='day', locale='es')

Limit the parsers
-----------------

Set the ``PARSERS`` :ref:`setting <settings>` to the parsers that your input
needs, as in the example above, which skips relative dates like “3 days ago”.

Try previous locales first
--------------------------

With ``try_previous_locales=True``, a :class:`DateDataParser
<dateparser.date.DateDataParser>` first tries the locales that parsed earlier
strings, which is faster when most strings share a locale:

    >>> ddp = DateDataParser(try_previous_locales=True)

The result for a string that is valid in more than one locale, e.g. with a
different date order, then depends on the strings parsed before it.
