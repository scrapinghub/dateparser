DateParser
==========

This is a date parsing library which aims to make easy parsing dates
commonly found in web pages.


How to install
---------------

To use it, add to the `requirements.txt` file for your project the line:

    -e git+ssh://git@bitbucket.org/scrapinghub/dateparser#egg=dateparser

And install the dependencies from the file:

    pip install -r requirements.txt


How to use in a project in dash
-------------------------------

To use in dash, first you need to build an egg for the library.
Check out the code and run the command:

    python setup.py bdist_egg

After that, you can upload the egg using Dash UI, or you can use [shubc][1]
and do:

    shubc eggs-add <YOUR_PROJECT_ID> dist/dateparser-0.1-py2.7.egg


[1]: https://github.com/scrapinghub/shubc


Running the tests
-----------------

To run the tests, first install the test dependencies:

    pip install -r tests/dependencies.txt


Then you can run the tests using:

    nosetests -v
