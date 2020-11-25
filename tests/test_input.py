from unittest.mock import patch

from dateparser import parse
from tests import BaseTestCase


class InputTest(BaseTestCase):

    def _test_ignored_input(self, input_text):
        with patch('dateparser._default_parser', ) as mock_parser:
            result = parse(input_text)
        mock_parser.get_date_data.assert_not_called()
        self.assertEqual(result, None)

    def empty_input_test(self):
        self._test_ignored_input('')

    def whitespace_input_test(self):
        self._test_ignored_input(' \t\n\r\f\v\x00')
