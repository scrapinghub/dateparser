===============================
DateParser
===============================

.. image:: https://badge.fury.io/py/dateparser.png
    :target: http://badge.fury.io/py/dateparser

.. image:: https://travis-ci.org/scrapinghub/dateparser.png?branch=master
        :target: https://travis-ci.org/scrapinghub/dateparser

.. image:: https://pypip.in/d/dateparser/badge.png
        :target: https://pypi.python.org/pypi/dateparser


Date parsing library designed to make it easy parsing dates commonly found in web pages


* Free software: BSD license
* Documentation: https://dateparser.readthedocs.org.

Features
--------

If you have needed to parse dates before, you probably have used the date
parser of the dateutil_ module.
We built this library on top of it, adding a few features:

* dateparser support dates in languages other than English
* in fact, it can detect the language automatically
* it can give you the date for text like: ``'1 min ago'``, ``'2 weeks ago'``, ``'3 months, 1 weeks and 1 day ago'``, etc


The goal is to support the common date formats used in websites all around the world.

.. _dateutil: https://pypi.python.org/pypi/python-dateutil


Limitations
-----------

DateParser currently tries hard to get the date information right (year, month and day),
but it has limited support for parsing time (hours, minutes and seconds).

