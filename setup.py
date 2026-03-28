import re

from setuptools import setup

introduction = re.sub(
    r":members:.+|..\sautomodule::.+|:class:|:func:|:ref:",
    "",
    open("docs/introduction.rst", encoding="utf-8").read(),
)
history = re.sub(
    r":mod:|:class:|:func:", "", open("HISTORY.rst", encoding="utf-8").read()
)

setup(
    long_description=introduction + "\n\n" + history,
)
