.. :changelog:

History
=======

0.3.1 (2015-10-28)
------------------
New features:

* Support for Jalali Calendar.
* Belarusian language support.
* Indonesian language support.


Improvements:

* Extended support for Russian and Polish.
* Fixed bug with time zone recognition.
* Fixed bug with incorrect translation of "second" for Portuguese.


0.3.0 (2015-07-29)
------------------
New features:

* Compatibility with Python 3 and PyPy.

Improvements:

* `languages.yaml` data cleaned up to make it human-readable.
* Improved Spanish date parsing.


0.2.1 (2015-07-13)
------------------
* Support for generic parsing of dates with UTC offset.
* Support for Filipino dates.
* Improved support for French and Spanish dates.


0.2.0 (2015-06-17)
------------------
* Easy to use `parse` function
* Languages definitions using YAML.
* Using translation based approach for parsing non-english languages. Previously, :mod:`dateutil.parserinfo` was used for language definitions.
* Better period extraction.
* Improved tests.
* Added a number of new simplifications for more comprehensive generic parsing.
* Improved validation for dates.
* Support for Polish, Thai and Arabic dates.
* Support for :mod:`pytz` timezones.
* Fixed building and packaging issues.


0.1.0 (2014-11-24)
------------------

* First release on PyPI.
