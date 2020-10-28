from datetime import datetime

import pytest

from dateparser.date import DateData


class TestDateData:

    def test_get_item_like_dict(self):
        date = datetime(year=5432, month=3, day=1)
        dd = DateData(date_obj=date, period='day', locale='de')
        assert dd['date_obj'] == date
        assert dd['period'] == 'day'
        assert dd['locale'] == 'de'
        assert dd['locale'] == 'de'

    def test_get_item_like_dict_keyerror(self):
        dd = DateData(date_obj=None, period='day', locale='de')
        with pytest.raises(KeyError) as e:
            date_obj = dd['date']
            assert e == 'date'
            assert not date_obj

    def test_set_item_like_dict(self):
        dd = DateData()
        assert dd.date_obj is None

        date = datetime(year=5432, month=3, day=1)
        dd['date_obj'] = date
        assert dd.date_obj == date

    def test_set_item_like_dict_keyerror(self):
        dd = DateData()
        with pytest.raises(KeyError) as e:
            dd['date'] = datetime(year=5432, month=3, day=1)
            assert e == 'date'

    @pytest.mark.parametrize(
        "date,period,locale",
        [
            (datetime(year=2020, month=10, day=28), 'day', 'en'),
            (datetime(year=2014, month=5, day=29), 'day', 'es'),
            (datetime(year=1994, month=8, day=1), 'month', 'ca'),
            (datetime(year=2033, month=10, day=12), 'month', None),
            (None, 'day', None),
            (None, 'year', 'fr'),
        ],
    )
    def test_repr(self, date, period, locale):
        dd = DateData(date_obj=date, period='day', locale='en')
        assert dd.__repr__() == "DateData(date_obj={}, period='day', locale='en')".format(
            date.__repr__() if date else 'None'
        )
