from dateparser.search_dates import search_dates

# THIS IS TEMPORARY for Debugging

text = """2021-08-04T14:21:37&#x2B;05:30"""

out1 = search_dates(text)
print(out1)



# tox -e py -- tests/test_search_dates.py