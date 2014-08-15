
from setuptools import setup

setup(
    name='dateparser',
    version='0.1',
    author='ScrapingHub',
    packages=['dateparser'],
    description='Date parsing library designed to parse dates from HTML pages',
    requires=['dateutil'],
    install_requires=[
        "python-dateutil >= 2.2",
    ]
)
