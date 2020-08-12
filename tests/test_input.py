from dateparser import parse
from tests import BaseTestCase

class InputTest(BaseTestCase):
    def empty_input_test(self):
        result = parse('')
        self.assertEqual(result, None)

    def whitespace_input_test(self):
        result = parse(' \t\n\r\f\v\x00')
        self.assertEqual(result, None)
