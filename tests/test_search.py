from nose_parameterized import parameterized, param
from tests import BaseTestCase
from dateparser.search import ExactLanguageSearch


class TestExactLanguageSearch(BaseTestCase):

    def setUp(self):
        super(TestExactLanguageSearch, self).setUp()
        self.els = ExactLanguageSearch()

    @parameterized.expand([
        # general multilanguage formats (only numbers)
        param('en', "text2006.05.30  (30.05.2006) 05.05.2006text", ['2006.05.30', '30.05.2006', '05.05.2006']),
        param('en', "(2006.30.05. 30.5.2006text", ['2006.30.05', '30.5.2006']),
        param('en', "30/5/2006 2006/5/30 2006/05/30. 5/30/2006", ['30/5/2006', '2006/5/30', '2006/05/30', '5/30/2006']),
        param('en', " 30-5-2006 2006-5-30 ", ['30-5-2006', '2006-5-30']),
        param('en', " 30-05-2006 2006-05-30 28/05/2006-30/05/2006", ['30-05-2006', '2006-05-30', '28/05/2006',
                                                                     '30/05/2006']),
        param('en', " 30 - 05 - 2006, 2006 05 30, 30 / 05 / 2006 ", ['30 - 05 - 2006', '2006 05 30', '30 / 05 / 2006']),
        param('en', " 30 - 05 - 2006, 05 30 2006 text text texttext2008", ['30 - 05 - 2006', '05 30 2006', '2008']),
        param('en', " 30052006, 05302006. 20063005-2006305", ['30052006', '05302006', '20063005', '2006305']),
        param('en', " 30/05. 30/5, 5/30-5/31", ['30/05', '30/5', '5/30', '5/31']),
        ])
    def test_search(self, shortname, string, expected):
        result = self.els.final_search(shortname, string)
        self.assertEqual(result, expected)



