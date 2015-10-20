dateparser.calendars package
============================

Submodules
----------


dateparser.calendars.jalali module
----------------------------------

.. automodule:: dateparser.calendars.jalali
	:members: JalaliParser
	:show-inheritance:

Example of Use
~~~~~~~~~~~~~~
.. code-block:: python

	In [1]: from dateparser.calendars.jalali import JalaliParser
	
	In [2]: JalaliParser(u'جمعه سی ام اسفند ۱۳۸۷').get_date()
	Out[2]: datetime.datetime(2009, 3, 20, 0, 0)


Module contents
---------------
.. automodule:: dateparser.calendars
	:members:
	:show-inheritance:
    