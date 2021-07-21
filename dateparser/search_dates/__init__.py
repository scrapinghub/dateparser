from dateparser.search_dates.search import DateSearch
from dateparser.conf import apply_settings


_search_dates = DateSearch()


@apply_settings
def search_dates(text, languages=None, settings=None):
    result = _search_dates.search_dates(
        text=text, languages=languages, settings=settings
    )

    dates = result.get('Dates')
    return dates


@apply_settings
def search_first_date(text, languages=None, settings=None):
    result = _search_dates.search_dates(
        text=text, languages=languages, limit_date_search_results=1, settings=settings
    )
    dates = result.get('Dates')
    return dates
