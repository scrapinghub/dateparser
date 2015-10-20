============
Installation
============

At the command line::

    $ pip install dateparser

Or, if you don't have pip installed::

    $ easy_install dateparser

If you want to install from the latest sources, you can do::

    $ git clone https://github.com/scrapinghub/dateparser.git
    $ cd dateparser
    $ python setup.py install


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


1) Then, use ``shub`` to install `python-dateutil`_ (we require at least 2.3 version), `jdatetime`_ and `PyYAML`_ dependencies from `PyPI`_::

    shub deploy-egg --from-pypi python-dateutil YOUR_PROJECT_ID
    shub deploy-egg --from-pypi jdatetime YOUR_PROJECT_ID
    shub deploy-egg --from-pypi PyYAML YOUR_PROJECT_ID


2) Finally, deploy dateparser from PyPI::

    shub deploy-egg --from-pypi dateparser YOUR_PROJECT_ID

.. _python-dateutil: https://pypi.python.org/pypi/python-dateutil
.. _PyYAML: https://pypi.python.org/pypi/PyYAML
.. _jdatetime: https://pypi.python.org/pypi/jdatetime
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
<http://dash.scrapinghub.com>`_ under Settings > Eggs section.

Dependencies
************

Similarly, you can download source and package `PyYAML <https://pypi.python.org/pypi/PyYAML>`_, `jdatetime <https://pypi.python.org/pypi/jdatetime>`_ and `dateutil <https://pypi.python.org/pypi/python-dateutil>`_ (version >= 2.3) as `eggs` and deploy them like above.

