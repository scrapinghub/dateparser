import re

from setuptools import setup

readme = open("README.rst", encoding="utf-8").read()
# Remove `.. raw:: html` blocks, which are not supported by PyPI.
readme = re.sub(r"(?m)^\.\. raw:: html\n(?:^[ \t].*\n|^[ \t]*\n)*?\n\n", "", readme)
history = re.sub(
    r":mod:|:class:|:func:", "", open("HISTORY.rst", encoding="utf-8").read()
)

setup(
    long_description=readme + "\n\n" + history,
    long_description_content_type="text/x-rst",
)
