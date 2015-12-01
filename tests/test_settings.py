from tests import BaseTestCase

from dateparser.conf import settings
from dateparser.conf import apply_settings

def test_function(settings=None):
    return settings


class SettingsTest(BaseTestCase):

    def setUp(self):
        super(SettingsTest, self).setUp()
        self.default_settings = settings

    def test_apply_settings_should_return_default_settings_when_no_settings_are_supplied_to_the_decorated_function(self):
        test_func = apply_settings(test_function)
        self.assertEqual(test_func(), self.default_settings)

    def test_apply_settings_should_return_non_default_settings_when_settings_are_supplied_to_the_decorated_function(self):
        test_func = apply_settings(test_function)
        self.assertNotEqual(test_func(settings={'PREFER_DATES_FROM': 'past'}), self.default_settings)

    def test_apply_settings_should_not_create_new_settings_when_same_settings_are_supplied_to_the_decorated_function_more_than_once(self):
        test_func = apply_settings(test_function)
        settings_once = test_func(settings={'PREFER_DATES_FROM': 'past'})
        settings_twice = test_func(settings={'PREFER_DATES_FROM': 'past'})
        self.assertEqual(settings_once, settings_twice)

    def test_apply_settings_should_return_default_settings_when_called_with_no_settings_after_once_called_with_settings_supplied_to_the_decorated_function(self):
        test_func = apply_settings(test_function)
        settings_once = test_func(settings={'PREFER_DATES_FROM': 'past'})
        settings_twice = test_func()
        self.assertNotEqual(settings_once, self.default_settings)
        self.assertEqual(settings_twice, self.default_settings)
