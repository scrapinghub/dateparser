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

Fix Bugs and Implement Features
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Look through the GitHub issues for bugs and feature requests. To avoid
duplicate efforts, try to choose issues without related PRs or with staled PRs.
We also encourage you to add new languages to the existing stack.

Write Documentation
~~~~~~~~~~~~~~~~~~~

Dateparser could always use more documentation, whether as part of the
official Dateparser docs, in docstrings, or even on the web in blog posts,
articles, and such.

After you make local changes to the documentation, you will be able to build the
project running::

    tox -e docs


Then open ``.tox/docs/tmp/html/index.html`` in a web browser to see your local
build of the documentation.

.. note::

    If you don't have ``tox`` installed, you need to install it first using
    ``pip install tox``.

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

3. Install your local copy into a virtualenv. Assuming you have virtualenvwrapper
installed, this is how you set up your fork for local development::

    $ mkvirtualenv dateparser
    $ cd dateparser/
    $ python setup.py develop

4. Create a branch for local development::

    $ git checkout -b name-of-your-bugfix-or-feature

   Now you can make your changes locally.

5. When you're done making changes, check that your changes pass flake8 and the
tests, including testing other Python versions with tox::

    $ tox

   To get ``tox``, just ``pip install`` it into your virtualenv. In addition to tests, ``tox`` checks for code style and maximum line length (119 characters).

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
3. Check the pipelines (Github Actions) in the PR comments (or in
   https://github.com/scrapinghub/dateparser/actions) and make sure that the
   tests pass for all supported Python versions.
4. Check the new project coverage in the PR comments (or in
   https://app.codecov.io/gh/scrapinghub/dateparser/pulls) and make sure that
   it remained equal or higher than previously.
5. Follow the core developers' advice which aims to ensure code's consistency
   regardless of the variety of approaches used by many contributors.
6. In case you are unable to continue working on a PR, please leave a short
   comment to notify us. We will be pleased to make any changes required to get
   it done.

Guidelines for Editing Translation Data
---------------------------------------

English is the primary language of Dateparser. Dates in all other languages are
translated into English equivalents before they are parsed.

The language data that Dateparser uses to parse dates is in
``dateparser/data/date_translation_data``. For each supported language, there
is a Python file containing translation data.

Each translation data Python files contains different kinds of translation data
for date parsing: month and week names - and their abbreviations, prepositions,
conjunctions, frequently used descriptive words and phrases (like “today”),
etc.

Translation data Python files are generated from the following sources:

-   `Unicode CLDR <http://cldr.unicode.org/>`_ data in JSON format, located at
    ``dateparser_data/cldr_language_data/date_translation_data``

-   Additional data from the Dateparser community in YAML format, located at
    ``dateparser_data/supplementary_language_data/date_translation_data``

If you wish to extend the data of an existing language, or add data for a new
language, you must:

#.  Edit or create the corresponding file within
    ``dateparser_data/supplementary_language_data/date_translation_data``

    See existing files to learn how they are defined, and see
    :ref:`language-data-template` for details.

#.  Regenerate the corresponding file within
    ``dateparser/data/date_translation_data`` running the following script::

        dateparser_scripts/write_complete_data.py

#.  Write tests that cover your changes

    You should be able to find tests that cover the affected data, and use
    copy-and-paste to create the corresponding new test.

    If in doubt, ask Dateparser maintainers for help.

.. toctree::
   :maxdepth: 2
   :hidden:

   template

Updating the List of Supported Languages and Locales
----------------------------------------------------

Whenever the content of
``dateparser.data.languages_info.language_locale_dict`` is modified, use
``dateparser_scripts/update_supported_languages_and_locales.py`` to update
the corresponding documentation table::

    dateparser_scripts/update_supported_languages_and_locales.py
