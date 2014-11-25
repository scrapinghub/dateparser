
from dateparser import __version__


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

requirements = ['wheel==0.23.0'] + open('requirements.txt').read().splitlines()

test_requirements = open('tests/requirements.txt').read().splitlines()

setup(
    name='dateparser',
    version=__version__,
    description='Date parsing library designed to parse dates from HTML pages',
    long_description=readme + '\n\n' + history,
    author='Scrapinghub',
    author_email='info@scrapinghub.com',
    url='https://github.com/scrapinghub/dateparser',
    packages=[
        'dateparser',
    ],
    package_dir={'dateparser':
                 'dateparser'},
    include_package_data=True,
    install_requires=requirements,
    license="BSD",
    zip_safe=False,
    keywords='dateparser',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
