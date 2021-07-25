from dateparser.search_dates import search_dates
from dateparser.search import search_dates as sd
from dateparser import parse

# THIS IS TEMPORARY FILE FOR TESTS

text = """19 марта 2001, 20 марта, 21 марта был отличный день."""

out = search_dates(text, languages=["ru"])
print(out)

print(sd("19 марта 2001, 20 марта, 21 марта был отличный день."))

# tox -e py -- tests/test_search.py