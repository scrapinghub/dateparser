import concurrent.futures
import random
from datetime import datetime

import dateparser
from tests import BaseTestCase

RELATIVE = {'RELATIVE_BASE': datetime(2014, 9, 15, 10, 30)}

TEST_DATA = [
    {'ds': 'Tue May 07, 2018 10:55 PM', 'expected': datetime(2018, 5, 7, 22, 55), 'loc': 'en'},
    {'ds': '2018-10-07T22:55:01', 'expected': datetime(2018, 10, 7, 22, 55, 1), 'loc': 'en'},
    {'ds': '2018-Oct-11', 'expected': datetime(2018, 10, 11, 0, 0), 'loc': 'en'},
    {'ds': '12.04.2018', 'expected': datetime(2018, 12, 4, 0, 0), 'loc': 'en'},
    {'ds': '12-10-2018 20:13', 'expected': datetime(2018, 12, 10, 20, 13), 'loc': 'en'},
    {'ds': '03.04.2019', 'expected': datetime(2019, 4, 3, 0, 0), 'loc': 'en-150'},
    {'ds': 'on Tue October 7, 2019 04:55 PM', 'expected': datetime(2019, 10, 7, 16, 55), 'loc': 'en-150'},
    {'ds': '2019Oct8', 'expected': datetime(2019, 10, 8, 0, 0), 'loc': 'en-150'},
    {'ds': '07.03.2020 - 11:13', 'expected': datetime(2020, 3, 7, 11, 13), 'loc': 'ru'},
    {'ds': '9 Авг. 2020 17:11:01', 'expected': datetime(2020, 8, 9, 17, 11, 1), 'loc': 'ru'},
    {'ds': '07.01.2020', 'expected': datetime(2020, 1, 7, 0, 0), 'loc': 'ru'},
    {'ds': 'yesterday 11:00', 'expected': datetime(2014, 9, 14, 11), 'loc': 'en', 'extra': RELATIVE},
    {'ds': '13 days ago', 'expected': datetime(2014, 9, 2, 10, 30), 'loc': 'en', 'extra': RELATIVE},
           ] * 180

random.shuffle(TEST_DATA)


class TestConcurrency(BaseTestCase):

    def test_concurrency(self):
        with concurrent.futures.ThreadPoolExecutor() as executor:

            results = list(executor.map(self.concurrency_test, TEST_DATA))
            results_with_error = [(r['ds'], r['error']) for r in results if r['error']]
            self.assertEqual([], results_with_error,
                             f'{len(results_with_error)} Threads failed with errors:\n{set(results_with_error)}')

            wrong_results = [str(r) for r in results if (r['expected'] != r['date'])]
            w_r_output = '\n'.join(wrong_results)
            self.assertEqual([], wrong_results,
                             f'{len(wrong_results)} Threads returned wrong date time:\n{w_r_output}')

    @staticmethod
    def concurrency_test(data_for_test):
        try:
            date_string = data_for_test['ds']
            date = dateparser.parse(date_string, locales=[data_for_test['loc']],
                                    settings=data_for_test.get('extra'))
            if date:
                data_for_test['date'] = date
                data_for_test['error'] = None
        except Exception as error:
            data_for_test['error'] = str(error)
            data_for_test['date'] = None
        finally:
            return data_for_test
