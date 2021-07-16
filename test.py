from dateparser.search_dates import search_dates, search_first_date
from dateparser.search import search_dates as sd
from dateparser import parse


text = "Сервис будет недоступен с 12 января по 30 апреля"

out = search_first_date(text)
print(out)


