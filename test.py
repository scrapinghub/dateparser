from dateparser.search_dates import search_dates
from dateparser.search import search_dates as sd
from dateparser import parse

# THIS IS TEMPORARY FILE FOR TESTS

text = 'July 13th, 2014 July 14th, 2014'

out = search_dates(text, languages=["en"])
print(out)


# tox -e py -- tests/test_search.py