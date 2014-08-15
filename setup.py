
from setuptools import setup
from dateparser import __version__

setup(
    name='dateparser',
    version=__version__,
    author='ScrapingHub',
    author_email='info@scrapinghub.com',
    url='http://scrapinghub.com',
    packages=['dateparser'],
    description='Date parsing library designed to parse dates from HTML pages',
    requires=['dateutil'],
    install_requires=[
        "python-dateutil >= 2.2",
    ]
)
