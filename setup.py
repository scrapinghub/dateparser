import re
from pathlib import Path

from setuptools import setup

readme = Path("README.rst").read_text(encoding="utf-8")
# Remove `.. raw:: html` blocks, which are not supported by PyPI.
readme = re.sub(r"(?m)^\.\. raw:: html\n(?:^[ \t].*\n|^[ \t]*\n)*?\n\n", "", readme)
history = re.sub(
    r":mod:|:class:|:func:", "", Path("HISTORY.rst").read_text(encoding="utf-8")
)

setup(
    long_description=readme + "\n\n" + history,
    long_description_content_type="text/x-rst",
)
