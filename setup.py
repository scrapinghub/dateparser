import re
import io
from setuptools import setup, find_packages

open_as_utf = lambda x: io.open(x, encoding='utf-8')

(__version__, ) = re.findall(r"__version__.*\s*=\s*[']([^']+)[']",
                             open('dateparser/__init__.py').read())

readme = re.sub(r':members:.+|..\sautomodule::.+|:class:|:func:', '', open_as_utf('README.rst').read())
readme = re.sub(r'`Settings`_', '`Settings`', readme)
readme = re.sub(r'`Contributing`_', '`Contributing`', readme)
history = re.sub(r':mod:|:class:|:func:', '', open_as_utf('HISTORY.rst').read())


test_requirements = open('tests/requirements.txt').read().splitlines()

setup(
    name='dateparser',
    version=__version__,
    description='Date parsing library designed to parse dates from HTML pages',
    long_description=readme + '\n\n' + history,
    author='Scrapinghub',
    author_email='info@scrapinghub.com',
    url='https://github.com/scrapinghub/dateparser',
    project_urls={
        'History': 'https://dateparser.readthedocs.io/en/latest/history.html',
    },
    packages=find_packages(exclude=('tests', 'tests.*')),
    include_package_data=True,
    install_requires=[
        'python-dateutil',
        'pytz',
        # https://bitbucket.org/mrabarnett/mrab-regex/issues/314/import-error-no-module-named
        'regex !=2019.02.19',
        'tzlocal',
    ],
    extras_require={
        'calendars:python_version<"3.6"': ['convertdate'],
        'calendars:python_version>="3.6"': ['hijri-converter', 'convertdate'],
    },
    license="BSD",
    zip_safe=False,
    keywords='dateparser',
    python_requires='>=3.5',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ],
)
