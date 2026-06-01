import re

from setuptools import setup

readme = open("README.rst", encoding="utf-8").read()
history = re.sub(
    r":mod:|:class:|:func:", "", open("HISTORY.rst", encoding="utf-8").read()
)

setup(
    long_description=readme + "\n\n" + history,
)
