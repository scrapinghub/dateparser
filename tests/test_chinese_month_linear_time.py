import pytest

from tests.linear_time import assert_fast

SETUP = """
from dateparser.conf import settings
from dateparser.languages import default_loader

def simplify(shortname, text):
    default_loader.get_locale(shortname)._simplify(text, settings=settings)
"""


@pytest.mark.parametrize("shortname", ["zh", "zh-Hans", "zh-Hant", "yue", "ja"])
@pytest.mark.parametrize("unit", ["1月", "12月", "1.5月", "1,5月", "1月 "])
def test_repeated_month_does_not_take_quadratic_time(shortname: str, unit: str) -> None:
    assert_fast(SETUP, [f"simplify({shortname!r}, {unit!r} * (45_000 // {len(unit)}))"])
