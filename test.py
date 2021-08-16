from dateparser.search_dates import search_dates
# from dateparser.search import search_dates
import pytz

# THIS IS TEMPORARY for Debugging

x = "May 31, 8am UTC"

out1 = search_dates(x)
print(out1[0][1])

# tox -e py -- tests/test_search_dates.py
