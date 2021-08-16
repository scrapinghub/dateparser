from dateparser.search_dates import search_dates
#from dateparser.search import search_dates

# THIS IS TEMPORARY for Debugging

x = "May 31, 8AM UTC"


out1 = search_dates(x)
print(out1)

# tox -e py -- tests/test_search_dates.py