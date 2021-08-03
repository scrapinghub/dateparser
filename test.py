from dateparser.search_dates import search_dates

# THIS IS TEMPORARY FILE FOR TESTS

text = """DECEMBER 21 19.87 87"""

out1 = search_dates(text, languages=['en'])
print(out1)


"""

print("123456789")
from dateparser.search import search_dates, DateSearchWithDetection
from dateparser.conf import apply_settings

# THIS IS TEMPORARY FILE FOR TESTS

text = "2014. July 12th, July 13th, July 14th"

@apply_settings
def main(settings):
    print(DateSearchWithDetection().search.search_parse(shortname="en",text=text, settings=settings))

main()

"""

# tox -e py -- tests/test_search_dates.py