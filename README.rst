==========
dateparser
==========

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
* Generic parsing of contextual dates like: ``'1 min ago'``, ``'2 weeks ago'``, ``'3 months, 1 weeks and 1 day ago'``.
* Generic parsing of dates with time zones abbreviations like: ``'August 14, 2015 EST'``, ``'July 4, 2013 PST'``.
* Easy confingurations to change default parsing behavior.
* Extensive test coverage.


Usage
-----
The most common way is to use the :py:meth:``dateparser.parse`` function,
that wraps around most of the functionality in the module.

Here is a quick example of usage::


Popular Formats
~~~~~~~~~~~~~~~

    >>> import dateparser
    >>> ddp.get_date_data('12/12/12')
    datetime.datetime(2012, 12, 12, 0, 0)
    >>> dateparser.parse(u'Fri, 12 Dec 2014 10:55:50')
    datetime.datetime(2014, 12, 12, 10, 55, 50)
    >>> dateparser.parse(u'Martes 21 de Octubre de 2014')  # Spanish
    datetime.datetime(2014, 10, 21, 0, 0)
    >>> dateparser.parse(u'Le 11 Décembre 2014 à 09:00')  # French
    datetime.datetime(2014, 12, 11, 9, 0)
    >>> dateparser.parse(u'13 января 2015 г. в 13:34')  # Russian
    datetime.datetime(2015, 1, 13, 13, 34)
    >>> dateparser.parse(u'1 เดือนตุลาคม 2005, 1:00 AM')  # Thai
    datetime.datetime(2005, 10, 1, 1, 0)


Contextual Dates
~~~~~~~~~~~~~~~~

    >>> parse('1 hour ago')
    datetime.datetime(2012, 12, 21, 23, 0)
    >>> parse(u'Il ya 2 heures')  # French
    datetime.datetime(2012, 12, 21, 22, 0)
    >>> parse(u'1 anno 2 mesi')  # Italian
    datetime.datetime(2011, 10, 22, 0, 0)
    >>> parse(u'yaklaşık 23 saat önce')  # Russian
    datetime.datetime(2012, 12, 21, 1, 0)
    >>> parse(u'Hace una semana')  # Spanish
    datetime.datetime(2012, 12, 15, 0, 0)
    >>> parse(u'2小时前')  # Chinese
    datetime.datetime(2012, 12, 21, 22, 0)

.. note:: Testing above code might return different values for you depending on your environment's current date time. To reproduce exactly above results, you can patch your environment as follows:

    >>> from dateparser.date import freshness_date_parser
    >>> patch.object(freshness_date_parser, 'now', datetime(2012, 12, 22, 0, 0)).start()


Dependencies
------------
`dateparser` translates non-english dates to English and uses dateutil_ module ``'parser'`` to parse the translated date. 
Also, it requires PyYAML_ for its language detection module to work.

.. _dateutil: https://pypi.python.org/pypi/python-dateutil
.. _PyYAML: https://pypi.python.org/pypi/PyYAML


Limitations
-----------
`dateparser` at this point does not support generic parsing of dates with fixed UTC offsets. This restricts its ability to reliably parse time zone aware dates since the use of abbreviated time zones as a sole designator of time zones is not recommended.

