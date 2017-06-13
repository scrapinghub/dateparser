from nose_parameterized import parameterized, param
from tests import BaseTestCase
from dateparser.search import ExactLanguageSearch


class TestTranslateSearch(BaseTestCase):

    def setUp(self):
        super(TestTranslateSearch, self).setUp()
        self.els = ExactLanguageSearch()

    @parameterized.expand([
        param('en', 'Game 1 is July 12, 2017. Game 2 on July 13th. Game 3 on July 15th',
              (['july 12, 2017', 'july 13th', 'july 15th'],
               ['July 12, 2017', 'on July 13th', 'on July 15th'])),
        param('en', 'I will meet you tomorrow at noon',
              (['in 1 day 12:00'], ['tomorrow at noon'])),
        param('en', 'January 3, 2017 - February 1st',
              (['january 3, 2017', 'february 1st'], ['January 3, 2017', 'February 1st'])),
        param('en', 'in a minute',
              (['in 1 minute'], ['in a minute'])),
        param('en', 'July 13th. July 14th',
              (['july 13th', 'july 14th'], ['July 13th', 'July 14th'])),
        param('en', 'July 13th, July 14th',
              (['july 13th', 'july 14th'], ['July 13th', 'July 14th'])),
        param('en', 'July 13th July 14th',
              (['july 13th', 'july 14th'], ['July 13th', 'July 14th'])),
        ])
    def test_search(self, shortname, string, expected):
        result = self.els.search(shortname, string)
        self.assertEqual(result, expected)



