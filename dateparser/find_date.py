from datetime import datetime
import logging
import re
from typing import List, Optional

from dateparser.conf import apply_settings
from dateparser.date import DateDataParser
from dateparser.languages.loader import LocaleDataLoader
from dateparser.search.search import DateSearchWithDetection


LANGUAGES = set(LocaleDataLoader().get_locale_map())
_bad_date_re = re.compile(
    # whole dates we black-list (can still be parts of valid dates)
    '^(' + '|'.join([
        r'\d{1,3}',  # less than 4 digits
        r'#\d+',  # this is a sequence number
        # some common false positives
        # (https://github.com/scrapinghub/dateparser/issues/568)
        r'[-/.]+',  # bare separators parsed as current date
        r'\w\.?',  # one letter (with optional dot)
        'an',
    ]) + ')$')
_date_separator = re.compile(r'[ ,|\(\)@]')  # never part of the date
_drop_words = {'on', 'at', 'of', 'a'}  # cause annoying false positives
_date_search = DateSearchWithDetection()


@apply_settings
def find_date(
        text: str, *,
        languages: Optional[List[str]],
        settings,
        max_join: int = 7,
        ) -> Optional[datetime]:
    """ Look for a date in the string, return the first date that is parsed.
    This is used instead of search_dates from dateparser, because it has more
    predictable performance and gets more dates correct, although it's still
    not perfect.
    Approach:
    - split the date into tokens using _date_separator
    - move over tokens and try to parse multiple tokens joined with
      dateparser.parse, and return the first date. At each position start with
      the longest n-gram, to parse the most complete date (max_join sets the
      maximum length of the ngram)
    """
    languages = list(languages or [])
    languages = [l for l in languages if l in LANGUAGES]
    if not languages:
        detected = _date_search.detect_language(text=text, languages=languages)
        if detected:
            languages = [detected]
    if 'en' not in languages:
        languages.append('en')
    parser = DateDataParser(languages=languages, settings=settings)
    to_parse = [p for p in _date_separator.split(text)
                if p and p not in _drop_words]
    for i in range(len(to_parse)):
        for j in reversed(range(min(max_join, len(to_parse) - i))):
            x = ' '.join(to_parse[i: i + j + 1])
            if _bad_date_re.match(x):
                continue

            try:
                match = parser.get_date_data(x)['date_obj']
            except Exception as e:
                logging.exception(e)
            else:
                if match:
                    return match
