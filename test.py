from dateparser.search_dates import DateSearch, search_dates

# THIS IS TEMPORARY for Debugging

text = """15 de outubro de 1936"""

search_dates = DateSearch()
out1 = search_dates.search_parse(text, "pt", settings=None)
print(out1)



# tox -e py -- tests/test_search_dates.py