========
Usage
========

The most common way is to use the ``dateparser.date.DateDataParser`` class,
that wraps around most of the functionality in the module.

Here is a quick example of usage::

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


Note about language detection
-----------------------------

As it is now, an instance of DateDataParser by default assumes that
all of the dates fed to it will be in the same language.

So, it will keep trying to detect the possible languages until it reduces it
to only one possibility. When it does, it will just assume that for the next
dates and won't try to execute the language detection again::


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


If you want it to redetect the language every time, you can use a custom date_parser, like so::


    >>> ddp = DateDataParser()
    >>> from dateparser.date_parser import DateParser
    >>> ddp.date_parser = DateParser(allow_redetect_language=True)
    >>> ddp.get_date_data('1 minuto atrás')
    {'date_obj': datetime.datetime(2014, 8, 20, 21, 1, 42, 590596), 'period': u'day'}
    >>> ddp.get_date_data('13 Agosto 2014')
    {'date_obj': datetime.datetime(2014, 8, 13, 0, 0), 'period': 'day'}
    >>> ddp.get_date_data('13 Marzo 2014')
    {'date_obj': datetime.datetime(2014, 3, 13, 0, 0), 'period': 'day'}
    >>> ddp.get_date_data('13 Maio 2014')
    {'date_obj': datetime.datetime(2014, 5, 13, 0, 0), 'period': 'day'}


How to use in a Scrapy Cloud project
------------------------------------

To use in `Scrapy Cloud <http://scrapinghub.com/scrapy-cloud>`_, first you need to build an egg for the library.

Clone the repo and inside its directory, run the command::

    python setup.py bdist_egg

After that, you can upload the egg using
`Scrapy Cloud's Dashboard interface <http://dash.scrapinghub.com>`_,
or you can use shubc_ command and do::

    shubc eggs-add <YOUR_PROJECT_ID> dist/dateparser-0.1-py2.7.egg


.. _shubc: https://github.com/scrapinghub/shubc


