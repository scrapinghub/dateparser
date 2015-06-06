Using dateparser
================

Quickstart
----------

The most straightforward way to parse a date with ``dateparser`` is to
use the :py:meth:`dateparser.parse` function::

    >>> import dateparser
    >>> dateparser.parse('18 Julho 1997')
    datetime.datetime(1997, 7, 18, 0, 0)
    >>> dateparser.parse('2015, Jun 13, 1:08 pm')
    datetime.datetime(2015, 6, 13, 13, 8)
    >>> dateparser.parse('15 min ago')
    datetime.datetime(2015, 6, 6, 17, 21, 36, 23723)
    >>> dateparser.parse(u'15 minutos atrás')
    datetime.datetime(2015, 6, 6, 17, 21, 36, 23723)


This will try to parse a date from the given string, attempting to
detect the language each time.

If you know beforehand the languages that the date should be, you can skip
language detection specifying them using the ``languages`` argument::

    >>> dateparser.parse('2015, Ago 15, 1:08 pm', languages=['pt', 'es'])
    datetime.datetime(2015, 8, 15, 13, 8)
    >>> dateparser.parse(u'il y a 15 minutes', languages=['fr'])
    datetime.datetime(2015, 6, 6, 17, 21, 36, 23723)
    >>> dateparser.parse(u'ayer', languages=['es'])
    datetime.datetime(2015, 6, 5, 17, 36, 36, 23723)


If you know the possible formats that the date will be, you can
use the ``date_formats`` argument::

    >>> dateparser.parse(u'22 Décembre 2010', date_formats=['%d %B %Y'])
    datetime.datetime(2010, 12, 22, 0, 0)


DateDataParser: deducing language and period detail
----------------------------------------------------

If you have a set of dates that are expected to be in the same language
(for example, if they belong to the same documents), but you don't know
what the language is at first, you can use the ``DateDataParser``
class directly.

This class wraps around the core ``dateparser`` functionality, and by default
it assumes that all of the dates fed to it will be in the same language.

The result of parsing will be a dict containing the datetime object and also an
indication of the period detail recognized for the date under the `'period'`
key.

Here are some usage examples::

    >>> from dateparser.date import DateDataParser
    >>> ddp = DateDataParser()
    >>> ddp.get_date_data('1 min ago')
    {'date_obj': datetime.datetime(2014, 8, 20, 21, 1, 42, 590596), 'period': u'day'}
    >>> ddp.get_date_data('1 week ago')
    {'date_obj': datetime.datetime(2014, 8, 13, 21, 2, 42, 590596), 'period': u'weeks'}
    >>> ddp.get_date_data('1 year ago')
    {'date_obj': datetime.datetime(2013, 8, 20, 21, 2, 42, 590596), 'period': u'years'}
    >>> ddp.get_date_data('12/12/12')
    {'date_obj': datetime.datetime(2012, 12, 12, 0, 0), 'period': 'day'}
    >>> ddp.get_date_data('13 August, 2014')
    {'date_obj': datetime.datetime(2014, 8, 13, 0, 0), 'period': 'day'}

Note: the possible values for `'period'` are currently: `'years'`, `weeks` or `day`.

By default, an instance of DateDataParser will keep trying to reduce the number
of possible languages, until it reduces it to only one possibility. It will
assume the previously detected languages for all the next dates and won't try
to execute the language detection again after a language is discarded::


    >>> ddp = DateDataParser()
    >>> ddp.get_date_data('1 minuto atrás')
    {'date_obj': datetime.datetime(2014, 8, 20, 21, 1, 42, 590596), 'period': u'day'}
    >>> ddp.get_date_data('13 Agosto 2014')
    {'date_obj': datetime.datetime(2014, 8, 13, 0, 0), 'period': 'day'}
    >>> ddp.get_date_data('13 Marzo 2014')
    {'date_obj': datetime.datetime(2014, 3, 13, 0, 0), 'period': 'day'}
    >>> ddp.get_date_data('13 Maio 2014')
    Traceback (most recent call last):
    ...
    dateparser.date_parser.LanguageWasNotSeenBeforeError


If you want it to redetect the language every time, you can set the argument
allow_redetect_language, like so::


    >>> ddp = DateDataParser(allow_redetect_language=True)
    >>> ddp.get_date_data(u'1 minuto atrás')
    {'date_obj': datetime.datetime(2015, 6, 6, 19, 0, 42, 300135), 'period': u'day'}
    >>> ddp.get_date_data('13 Agosto 2014')
    {'date_obj': datetime.datetime(2014, 8, 13, 0, 0), 'period': 'day'}
    >>> ddp.get_date_data('13 Marzo 2014')
    {'date_obj': datetime.datetime(2014, 3, 13, 0, 0), 'period': 'day'}
    >>> ddp.get_date_data('13 Maio 2014')
    {'date_obj': datetime.datetime(2014, 5, 13, 0, 0), 'period': 'day'}


Deploying dateparser in a Scrapy Cloud project
----------------------------------------------

The initial use cases for `dateparser` were for Scrapy projects doing web
scraping that needed to parse dates from websites. These instructions show how
you can deploy it in a Scrapy project running in `Scrapy Cloud
<http://scrapinghub.com/scrapy-cloud>`_.


Deploying with shub
~~~~~~~~~~~~~~~~~~~

The most straightforward way to do that is to use the
latest version of the `shub <https://github.com/scrapinghub/shub>`
utility, and just run::

    shub deploy-egg --from-url git@github.com:scrapinghub/dateparser.git YOUR_PROJECT_ID


Deploying the egg manually
~~~~~~~~~~~~~~~~~~~~~~~~~~

In case you run into trouble with the above procedure, you can deploy the egg
manually. First clone the ``dateparser``'s repo, then inside its directory run
the command::

    python setup.py bdist_egg

After that, you can upload the egg using `Scrapy Cloud's Dashboard interface
<http://dash.scrapinghub.com>`_.
