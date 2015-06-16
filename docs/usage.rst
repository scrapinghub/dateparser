Using DateDataParser
--------------------

:func:`dateparser.parse` uses a default parser which tries to detect language
every time it is called and is not the most efficient way while parsing dates
from the same source.

:class:`dateparser.date.DateDataParser` provides an alternate and efficient way
to control language detection behavior.

The instance of :class:`dateparser.date.DateDataParser` reduces the number
of applicable languages, until only one or no language is left. It 
assumes the previously detected language for all the next dates and does not try
to execute the language detection again after a language is discarded.

This class wraps around the core :mod:`dateparser` functionality, and by default
assumes that all of the dates fed to it are in the same language.

.. autoclass:: dateparser.date.DateDataParser
   :members: get_date_data

Once initialized, :func:`dateparser.date.DateDataParser.get_date_data` parses date strings::

    >>> from dateparser.date import DateDataParser
    >>> ddp = DateDataParser()
    >>> ddp.get_date_data(u'Martes 21 de Octubre de 2014')  # Spanish
    {'date_obj': datetime.datetime(2014, 10, 21, 0, 0), 'period': u'day'}
    >>> ddp.get_date_data(u'13 Septiembre, 2014')  # Spanish
    {'date_obj': datetime.datetime(2014, 9, 13, 0, 0), 'period': u'day'}

.. warning:: It fails to parse *English* dates in the example below, because *Spanish* was detected and stored with the ``ddp`` instance::

    >>> ddp.get_date_data('11 August 2012')
    {'date_obj': None, 'period': 'day'} 


.. note:: the possible values for `'period'` are currently: `'year'`, `week` or `day`.

:class:`dateparser.date.DateDataParser` can also be initialized with known languages::

    >>> ddp = DateDataParser(languages=['de', 'nl'])
    >>> ddp.get_date_data(u'vr jan 24, 2014 12:49')
    {'date_obj': datetime.datetime(2014, 1, 24, 12, 49), 'period': u'day'}
    >>> ddp.get_date_data(u'18.10.14 um 22:56 Uhr')
    {'date_obj': datetime.datetime(2014, 10, 18, 22, 56), 'period': u'day'}


Deploying dateparser in a Scrapy Cloud project
----------------------------------------------

The initial use cases for `dateparser` were for Scrapy projects doing web
scraping that needed to parse dates from websites. These instructions show how
you can deploy it in a Scrapy project running in `Scrapy Cloud
<http://scrapinghub.com/scrapy-cloud>`_.


Deploying with shub
~~~~~~~~~~~~~~~~~~~

The most straightforward way to do that is to use the
latest version of the `shub <https://github.com/scrapinghub/shub>`_
command line tool.

First, install ``shub``, if you haven't already::

    pip install shub

Then, you can choose between deploying a stable release or the latest from
development.


Deploying a stable dateparser release:
**************************************


1) Then, use ``shub`` to install `python-dateutil`_ and `PyYAML`_ dependencies from `PyPI`_::

    shub deploy-egg --from-pypi python-dateutil YOUR_PROJECT_ID
    shub deploy-egg --from-pypi PyYAML YOUR_PROJECT_ID


2) Finally, deploy dateparser from PyPI::

    shub deploy-egg --from-pypi dateparser YOUR_PROJECT_ID

.. _python-dateutil: https://pypi.python.org/pypi/python-dateutil
.. _PyYAML: https://pypi.python.org/pypi/PyYAML
.. _PyPI: https://pypi.python.org/pypi


Deploying from latest sources
*****************************

Optionally, you can deploy it from the latest sources:

Inside the ``dateparser`` root directory::

1) Run the command to deploy the dependencies::

    shub deploy-reqs YOUR_PROJECT_ID requirements.txt

2) Then, either deploy from the latest sources on GitHub::

    shub deploy-egg --from-url git@github.com:scrapinghub/dateparser.git YOUR_PROJECT_ID

Or, just deploy from the local sources (useful if you have local
modifications)::

    shub deploy-egg


Deploying the egg manually
~~~~~~~~~~~~~~~~~~~~~~~~~~

In case you run into trouble with the above procedure, you can deploy the egg
manually. First clone the ``dateparser``'s repo, then inside its directory run
the command::

    python setup.py bdist_egg

After that, you can upload the egg using `Scrapy Cloud's Dashboard interface
<http://dash.scrapinghub.com>`_.
