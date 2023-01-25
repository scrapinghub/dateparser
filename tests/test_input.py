from dateparser import parse
from tests import BaseTestCase

class _test(BaseTestCase):
    def test_A(self):
        #empty input
        self.assertFalse(parse(''))

    def test_B(self):
        #single whitespace
        self.assertFalse(parse(' '))

    def test_C(self):
        #multiple whitespaces
        self.assertFalse(parse('      '))

    def test_D(self):
        #tabs
        self.assertFalse(parse('    '))
    
    def test_E(self):
        #escape character
        self.assertFalse(parse('\n'))