from dateparser.search_dates import search_dates
from dateparser.search import search_dates as sd
from dateparser import parse

# THIS IS TEMPORARY FILE FOR TESTS

text = """July 12th, 2014. July 13th, July 14th"""

out = search_dates(text, languages=["en"])
print(out)

print(sd(text, languages=["en"]))

# tox -e py -- tests/test_search.py