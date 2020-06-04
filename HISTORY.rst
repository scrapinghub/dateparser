.. :changelog:

History
=======


0.7.5 (2020-06-10)
------------------

New features:

* Add Python 3.8 support (see #664)
* Implement a ``REQUIRE_PARTS`` setting (see #703)
* Add support for subscript and superscript numbers (see #684)
* Extended French support (see #672)
* Extended German support (see #673)


Improvements:

* Migrate test suite to Pytest (see #662)
* Add test to check the `yaml` and `json` files content (see #663 and #692)
* Add flake8 pipeline with pytest-flake8 (see #665)
* Add partial support for 8-digit dates without separators (see #639)
* Fix possible ``OverflowError`` errors and explicitly avoid to raise ``ValueError`` when parsing relative dates (see #686)
* Fix double-digit GMT and UTC parsing (see #632)
* Fix bug when using ``DATE_ORDER`` (see #628)
* Fix bug when parsing relative time with timezone (see #503)
* Fix milliseconds parsing (see #572 and #661)
* Fix wrong values to be interpreted as ``'future'`` in ``PREFER_DATES_FROM`` (see #629)
* Other small improvements (see #667, #675, #511, #626, #512, #509, #696, #702 and #699)


0.7.4 (2020-03-06)
------------------
New features:

* Extended Norwegian support (see #598)
* Implement a ``PARSERS`` setting (see #603)

Improvements:

* Add support for ``PREFER_DATES_FROM`` in relative/freshness parser (see #414)
* Add support for ``PREFER_DAY_OF_MONTH`` in base-formats parser (see #611)
* Added UTC -00:00 as a valid offset (see #574)
* Fix support for “one” (see #593)
* Fix TypeError when parsing some invalid dates (see #536)
* Fix tokenizer for non recognized characters (see #622)
* Prevent installing regex 2019.02.19 (see #600)
* Resolve DeprecationWarning related to raw string escape sequences (see #596)
* Implement a tox environment to build the documentation (see #604)
* Improve tests stability (see #591, #605)
* Documentation improvements (see #510, #578, #619, #614, #620)
* Performance improvements (see #570, #569, #625)


0.7.3 (2020-03-06)
------------------
* Broken version


0.7.2 (2019-09-17)
------------------

Features:

* Extended Czech support
* Added ``time`` to valid periods
* Added timezone information to dates found with ``search_dates()``
* Support strings as date formats


Improvements:

* Fixed Collections ABCs depreciation warning
* Fixed dates with trailing colons not being parsed
* Fixed date format override on any settings change
* Fixed parsing current weekday as past date, regardless of settings
* Added UTC -2:30 as a valid offset
* Added Python 3.7 to supported versions, dropped support for Python 3.3 and 3.4
* Moved to importlib from imp where possible
* Improved support for Catalan
* Documentation improvements


0.7.1 (2019-02-12)
------------------

Features/news:

* Added detected language to return value of ``search_dates()``
* Performance improvements
* Refreshed versions of dependencies

Improvements:

* Fixed unpickleable ``DateTime`` objects with timezones
* Fixed regex pattern to avoid new behaviour of re.split in Python 3.7
* Fixed an exception thrown when parsing colons
* Fixed tests failing on days with number greater than 30
* Fixed ``ZeroDivisionError`` exceptions



0.7.0 (2018-02-08)
------------------

Features added during Google Summer of Code 2017:

* Harvesting language data from Unicode CLDR database (https://github.com/unicode-cldr/cldr-json), which includes over 200 locales (#321) - authored by Sarthak Maddan.
  See full currently supported locale list in README.
* Extracting dates from longer strings of text (#324) - authored by Elena Zakharova.
  Special thanks for their awesome contributions!


New features:

* Added (independently from CLDR) Georgian (#308) and Swedish (#305)

Improvements:

* Improved support of Chinese (#359), Thai (#345), French (#301, #304), Russian (#302)
* Removed ruamel.yaml from dependencies (#374). This should reduce the number of installation issues and improve performance as the result of moving away from YAML as basic data storage format.
  Note that YAML is still used as format for support language files.
* Improved performance through using pre-compiling frequent regexes and lazy loading of data (#293, #294, #295, #315)
* Extended tests (#316, #317, #318, #323)
* Updated nose_parameterized to its current package, parameterized (#381)


Planned for next release:

* Full language and locale names
* Performance and stability improvements
* Documentation improvements


0.6.0 (2017-03-13)
------------------

New features:

* Consistent parsing in terms of true python representation of date string. See #281
* Added support for Bangla, Bulgarian and Hindi languages.

Improvements:

* Major bug fixes related to parser and system's locale. See #277, #282
* Type check for timezone arguments in settings. see #267
* Pinned dependencies' versions in requirements. See #265
* Improved support for cn, es, dutch languages. See #274, #272, #285

Packaging:

* Make calendars extras to be used at the time of installation if need to use calendars feature.


0.5.1 (2016-12-18)
------------------

New features:

* Added support for Hebrew

Improvements:

* Safer loading of YAML. See #251
* Better timezone parsing for freshness dates. See #256
* Pinned dependencies' versions in requirements. See #265
* Improved support for zh, fi languages. See #249, #250, #248, #244


0.5.0 (2016-09-26)
------------------

New features:

* ``DateDataParser`` now also returns detected language in the result dictionary.
* Explicit and lucid timezone conversion for a given datestring using ``TIMEZONE``, ``TO_TIMEZONE`` settings.
* Added Hungarian language.
* Added setting, ``STRICT_PARSING`` to ignore incomplete dates.

Improvements:

* Fixed quite a few parser bugs reported in issues #219, #222, #207, #224.
* Improved support for chinese language.
* Consistent interface for both Jalali and Hijri parsers.


0.4.0 (2016-06-17)
------------------

New features:

* Support for Language based date order preference while parsing ambiguous dates.
* Support for parsing dates with no spaces in between components.
* Support for custom date order preference using ``settings``.
* Support for parsing generic relative dates in future.e.g. "tomorrow", "in two weeks", etc.
* Added ``RELATIVE_BASE`` settings to set date context to any datetime in past or future.
* Replaced ``dateutil.parser.parse`` with dateparser's own parser.

Improvements:

* Added simplifications for "12 noon" and "12 midnight".
* Fixed several bugs
* Replaced PyYAML library by its active fork `ruamel.yaml` which also fixed the issues with installation on windows using python35.
* More predictable ``date_formats`` handling.


0.3.5 (2016-04-27)
------------------

New features:

* Danish language support.
* Japanese language support.
* Support for parsing date strings with accents.

Improvements:

* Transformed languages.yaml into base file and separate files for each language.
* Fixed vietnamese language simplifications.
* No more version restrictions for python-dateutil.
* Timezone parsing improvements.
* Fixed test environments.
* Cleaned language codes. Now we strictly follow codes as in ISO 639-1.
* Improved chinese dates parsing.


0.3.4 (2016-03-03)
------------------

Improvements:

* Fixed broken version 0.3.3 by excluding latest python-dateutil version.

0.3.3 (2016-02-29)
------------------

New features:

* Finnish language support.

Improvements:

* Faster parsing with switching to regex module.
* ``RETURN_AS_TIMEZONE_AWARE`` setting to return tz aware date object.
* Fixed conflicts with month/weekday names similarity across languages.

0.3.2 (2016-01-25)
------------------

New features:

* Added Hijri Calendar support.
* Added settings for better control over parsing dates.
* Support to convert parsed time to the given timezone for both complete and relative dates.

Improvements:

* Fixed problem with caching :func:`datetime.now` in :class:`FreshnessDateDataParser`.
* Added month names and week day names abbreviations to several languages.
* More simplifications for Russian and Ukrainian languages.
* Fixed problem with parsing time component of date strings with several kinds of apostrophes.


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
* Support for Tagalog/Filipino dates.
* Improved support for French and Spanish dates.


0.2.0 (2015-06-17)
------------------

* Easy to use ``parse`` function
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
