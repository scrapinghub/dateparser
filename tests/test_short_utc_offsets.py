from datetime import timedelta

import pytest

from dateparser.utils import get_timezone_from_tz_string


@pytest.mark.parametrize(
    ("tz_string", "expected_offset"),
    [
        ("+08", timedelta(hours=8)),
        ("-03", -timedelta(hours=3)),
    ],
)
def test_two_digit_utc_offsets_without_minutes_are_supported(
    tz_string, expected_offset
):
    tzinfo = get_timezone_from_tz_string(tz_string)

    assert tzinfo.utcoffset(None) == expected_offset
