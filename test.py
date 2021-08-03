from dateparser.search_dates import search_dates

# THIS IS TEMPORARY FILE FOR TESTS

text = """10 Febbraio 2020  15:00 ciao moka"""

out1 = search_dates(text)
print(out1)



# tox -e py -- tests/test_search_dates.py