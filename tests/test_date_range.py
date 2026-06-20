from datetime import datetime

import pytest

from dateparser import date


@pytest.mark.parametrize("step", [{"months": 0}, {"days": -1}])
def test_date_range_rejects_steps_that_do_not_advance(step):
    with pytest.raises(ValueError, match="date_range step must be positive"):
        next(date.date_range(datetime(2014, 6, 15), datetime(2014, 6, 25), **step))
