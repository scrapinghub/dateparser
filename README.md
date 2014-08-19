DateParser
==========

This is a date parsing library which aims to make easy parsing dates
commonly found in web pages.


How to install
---------------

This is still on the early stages, being extracted and sync from the
code of the [Sprinklr project](https://bitbucket.org/scrapinghub/sprinklr-crawler)

To use it, add to the `requirements.txt` file for your project the line:

    -e git+ssh://git@bitbucket.org/scrapinghub/dateparser#egg=dateparser

And install the dependencies from the file:

    pip install -r requirements.txt


Running the tests
-----------------

To run the tests, first install the test dependencies:

    pip install -r tests/dependencies.txt


Then you can run the tests using:

    nosetests -v
