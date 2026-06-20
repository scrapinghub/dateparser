import pytest

from dateparser import DateDataParser
from dateparser.conf import SettingValidationError


def test_cache_size_limit_rejects_negative_values():
    with pytest.raises(
        SettingValidationError,
        match="CACHE_SIZE_LIMIT cannot be negative",
    ):
        DateDataParser(settings={"CACHE_SIZE_LIMIT": -1})
