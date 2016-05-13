============
Contributing
============

Contributions are welcome, and they are greatly appreciated! Every
little bit helps, and credit will always be given.

You can contribute in many ways:

Types of Contributions
----------------------

Report Bugs
~~~~~~~~~~~

Report bugs at https://github.com/scrapinghub/dateparser/issues.

If you are reporting a bug, please include:

* Your operating system name and version.
* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.

Fix Bugs
~~~~~~~~

Look through the GitHub issues for bugs. Anything tagged with "bug"
is open to whoever wants to implement it.

Implement Features
~~~~~~~~~~~~~~~~~~

Look through the GitHub issues for features. Anything tagged with "feature"
is open to whoever wants to implement it.
We encourage you to add new languages to existing stack.

Write Documentation
~~~~~~~~~~~~~~~~~~~

DateParser could always use more documentation, whether as part of the
official DateParser docs, in docstrings, or even on the web in blog posts,
articles, and such.

Submit Feedback
~~~~~~~~~~~~~~~

The best way to send feedback is to file an issue at https://github.com/scrapinghub/dateparser/issues.

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
* Remember that contributions are welcome :)


Get Started!
------------

Ready to contribute? Here's how to set up `dateparser` for local development.

1. Fork the `dateparser` repo on GitHub.
2. Clone your fork locally::

    $ git clone git@github.com:your_name_here/dateparser.git

3. Install your local copy into a virtualenv. Assuming you have virtualenvwrapper installed, this is how you set up your fork for local development::

    $ mkvirtualenv dateparser
    $ cd dateparser/
    $ python setup.py develop

4. Create a branch for local development::

    $ git checkout -b name-of-your-bugfix-or-feature

   Now you can make your changes locally.

5. When you're done making changes, check that your changes pass flake8 and the tests, including testing other Python versions with tox::

    $ pip install -r tests/requirements.txt # install test dependencies
    $ flake8 dateparser tests
    $ nosetests
    $ tox

   To get flake8 and tox, just pip install them into your virtualenv. (Note that we use ``max-line-length = 100`` for flake8, this is configured in ``setup.cfg`` file.)

6. Commit your changes and push your branch to GitHub::

    $ git add .
    $ git commit -m "Your detailed description of your changes."
    $ git push origin name-of-your-bugfix-or-feature

7. Submit a pull request through the GitHub website.

Pull Request Guidelines
-----------------------

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests.
2. If the pull request adds functionality, the docs should be updated. Put
   your new functionality into a function with a docstring, and add the
   feature to the list in *README.rst*.
3. Check https://travis-ci.org/scrapinghub/dateparser/pull_requests
   and make sure that the tests pass for all supported Python versions.
4. Follow the core developers' advice which aim to ensure code's consistency regardless of variety of approaches used by many contributors.
5. In case you are unable to continue working on a PR, please leave a short comment to notify us. We will be pleased to make any changes required to get it done.

Guidelines for Adding New Languages
-----------------------------------
English is the primary language of the dateparser. Dates in all other languages are translated into English equivalents before they are parsed.
The language data required for parsing dates is contained in *data/languages.yml* file. It contains variable parts that can be used in dates, language by language: month and week names - and their abbreviations, prepositions, conjunctions and frequently used descriptive words and phrases (like "today").
The chosen data format is YAML because it is readable and simple to edit.
Language data is extracted per language from YAML with :class:`LanguageDataLoader` and validated before being put into :class:`Language` class.

Refer to :ref:`language-data-template` for details about its structure and take a look at already implemented languages for examples.
As we deal with the delicate fabric of interwoven languages, tests are essential to keep the functionality across them.
Therefore any addition or change should be reflected in tests.
However, there is nothing to be afraid of: our tests are highly parameterized and in most cases a test fits in one declarative line of data.
Alternatively, you can provide required information and ask the maintainers to create the tests for you.
