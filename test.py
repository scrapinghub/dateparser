from dateparser.search_dates import search_dates
from dateparser.search import search_dates as sd
from dateparser import parse

# THIS IS TEMPORARY FILE FOR TESTS

text = """II wojna światowa – największa wojna światowa w historii, trwająca od 1 września 1939 do 2 września 1945 (w Europie do 8 maja 1945)"""

out = search_dates(text, languages=["pl"])
print(out)



a = "1234567890"
print(a[2:-2])

# tox -e py -- tests/test_search.py