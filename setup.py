import re

from setuptools import find_packages, setup

__version__ = re.search(
    r"__version__.*\s*=\s*[\"]([^\"]+)[\"]", open("dateparser/__init__.py").read()
).group(1)

introduction = re.sub(
    r":members:.+|..\sautomodule::.+|:class:|:func:|:ref:",
    "",
    open("docs/introduction.rst", encoding="utf-8").read(),
)
history = re.sub(
    r":mod:|:class:|:func:", "", open("HISTORY.rst", encoding="utf-8").read()
)

setup(
    name="dateparser",
    version=__version__,
    description="Date parsing library designed to parse dates from HTML pages",
    long_description=introduction + "\n\n" + history,
    author="Scrapinghub",
    author_email="opensource@zyte.com",
    url="https://github.com/scrapinghub/dateparser",
    project_urls={
        "History": "https://dateparser.readthedocs.io/en/latest/history.html",
    },
    packages=find_packages(exclude=("tests", "tests.*")),
    include_package_data=True,
    install_requires=[
        "python-dateutil>=2.7.0",
        "pytz>=2024.2",
        "regex>=2024.9.11",
        "tzlocal>=0.2",
    ],
    entry_points={
        "console_scripts": ["dateparser-download = dateparser_cli.cli:entrance"],
    },
    extras_require={
        "calendars": ["convertdate>=2.2.1", "hijridate"],
        "fasttext": ["fasttext>=0.9.2", "numpy>=1.19.3,<2"],
        "langdetect": ["langdetect>=1.0.0"],
    },
    license="BSD",
    zip_safe=False,
    keywords="dateparser",
    python_requires=">=3.8",  # Python 3.8 is required for fuzzing
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: Implementation :: CPython",
    ],
)
