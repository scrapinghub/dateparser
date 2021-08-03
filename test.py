from dateparser.search_dates import search_dates

# THIS IS TEMPORARY FILE FOR TESTS

text = """The following isn't a correct date 100M"""

out1 = search_dates(text, languages=['en'])
print(out1)



# tox -e py -- tests/test_search_dates.py