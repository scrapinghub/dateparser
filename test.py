from dateparser.search_dates import search_dates

# THIS IS TEMPORARY FILE FOR TESTS

text = """of 629"""

out1 = search_dates(text)
print(out1)



# tox -e py -- tests/test_search_dates.py