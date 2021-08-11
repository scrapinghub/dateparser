from dateparser.search_dates import DateSearch, search_dates

# THIS IS TEMPORARY for Debugging

text = """need of -43.4 30"""

out1 = search_dates(text, languages=["en"], settings=None)
print(out1)



# tox -e py -- tests/test_search_dates.py