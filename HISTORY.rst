.. :changelog:

History
=======

1.1.5 (2022-12-29)
------------------

Improvements:

- Parse short versions of day, month, and year (#1103)
- Add a test for “in 1d” (#1104)
- Update languages_info (#1107)
- Add a workaround for zipimporter not having exec_module before Python 3.10 (#1069)
- Stabilize tests at midnight (#1111)
- Add a test case for French (#1110)

Cleanups:

- Remove the requirements-build file (#1113)


1.1.4 (2022-11-21)
------------------

Improvements:

- Improved support for languages such as Slovak, Indonesian, Hindi, German and Japanese (#1064, #1094, #986, #1071, #1068)
- Recursively create a model home (#996)
- Replace regex sub with simple string replace (#1095)
- Add Python 3.10, 3.11 support (#1096)
- Drop support for Python 3.5, 3.6 versions (#1097)


1.1.3 (2022-11-03)
------------------

New features:

- Add support for fractional units (#876)

Improvements:

- Fix the returned datetime skipping a day with time+timezone input and PREFER_DATES_FROM = 'future' (#1002)
- Fix input translatation breaking keep_formatting (#720)
- English: support "till date" (#1005)
- English: support “after” and “before” in relative dates (#1008)

Cleanups:

- Reorganize internal data (#1090)
- CI updates (#1088)


1.1.2 (2022-10-20)
------------------

Improvements:

- Added support for negative timestamp (#1060)
- Fixed PytzUsageWarning for Python versions >= 3.6 (#1062)
- Added support for dates with dots and spaces (#1028)
- Improved support for Ukrainian, Croatian and Russian (#1072, #1074, #1079, #1082, #1073, #1083)
- Added support for parsing Unix timestamps consistently regardless of timezones (#954)
- Improved tests (#1086)


1.1.1 (2022-03-17)
------------------

Improvements:

- Fixed issue with regex library by pinning dependencies to an earlier version (< 2022.3.15, #1046).
- Extended support for Russian language dates starting with lowercase (#999).
- Allowed to use_given_order for languages too (#997).
- Fixed link to settings section (#1018).
- Defined UTF-8 encoding for Windows (#998).
- Fixed directories creation error in CLI utils (#1022).


1.1.0 (2021-10-04)
------------------

New features:

* Support language detection based on ``langdetect``, ``fastText``, or a
  custom implementation (see #932)
* Add support for 'by <time>' (see #839)
* Sort default language list by internet usage (see #805)

Improvements:

* Improved support of Chinese (#910), Czech (#977)
* Improvements in ``search_dates`` (see #953)
* Make order of previous locales deterministic (see #851)
* Fix parsing with trailing space (see #841)
* Consider ``RETURN_TIME_AS_PERIOD`` for timestamp times (see #922)
* Exclude failing regex version (see #974)
* Ongoing work multithreading support (see #881, #885)
* Add demo URL (see #883)

QA:

* Migrate pipelines from Travis CI to Github Actions (see #859, #879, #884,
  #886, #911, #966)
* Use versioned CLDR data (see #825)
* Add a script to update table of supported languages and locales (see #601)
* Sort 'skip' keys in yaml files (see #844)
* Improve test coverage (see #827)
* Code cleanup (see #888, #907, #951, #958, #957)


1.0.0 (2020-10-29)
------------------

Breaking changes:

* Drop support for Python 2.7 and pypy (see #727, #744, #748, #749, #754, #755, #758, #761, #763, #764, #777 and #783)
* Now ``DateDataParser.get_date_data()`` returns a ``DateData`` object instead of a ``dict`` (see #778).
* From now wrong ``settings`` are not silenced and raise ``SettingValidationError`` (see #797)
* Now ``dateparser.parse()`` is deterministic and doesn't try previous locales. Also, ``DateDataParser.get_date_data()`` doesn't try the previous locales by default (see #781)
* Remove the ``'base-formats'`` parser (see #721)
* Extract the ``'no-spaces-time'`` parser from the ``'absolute-time'`` parser and make it an optional parser (see #786)
* Remove ``numeral_translation_data`` (see #782)
* Remove the undocumented ``SKIP_TOKENS_PARSER`` and ``FUZZY`` settings (see #728, #794)
* Remove support for using strings in ``date_formats`` (see #726)
* The undocumented ``ExactLanguageSearch`` class has been moved to the private scope and some internal methods have changed (see #778)
* Changes in ``dateparser.utils``: ``normalize_unicode()`` doesn't accept ``bytes`` as input and ``convert_to_unicode`` has been deprecated (see #749)

New features:

* Add Python 3.9 support (see #732, #823)
* Detect hours separated with a period/dot (see #741)
* Add support for "decade" (see #762)
* Add support for the hijri calendar in Python ≥ 3.6 (see #718)

Improvements:

* New logo! (see #719)
* Improve the README and docs (see #779, #722)
* Fix the "calendars" extra (see #740)
* Fix leap years when ``PREFER_DATES_FROM`` is set (see #738)
* Fix ``STRICT_PARSING`` setting in ``no-spaces-time`` parser (see #715)
* Consider ``RETURN_AS_TIME_PERIOD`` setting for ``relative-time`` parser (see #807)
* Parse the 24hr time format with meridian info (see #634)
* Other small improvements (see #698, #709, #710, #712, #730, #731, #735, #739, #784, #788, #795 and #801)


0.7.6 (2020-06-12)
------------------

Improvements:

* Rename ``scripts`` to ``dateparser_scripts`` to avoid name collisions with modules from other packages or projects (see #707)


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
