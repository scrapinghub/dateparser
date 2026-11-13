import pytest

from dateparser.conf import settings
from dateparser.languages import default_loader
from tests.linear_time import assert_fast

SETUP = """
from dateparser.conf import settings
from dateparser.languages import default_loader

def split(shortname, text):
    list(default_loader.get_locale(shortname)._sentence_split(text, settings=settings))
"""

# The punctuation that can end a sentence, in each group of splitters of
# Locale._sentence_split that needs a space or the end after it: Hindi and
# Bangla, Japanese and Chinese, Arabic and Farsi.
PUNCTUATION = {
    "hi": "|!?;",
    "bn": "|!?;",
    "ja": "。…‥.!?？！;",
    "zh": "。…‥.!?？！;",
    "yue": "。…‥.!?？！;",
    "ar": "؟!.…",
    "fa": "؟!.…",
}


@pytest.mark.parametrize("shortname", PUNCTUATION)
def test_long_punctuation_run_does_not_take_quadratic_time(shortname: str) -> None:
    characters = PUNCTUATION[shortname]
    runs = [*characters, characters]
    statements = [
        f"split({shortname!r}, {run!r} * {30_000 // len(run)} + 'x')" for run in runs
    ]
    assert_fast(SETUP, statements)


SEARCH_SETUP = """
from dateparser.search import search_dates
"""


@pytest.mark.parametrize("shortname", ["ar", "hi", "ja", "zh"])
def test_search_dates_on_a_long_punctuation_run_does_not_take_quadratic_time(
    shortname: str,
) -> None:
    character = PUNCTUATION[shortname][0]
    statement = (
        f"search_dates('ct' + {character!r} * 30_000 + 'x', languages=[{shortname!r}])"
    )
    assert_fast(SEARCH_SETUP, [statement])


# Text shaped like the lookbehinds that keep a full stop inside a date: an
# abbreviated month or weekday name, a day number before a month name, and
# "a.m."/"p.m.". Each is matched by a variable-length lookbehind, which scans
# backwards from every full stop, so a long run of them could take quadratic
# time.
IN_DATE_FULL_STOPS = [
    "jan.",  # abbreviated month name
    "fri.",  # abbreviated weekday name
    "15. november ",  # day number before a month name
    "a.m.",
    "janr. ",  # near miss: starts like a month name but is not one
    "a",  # near miss: a run of letters before the full stop of "a.m."
]


@pytest.mark.parametrize("text", IN_DATE_FULL_STOPS)
def test_full_stops_inside_dates_do_not_take_quadratic_time(text: str) -> None:
    statement = f"split('en', {text!r} * {30_000 // len(text)} + '.m.')"
    assert_fast(SETUP, [statement])


@pytest.mark.parametrize("shortname", PUNCTUATION)
def test_punctuation_runs_still_end_sentences(shortname: str) -> None:
    locale = default_loader.get_locale(shortname)
    for character in PUNCTUATION[shortname]:
        run = character * 3
        text = f"a{run} b{run} c{run}"
        assert list(locale._sentence_split(text, settings=settings)) == ["a", "b", "c"]
