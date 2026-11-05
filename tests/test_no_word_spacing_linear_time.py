import pytest

from tests.linear_time import assert_fast

SETUP = """
from dateparser.conf import settings
from dateparser.languages import default_loader
from dateparser.languages.dictionary import Dictionary

keep_case = settings.replace(NORMALIZE=False)

def split_relative(shortname, text):
    dictionary = Dictionary(default_loader.get_locale(shortname).info, settings)
    dictionary._get_split_relative_regex_cache().split(text)

def simplify(shortname, text, normalize):
    locale = default_loader.get_locale(shortname)
    locale._simplify(text, settings=settings if normalize else keep_case)
"""

# The languages written without spaces between words.
LANGUAGES = ["ja", "zh", "zh-Hans", "zh-Hant", "yue"]


# Every simplification starts with a number, and a regular expression looks
# for the text after it before it tries one, so the number has to be followed
# by one of the words the simplifications of these languages expect.
UNITS = ["年", "月", "日", "時", "时", "点", "分", "秒", "週", "周"]


@pytest.mark.parametrize("normalize", [True, False])
@pytest.mark.parametrize("shortname", LANGUAGES)
def test_simplify_digit_run_does_not_take_quadratic_time(
    shortname: str, normalize: bool
) -> None:
    # Japanese takes a long run to show.
    size = 80_000 if shortname == "ja" else 40_000
    assert_fast(
        SETUP,
        [
            f"simplify({shortname!r}, {digit!r} * {size} + {unit!r}, {normalize})"
            for digit in ("1", "٣")
            for unit in UNITS
        ],
    )


@pytest.mark.parametrize("shortname", ["ar", "fa", "hi", "bn", "ja"])
def test_translate_numerals_of_a_long_run(shortname: str) -> None:
    # int() refuses a string of more than 4300 digits.
    assert_fast(
        SETUP,
        [
            "from dateparser.languages import default_loader as loader\n"
            f"locale = loader.get_locale({shortname!r})\n"
            f"assert locale._translate_numerals({digits!r} * 100_000) == "
            f"{digits!r} * 100_000"
            for digits in ("1",)
        ],
    )


@pytest.mark.parametrize("shortname", LANGUAGES)
def test_split_relative_digit_run_does_not_take_quadratic_time(shortname: str) -> None:
    assert_fast(
        SETUP,
        [
            f"split_relative({shortname!r}, {digit!r} * 12_000 + {tail!r})"
            for digit in ("9", "٣")
            for tail in ("", "x")
        ],
    )
